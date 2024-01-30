# app.py

from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from image_processing import extract_image
import os
import shutil
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import re
import cv2

# 현재 스크립트 파일의 디렉토리 경로를 구합니다.
script_dir = os.path.dirname(os.path.abspath(__file__))

# 상대 경로를 사용하여 'firebase-adminsdk.json' 파일의 전체 경로를 구합니다.
firebase_sdk_path = os.path.join(script_dir, 'firebase-adminsdk.json')

# Firebase Admin SDK를 초기화합니다.
cred = credentials.Certificate(firebase_sdk_path)
firebase_admin.initialize_app(cred)

UPLOAD_FOLDER = 'uploads/'
PROCESSED_FOLDER = 'processed/'

app = Flask(__name__)

@app.route('/', methods=['GET'])
def upload_form():
    return render_template('upload_form.html')

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
                
    action = request.form['action']
    if action == '분석하기':        
        # 마지막으로 처리한 이미지의 인덱스를 사용하여 분류된 이미지를 모두 표시하는 웹 페이지로 리다이렉션
        
        print('mode_develop')
        
        return redirect(url_for('mode_develop', start_index=0, end_index=idx, page=1))
    
    elif action == '코어 분석':
        
        print('core_analysis')
        
        selected_core = request.form.get('coreOption')
        # 코어 분석 로직
        # 예: 이미지 비교, 결과 생성 등
        return render_template('core_analysis_result.html', ...)

    return 'Invalid action'

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
    # 'lambda/' 부분을 제거합니다.
    # modified_filename = filename.replace('lambda/', '', 1)

    # 수정된 경로로 파일을 제공합니다.
    # return send_from_directory('', modified_filename)

    return send_from_directory('', filename)

def sorted_nicely(l):
    def alphanum_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]{2})', s)]
    return sorted(l, key=alphanum_key)

@app.route('/mode_develop/<int:page>', methods=['GET'])
def mode_develop(page):
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
        user_folder = os.path.join(PROCESSED_FOLDER, folder.replace('image_', 'user_'))

        # 각 폴더에서 이미지 파일을 가져와 URL을 생성합니다.
        image_files = sorted_nicely([f for f in os.listdir(image_folder) if f.startswith("extracted_")])
        user_files = sorted_nicely([f for f in os.listdir(user_folder) if f.startswith("extracted_")])

        for main_image_file in image_files:
            # 메인 이미지에 대한 URL을 생성합니다.
            main_image_url = url_for('send_file', filename=os.path.join(image_folder, main_image_file).replace("\\", "/"))

            # 현재 메인 이미지와 관련된 모든 하위 이미지를 가져옵니다.
            sub_images_url = [url_for('send_file', filename=os.path.join(user_folder, f).replace("\\", "/")) for f in user_files if f.startswith(os.path.splitext(main_image_file)[0])]

            gallery.append((main_image_url, sub_images_url))

    # 이미지가 더 있는지 확인하여 "다음" 버튼을 활성화/비활성화 합니다.
    has_next = end_index < len(processed_folders)

    total_pages = len(processed_folders) // images_per_page + (1 if len(processed_folders) % images_per_page else 0)
    return render_template('mode_develop.html', gallery=gallery, page=page, has_next=has_next, len=len, total_pages=total_pages)
    # return render_template('mode_develop.html', gallery=gallery, page=page, has_next=has_next, len=len)

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
        image_path = os.path.join(PROCESSED_FOLDER, 'user_01', image_name)

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
    
if __name__ == "__main__":
    app.run(debug=True)
