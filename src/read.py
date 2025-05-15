
from PIL import Image
import numpy as np
import json
import csv
import requests

from transformers import AutoTokenizer, AutoModelForImageTextToText

tokenizer = AutoTokenizer.from_pretrained("microsoft/trocr-small-handwritten")
model = AutoModelForImageTextToText.from_pretrained("microsoft/trocr-small-handwritten")

img_path = "../data/raw/5b8f64eb4d.jpg"
pers_boxs = "../data/processed/pers/5b8f64eb4d.json"


def extract_text_from_box(image, box):
    """Extract text from a bounding box using TrOCR."""
    x1, y1, x2, y2 = map(int, box["coordinates"])
    cropped_image = image[y1:y2, x1:x2]

    pil_image = Image.fromarray(cropped_image)
    return pil_image


if __name__ == "__main__":
    # Load the image
    image = Image.open(img_path)
    image = image.convert("RGB")
    image = np.array(image)

    # Load the bounding boxes from the JSON file
    with open(pers_boxs, 'r') as f:
        persons = json.load(f)

    # Iterate through the bounding boxes and extract text
    for i, person in enumerate(persons):
        print("Person ID:", i)
        for box in person:
            pil_img = extract_text_from_box(image, box)
            # Save the cropped image temporarily
            temp_image_path = "temp_image.png"
            pil_img.save(temp_image_path)
            
            # Pass the file path directly to the image_to_text method
            pixel_values = processor(images=image, return_tensors="pt").pixel_values
            generated_ids = model.generate(pixel_values)
            generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            print("Extracted Text:", generated_text)