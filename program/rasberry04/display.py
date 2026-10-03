import cv2


class Display:

    def __init__(self, settings):

        cfg = settings["display"]

        self.title = cfg["title"]

        self.width = cfg["width"]

        self.height = cfg["height"]


        cv2.namedWindow(
            self.title,
            cv2.WINDOW_NORMAL
        )


        cv2.resizeWindow(
            self.title,
            self.width,
            self.height
        )


    # ======================================================
    # TEXT
    # ======================================================

    def text(
        self,
        image,
        value,
        x,
        y,
        color,
        size=0.55,
        thickness=2
    ):

        cv2.putText(
            image,
            str(value),
            (
                int(x),
                int(y)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            size,
            color,
            thickness,
            cv2.LINE_AA
        )


    # ======================================================
    # LINE
    # ======================================================

    def line(
        self,
        image,
        x1,
        y1,
        x2,
        y2,
        color,
        thickness=2
    ):

        cv2.line(
            image,
            (
                int(x1),
                int(y1)
            ),
            (
                int(x2),
                int(y2)
            ),
            color,
            thickness,
            cv2.LINE_AA
        )


    # ======================================================
    # POINT
    # ======================================================

    def point(
        self,
        image,
        x,
        y,
        color,
        radius=7
    ):

        cv2.circle(
            image,
            (
                int(x),
                int(y)
            ),
            radius,
            color,
            -1,
            cv2.LINE_AA
        )


    # ======================================================
    # STATUS COLOR
    # ======================================================

    def status_color(
        self,
        status
    ):

        if status == "OK":

            return (
                0,
                255,
                0
            )


        if status == "NG":

            return (
                0,
                0,
                255
            )


        return (
            255,
            255,
            255
        )


    # ======================================================
    # SHOW
    # ======================================================

    def show(
        self,
        frame,
        result,
        camera_index
    ):

        image = frame.copy()


        h, w = image.shape[:2]


        # ==================================================
        # WARNA
        # ==================================================

        GREEN = (
            0,
            255,
            0
        )


        BLUE = (
            255,
            0,
            0
        )


        YELLOW = (
            0,
            255,
            255
        )


        RED = (
            0,
            0,
            255
        )


        WHITE = (
            255,
            255,
            255
        )


        # ==================================================
        # JUDUL
        # ==================================================

        self.text(
            image,
            "PENGUKURAN SPAKBOR",
            20,
            35,
            WHITE,
            0.8,
            2
        )


        self.text(
            image,
            f"CAMERA : {camera_index}",
            20,
            65,
            WHITE,
            0.5,
            1
        )


        # ==================================================
        # TIDAK TERDETEKSI
        # ==================================================

        if not result["found"]:

            self.text(
                image,
                "SPAKBOR TIDAK TERDETEKSI",
                20,
                105,
                RED,
                0.65,
                2
            )


            self.text(
                image,
                "Posisikan spakbor di tengah",
                20,
                135,
                WHITE,
                0.5,
                1
            )


            cv2.imshow(
                self.title,
                image
            )


            return


        # ==================================================
        # DATA
        # ==================================================

        x, y, bw, bh = (
            result["box"]
        )


        left_top = (
            result["left_top"]
        )


        right_top = (
            result["right_top"]
        )


        base_y = (
            result["base_y"]
        )


        left_x = (
            left_top[0]
        )


        right_x = (
            right_top[0]
        )


        # ==================================================
        # KONTOUR SPAKBOR
        # ==================================================

        if result["contour"] is not None:

            cv2.drawContours(
                image,
                [
                    result["contour"]
                ],
                -1,
                WHITE,
                2
            )


        # ==================================================
        # TITIK PUNCAK KIRI
        # ==================================================

        self.point(
            image,
            left_top[0],
            left_top[1],
            GREEN,
            7
        )


        self.text(
            image,
            "PUNCAK KIRI",
            left_top[0] - 65,
            left_top[1] - 15,
            GREEN,
            0.5,
            2
        )


        # ==================================================
        # TITIK PUNCAK KANAN
        # ==================================================

        self.point(
            image,
            right_top[0],
            right_top[1],
            BLUE,
            7
        )


        self.text(
            image,
            "PUNCAK KANAN",
            right_top[0] - 70,
            right_top[1] - 15,
            BLUE,
            0.5,
            2
        )


        # ==================================================
        # GARIS DASAR 0 MM
        # ==================================================

        self.line(
            image,
            x - 50,
            base_y,
            x + bw + 50,
            base_y,
            RED,
            3
        )


        self.text(
            image,
            "GARIS DASAR 0 mm",
            x + bw // 2 - 80,
            base_y + 30,
            RED,
            0.55,
            2
        )


        # ==================================================
        # GARIS TINGGI KIRI
        # ==================================================

        self.line(
            image,
            left_x,
            left_top[1],
            left_x,
            base_y,
            GREEN,
            3
        )


        # ==================================================
        # GARIS TINGGI KANAN
        # ==================================================

        self.line(
            image,
            right_x,
            right_top[1],
            right_x,
            base_y,
            BLUE,
            3
        )


        # ==================================================
        # TINGGI KIRI
        # ==================================================

        left_height = (
            result["left_height"]
        )


        self.text(
            image,
            f"Tinggi Kiri : {left_height:.2f} mm",
            20,
            105,
            GREEN,
            0.6,
            2
        )


        # ==================================================
        # TINGGI KANAN
        # ==================================================

        right_height = (
            result["right_height"]
        )


        self.text(
            image,
            f"Tinggi Kanan : {right_height:.2f} mm",
            20,
            135,
            BLUE,
            0.6,
            2
        )


        # ==================================================
        # LOWER KIRI
        # ==================================================

        left_lower_y = (
            result["left_lower_y"]
        )


        self.line(
            image,
            left_x - 100,
            left_lower_y,
            left_x + 70,
            left_lower_y,
            YELLOW,
            2
        )


        self.text(
            image,
            f"LOWER KIRI {result['left_lower']:.2f} mm",
            left_x - 100,
            left_lower_y - 10,
            YELLOW,
            0.5,
            2
        )


        # ==================================================
        # UPPER KIRI
        # ==================================================

        left_upper_y = (
            result["left_upper_y"]
        )


        self.line(
            image,
            left_x - 100,
            left_upper_y,
            left_x + 70,
            left_upper_y,
            YELLOW,
            2
        )


        self.text(
            image,
            f"UPPER KIRI {result['left_upper']:.2f} mm",
            left_x - 100,
            left_upper_y - 10,
            YELLOW,
            0.5,
            2
        )


        # ==================================================
        # LOWER KANAN
        # ==================================================

        right_lower_y = (
            result["right_lower_y"]
        )


        self.line(
            image,
            right_x - 70,
            right_lower_y,
            right_x + 100,
            right_lower_y,
            YELLOW,
            2
        )


        self.text(
            image,
            f"LOWER KANAN {result['right_lower']:.2f} mm",
            right_x - 70,
            right_lower_y - 10,
            YELLOW,
            0.5,
            2
        )


        # ==================================================
        # UPPER KANAN
        # ==================================================

        right_upper_y = (
            result["right_upper_y"]
        )


        self.line(
            image,
            right_x - 70,
            right_upper_y,
            right_x + 100,
            right_upper_y,
            YELLOW,
            2
        )


        self.text(
            image,
            f"UPPER KANAN {result['right_upper']:.2f} mm",
            right_x - 70,
            right_upper_y - 10,
            YELLOW,
            0.5,
            2
        )


        # ==================================================
        # STATUS
        # ==================================================

        y_status = 180


        left_upper_status = (
            result["left_upper_status"]
        )


        left_lower_status = (
            result["left_lower_status"]
        )


        right_upper_status = (
            result["right_upper_status"]
        )


        right_lower_status = (
            result["right_lower_status"]
        )


        self.text(
            image,
            f"UPPER KIRI : {left_upper_status}",
            20,
            y_status,
            self.status_color(
                left_upper_status
            ),
            0.55,
            2
        )


        self.text(
            image,
            f"LOWER KIRI : {left_lower_status}",
            20,
            y_status + 30,
            self.status_color(
                left_lower_status
            ),
            0.55,
            2
        )


        self.text(
            image,
            f"UPPER KANAN : {right_upper_status}",
            20,
            y_status + 60,
            self.status_color(
                right_upper_status
            ),
            0.55,
            2
        )


        self.text(
            image,
            f"LOWER KANAN : {right_lower_status}",
            20,
            y_status + 90,
            self.status_color(
                right_lower_status
            ),
            0.55,
            2
        )


        # ==================================================
        # INFO CAMERA
        # ==================================================

        self.text(
            image,
            "KAMERA : BAWAH - TENGAH",
            20,
            h - 45,
            WHITE,
            0.5,
            1
        )


        self.text(
            image,
            "JARAK : ±55 CM",
            20,
            h - 20,
            WHITE,
            0.5,
            1
        )


        # ==================================================
        # DISPLAY
        # ==================================================

        cv2.imshow(
            self.title,
            image
        )


    # ======================================================
    # CLOSE
    # ======================================================

    def close(self):

        cv2.destroyAllWindows()