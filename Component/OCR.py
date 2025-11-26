import concurrent.futures
import os
import numpy as np

# Function to extract the bounding box as (x_min, y_min, x_max, y_max)
def get_box_bounds(box):
    x_min = min(point[0] for point in box)
    y_min = min(point[1] for point in box)
    x_max = max(point[0] for point in box)
    y_max = max(point[1] for point in box)
    return x_min, y_min, x_max, y_max

# Function to check if two bounding boxes overlap or are close
def boxes_overlap(box1, box2, threshold=5):
    x1_min, y1_min, x1_max, y1_max = get_box_bounds(box1)
    x2_min, y2_min, x2_max, y2_max = get_box_bounds(box2)

    # Check if boxes overlap (or are within a threshold distance)
    if (x1_min < x2_max + threshold and x1_max > x2_min - threshold and
        y1_min < y2_max + threshold and y1_max > y2_min - threshold):
        return True
    return False

# Function to merge overlapping boxes and texts
def merge_overlapping_boxes(boxes, texts, threshold=5):
    merged_boxes = []
    merged_texts = []

    for i, box in enumerate(boxes):
        merged = False
        for j, m_box in enumerate(merged_boxes):
            if boxes_overlap(box, m_box, threshold):
                # Merge the current box into the existing merged box
                merged_boxes[j] = np.vstack([m_box, box])
                merged_texts[j] = merged_texts[j] + " " + texts[i]
                merged = True
                break
        if not merged:
            # If no merge happened, add it as a new box and text
            merged_boxes.append(box)
            merged_texts.append(texts[i])

    return merged_boxes, merged_texts

# Function to process an individual image file
def process_image(file_path, ocr):
    result = ocr.ocr(file_path)
    boxes = []
    texts = []
    
    for item in result[0]:
        if not item[1][0].startswith(('JL', 'jl', 'Jl', 'Jalan', 'jalan', 'Blok', 'Blk', 'blok', ''
                                        'Gg', 'gg', 'blok', 'blk', 'BLK', 'GG', 'JI.', 
                                        '0 Disimpan', 'Disimpan', 'Terbaru', 'Google', 
                                        'Telusuri', 'Login', 'Medan', '1 Restoran', 
                                        '@ Transportasi umum', 'p Hotel', '10mL', 
                                        'Persyaratan', 'Data peta @2024', 'Lihat topografi', 
                                        '=', '+', 'Tidak ada', 'Disimpan')) and len(item[1][0]) >= 3:
            boxes.append(item[0])
            texts.append(item[1][0])
    
    return merge_overlapping_boxes(boxes, texts)

# Define the OCR processing function for a single image file
def process_image_file(image_path, ocr_model):
    combined_box = []

    try:
        merged_boxes, merged_texts = process_image(image_path, ocr_model)
        combined_box.extend(merged_texts)
    except Exception as e:
        print(f"Error processing file {image_path}: {e}")

    return combined_box


# Example usage
# image_path = "/path/to/image_directory"  # Set your image directory path
# combined_box = process_images_in_directory(image_path)
# print("Combined Texts:", len(combined_box))