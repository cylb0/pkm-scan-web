import numpy
import cv2
from errors.processing import PokemonCardDetectionError

CARD_ASPECT_RATIO = 63 / 88  # ~0.716  short/long
ASPECT_TOLERANCE = 0.08
MIN_CARD_AREA_RATIO = 0.05
AXIS_ALIGNMENT_THRESHOLD = 0.05


def crop_card_border(input_path: str) -> numpy.ndarray:
    """Isolates a pokemon card within an image by detecting its yellow border.
    Raises:
        ValueError if OpenCV can't read input
    """
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError(f"Failed to read image at {input_path}")

    return detect_and_crop_yellow_border(img)


def _compute_perspective_matrix(
    pts: numpy.ndarray, width: int, height: int
) -> numpy.ndarray:
    """
    Computes a transformation matrix by:
        - Ordering all 4 corners
        - Using vector norms to define output dimensions
        - Mapping original quad to a perfect rectangle
    Returns:
        Transformation matrix to cancel perspective
    """
    # Perfect rectangle
    dst = numpy.array(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
        dtype=numpy.float32,
    )

    return cv2.getPerspectiveTransform(pts, dst)


def _compute_card_dimension(quad: numpy.ndarray) -> tuple[numpy.ndarray, int, int]:
    """
    Orders 4 points of the quad and uses norm vector to compute card output dimensions
    """
    pts = _order_quad_points(quad.reshape(4, 2).astype(numpy.float32))
    tl, tr, br, bl = pts

    width = int(max(numpy.linalg.norm(br - bl), numpy.linalg.norm(tr - tl)))
    height = int(max(numpy.linalg.norm(tr - br), numpy.linalg.norm(tl - bl)))

    return pts, width, height


def _is_axis_aligned(pts: numpy.ndarray, width: int, height: int) -> bool:
    """
    Uses variations between opposing sides (norm vectors) to decides wether a
    card is tilted by perspective or not
    Returns true if the card is aligned
    """
    tl, tr, br, bl = pts
    horizontal_deviation = (
        abs(numpy.linalg.norm(tr - tl) - numpy.linalg.norm(br - bl)) / width
    )
    vertical_deviation = (
        abs(numpy.linalg.norm(tr - br) - numpy.linalg.norm(tl - bl)) / height
    )

    return (
        horizontal_deviation < AXIS_ALIGNMENT_THRESHOLD
        and vertical_deviation < AXIS_ALIGNMENT_THRESHOLD
    )


def _straighten_card(img: numpy.ndarray, quad: numpy.ndarray) -> numpy.ndarray:
    """
    Straighten a tilted card by:
        - Computing dimensions
        - Falling back to simple boundingRect logic if card is already axis aligned
        - Computing and applying a transformation matrix
    """
    pts, width, height = _compute_card_dimension(quad)

    if _is_axis_aligned(pts, width, height):
        x, y, w, h = cv2.boundingRect(quad)
        return img[y : y + h, x : x + w]

    m = _compute_perspective_matrix(pts, width, height)
    return cv2.warpPerspective(img, m, (width, height))


def _order_quad_points(pts: numpy.ndarray) -> numpy.ndarray:
    """
    Sorts 4 points by:
        - Retrieving a centroid for those points
        - Calculateing how far each point is from center
        - Converting distances into angles
        - Sorting input points by angle
    Returns: [top-left, top-right, bottom-right, bottom-left]
    """
    centroid = pts.mean(axis=0)
    angles = numpy.arctan2(pts[:, 1] - centroid[1], pts[:, 0] - centroid[0])
    ordered_indices = numpy.argsort(angles)
    return pts[ordered_indices].astype(numpy.float32)


def detect_and_crop_yellow_border(img: numpy.ndarray) -> numpy.ndarray:
    """
    Raises:
    PokemonCardDetectionError:  If no yellow contours are found or the detected area is too small to be a card.
    """
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
