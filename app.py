# app.py

from flask import Flask, jsonify, render_template, request, send_from_directory, redirect, url_for
from image_processing import extract_image, compare_image_with_folder, extract_and_compare_images
import os
import shutil
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import re
import cv2
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('app.log 파일에 저장됩니다.')
# logging.debug('디버그 메시지')
# logging.info('정보 메시지')
# logging.warning('경고 메시지')
# logging.error('에러 메시지')
# logging.critical('치명적인 에러 메시지')

# 현재 스크립트 파일의 디렉토리 경로를 구합니다.
script_dir = os.path.dirname(os.path.abspath(__file__))

# 상대 경로를 사용하여 'firebase-adminsdk.json' 파일의 전체 경로를 구합니다.
firebase_sdk_path = os.path.join(script_dir, 'firebase-adminsdk.json')

# Firebase Admin SDK를 초기화합니다.
cred = credentials.Certificate(firebase_sdk_path)
firebase_admin.initialize_app(cred)

UPLOAD_FOLDER = 'static/uploads/'
PROCESSED_FOLDER = 'static/processed/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# 이미지 변환 및 분석 결과를 저장하는 전역 변수
images_data = []

# 허용될 파일 확장자 설정
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

def clear_folder(folder_path):
    # 폴더가 존재하는지 확인
    if os.path.exists(folder_path):
        # 폴더 안의 모든 파일을 순회
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            # 파일이면 삭제
            if os.path.isfile(file_path):
                os.remove(file_path)
            # 디렉토리이면 해당 디렉토리를 재귀적으로 비움
            elif os.path.isdir(file_path):
                clear_folder(file_path)
                os.rmdir(file_path)  # 내부 파일이 삭제된 후, 빈 디렉토리 삭제
    else:
        # 폴더가 존재하지 않으면 새로 생성
        os.makedirs(folder_path)

@app.route('/core_info_check', methods=['POST'])
def core_info_check():
    logging.info('코어 정보 확인')

    # 이미지 변환 로직 수행 (예시)
    # transform_images()
    
    logging.info('파일 삭제 및 폴더 체크')
    clear_folder(UPLOAD_FOLDER)
    clear_folder(PROCESSED_FOLDER)
    
    uploaded_files = request.files.getlist('files')
    valid_files = [f for f in uploaded_files if f and f.filename.endswith('.png')]

    start_time = time.time()
    logging.info('이미지 분석 준비')
    send_notification('이미지 분석 준비')
    for idx, file in enumerate(valid_files[:15]):  # 최대 15개의 파일만 처리
        file_path = os.path.join(UPLOAD_FOLDER, "image_{:02d}.png".format(idx+1))
        file.save(file_path)
        logging.info('이미지 추출 시작')
        extract_image(file_path, idx)
        if idx % 5 == 0:
            # 5개의 파일을 처리할 때마다 알림을 전송
            send_notification('이미지를 추출 중입니다!')

    # 성공 메시지 반환
    return jsonify({"status": "success", "message": "이미지 변환 완료"})

def transform_images():
    logging.info('파일 삭제 및 폴더 체크')
    clear_folder(UPLOAD_FOLDER)
    clear_folder(PROCESSED_FOLDER)
    
    uploaded_files = request.files.getlist('files')
    logging.info(f"Uploaded files: {uploaded_files}")
    valid_files = [f for f in uploaded_files if f and f.filename.endswith('.png')]

    start_time = time.time()
    logging.info('이미지 분석 준비')
    send_notification('이미지 분석 준비')
    for idx, file in enumerate(valid_files[:15]):  # 최대 15개의 파일만 처리
        file_path = os.path.join(UPLOAD_FOLDER, "image_{:02d}.png".format(idx+1))
        file.save(file_path)
        logging.info('이미지 분석 시작')
        extract_image(file_path, idx)
        if idx % 5 == 0:
            # 5개의 파일을 처리할 때마다 알림을 전송
            send_notification('이미지를 추출 중입니다!')
    

def send_notification(message):
    # FCM 알림을 보내기 위한 메시지 객체 생성
    message_obj = messaging.Message(
        notification=messaging.Notification(
            title='이미지 추출 알림',
            body=message,
        ),
        topic='CogemLive'  # 알림을 받을 사용자들이 구독하고 있는 토픽
    )

    try:
        # FCM 알림 전송
        response = messaging.send(message_obj)
        print('Successfully sent message:', response)
        print('푸시 알림을 성공적으로 전송했습니다.')
    except Exception as e:
        print('푸시 알림을 전송하지 못했습니다:', e)

@app.route('/get_image/<path:filename>', methods=['GET'])
def send_file(filename):
    return send_from_directory('', filename)

def sorted_nicely(l):
    def alphanum_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]{2})', s)]
    return sorted(l, key=alphanum_key)

