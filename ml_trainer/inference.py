from ultralytics import YOLO
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.getenv(
    "YOLO_MODEL_PATH", os.path.join(BASE_DIR, "models/latest_seg.pt")
)
RESULTS_DIR = os.path.join(BASE_DIR, "results")

model = YOLO(MODEL_PATH)

result = model(
    "test.jpg",
    imgsz=1024,
    save=True,
    project=RESULTS_DIR,
    name="predict1",
    exist_ok=True,
)
