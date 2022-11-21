""" Image Modules"""
import base64
from io import BytesIO
from typing import Any

from PIL import Image


class ImageConvert:
    """Image convert class"""
    def __init__(self) -> None:
        pass

    def img_base64(self, img):
        """Image convert to base64"""
        with Image.open(img) as im:
            MAX_SIZE = (240, 240)
            im.thumbnail(MAX_SIZE, Image.ANTIALIAS)

            # turn image to base64 string
            output_buffer = BytesIO()
            im.save(output_buffer, format='JPEG')
            byte_data = output_buffer.getvalue()
            base64_str = base64.b64encode(byte_data)
            base64_decode = base64_str.decode("utf-8")
            print(base64_decode)
            return base64_decode