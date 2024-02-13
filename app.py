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
                
@app.route('/upload', methods=['POST'])
def upload_file():
    # 기존의 파일들 삭제 후 폴더 유뮤 확인 체크 생성
    clear_folder(UPLOAD_FOLDER)
    clear_folder(PROCESSED_FOLDER)
    
    uploaded_files = request.files.getlist('files')
    logging.info(f"Uploaded files: {uploaded_files}")
    
    valid_files = [f for f in uploaded_files if f and f.filename.endswith('.png')]

    start_time = time.time()
    send_notification('이미지 분석 시작!')
    for idx, file in enumerate(valid_files[:15]):  # 최대 15개의 파일만 처리
        logging.info('1')
        file_path = os.path.join(UPLOAD_FOLDER, "image_{:02d}.png".format(idx+1))
        logging.info('2')
        file.save(file_path)
        logging.info('3')
        extract_image(file_path, idx)
        if idx % 5 == 0:
            # 5개의 파일을 처리할 때마다 알림을 전송
            send_notification('이미지를 추출 중입니다!')
                
    action = request.form['action']
    if action == '분석하기':        
        # 마지막으로 처리한 이미지의 인덱스를 사용하여 분류된 이미지를 모두 표시하는 웹 페이지로 리다이렉션
        
        logging.info('분석하기')
        
        # 기존 코드
        return redirect(url_for('analyze', start_index=0, end_index=idx, page=1))
    
        # 2번째 코드
        # 처리 결과를 HTML 형식으로 반환
        # result_html = "<p>개발자 모드 결과 표시</p>"  # 결과에 따라 동적으로 HTML 생성
        # return jsonify(html=result_html)
        
        # 3번째 코드
        # page = 1
        # gallery = [...]  # 갤러리 데이터
        # rendered_html = render_template('analyze.html', page=page, gallery=gallery)
        # return jsonify(html=rendered_html)
        
    elif action == '코어 정보 확인':
    
        logging.info('코어 정보 확인')
        
        return 0;
    
    elif action == '코어 분석':
        
        logging.info('코어 분석')
        
        selected_core = request.form.get('coreOption')
        # 코어 분석 로직
        # 예: 이미지 비교, 결과 생성 등
        # return render_template('core_analysis_result.html', ...)
    
        # HTML 콘텐츠 렌더링
        rendered_html = render_template('core_analysis_result.html', ...)
        # JSON 형식으로 반환
        return jsonify(html=rendered_html)

    elif action == '테스트':
        
        logging.info('테스트')
        
        # return redirect(url_for('test', start_index=0, end_index=idx, page=1))
        
        rendered_html = render_template('analyze2.html', start_index=0, end_index=idx, page=1)
        return jsonify(html=rendered_html)
    
        # 파일 처리 로직
        uploaded_files = request.files.getlist('files')
        # 간단한 예시로 파일 이름을 출력하고 파일을 저장합니다.
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                logging.info(f"File saved: {file_path}")

        # 분석 결과를 위한 가상 데이터
        # 실제 상황에서는 여기에 분석 로직 결과를 사용합니다.
        page = 1
        has_next = False
        total_pages = 1

        # analyze.html을 렌더링하고 결과를 반환합니다.
        # rendered_html = render_template('analyze.html', page=page, gallery=gallery, has_next=has_next, total_pages=total_pages)
        # return jsonify(html=rendered_html)
        
        gallery = [...]  # 갤러리 데이터 생성
        gallery_length = len(gallery)  # 갤러리의 길이 계산
        rendered_html = render_template('analyze2.html', page=page, gallery=gallery, gallery_length=gallery_length, has_next=has_next, total_pages=total_pages)
        return jsonify(html=rendered_html)

    return 'Invalid action'

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

