"""
Image utility functions for preprocessing farm photos.
Handles common issues: rotation, poor lighting, large file sizes.
"""
import cv2
import numpy as np
import os


def validate_image(image_path):
    """Check if image is valid and usable for classification."""
    if not os.path.exists(image_path):
        return False, "File not found"

    img = cv2.imread(image_path)
    if img is None:
        return False, "Cannot read image file"

    h, w = img.shape[:2]
    if h < 100 or w < 100:
        return False, "Image too small, need at least 100x100 pixels"

    # Check if image is too blurry (Laplacian variance)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    if blur_score < 50:
        return False, "Image is too blurry, please take a clearer photo"

    return True, "ok"


def fix_rotation(image_path):
    """
    Fix image rotation using EXIF data.
    Phone cameras often save rotated images.
    """
    img = cv2.imread(image_path)
    # OpenCV doesn't read EXIF, so we use a simple heuristic:
    # if image is taller than wide by a lot, it's probably portrait
    # and needs rotation for our model (which expects landscape-ish)
    h, w = img.shape[:2]
    if h > w * 1.5:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img


def compress_image(image_path, max_size_kb=500):
    """Compress image to reduce upload size on slow rural networks."""
    img = cv2.imread(image_path)
    if img is None:
        return image_path

    quality = 85
    while quality > 20:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, encoded = cv2.imencode(".jpg", img, encode_param)
        size_kb = len(encoded) / 1024

        if size_kb <= max_size_kb:
            output_path = image_path.rsplit(".", 1)[0] + "_compressed.jpg"
            cv2.imwrite(output_path, img, encode_param)
            return output_path

        quality -= 10

    return image_path


def crop_leaf_region(image_path):
    """
    Try to auto-detect and crop the leaf region from the photo.
    Uses simple green color masking - works for most leaf photos.
    """
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Green color range for leaves
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Also include brown/yellow for diseased parts
    lower_brown = np.array([10, 50, 50])
    upper_brown = np.array([30, 255, 255])
    mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)
    mask = cv2.bitwise_or(mask, mask_brown)

    # Find the bounding box of the leaf
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img  # Return original if no leaf detected

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    # Add some padding
    pad = 20
    x = max(0, x - pad)
    y = max(0, y - pad)
    w = min(img.shape[1] - x, w + 2 * pad)
    h = min(img.shape[0] - y, h + 2 * pad)

    return img[y:y+h, x:x+w]
