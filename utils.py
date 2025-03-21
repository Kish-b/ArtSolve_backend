import numpy as np
import cv2
from PIL import Image
from io import BytesIO

def preprocess_image(image_bytes):
    image = Image.open(BytesIO(image_bytes)).convert("L")
    image = np.array(image)
    _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)
    return binary_image.tolist()
