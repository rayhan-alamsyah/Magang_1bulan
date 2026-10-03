# ==========================================================
# CAMERA.PY
# SISTEM KAMERA SPAKBOR QC
# ==========================================================

import cv2
import platform

from pathlib import Path


# ==========================================================
# CLASS CAMERA
# ==========================================================

class Camera:

    def __init__(self, settings):

        cfg = settings["camera"]

        self.auto_detect = cfg["auto_detect"]

        self.index = cfg["index"]

        self.max_index = cfg["max_index"]

        self.width = cfg["width"]

        self.height = cfg["height"]

        self.fps = cfg["fps"]

        self.mirror = cfg["mirror"]

        self.external_only = cfg.get(
            "external_only",
            True
        )

        self.cap = None

        self.backend_name = (
            "OpenCV default"
        )


    # ======================================================
    # CREATE CAPTURE
    # ======================================================

    def create_capture(
        self,
        index
    ):

        system = platform.system()


        # --------------------------------------------------
        # WINDOWS
        # --------------------------------------------------

        if system == "Windows":

            cap = cv2.VideoCapture(
                index,
                cv2.CAP_DSHOW
            )

            self.backend_name = (
                "DirectShow"
            )

            return cap


        # --------------------------------------------------
        # LINUX / RASPBERRY PI
        # --------------------------------------------------

        if system == "Linux":

            cap = cv2.VideoCapture(
                index,
                cv2.CAP_V4L2
            )

            self.backend_name = (
                "V4L2"
            )

            return cap


        # --------------------------------------------------
        # DEFAULT
        # --------------------------------------------------

        self.backend_name = (
            "OpenCV default"
        )

        return cv2.VideoCapture(
            index
        )


    # ======================================================
    # CEK USB CAMERA
    # ======================================================

    def is_usb_camera(
        self,
        index
    ):

        if platform.system() != "Linux":

            return False


        device = Path(
            f"/dev/video{index}"
        )


        if not device.exists():

            return False


        try:

            sys_device = Path(
                f"/sys/class/video4linux/"
                f"video{index}/device"
            )


            if not sys_device.exists():

                return False


            real_path = (
                sys_device.resolve()
            )


            path_text = str(
                real_path
            ).lower()


            if "usb" in path_text:

                return True


            for parent in real_path.parents:

                if "usb" in str(
                    parent
                ).lower():

                    return True


        except Exception:

            pass


        return False


    # ======================================================
    # TEST CAMERA
    # ======================================================

    def test_camera(
        self,
        index
    ):

        print(
            f"Mencoba Camera {index}..."
        )


        cap = self.create_capture(
            index
        )


        if not cap.isOpened():

            print(
                f"Camera {index}: "
                f"gagal dibuka."
            )

            cap.release()

            return False


        # --------------------------------------------------
        # SET RESOLUSI
        # --------------------------------------------------

        cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.width
        )

        cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.height
        )

        cap.set(
            cv2.CAP_PROP_FPS,
            self.fps
        )


        # --------------------------------------------------
        # TEST BACA FRAME
        # --------------------------------------------------

        ret, frame = cap.read()


        if not ret or frame is None:

            print(
                f"Camera {index}: "
                f"tidak dapat membaca frame."
            )

            cap.release()

            return False


        actual_height, actual_width = (
            frame.shape[:2]
        )


        print(
            f"Camera {index}: "
            f"TERDETEKSI "
            f"({actual_width} x "
            f"{actual_height})"
        )


        cap.release()


        return True


    # ======================================================
    # FIND CAMERA
    # ======================================================

    def find_camera(self):

        print(
            "\n" +
            "=" * 50
        )

        print(
            "MENCARI KAMERA EXTERNAL"
        )

        print(
            "=" * 50
        )


        # ==================================================
        # LINUX
        # ==================================================

        if platform.system() == "Linux":

            usb_cameras = []

            other_cameras = []


            # ------------------------------------------------
            # CARI DEVICE CAMERA
            # ------------------------------------------------

            for index in range(
                self.max_index
            ):

                device = Path(
                    f"/dev/video{index}"
                )


                if not device.exists():

                    continue


                if self.is_usb_camera(
                    index
                ):

                    usb_cameras.append(
                        index
                    )

                else:

                    other_cameras.append(
                        index
                    )


            # ------------------------------------------------
            # USB TERLEBIH DAHULU
            # ------------------------------------------------

            daftar_kamera = (
                usb_cameras
            )


            # Jika external_only False
            # maka kamera lain juga boleh
            if not self.external_only:

                daftar_kamera += (
                    other_cameras
                )


            for index in daftar_kamera:

                if self.test_camera(
                    index
                ):

                    print(
                        "Menggunakan kamera "
                        f"EXTERNAL: {index}"
                    )

                    return index


        # ==================================================
        # WINDOWS
        # ==================================================

        elif platform.system() == "Windows":

            # ------------------------------------------------
            # COBA INDEX 1 TERLEBIH DAHULU
            # ------------------------------------------------

            for index in range(
                1,
                self.max_index
            ):

                if self.test_camera(
                    index
                ):

                    print(
                        "Menggunakan kamera "
                        f"EXTERNAL: {index}"
                    )

                    return index


            # ------------------------------------------------
            # FALLBACK CAMERA 0
            # ------------------------------------------------

            if not self.external_only:

                if self.test_camera(0):

                    print(
                        "Menggunakan kamera "
                        "INDEX 0"
                    )

                    return 0


        # ==================================================
        # PLATFORM LAIN
        # ==================================================

        else:

            for index in range(
                self.max_index
            ):

                if self.test_camera(
                    index
                ):

                    return index


        raise RuntimeError(
            "Tidak ada kamera "
            "yang dapat dibuka."
        )


    # ======================================================
    # OPEN CAMERA
    # ======================================================

    def open(self):

        # --------------------------------------------------
        # AUTO DETECT
        # --------------------------------------------------

        if self.auto_detect:

            self.index = (
                self.find_camera()
            )


        # --------------------------------------------------
        # BUKA CAMERA
        # --------------------------------------------------

        self.cap = (
            self.create_capture(
                self.index
            )
        )


        if not self.cap.isOpened():

            raise RuntimeError(
                f"Kamera index "
                f"{self.index} "
                f"tidak dapat dibuka."
            )


        # --------------------------------------------------
        # SET RESOLUSI
        # --------------------------------------------------

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.width
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.height
        )

        self.cap.set(
            cv2.CAP_PROP_FPS,
            self.fps
        )


        actual_width = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )


        actual_height = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )


        actual_fps = self.cap.get(
            cv2.CAP_PROP_FPS
        )


        print(
            "\nKAMERA BERHASIL DIBUKA"
        )

        print(
            f"Index     : {self.index}"
        )

        print(
            f"Resolusi  : "
            f"{actual_width} x "
            f"{actual_height}"
        )

        print(
            f"FPS       : "
            f"{actual_fps:.1f}"
        )

        print(
            f"Backend   : "
            f"{self.backend_name}"
        )


    # ======================================================
    # READ
    # ======================================================

    def read(self):

        if self.cap is None:

            return None


        ret, frame = (
            self.cap.read()
        )


        if not ret or frame is None:

            return None


        # --------------------------------------------------
        # MIRROR
        # --------------------------------------------------

        if self.mirror:

            frame = cv2.flip(
                frame,
                1
            )


        return frame


    # ======================================================
    # RELEASE
    # ======================================================

    def release(self):

        if self.cap is not None:

            self.cap.release()

            self.cap = None

            print(
                "Camera ditutup."
            )