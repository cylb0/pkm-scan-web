import unittest
import numpy as np
import cv2
from processor import detect_and_crop_yellow_border
from errors.processing import PokemonCardDetectionError


class TestCVLogic(unittest.TestCase):
    TOP_LEFT = (100, 100)
    BOTTOM_RIGHT = (200, 300)
    YELLOW = (0, 255, 255)
    BLACK = (0, 0, 0)

    # test perfect card
    def test_detect_yellow_rectangle(self):
        canvas = np.zeros((500, 500, 3), dtype=np.uint8)

        cv2.rectangle(canvas, self.TOP_LEFT, self.BOTTOM_RIGHT, self.YELLOW, -1)

        cropped = detect_and_crop_yellow_border(canvas)

        self.assertAlmostEqual(cropped.shape[0], 200, delta=10)
        self.assertAlmostEqual(cropped.shape[1], 100, delta=10)
        self.assertEqual(cropped[10, 10][1], 255)
        self.assertEqual(cropped[10, 10][2], 255)

    # test no card
    def test_no_yellow_border_raises_error(self):
        canvas = np.zeros((500, 500, 3), dtype=np.uint8)

        with self.assertRaises(PokemonCardDetectionError):
            detect_and_crop_yellow_border(canvas)

    # ensures algorithm doesnt detect artifact within card
    def test_max_ignores_small_noise(self):
        canvas = np.zeros((500, 500, 3), dtype=np.uint8)

        cv2.rectangle(canvas, (10, 10), (15, 15), self.YELLOW, -1)

        cv2.rectangle(canvas, self.TOP_LEFT, self.BOTTOM_RIGHT, self.YELLOW, -1)

        cropped = detect_and_crop_yellow_border(canvas)

        self.assertAlmostEqual(cropped.shape[0], 200, delta=10)
        self.assertAlmostEqual(cropped.shape[1], 100, delta=10)

    # test that bounding box doesnt cause IndexError with coordinates outside the img
    def test_card_at_image_edge(self):
        canvas = np.zeros((500, 500, 3), dtype=np.uint8)
        yellow = (0, 255, 255)

        cv2.rectangle(canvas, (0, 0), (100, 150), yellow, -1)

        cropped = detect_and_crop_yellow_border(canvas)

        self.assertAlmostEqual(cropped.shape[0], 150, delta=10)
        self.assertAlmostEqual(cropped.shape[1], 100, delta=10)

    # morphology succesfully bridges a gap in the border
    def test_detect_yellow_rectangle_with_gap_in_the_border(self):
        canvas = np.zeros((500, 500, 3), dtype=np.uint8)

        cv2.rectangle(canvas, self.TOP_LEFT, self.BOTTOM_RIGHT, self.YELLOW, -1)

        # splits the "card" in two parts
        cv2.line(canvas, self.TOP_LEFT, self.BOTTOM_RIGHT, self.BLACK, 2)

        cropped = detect_and_crop_yellow_border(canvas)

        self.assertAlmostEqual(cropped.shape[0], 200, delta=10)
        self.assertAlmostEqual(cropped.shape[1], 100, delta=10)
