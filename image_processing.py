# image_processing.py

import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import logging
from werkzeug.utils import secure_filename
import glob
from skimage.metrics import structural_similarity as ssim

UPLOAD_FOLDER = 'static/uploads/'
PROCESSED_FOLDER = 'static/processed/'
READYREGIONS_FOLDER = "static/processed/ReadyRegions"


# V매트릭스 좌표
vmatrix_boxes = (615, 198, 1305, 882)

# 1920 좌표
absolute_boxes = [
    (1004, 733, 32, 32),
    (894, 733, 32, 32),
    (784, 733, 32, 32),
    (674, 733, 32, 32),
    (949, 676, 32, 32),
    (839, 676, 32, 32),
    (729, 676, 32, 32),
    (1004, 619, 32, 32),
    (894, 619, 32, 32),
    (784, 619, 32, 32),
    (674, 619, 32, 32),
    (949, 562, 32, 32),
    (839, 562, 32, 32),
    (729, 562, 32, 32),
    (1004, 505, 32, 32),
    (894, 505, 32, 32),
    (784, 505, 32, 32),
    (674, 505, 32, 32),
    (949, 448, 32, 32),
    (839, 448, 32, 32),
    (729, 448, 32, 32),
    (1004, 391, 32, 32),
    (894, 391, 32, 32),
    (784, 391, 32, 32),
    (674, 391, 32, 32),
    (949, 334, 32, 32),
    (839, 334, 32, 32),
    (729, 334, 32, 32),
    (1004, 277, 32, 32),
    (894, 277, 32, 32),
    (784, 277, 32, 32),
    (674, 277, 32, 32)
]

# 스킬 코어 좌표
classified_coords = {
    '1st': ((3, 16), (15, 29)),
    '2st': ((12, 3), (20, 11)),
    '3st': ((18, 16), (29, 29))
}

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# 큰 이미지에서 V Matrix 영역을 크롭하는 함수
def vmatrix_crop(uploaded_files):    
    ensure_dir(READYREGIONS_FOLDER)  # 경로가 존재하지 않으면 생성
    
    for idx, file in enumerate(uploaded_files):
        # 업로드된 파일을 읽음
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # 파일을 읽어서 크롭하고 저장
        large_image = cv2.imread(file_path)
        x, y, w, h = vmatrix_boxes
        vmatrix_area = large_image[y:y+h, x:x+w]
        cropped_image_path = os.path.join(READYREGIONS_FOLDER, f"vmatrix_{idx+1:02d}.png")
        cv2.imwrite(cropped_image_path, vmatrix_area)
        
        # 파일 경로를 출력 (또는 로그로 남김)
        print(f"Cropped image saved to: {cropped_image_path}")

        
def extract_regions_from_large_image(image_path, offset, boxes):
    large_image = cv2.imread(image_path)
    extracted_regions = []
    
    for box in boxes:
        x, y, w, h = box
        x += offset[0]
        y += offset[1]
        region = large_image[y:y+h, x:x+w]
        extracted_regions.append(region)

    return extracted_regions

def extract_image(image_path, file_index):
    logging.info('사각형 영역들을 추출')
    # 이미지에서 사각형 영역들을 추출하고 저장합니다.
    extracted_regions = extract_regions_from_large_image(image_path, (0, 0), absolute_boxes)

    # 추출된 영역들을 각각의 폴더에 저장합니다.
    output_folder = os.path.join(PROCESSED_FOLDER, f"image_{file_index + 1:02}")
    
    ensure_dir(output_folder)  # 경로가 존재하지 않으면 생성
    
    for idx, region in enumerate(reversed(extracted_regions)):
        output_filename = f"extracted_{idx + 1:02}.png"
        output_path = os.path.join(output_folder, output_filename)
        cv2.imwrite(output_path, region)
        
        new_img = region

        # 추출된 이미지들을 각각의 폴더에 저장합니다.
        extracted_folder = os.path.join(PROCESSED_FOLDER, f"extracted_{file_index + 1:02}")
        
        ensure_dir(extracted_folder)  # 경로가 존재하지 않으면 생성
        
        logging.info(f"이미지 추출 중: {output_path}")
        # 주어진 좌표에 따라 이미지 추출 및 저장
        classified_imgs = {}
        for sub_idx, (key, (top_left, bottom_right)) in enumerate(classified_coords.items()):
            classified_imgs[key] = new_img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            
            save_path = os.path.join(extracted_folder, f"extracted_{idx + 1:02}_{sub_idx + 1:02}.png")
            save_result = cv2.imwrite(save_path, classified_imgs[key])
            if not save_result:
                logging.info(f"Error saving to {save_path}")
                continue

