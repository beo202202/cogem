from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from image_processing import process_image
import os
import shutil
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import re

# 현재 스크립트 파일의 디렉토리 경로를 구합니다.
script_dir = os.path.dirname(os.path.abspath(__file__))

# 상대 경로를 사용하여 'firebase-adminsdk.json' 파일의 전체 경로를 구합니다.
firebase_sdk_path = os.path.join(script_dir, 'firebase-adminsdk.json')

# Firebase Admin SDK를 초기화합니다.
cred = credentials.Certificate(firebase_sdk_path)
firebase_admin.initialize_app(cred)

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
PROCESSED_FOLDER = 'processed/'

@app.route('/', methods=['GET'])
def upload_form():
    return '''
    <!doctype html>
    <html>
    <body>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="files" multiple><br>
            <input type="submit" value="Upload and Process">
        </form>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    # 기존의 파일들 삭제
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
    if os.path.exists(PROCESSED_FOLDER):
        shutil.rmtree(PROCESSED_FOLDER)
    os.makedirs(UPLOAD_FOLDER)
    os.makedirs(PROCESSED_FOLDER)
    
    uploaded_files = request.files.getlist('files')
    valid_files = [f for f in uploaded_files if f and f.filename.endswith('.png')]

    start_time = time.time()
    send_notification('이미지 추출이 시작되었습니다!')
    for idx, file in enumerate(valid_files[:15]):  # 최대 15개의 파일만 처리
        file_path = os.path.join(UPLOAD_FOLDER, "image_{:02d}.png".format(idx+1))
        file.save(file_path)
        process_image(file_path, idx)
        if idx % 5 == 0:
            # 5개의 파일을 처리할 때마다 알림을 전송
            send_notification('이미지를 추출 중입니다!')
        
    #return '업로드 및 처리가 완료되었습니다.'
    
    # 마지막으로 처리한 이미지의 인덱스를 사용하여 분류된 이미지를 모두 표시하는 웹 페이지로 리다이렉션
    return redirect(url_for('display_images', start_index=0, end_index=idx, page=1))

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

@app.route('/display_images/<int:page>', methods=['GET'])
def display_images(page):
    images_per_page = 1  # 한 페이지에 표시할 이미지 수를 설정합니다.

    # 페이지 번호에 따라 표시할 이미지의 범위를 결정합니다.
    start_index = (page - 1) * images_per_page
    end_index = start_index + images_per_page

    # 모든 처리된 이미지 폴더를 가져옵니다.
    processed_folders = sorted_nicely([f for f in os.listdir('processed') if f.startswith('image_')])

    # 페이지 범위 내의 이미지 폴더만 선택합니다.
    current_page_folders = processed_folders[start_index:end_index]

    gallery = []
    for folder in current_page_folders:
        image_folder = os.path.join('processed', folder)
        user_folder = os.path.join('processed', folder.replace('image_', 'user_'))

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

    return render_template('display_images.html', gallery=gallery, page=page, has_next=has_next, len=len)





if __name__ == "__main__":
    app.run(debug=True)
