"""Unit tests for image processing utilities."""

import io
import unittest
from PIL import Image
from app.utils.image import process_image


class TestImageUtils(unittest.TestCase):
    """Test suite for process_image utility."""

    def test_process_normal_image(self):
        # Create a 400x300 image
        img = Image.new("RGB", (400, 300), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        raw_bytes = buf.getvalue()

        out_bytes, w, h, size_kb = process_image(raw_bytes, max_side=1280)
        self.assertEqual((w, h), (400, 300))
        self.assertTrue(len(out_bytes) > 0)
        self.assertTrue(size_kb > 0)

    def test_resize_large_image(self):
        # Create a large 2000x1000 image
        img = Image.new("RGB", (2000, 1000), color="green")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        raw_bytes = buf.getvalue()

        out_bytes, w, h, size_kb = process_image(raw_bytes, max_side=1280)
        self.assertEqual(w, 1280)
        self.assertEqual(h, 640)  # Preserved 2:1 aspect ratio
        self.assertTrue(len(out_bytes) > 0)

    def test_process_rgba_image(self):
        # Create an RGBA image with alpha channel
        img = Image.new("RGBA", (200, 200), color=(255, 0, 0, 128))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        raw_bytes = buf.getvalue()

        out_bytes, w, h, size_kb = process_image(raw_bytes, max_side=1280)
        self.assertEqual((w, h), (200, 200))
        # Ensure it's valid JPEG bytes
        with Image.open(io.BytesIO(out_bytes)) as result_img:
            self.assertEqual(result_img.format, "JPEG")
            self.assertEqual(result_img.mode, "RGB")


if __name__ == "__main__":
    unittest.main()