def compare_image_with_folder(image_path, folder_path):
    """
    주어진 이미지와 폴더의 경로를 받아 이미지 비교를 하는 함수
    """
    logging.info(f"이미지 비교 시작: {image_path}")
    
    # 이미지 비교를 위한 기준 이미지 로드
    base_image = cv2.imread(image_path)
    if base_image is None:
        logging.error(f"기준 이미지 로딩 실패: {image_path}")
        return False  # 또는 적절한 예외 처리
    
    for filename in os.listdir(folder_path):
        folder_compare_path = os.path.join(folder_path, filename)
        compare_image = cv2.imread(folder_compare_path)
        
        if compare_image is None:
            logging.error(f"비교 이미지 로딩 실패: {folder_compare_path}")
            continue  # 다음 이미지로 넘어감
        
        # 이미지 크기가 같은지 확인
        if base_image.shape == compare_image.shape:
            # 두 이미지의 차이를 계산
            difference = cv2.subtract(base_image, compare_image)
            if not np.any(difference):
                logging.info(f"일치하는 이미지 발견: {image_path} == {folder_compare_path}")
                return folder_compare_path
                return True
            else:
                logging.info(f"일치하지 않음: {image_path} != {folder_compare_path}")
    
    logging.info(f"일치하는 이미지 없음: {image_path}")
    return False

def extract_and_compare_images(image_path, folder_path, highest_ssim):
    """
    주어진 이미지를 폴더의 모든 이미지와 비교하여 가장 유사한 이미지를 찾습니다,
    해당 이미지의 SSIM 점수를 부모 이미지 경로와 함께 반환합니다,
    단, SSIM 점수가 0.8보다 큰 경우에만 반환합니다.
    """
    logging.info(f"이미지 비교 시작: {image_path}")
    
    base_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if base_image is None:
        logging.error(f"기준 이미지 로딩 실패: {image_path}")
        return None, 0  # 또는 적절한 예외 처리

    # highest_ssim = 0.8  # 초기값을 0.8로 설정하여 이 이상의 점수만 고려되도록 합니다.
    most_similar_image_path = None

    for filename in os.listdir(folder_path):
        folder_compare_path = os.path.join(folder_path, filename)
        compare_image = cv2.imread(folder_compare_path, cv2.IMREAD_GRAYSCALE)
        
        if compare_image is None:
            logging.error(f"비교 이미지 로딩 실패: {folder_compare_path}")
            continue
        
        if base_image.shape != compare_image.shape:
            logging.info(f"이미지 크기 불일치: {folder_compare_path}")
            continue
        
        # SSIM 계산
        score, _ = ssim(base_image, compare_image, full=True)
        
        if score > highest_ssim:
            highest_ssim = score
            most_similar_image_path = folder_compare_path

    if most_similar_image_path:
        logging.info(f"가장 유사한 이미지: {most_similar_image_path} (SSIM: {highest_ssim})")
        return most_similar_image_path, highest_ssim
    else:
        logging.info("SSIM 0.8 이상에서 일치하는 이미지 없음")
        return False
        # return None, 0