@app.route('/analyze/<int:page>', methods=['GET'])
def analyze(page):
    images_per_page = 1  # 한 페이지에 표시할 이미지 수를 설정합니다.

    # 페이지 번호에 따라 표시할 이미지의 범위를 결정합니다.
    start_index = (page - 1) * images_per_page
    end_index = start_index + images_per_page

    # 모든 처리된 이미지 폴더를 가져옵니다.
    processed_folders = sorted_nicely([f for f in os.listdir(PROCESSED_FOLDER) if f.startswith('image_')])

    # 페이지 범위 내의 이미지 폴더만 선택합니다.
    current_page_folders = processed_folders[start_index:end_index]

    gallery = []
    for folder in current_page_folders:
        image_folder = os.path.join(PROCESSED_FOLDER, folder)
        extracted_folder = os.path.join(PROCESSED_FOLDER, folder.replace('image_', 'extracted_'))

        # 각 폴더에서 이미지 파일을 가져와 URL을 생성합니다.
        image_files = sorted_nicely([f for f in os.listdir(image_folder) if f.startswith("extracted_")])
        extracted_files = sorted_nicely([f for f in os.listdir(extracted_folder) if f.startswith("extracted_")])

        for main_image_file in image_files:
            # 메인 이미지에 대한 URL을 생성합니다.
            main_image_url = url_for('send_file', filename=os.path.join(image_folder, main_image_file).replace("\\", "/"))

            # 현재 메인 이미지와 관련된 모든 하위 이미지를 가져옵니다.
            sub_images_url = [url_for('send_file', filename=os.path.join(extracted_folder, f).replace("\\", "/")) for f in extracted_files if f.startswith(os.path.splitext(main_image_file)[0])]

            gallery.append((main_image_url, sub_images_url))

    # 이미지가 더 있는지 확인하여 "다음" 버튼을 활성화/비활성화 합니다.
    has_next = end_index < len(processed_folders)

    total_pages = len(processed_folders) // images_per_page + (1 if len(processed_folders) % images_per_page else 0)
    return render_template('analyze.html', gallery=gallery, page=page, has_next=has_next, len=len, total_pages=total_pages)
    # return render_template('analyze.html', gallery=gallery, page=page, has_next=has_next, len=len)
    
@app.route('/test/<int:page>', methods=['GET'])
def test(page):
    # 기존의 파일들 삭제 후 폴더 유뮤 확인 체크 생성
    clear_folder(UPLOAD_FOLDER)
    clear_folder(PROCESSED_FOLDER)
    
    uploaded_files = request.files.getlist('files')
    valid_files = [f for f in uploaded_files if f and f.filename.endswith('.png')]

    start_time = time.time()
    send_notification('이미지 분석 시작!')
    for idx, file in enumerate(valid_files[:15]):  # 최대 15개의 파일만 처리
        file_path = os.path.join(UPLOAD_FOLDER, "image_{:02d}.png".format(idx+1))
        file.save(file_path)
        extract_image(file_path, idx)
        if idx % 5 == 0:
            # 5개의 파일을 처리할 때마다 알림을 전송
            send_notification('이미지를 추출 중입니다!')
            
    images_per_page = 1  # 한 페이지에 표시할 이미지 수를 설정합니다.

    # 페이지 번호에 따라 표시할 이미지의 범위를 결정합니다.
    start_index = (page - 1) * images_per_page
    end_index = start_index + images_per_page

    # 모든 처리된 이미지 폴더를 가져옵니다.
    processed_folders = sorted_nicely([f for f in os.listdir(PROCESSED_FOLDER) if f.startswith('image_')])

    # 페이지 범위 내의 이미지 폴더만 선택합니다.
    current_page_folders = processed_folders[start_index:end_index]

    gallery = []
    for folder in current_page_folders:
        image_folder = os.path.join(PROCESSED_FOLDER, folder)
        extracted_folder = os.path.join(PROCESSED_FOLDER, folder.replace('image_', 'extracted_'))

        # 각 폴더에서 이미지 파일을 가져와 URL을 생성합니다.
        image_files = sorted_nicely([f for f in os.listdir(image_folder) if f.startswith("extracted_")])
        extracted_files = sorted_nicely([f for f in os.listdir(extracted_folder) if f.startswith("extracted_")])

        for main_image_file in image_files:
            # 메인 이미지에 대한 URL을 생성합니다.
            main_image_url = url_for('send_file', filename=os.path.join(image_folder, main_image_file).replace("\\", "/"))

            # 현재 메인 이미지와 관련된 모든 하위 이미지를 가져옵니다.
            sub_images_url = [url_for('send_file', filename=os.path.join(extracted_folder, f).replace("\\", "/")) for f in extracted_files if f.startswith(os.path.splitext(main_image_file)[0])]

            gallery.append((main_image_url, sub_images_url))

    # 이미지가 더 있는지 확인하여 "다음" 버튼을 활성화/비활성화 합니다.
    has_next = end_index < len(processed_folders)

    total_pages = len(processed_folders) // images_per_page + (1 if len(processed_folders) % images_per_page else 0)
    return render_template('analyze2.html', gallery=gallery, page=page, has_next=has_next, len=len, total_pages=total_pages)
    # return render_template('analyze.html', gallery=gallery, page=page, has_next=has_next, len=len)


