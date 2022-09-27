"""
Testing Camera
"""

import cv2
import numpy as np


class Camera:
    """Camera Testing"""

    def __init__(self) -> None:
        pass

    def run_camera(self):
        """Run Camera"""
        cap = cv2.VideoCapture(0)

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            # Display the resulting frame
            cv2.imshow("frame", frame)
            if cv2.waitKey(20) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
