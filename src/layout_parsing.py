from ultralytics import YOLO
from matplotlib import pyplot as plt
import cv2
import os
import json

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

        os.makedirs(output_dir+'/sign', exist_ok=True)
        os.makedirs(output_dir+'/pers', exist_ok=True)
        os.makedirs(output_dir+'/rslt', exist_ok=True)

        output_signature_path = os.path.join(output_dir, 'sign', filename.replace('.jpg', '.json').replace('.png', '.json'))
        output_persons_path = os.path.join(output_dir, 'pers', filename.replace('.jpg', '.json').replace('.png', '.json'))

        # Save the bounding box data to JSON files
        with open(output_signature_path, 'w') as f:
            json.dump(signature_boxes, f, indent=4)
        
        with open(output_persons_path, 'w') as f:
            json.dump(persons, f, indent=4)

        output_path = os.path.join(output_dir+'/rslt', filename)
        # Draw bounding boxes for each person and save the image
        for person_id, person_boxes in enumerate(persons):
            for box in person_boxes:
                x1, y1, x2, y2 = map(int, box["coordinates"])
                color = (0, 255, 0)  # Green color for bounding boxes
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)

                # Put the person ID label
                label = f"Person {person_id}"
                cv2.putText(annotated_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Save the annotated image
        cv2.imwrite(output_path, annotated_image)


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
