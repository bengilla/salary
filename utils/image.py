"""
Image utility functions
"""

import base64
from io import BytesIO
from typing import Any

from PIL import Image


class ImageConverter:
    """Convert images to base64"""

    MAX_SIZE = (240, 240)

    def to_base64(self, img: Any) -> str:
        """Convert uploaded image to base64 string"""
        with Image.open(img) as im:
            im.thumbnail(self.MAX_SIZE, Image.LANCZOS)
            output_buffer = BytesIO()
            im.save(output_buffer, format="JPEG")
            byte_data = output_buffer.getvalue()
            return base64.b64encode(byte_data).decode("utf-8")
