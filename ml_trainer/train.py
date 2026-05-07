from ultralytics import YOLO
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config/data.yml")
PROJECT_PATH = os.path.join(BASE_DIR, "runs")

model = YOLO("yolov8n-seg.pt")
model.info()

results = model.train(
    data=CONFIG_PATH,
    project=PROJECT_PATH,
    name=os.getenv("YOLO_RUN_NAME", "v1"),
    epochs=300,
    imgsz=1024,
    batch=4,
    workers=0,
    patience=100,
    mosaic=1.0,
    mixup=0.2,
    scale=0.5,
    degrees=30.0,
    fliplr=0.5,
    box=7.5,
    overlap_mask=False,
    lr0=0.01,
    close_mosaic=20,
    perspective=0.0001,
)
