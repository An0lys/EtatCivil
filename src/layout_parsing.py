import torch
from ultralytics import YOLO

def train_yolov11_model(dataset_path, epochs=60, batch_size=16):
    # Load a model
    model = YOLO("yolo11n.pt")

    # Train the model
    model.train(
        data=f"{dataset_path}/data.yaml",  # Path to dataset configuration
        epochs=epochs,
        batch=batch_size,
        imgsz=1280,  # Image size
        project="layout_parsing",  # Project name
        name="yolov11_training",  # Experiment name
        device='cpu'
    )

if __name__ == "__main__":
    dataset_path = "../layout_dataset"  # Path to your dataset
    train_yolov11_model(dataset_path)