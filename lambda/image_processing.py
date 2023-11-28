import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

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

def process_image(image_path, file_index):
    # 이미지에서 사각형 영역들을 추출합니다.
    extracted_regions = extract_regions_from_large_image(image_path, (0, 0), absolute_boxes)

    # 추출된 영역들을 각각의 폴더에 저장합니다.
    output_folder = os.path.join('processed', f"image_{file_index + 1:02}")
    # 폴더가 없으면 생성
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for idx, region in enumerate(reversed(extracted_regions)):
        output_filename = f"extracted_{idx + 1:02}.png"
        output_path = os.path.join(output_folder, output_filename)
        cv2.imwrite(output_path, region)
        
        new_img = region

        
        # 폴더 안의 모든 이미지와 비교
        script_dir = os.path.dirname(os.path.abspath(__file__))
        eunwol_path = os.path.join(script_dir, 'Skill_Core', 'Eunwol')
        common_core_path = os.path.join(script_dir, 'Common_Core')
        folders = [eunwol_path, common_core_path]
        matched_img_path = None

        for folder in folders:
            for file_name in os.listdir(folder):
                path = os.path.join(folder, file_name)
                try:
                    compare_image = Image.open(path)
                    compare_img = np.array(compare_image)
                except Exception as e:
                    print(f"Error loading {path}: {e}")
                    continue
                
                # 이미지 크기와 내용이 동일한지 확인
                if new_img.shape == compare_img.shape and not(np.bitwise_xor(new_img, compare_img).any()):
                    matched_img_path = path
                    break

        if matched_img_path:
            print(f"Match success: {output_path} = {matched_img_path}")
            # 일치하는 이미지 보여주기
            matched_img = cv2.imread(matched_img_path, cv2.IMREAD_COLOR)
            # plt.imshow(cv2.cvtColor(matched_img, cv2.COLOR_BGR2RGB))
            # plt.title("일치하는 이미지")
            # plt.axis('off')
            # plt.show()
        else:
            # 추출된 이미지들을 각각의 폴더에 저장합니다.
            user_folder = os.path.join('processed', f"user_{file_index + 1:02}")
            # 폴더가 없으면 생성
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            
            print(f"Match fail: {output_path}")
            # 주어진 좌표에 따라 이미지 추출 및 저장
            classified_imgs = {}
            for sub_idx, (key, (top_left, bottom_right)) in enumerate(classified_coords.items()):
                classified_imgs[key] = new_img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                
                save_path = os.path.join(user_folder, f"extracted_{idx + 1:02}_{sub_idx + 1:02}.png")
                save_result = cv2.imwrite(save_path, classified_imgs[key])
                if not save_result:
                    print(f"Error saving to {save_path}")
                    continue

            # 분류된 이미지들을 보여주기 위해 matplotlib을 사용
            # fig, axes = plt.subplots(1, 3, figsize=(12, 4))
            # for ax, (key, img) in zip(axes, classified_imgs.items()):
            #     ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            #     ax.set_title(key)
            #     ax.axis('off')
            # plt.tight_layout()
            # plt.show()