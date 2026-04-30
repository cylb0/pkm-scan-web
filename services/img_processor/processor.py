import numpy
import cv2
from errors.processing import PokemonCardDetectionError


def crop_card_border(input_path: str, output_path: str):
    """Isolates a pokemon card within an image by detecting its yellow border.
    Raises:
        PokemonCardDetectionError:  If no yellow contours are found or the detected area is too small to be a card.
    """
    img = cv2.imread(input_path)

    if img is None:
        raise ValueError(f"Failed to read image at {input_path}")

    cropped_img = detect_and_crop_yellow_border(img)

    cv2.imwrite(output_path, cropped_img)


def detect_and_crop_yellow_border(img: numpy.ndarray) -> numpy.ndarray:
    # 1. HSV isolation: Targets the yellow border specifically.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_yellow = numpy.array([20, 150, 150])
    upper_yellow = numpy.array([30, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # 2. Noise reduction: Smooths edges and fills small gaps in the border.
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    kernel = numpy.ones((5, 5), numpy.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 3. Contour extraction: Finding the physical boundaries.
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise PokemonCardDetectionError("Border not found")

    # 4. Selection: Assume the largest yellow shape is the card.
    card_contour = max(contours, key=cv2.contourArea)

    # 5. Cropping: Calculate bounding box and slice the array.
    x, y, w, h = cv2.boundingRect(card_contour)
    return img[y : y + h, x : x + w]
