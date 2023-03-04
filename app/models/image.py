"""Image Section"""
import base64
from io import BytesIO
from PIL import Image


class ImageConvert:
    """把照片转成base64格式, 然后储存在db"""

    def img_base64(self, img) -> base64:
        """Image convert to base64"""
        with Image.open(img) as image:
            _max_size = (240, 240)
            image.thumbnail(_max_size, Image.ANTIALIAS)

            # turn image to base64 string
            output_buffer = BytesIO()
            image.save(output_buffer, format="JPEG")
            byte_data = output_buffer.getvalue()
            base64_str = base64.b64encode(byte_data)
            base64_decode = base64_str.decode("utf-8")
            return base64_decode