@app.route('/core_analysis', methods=['POST'])
def core_analysis():
    selected_core = request.form.get('coreOption')
    valid_files = []  # 유효한 파일 리스트

    # 이미지 추출 로직
    for idx, file in enumerate(valid_files[:15]):  # 예시로 15개 이미지를 처리
        file_path = os.path.join(UPLOAD_FOLDER, f"image_{idx+1:02}.png")
        extract_image(file_path, idx)  # 이미지 추출

    # 'Common_Core' 폴더와 'Hardened_Core/Eunwol' 폴더 경로 정의
    common_core_path = os.path.join(script_dir, 'Common_Core')
    eunwol_core_path = os.path.join(script_dir, 'Hardened_Core', 'Eunwol')

    # 이미지 비교 로직
    images = []
    for idx in range(1, 16):  # 추출된 이미지를 비교
        image_name = f"extracted_{idx:02}.png"
        image_path = os.path.join(PROCESSED_FOLDER, 'extracted_01', image_name)

        if selected_core == 'Eunwol':
            if compare_with_folder(image_path, common_core_path):
                images.append((image_name, ''))
            else:
                matched_image = compare_with_folder(image_path, eunwol_core_path, return_matched=True)
                images.append((image_name, matched_image))

    return render_template('core_analysis_result.html', images=images)

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
        


@app.route('/test_compare_images', methods=['POST'])
def test_compare_images():
    # Assuming the selected class is sent as a form data or part of a JSON payload
    # For form data
    selected_occupation = request.form.get('occupation') or request.json.get('occupation')
    # For JSON data
    # selected_occupation = request.json.get('selectedOption')
    
    # For form data
    selected_class = request.form.get('className') or request.json.get('selectedClass')
    
    # uploaded_files = request.files.getlist('files')
    base_screenshot_path = r'static\processed'
    common_nodes_folder = r'static\nodes\common_nodes'
    special_nodes_folder = r'static\nodes\special_nodes'
    # Dynamically construct the skill_nodes_folder path based on the selected class
    skill_nodes_folder = os.path.join('static', 'nodes', 'skill_nodes', selected_occupation, selected_class)
    # Dynamically construct the boost_nodes_folder path
    boost_nodes_folder = os.path.join('static', 'nodes', 'boost_nodes', selected_occupation, selected_class)
    # temp_folder = 'temp'
    results = []

    # temp 폴더가 존재하는지 확인하고, 없으면 생성
    # if not os.path.exists(temp_folder):
    #     os.makedirs(temp_folder)

    for i in range(1, 16):
        screenshot_folder = os.path.join(base_screenshot_path, f'image_{i:02}')
        
        if not os.path.exists(screenshot_folder):
            continue  # Skip if the folder does not exist
        
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