def compare_with_folder(image_path, folder_path, return_matched=False):
    # 주어진 이미지를 읽습니다.
    target_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    target_image = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # 폴더 내의 이미지를 읽습니다.
        compare_image = cv2.imread(file_path, cv2.IMREAD_COLOR)
        compare_image = cv2.cvtColor(compare_image, cv2.COLOR_BGR2GRAY)

        # 이미지 크기가 같은지 확인
        if target_image.shape == compare_image.shape:
            # 두 이미지의 차이를 계산
            difference = cv2.subtract(target_image, compare_image)
            b, g, r = cv2.split(difference)

            # 색상 채널이 모두 0인지 확인
            if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                if return_matched:
                    return filename  # 일치하는 이미지의 이름 반환
                else:
                    return True  # 단순 일치 여부 반환

    if return_matched:
        return None  # 일치하는 이미지가 없는 경우
    else:
        return False  # 일치하는 이미지가 없는 경우
        


@app.route('/compare_images', methods=['POST'])
def compare_images():
    # 선택한 클래스가 양식 데이터 또는 JSON 페이로드의 일부로 전송된다고 가정
    # form data인 경우
    selected_occupation = request.form.get('occupation') or request.json.get('occupation')
    # JSON data인 경우
    # selected_occupation = request.json.get('selectedOption')
    
    # form data인 경우
    selected_class = request.form.get('className') or request.json.get('selectedClass')
    
    # uploaded_files = request.files.getlist('files')
    base_screenshot_path = r'static\processed'
    common_nodes_folder = r'static\nodes\common_nodes'
    special_nodes_folder = r'static\nodes\special_nodes'
    # 스킬_노드_폴더 경로를 선택한 클래스에 따라 동적으로 구성
    skill_nodes_folder = os.path.join('static', 'nodes', 'skill_nodes', selected_occupation, selected_class)
    # boost_nodes_folder 경로 동적으로 구성
    boost_nodes_folder = os.path.join('static', 'nodes', 'boost_nodes', selected_occupation, selected_class)
    # temp_folder = 'temp'
    results = []

    # temp 폴더가 존재하는지 확인하고, 없으면 생성
    # if not os.path.exists(temp_folder):
    #     os.makedirs(temp_folder)

    for i in range(1, 16):
        screenshot_folder = os.path.join(base_screenshot_path, f'image_{i:02}')
        
        if not os.path.exists(screenshot_folder):
            continue  # 폴더가 존재하지 않으면 건너뛰기
        
        for filename in os.listdir(screenshot_folder):
            image_path = os.path.join(screenshot_folder, filename)
            match_info = {'image_path': image_path, 'matches': []}  # 'matches'는 각 스킬의 매치 결과를 저장
            
            # # 이미지 비교 로직을 여기에 구현
            # match = compare_image_with_folder(temp_path, common_core_folder)
            # os.remove(temp_path)  # 임시 파일 삭제

            # 스페셜 코어 이미지 비교 로직
            match = extract_and_compare_images(image_path, special_nodes_folder, 0.4)
            
            if match:
                # logging.info(f"match: {match}")
                results.append({'image_path': image_path, 'match': '빈 코어'})
            else:                    
                # 공용코어 이미지 비교 로직
                match = compare_image_with_folder(image_path, common_nodes_folder)
                
                if match:
                    results.append({'image_path': image_path, 'match': '공용 코어'})
                else:
                    # results.append({'image_path': image_path, 'match': 'No match found'})
                    # 은월 스킬 코어를 비교
                    match = compare_image_with_folder(image_path, skill_nodes_folder)
                    if match:
                        # results.append({'image_path': image_path, 'match': '스킬 코어'})
                        results.append({'image_path': match, 'match': '스킬 코어'})
                        # results.append({'folder_compare_path': match, 'match': '스킬 코어'})
                    else:
                        # 은월 강화 코어를 비교
                        base_path = image_path.replace('image', 'extracted').replace('.png', '')
                        suffixes = ['_01.png', '_02.png', '_03.png']
                        for idx, suffix in enumerate(suffixes, start=1):
                            extracted_image_path = f"{base_path}{suffix}"
                            match = extract_and_compare_images(extracted_image_path, boost_nodes_folder, 0.8)
                            if match:
                                # logging.info(f"match.most_similar_image_path: {match[0]}")
                                match_path = match[0]
                                length = len(match_path)
                                similar_image_path = match_path[:length-6] + match_path[length-4:]
                                logging.info(f"match_path: {match[0]}")
                                logging.info(f"similar_image_path: {similar_image_path}")
                                # match_info['matches'].append((f'extracted_image_path{idx}', extracted_image_path, f'강화 코어'))
                                match_info['matches'].append((f'extracted_image_path{idx}', similar_image_path, f'강화 코어'))
                            else:
                                match_info['matches'].append((f'extracted_image_path{idx}', extracted_image_path, 'not match'))

                        # 모든 비교가 완료된 후 results에 추가
                        if match_info['matches']:
                            for match in match_info['matches']:
                                match_info[match[0]] = match[1]  # 'extracted_image_path{idx}' : path 추가
                                match_info['match'] = match[2]  # 마지막 match 상태로 업데이트
                            results.append(match_info)
    
    return jsonify(results)



if __name__ == "__main__":
    app.run(debug=True)
