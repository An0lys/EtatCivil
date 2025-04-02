from ultralytics import YOLO
from matplotlib import pyplot as plt
import cv2
import os
import json

def find_topmost_and_bottommost(persons):
    """Find topmost and bottommost persons on the left and right sides."""
    topmost_left, topmost_left_coordinates, topmost_left_index = None, None, None
    topmost_right, topmost_right_coordinates, topmost_right_index = None, None, None
    bottommost_left, bottommost_left_coordinates, bottommost_left_index = None, None, None

    for idx, person_boxes in enumerate(persons):
        for box in person_boxes:
            if box["side"] == "right":
                if topmost_right is None or box["coordinates"][1] < topmost_right_coordinates[1]:
                    topmost_right, topmost_right_coordinates, topmost_right_index = person_boxes, box["coordinates"], idx
            elif box["side"] == "left":
                if bottommost_left is None or box["coordinates"][3] > bottommost_left_coordinates[3]:
                    bottommost_left, bottommost_left_coordinates, bottommost_left_index = person_boxes, box["coordinates"], idx
                elif topmost_left is None or box["coordinates"][1] < topmost_left_coordinates[1]:
                    topmost_left, topmost_left_coordinates, topmost_left_index = person_boxes, box["coordinates"], idx

    return topmost_left, topmost_left_index, topmost_right, topmost_right_index, bottommost_left, bottommost_left_index

def validate_nom_presence(topmost, class_id):
    """Check if a 'nom' class exists in the topmost boxes."""
    for box in topmost:
        if box["class"] == class_id:
            return True
    return False

def save_json_data(output_path, data):
    """Save data to a JSON file."""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

def annotate_and_save_image(output_path, annotated_image, persons):
    """Annotate and save the image with bounding boxes."""
    for person_id, person_boxes in enumerate(persons):
        for box in person_boxes:
            x1, y1, x2, y2 = map(int, box["coordinates"])
            color = (0, 255, 0)  # Green color for bounding boxes
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
            label = f"Person {person_id}"
            cv2.putText(annotated_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    cv2.imwrite(output_path, annotated_image)

def process_images(input_dir='../data/raw', output_dir='../data/processed', model_path='../layout/detect/train/weights/best.pt'):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the YOLO model
    model = YOLO(model_path)

    # Process the first 10 images in the input directory
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:10]
    for filename in image_files:
        image_path = os.path.join(input_dir, filename)
        results = model.predict(source=image_path, save=False)

        # Save the annotated image and bounding box data
        boxes_data = []
        for result in results:
            annotated_image = result.plot()

            # Extract bounding box information
            for box in result.boxes:
                boxes_data.append({
                    "class": box.cls.item(),  # Convert Tensor to Python scalar
                    "confidence": box.conf.item(),  # Convert Tensor to Python scalar
                    "coordinates": box.xyxy.tolist()[0],  # Convert Tensor to list
                    "side": check_side(box.xyxy.tolist()[0], annotated_image.shape[1])  # Check if the box is on the left or right side
                })

        signature_boxes = []
        for box in boxes_data:
            if box["class"] == 2:
                signature_boxes.append(box)
        
        persons = []
        for box in boxes_data:
            if box["class"] != 3:
                continue
            person_boxes = []
            person_boxes.append(box)
            for box2 in boxes_data:
                if box2["side"] != box["side"] or box2["class"] == 2:
                    continue
                if overlapping_height(box["coordinates"], box2["coordinates"]) > 0.5:
                    person_boxes.append(box2)
            persons.append(person_boxes)

        # Find topmost and bottommost persons
        topmost_left, topmost_left_index, topmost_right, topmost_right_index, bottommost_left, bottommost_left_index = find_topmost_and_bottommost(persons)

        # Merge or remove persons based on 'nom' presence
        if not validate_nom_presence(topmost_right, 1): 
            persons[bottommost_left_index] = persons[bottommost_left_index] + topmost_right
            persons[topmost_right_index] = []

        if not validate_nom_presence(topmost_left, 1): 
            persons[topmost_left_index] = []
        
        persons = [person_boxes for person_boxes in persons if person_boxes]  # Remove empty lists

        # Ensure output directories exist
        os.makedirs(output_dir+'/sign', exist_ok=True)
        os.makedirs(output_dir+'/pers', exist_ok=True)
        os.makedirs(output_dir+'/rslt', exist_ok=True)

        # Save signature and persons data to JSON
        save_json_data(os.path.join(output_dir, 'sign', filename.replace('.jpg', '.json').replace('.png', '.json')), signature_boxes)
        save_json_data(os.path.join(output_dir, 'pers', filename.replace('.jpg', '.json').replace('.png', '.json')), persons)

        # Annotate and save the image
        annotate_and_save_image(os.path.join(output_dir+'/rslt', filename), annotated_image, persons)

def overlapping_height(box1, box2):

    # Unpack the coordinates
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2

    # Calculate the overlapping height
    overlap_y = max(0, min(y2_1, y2_2) - max(y1_1, y1_2))
    min_height = min(y2_1 - y1_1, y2_2 - y1_2)

    return overlap_y/min_height

def overlapping_width(box1, box2):

    # Unpack the coordinates
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2

    # Calculate the overlapping width
    overlap_x = max(0, min(x2_1, x2_2) - max(x1_1, x1_2))
    min_width = min(x2_1 - x1_1, x2_2 - x1_2)

    return overlap_x/min_width

def check_side(box,image_width):
    # Unpack the coordinates
    x1, y1, x2, y2 = box

    # Calculate the center of the box
    center_x = (x1 + x2) / 2

    # Check if the box is on the left or right side of the image
    if center_x < 0.5*image_width:
        side = "left"
    else:
        side = "right"

    return side

if __name__ == "__main__":
    # Process all images in the raw directory and save to processed directory
    process_images()
