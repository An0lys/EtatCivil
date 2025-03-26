from PIL import Image
# Load model directly
from transformers import AutoTokenizer, AutoModelForImageTextToText

tokenizer = AutoTokenizer.from_pretrained("microsoft/trocr-large-handwritten")
model = AutoModelForImageTextToText.from_pretrained("microsoft/trocr-large-handwritten")

# Load the image
image_path = "data/img_prot.php?i=0a6bba2c54.jpg"
image = Image.open(image_path)

# Tokenize the image
inputs = tokenizer(image, return_tensors="pt")

# Generate the text
outputs = model.generate(**inputs)
predicted_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(predicted_text)