# ==========================================================
# NG_DETECTOR.PY
# SISTEM QUALITY CONTROL
# DETEKSI DAN PENGUKURAN SPAKBOR
# ==========================================================

import cv2
import numpy as np


# ==========================================================
# CLASS NG DETECTOR
# ==========================================================

class NGDetector:

    def __init__(
        self,
        settings
    ):

        self.settings = settings

        # ==================================================
        # AMBIL CONFIG
        # ==================================================

        measurement_cfg = settings.get(
            "measurement",
            {}
        )

        calibration_cfg = settings.get(
            "calibration",
            {}
        )

        detector_cfg = settings.get(
            "detector",
            {}
        )

        display_cfg = settings.get(
            "display",
            {}
        )

        # ==================================================
        # CONFIG KIRI
        # ==================================================

        left_cfg = measurement_cfg.get(
            "left",
            {}
        )

        self.left_target = float(
            left_cfg.get(
                "height",
                0
            )
        )

        self.left_lower = float(
            left_cfg.get(
                "lower",
                0
            )
        )

        self.left_upper = float(
            left_cfg.get(
                "upper",
                0
            )
        )

        # ==================================================
        # CONFIG KANAN
        # ==================================================

        right_cfg = measurement_cfg.get(
            "right",
            {}
        )

        self.right_target = float(
            right_cfg.get(
                "height",
                0
            )
        )

        self.right_lower = float(
            right_cfg.get(
                "lower",
                0
            )
        )

        self.right_upper = float(
            right_cfg.get(
                "upper",
                0
            )
        )

        # ==================================================
        # KALIBRASI KIRI
        # ==================================================

        self.left_pixels_per_mm = float(
            calibration_cfg.get(
                "left_pixels_per_mm",
                1.0
            )
        )

        # ==================================================
        # KALIBRASI KANAN
        # ==================================================

        self.right_pixels_per_mm = float(
            calibration_cfg.get(
                "right_pixels_per_mm",
                1.0
            )
        )

        if self.left_pixels_per_mm <= 0:
            self.left_pixels_per_mm = 1.0

        if self.right_pixels_per_mm <= 0:
            self.right_pixels_per_mm = 1.0

        # ==================================================
        # ROI
        # ==================================================

        self.roi_left = float(
            detector_cfg.get(
                "roi_left",
                0.0
            )
        )

        self.roi_right = float(
            detector_cfg.get(
                "roi_right",
                1.0
            )
        )

        self.roi_top = float(
            detector_cfg.get(
                "roi_top",
                0.0
            )
        )

        self.roi_bottom = float(
            detector_cfg.get(
                "roi_bottom",
                1.0
            )
        )

        # ==================================================
        # FILTER
        # ==================================================

        self.blur = int(
            detector_cfg.get(
                "blur",
                5
            )
        )

        if self.blur < 1:
            self.blur = 1

        if self.blur % 2 == 0:
            self.blur += 1

        self.canny_low = int(
            detector_cfg.get(
                "canny_low",
                50
            )
        )

        self.canny_high = int(
            detector_cfg.get(
                "canny_high",
                150
            )
        )

        self.min_area = float(
            detector_cfg.get(
                "min_area",
                500
            )
        )

        self.min_width = int(
            detector_cfg.get(
                "min_width",
                20
            )
        )

        self.min_height = int(
            detector_cfg.get(
                "min_height",
                20
            )
        )

        self.morph_kernel = int(
            detector_cfg.get(
                "morph_kernel",
                5
            )
        )

        if self.morph_kernel < 1:
            self.morph_kernel = 1

        if self.morph_kernel % 2 == 0:
            self.morph_kernel += 1

        self.threshold = int(
            detector_cfg.get(
                "threshold",
                85
            )
        )

        # ==================================================
        # DISPLAY
        # ==================================================

        self.show_contour = display_cfg.get(
            "show_contour",
            True
        )

        self.show_reference = display_cfg.get(
            "show_reference",
            True
        )

        # ==================================================
        # HASIL TERAKHIR
        # ==================================================

        self.last_result = (
            self.empty_result()
        )

    # ==========================================================
    # EMPTY RESULT
    # ==========================================================

    def empty_result(self):

        return {

            "found":
                False,

            "left_height":
                0.0,

            "right_height":
                0.0,

            "tinggi_kiri":
                0.0,

            "tinggi_kanan":
                0.0,

            "left_upper_status":
                "NG",

            "left_lower_status":
                "NG",

            "right_upper_status":
                "NG",

            "right_lower_status":
                "NG",

            "upper_kiri":
                "NG",

            "lower_kiri":
                "NG",

            "upper_kanan":
                "NG",

            "lower_kanan":
                "NG",

            "hasil":
                "NG",

            "status":
                "NO_OBJECT",

            "baseline_y":
                None,

            "left_peak":
                None,

            "right_peak":
                None,

            "left_lower_y":
                None,

            "left_upper_y":
                None,

            "right_lower_y":
                None,

            "right_upper_y":
                None
        }

    # ==========================================================
    # CLAMP
    # ==========================================================

    def clamp(
        self,
        value,
        minimum,
        maximum
    ):

        return max(
            minimum,
            min(
                value,
                maximum
            )
        )

    # ==========================================================
    # ROI
    # ==========================================================

    def get_roi(
        self,
        frame
    ):

        height, width = (
            frame.shape[:2]
        )

        x1 = int(
            self.clamp(
                self.roi_left,
                0,
                1
            ) * width
        )

        x2 = int(
            self.clamp(
                self.roi_right,
                0,
                1
            ) * width
        )

        y1 = int(
            self.clamp(
                self.roi_top,
                0,
                1
            ) * height
        )

        y2 = int(
            self.clamp(
                self.roi_bottom,
                0,
                1
            ) * height
        )

        x1 = min(
            x1,
            width - 1
        )

        x2 = max(
            x1 + 1,
            min(
                x2,
                width
            )
        )

        y1 = min(
            y1,
            height - 1
        )

        y2 = max(
            y1 + 1,
            min(
                y2,
                height
            )
        )

        roi = frame[
            y1:y2,
            x1:x2
        ]

        return (
            roi,
            x1,
            y1
        )

    # ==========================================================
    # FIND MAIN CONTOUR
    # ==========================================================

    def find_main_contour(
        self,
        frame
    ):

        roi, offset_x, offset_y = (
            self.get_roi(frame)
        )

        if (
            roi is None
            or
            roi.size == 0
        ):

            return None

        # --------------------------------------------------
        # GRAYSCALE
        # --------------------------------------------------

        gray = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2GRAY
        )

        # --------------------------------------------------
        # BLUR
        # --------------------------------------------------

        gray = cv2.GaussianBlur(
            gray,
            (
                self.blur,
                self.blur
            ),
            0
        )

        # --------------------------------------------------
        # CANNY
        # --------------------------------------------------

        edges = cv2.Canny(
            gray,
            self.canny_low,
            self.canny_high
        )

        # --------------------------------------------------
        # MORPHOLOGY
        # --------------------------------------------------

        kernel = (
            cv2.getStructuringElement(
                cv2.MORPH_RECT,
                (
                    self.morph_kernel,
                    self.morph_kernel
                )
            )
        )

        edges = cv2.morphologyEx(
            edges,
            cv2.MORPH_CLOSE,
            kernel
        )

        # --------------------------------------------------
        # CONTOUR
        # --------------------------------------------------

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        candidates = []

        # ==================================================
        # FILTER CONTOUR
        # ==================================================

        for contour in contours:

            area = cv2.contourArea(
                contour
            )

            if area < self.min_area:
                continue

            x, y, w, h = (
                cv2.boundingRect(
                    contour
                )
            )

            if w < self.min_width:
                continue

            if h < self.min_height:
                continue

            contour_global = (
                contour.copy()
            )

            contour_global[:, :, 0] += (
                offset_x
            )

            contour_global[:, :, 1] += (
                offset_y
            )

            candidates.append(
                (
                    area,
                    contour_global,
                    x + offset_x,
                    y + offset_y,
                    w,
                    h
                )
            )

        if not candidates:
            return None

        # ==================================================
        # AMBIL CONTOUR TERBESAR
        # ==================================================

        candidates.sort(
            key=lambda item: item[0],
            reverse=True
        )

        (
            area,
            contour,
            x,
            y,
            w,
            h
        ) = candidates[0]

        return {

            "contour":
                contour,

            "area":
                area,

            "x":
                x,

            "y":
                y,

            "w":
                w,

            "h":
                h
        }

    # ==========================================================
    # FIND PEAKS
    # ==========================================================

    def find_peaks(
        self,
        contour,
        frame_width
    ):

        points = contour.reshape(
            -1,
            2
        )

        if len(points) == 0:
            return None, None

        # --------------------------------------------------
        # TITIK PALING ATAS
        # --------------------------------------------------

        min_y = int(
            np.min(
                points[:, 1]
            )
        )

        tolerance = max(
            5,
            int(
                frame_width * 0.01
            )
        )

        top_points = points[
            points[:, 1]
            <=
            min_y + tolerance
        ]

        if len(top_points) == 0:
            top_points = points

        center_x = (
            frame_width / 2
        )

        # ==================================================
        # KIRI
        # ==================================================

        left_points = top_points[
            top_points[:, 0]
            <
            center_x
        ]

        if len(left_points) > 0:

            left_peak = (
                left_points[
                    np.argmin(
                        left_points[:, 0]
                    )
                ]
            )

        else:

            left_candidates = points[
                points[:, 0]
                <
                center_x
            ]

            if len(left_candidates) > 0:

                left_peak = (
                    left_candidates[
                        np.argmin(
                            left_candidates[:, 1]
                        )
                    ]
                )

            else:

                left_peak = None

        # ==================================================
        # KANAN
        # ==================================================

        right_points = top_points[
            top_points[:, 0]
            >=
            center_x
        ]

        if len(right_points) > 0:

            right_peak = (
                right_points[
                    np.argmax(
                        right_points[:, 0]
                    )
                ]
            )

        else:

            right_candidates = points[
                points[:, 0]
                >=
                center_x
            ]

            if len(right_candidates) > 0:

                right_peak = (
                    right_candidates[
                        np.argmin(
                            right_candidates[:, 1]
                        )
                    ]
                )

            else:

                right_peak = None

        # ==================================================
        # CONVERT KE INTEGER
        # ==================================================

        if left_peak is not None:

            left_peak = (
                int(left_peak[0]),
                int(left_peak[1])
            )

        if right_peak is not None:

            right_peak = (
                int(right_peak[0]),
                int(right_peak[1])
            )

        return (
            left_peak,
            right_peak
        )

    # ==========================================================
    # FIND BASELINE
    # ==========================================================

    def find_baseline(
        self,
        contour
    ):

        points = contour.reshape(
            -1,
            2
        )

        if len(points) == 0:
            return None

        max_y = int(
            np.max(
                points[:, 1]
            )
        )

        tolerance = 8

        bottom_points = points[
            points[:, 1]
            >=
            max_y - tolerance
        ]

        if len(bottom_points) == 0:
            return None

        baseline_y = int(
            np.median(
                bottom_points[:, 1]
            )
        )

        return baseline_y

    # ==========================================================
    # CALCULATE HEIGHT
    # ==========================================================

    def calculate_height(
        self,
        baseline_y,
        peak_y,
        pixels_per_mm
    ):

        if baseline_y is None:
            return 0.0

        if peak_y is None:
            return 0.0

        if pixels_per_mm <= 0:
            return 0.0

        pixel_height = (
            baseline_y -
            peak_y
        )

        if pixel_height <= 0:
            return 0.0

        return (
            pixel_height /
            pixels_per_mm
        )

    # ==========================================================
    # CHECK UPPER
    # ==========================================================

    def check_upper(
        self,
        height,
        upper_limit
    ):

        if upper_limit <= 0:
            return "OK"

        if height <= upper_limit:
            return "OK"

        return "NG"

    # ==========================================================
    # CHECK LOWER
    # ==========================================================

    def check_lower(
        self,
        height,
        lower_limit
    ):

        if lower_limit <= 0:
            return "OK"

        if height >= lower_limit:
            return "OK"

        return "NG"

    # ==========================================================
    # CALCULATE RESULT
    # ==========================================================

    def calculate_result(
        self,
        left_upper_status,
        left_lower_status,
        right_upper_status,
        right_lower_status
    ):

        statuses = [

            left_upper_status,

            left_lower_status,

            right_upper_status,

            right_lower_status

        ]

        if all(
            status == "OK"
            for status in statuses
        ):

            return "GOOD"

        upper_ng = (

            left_upper_status == "NG"

            or

            right_upper_status == "NG"

        )

        lower_ng = (

            left_lower_status == "NG"

            or

            right_lower_status == "NG"

        )

        if (
            upper_ng
            and
            lower_ng
        ):

            return "NG UPPER + LOWER"

        if upper_ng:
            return "NG UPPER"

        if lower_ng:
            return "NG LOWER"

        return "NG"

    # ==========================================================
    # DRAW REFERENCE LINES
    # ==========================================================

    def draw_reference_lines(
        self,
        frame,
        baseline_y,
        frame_width
    ):

        if baseline_y is None:
            return

        # ==================================================
        # LOWER KIRI
        # ==================================================

        if self.left_lower > 0:

            y_left_lower = int(
                baseline_y -
                (
                    self.left_lower *
                    self.left_pixels_per_mm
                )
            )

            cv2.line(
                frame,

                (
                    0,
                    y_left_lower
                ),

                (
                    frame_width // 2,
                    y_left_lower
                ),

                (
                    0,
                    255,
                    255
                ),

                2
            )

            cv2.putText(
                frame,

                f"LOWER KIRI: "
                f"{self.left_lower:.2f} mm",

                (
                    10,
                    max(
                        25,
                        y_left_lower - 5
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.55,

                (
                    0,
                    255,
                    255
                ),

                2
            )

        # ==================================================
        # UPPER KIRI
        # ==================================================

        if self.left_upper > 0:

            y_left_upper = int(
                baseline_y -
                (
                    self.left_upper *
                    self.left_pixels_per_mm
                )
            )

            cv2.line(
                frame,

                (
                    0,
                    y_left_upper
                ),

                (
                    frame_width // 2,
                    y_left_upper
                ),

                (
                    0,
                    255,
                    255
                ),

                2
            )

            cv2.putText(
                frame,

                f"UPPER KIRI: "
                f"{self.left_upper:.2f} mm",

                (
                    10,
                    max(
                        25,
                        y_left_upper - 5
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.55,

                (
                    0,
                    255,
                    255
                ),

                2
            )

        # ==================================================
        # LOWER KANAN
        # ==================================================

        if self.right_lower > 0:

            y_right_lower = int(
                baseline_y -
                (
                    self.right_lower *
                    self.right_pixels_per_mm
                )
            )

            cv2.line(
                frame,

                (
                    frame_width // 2,
                    y_right_lower
                ),

                (
                    frame_width,
                    y_right_lower
                ),

                (
                    0,
                    255,
                    255
                ),

                2
            )

            cv2.putText(
                frame,

                f"LOWER KANAN: "
                f"{self.right_lower:.2f} mm",

                (
                    frame_width // 2 + 10,
                    max(
                        25,
                        y_right_lower - 5
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.55,

                (
                    0,
                    255,
                    255
                ),

                2
            )

        # ==================================================
        # UPPER KANAN
        # ==================================================

        if self.right_upper > 0:

            y_right_upper = int(
                baseline_y -
                (
                    self.right_upper *
                    self.right_pixels_per_mm
                )
            )

            cv2.line(
                frame,

                (
                    frame_width // 2,
                    y_right_upper
                ),

                (
                    frame_width,
                    y_right_upper
                ),

                (
                    0,
                    255,
                    255
                ),

                2
            )

            cv2.putText(
                frame,

                f"UPPER KANAN: "
                f"{self.right_upper:.2f} mm",

                (
                    frame_width // 2 + 10,
                    max(
                        25,
                        y_right_upper - 5
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.55,

                (
                    0,
                    255,
                    255
                ),

                2
            )

    # ==========================================================
    # DRAW MEASUREMENT LINE
    # ==========================================================

    def draw_measurement_line(
        self,
        frame,
        peak,
        baseline_y,
        label,
        value,
        line_color
    ):

        if peak is None:
            return

        if baseline_y is None:
            return

        x, y = peak

        # --------------------------------------------------
        # GARIS
        # --------------------------------------------------

        cv2.line(
            frame,

            (
                x,
                baseline_y
            ),

            (
                x,
                y
            ),

            line_color,

            3
        )

        # --------------------------------------------------
        # TITIK PEAK
        # --------------------------------------------------

        cv2.circle(
            frame,

            (
                x,
                y
            ),

            7,

            line_color,

            -1
        )

        # --------------------------------------------------
        # TICK BASELINE
        # --------------------------------------------------

        cv2.line(
            frame,

            (
                x - 10,
                baseline_y
            ),

            (
                x + 10,
                baseline_y
            ),

            line_color,

            3
        )

        # --------------------------------------------------
        # TEXT
        # --------------------------------------------------

        text = (
            f"{label}: "
            f"{float(value):.2f} mm"
        )

        text_x = x + 10

        text_y = max(
            25,
            y - 10
        )

        cv2.putText(
            frame,

            text,

            (
                text_x,
                text_y
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.65,

            line_color,

            2
        )

    # ==========================================================
    # DRAW OVERLAY
    # ==========================================================

    def draw_overlay(
        self,
        frame,
        contour,
        result
    ):

        output = frame.copy()

        height, width = (
            output.shape[:2]
        )

        # ==================================================
        # CONTOUR
        # ==================================================

        if (
            self.show_contour
            and
            contour is not None
        ):

            cv2.drawContours(
                output,

                [
                    contour
                ],

                -1,

                (
                    255,
                    255,
                    255
                ),

                2
            )

        # ==================================================
        # DATA
        # ==================================================

        baseline_y = result.get(
            "baseline_y"
        )

        left_peak = result.get(
            "left_peak"
        )

        right_peak = result.get(
            "right_peak"
        )

        # ==================================================
        # BASELINE
        # ==================================================

        if baseline_y is not None:

            cv2.line(
                output,

                (
                    0,
                    baseline_y
                ),

                (
                    width,
                    baseline_y
                ),

                (
                    0,
                    0,
                    255
                ),

                3
            )

            cv2.putText(
                output,

                "BASELINE",

                (
                    10,
                    max(
                        25,
                        baseline_y - 10
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (
                    0,
                    0,
                    255
                ),

                2
            )

        # ==================================================
        # REFERENCE
        # ==================================================

        if self.show_reference:

            self.draw_reference_lines(
                output,
                baseline_y,
                width
            )

        # ==================================================
        # KIRI
        # ==================================================

        self.draw_measurement_line(
            output,

            left_peak,

            baseline_y,

            "KIRI",

            result.get(
                "left_height",
                0
            ),

            (
                0,
                255,
                0
            )
        )

        # ==================================================
        # KANAN
        # ==================================================

        self.draw_measurement_line(
            output,

            right_peak,

            baseline_y,

            "KANAN",

            result.get(
                "right_height",
                0
            ),

            (
                255,
                0,
                0
            )
        )

        # ==================================================
        # PANEL
        # ==================================================

        panel_height = 180

        overlay = output.copy()

        cv2.rectangle(
            overlay,

            (
                0,
                0
            ),

            (
                min(
                    width,
                    500
                ),
                panel_height
            ),

            (
                0,
                0,
                0
            ),

            -1
        )

        output = cv2.addWeighted(
            overlay,

            0.65,

            output,

            0.35,

            0
        )

        # ==================================================
        # NILAI KIRI
        # ==================================================

        left_height = float(
            result.get(
                "left_height",
                0
            )
        )

        right_height = float(
            result.get(
                "right_height",
                0
            )
        )

        cv2.putText(
            output,

            f"KIRI  : "
            f"{left_height:.2f} mm",

            (
                10,
                30
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.65,

            (
                0,
                255,
                0
            ),

            2
        )

        # ==================================================
        # NILAI KANAN
        # ==================================================

        cv2.putText(
            output,

            f"KANAN : "
            f"{right_height:.2f} mm",

            (
                10,
                60
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.65,

            (
                255,
                0,
                0
            ),

            2
        )

        # ==================================================
        # STATUS KIRI
        # ==================================================

        cv2.putText(
            output,

            "Upper Kiri : "
            +
            result.get(
                "left_upper_status",
                "NG"
            ),

            (
                10,
                90
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (
                255,
                255,
                255
            ),

            2
        )

        cv2.putText(
            output,

            "Lower Kiri : "
            +
            result.get(
                "left_lower_status",
                "NG"
            ),

            (
                10,
                115
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (
                255,
                255,
                255
            ),

            2
        )

        # ==================================================
        # STATUS KANAN
        # ==================================================

        cv2.putText(
            output,

            "Upper Kanan : "
            +
            result.get(
                "right_upper_status",
                "NG"
            ),

            (
                250,
                90
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (
                255,
                255,
                255
            ),

            2
        )

        cv2.putText(
            output,

            "Lower Kanan : "
            +
            result.get(
                "right_lower_status",
                "NG"
            ),

            (
                250,
                115
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (
                255,
                255,
                255
            ),

            2
        )

        # ==================================================
        # HASIL
        # ==================================================

        hasil = result.get(
            "hasil",
            "NG"
        )

        if hasil == "GOOD":

            hasil_color = (
                0,
                255,
                0
            )

        else:

            hasil_color = (
                0,
                0,
                255
            )

        cv2.putText(
            output,

            f"HASIL: {hasil}",

            (
                10,
                150
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.75,

            hasil_color,

            3
        )

        return output

    # ==========================================================
    # DETECT
    # ==========================================================

    def detect(
        self,
        frame
    ):

        if frame is None:

            result = (
                self.empty_result()
            )

            self.last_result = (
                result.copy()
            )

            return result

        # ==================================================
        # CARI CONTOUR
        # ==================================================

        contour_data = (
            self.find_main_contour(
                frame
            )
        )

        # ==================================================
        # TIDAK ADA OBJEK
        # ==================================================

        if contour_data is None:

            result = (
                self.empty_result()
            )

            self.last_result = (
                result.copy()
            )

            return result

        contour = contour_data[
            "contour"
        ]

        frame_height, frame_width = (
            frame.shape[:2]
        )

        # ==================================================
        # CARI PEAK
        # ==================================================

        left_peak, right_peak = (
            self.find_peaks(
                contour,
                frame_width
            )
        )

        # ==================================================
        # CARI BASELINE
        # ==================================================

        baseline_y = (
            self.find_baseline(
                contour
            )
        )

        # ==================================================
        # TINGGI KIRI
        # ==================================================

        left_height = (
            self.calculate_height(

                baseline_y,

                left_peak[1]
                if left_peak is not None
                else None,

                self.left_pixels_per_mm

            )
        )

        # ==================================================
        # TINGGI KANAN
        # ==================================================

        right_height = (
            self.calculate_height(

                baseline_y,

                right_peak[1]
                if right_peak is not None
                else None,

                self.right_pixels_per_mm

            )
        )

        # ==================================================
        # STATUS KIRI
        # ==================================================

        left_upper_status = (
            self.check_upper(

                left_height,

                self.left_upper

            )
        )

        left_lower_status = (
            self.check_lower(

                left_height,

                self.left_lower

            )
        )

        # ==================================================
        # STATUS KANAN
        # ==================================================

        right_upper_status = (
            self.check_upper(

                right_height,

                self.right_upper

            )
        )

        right_lower_status = (
            self.check_lower(

                right_height,

                self.right_lower

            )
        )

        # ==================================================
        # HASIL
        # ==================================================

        hasil = (
            self.calculate_result(

                left_upper_status,

                left_lower_status,

                right_upper_status,

                right_lower_status

            )
        )

        # ==================================================
        # KOORDINAT GARIS REFERENSI
        # ==================================================

        left_lower_y = None
        left_upper_y = None
        right_lower_y = None
        right_upper_y = None

        if baseline_y is not None:

            if self.left_lower > 0:

                left_lower_y = int(
                    baseline_y -
                    (
                        self.left_lower *
                        self.left_pixels_per_mm
                    )
                )

            if self.left_upper > 0:

                left_upper_y = int(
                    baseline_y -
                    (
                        self.left_upper *
                        self.left_pixels_per_mm
                    )
                )

            if self.right_lower > 0:

                right_lower_y = int(
                    baseline_y -
                    (
                        self.right_lower *
                        self.right_pixels_per_mm
                    )
                )

            if self.right_upper > 0:

                right_upper_y = int(
                    baseline_y -
                    (
                        self.right_upper *
                        self.right_pixels_per_mm
                    )
                )

        # ==================================================
        # RESULT
        # ==================================================

        result = {

            "found":
                True,

            "left_height":
                left_height,

            "right_height":
                right_height,

            "tinggi_kiri":
                left_height,

            "tinggi_kanan":
                right_height,

            "left_upper_status":
                left_upper_status,

            "left_lower_status":
                left_lower_status,

            "right_upper_status":
                right_upper_status,

            "right_lower_status":
                right_lower_status,

            "upper_kiri":
                left_upper_status,

            "lower_kiri":
                left_lower_status,

            "upper_kanan":
                right_upper_status,

            "lower_kanan":
                right_lower_status,

            "hasil":
                hasil,

            "status":
                "OBJECT_DETECTED",

            "baseline_y":
                baseline_y,

            "left_peak":
                left_peak,

            "right_peak":
                right_peak,

            "left_lower_y":
                left_lower_y,

            "left_upper_y":
                left_upper_y,

            "right_lower_y":
                right_lower_y,

            "right_upper_y":
                right_upper_y
        }

        self.last_result = (
            result.copy()
        )

        return result

    # ==========================================================
    # PROCESS
    # ==========================================================

    def process(
        self,
        frame
    ):

        if frame is None:

            return (
                None,
                self.empty_result()
            )

        # ==================================================
        # DETECT
        # ==================================================

        result = (
            self.detect(
                frame
            )
        )

        # ==================================================
        # NO OBJECT
        # ==================================================

        if not result.get(
            "found",
            False
        ):

            output = frame.copy()

            cv2.putText(
                output,

                "OBJEK TIDAK TERDETEKSI",

                (
                    20,
                    40
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.8,

                (
                    0,
                    0,
                    255
                ),

                3
            )

            return (
                output,
                result
            )

        # ==================================================
        # CONTOUR UNTUK OVERLAY
        # ==================================================

        contour_data = (
            self.find_main_contour(
                frame
            )
        )

        contour = None

        if contour_data is not None:

            contour = contour_data[
                "contour"
            ]

        # ==================================================
        # DRAW OVERLAY
        # ==================================================

        output = (
            self.draw_overlay(

                frame,

                contour,

                result

            )
        )

        return (
            output,
            result
        )

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(
        self,
        frame
    ):

        return self.process(
            frame
        )

    # ==========================================================
    # GET RESULT
    # ==========================================================

    def get_result(self):

        return (
            self.last_result.copy()
        )