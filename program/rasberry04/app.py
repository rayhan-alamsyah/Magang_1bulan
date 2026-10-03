# ==========================================================
# APP.PY
# SISTEM QUALITY CONTROL SPAKBOR
# ==========================================================

from flask import (
    Flask,
    send_from_directory,
    send_file,
    jsonify,
    request,
    Response
)

from pathlib import Path

import socket
import cv2
import threading
import time
import os
import subprocess


import excel

from camera import Camera

from ng_detector import NGDetector

from config import SETTINGS


# ==========================================================
# PATH
# ==========================================================

BASE_DIR = (
    Path(__file__).resolve().parent
)


PROGRAM_DIR = (
    BASE_DIR.parent
)


ROOT_DIR = (
    PROGRAM_DIR.parent
)


FRONTEND_DIR = (
    PROGRAM_DIR /
    "frontend"
)


# ==========================================================
# FLASK
# ==========================================================

app = Flask(
    __name__
)


# ==========================================================
# CAMERA
# ==========================================================

camera = Camera(
    SETTINGS
)


camera_lock = threading.Lock()


# ==========================================================
# DETECTOR
# ==========================================================

detector = None

detector_lock = threading.Lock()


# ==========================================================
# HASIL DETEKSI TERBARU
# ==========================================================

latest_detection = {

    "found":
        False,

    "tinggi_kiri":
        0.0,

    "tinggi_kanan":
        0.0,

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
        "NO_OBJECT"
}


latest_detection_lock = (
    threading.Lock()
)


# ==========================================================
# FRAME TERAKHIR
#
# FRAME INI SUDAH MEMILIKI:
# - CONTOUR
# - BASELINE
# - GARIS KIRI
# - GARIS KANAN
# - STATUS
# - HASIL
#
# FRAME INI YANG AKAN DISIMPAN
# ==========================================================

latest_frame = None

latest_frame_lock = (
    threading.Lock()
)


# ==========================================================
# BUAT DETECTOR
# ==========================================================

def buat_detector():

    try:

        print(
            "\n" +
            "=" * 60
        )


        print(
            "MEMBUAT NG DETECTOR"
        )


        print(
            "=" * 60
        )


        detector_obj = NGDetector(
            SETTINGS
        )


        print(
            "Detector : NGDetector"
        )


        print(
            "Config   : SETTINGS"
        )


        print(
            "Overlay  : AKTIF"
        )


        print(
            f"Kiri     : "
            f"{detector_obj.left_lower:.2f}"
            f" - "
            f"{detector_obj.left_upper:.2f}"
            f" mm"
        )


        print(
            f"Kanan    : "
            f"{detector_obj.right_lower:.2f}"
            f" - "
            f"{detector_obj.right_upper:.2f}"
            f" mm"
        )


        print(
            f"Pixel/mm : "
            f"kiri "
            f"{detector_obj.left_pixels_per_mm:.2f}"
            f" | kanan "
            f"{detector_obj.right_pixels_per_mm:.2f}"
        )


        return detector_obj


    except Exception as error:

        print(
            "ERROR NG DETECTOR:",
            error
        )


        return None


# ==========================================================
# UPDATE DETECTION
# ==========================================================

def update_detection(
    data
):

    global latest_detection


    if not isinstance(
        data,
        dict
    ):

        return


    # ======================================================
    # CEK OBJECT
    # ======================================================

    found = (

        bool(
            data.get(
                "found",
                False
            )
        )

        and

        data.get(
            "status"
        ) != "NO_OBJECT"

    )


    # ======================================================
    # TINGGI KIRI
    # ======================================================

    try:

        left_height = float(

            data.get(
                "left_height",
                data.get(
                    "tinggi_kiri",
                    0
                )
            )

            or 0

        )

    except Exception:

        left_height = 0.0


    # ======================================================
    # TINGGI KANAN
    # ======================================================

    try:

        right_height = float(

            data.get(
                "right_height",
                data.get(
                    "tinggi_kanan",
                    0
                )
            )

            or 0

        )

    except Exception:

        right_height = 0.0


    # ======================================================
    # TIDAK ADA OBJEK
    # ======================================================

    if not found:

        left_height = 0.0

        right_height = 0.0

        upper_kiri = "NG"

        lower_kiri = "NG"

        upper_kanan = "NG"

        lower_kanan = "NG"

        hasil = "NG"


    # ======================================================
    # ADA OBJEK
    # ======================================================

    else:

        upper_kiri = (

            "NG"

            if data.get(
                "left_upper_status",
                data.get(
                    "upper_kiri"
                )
            ) == "NG"

            else "OK"

        )


        lower_kiri = (

            "NG"

            if data.get(
                "left_lower_status",
                data.get(
                    "lower_kiri"
                )
            ) == "NG"

            else "OK"

        )


        upper_kanan = (

            "NG"

            if data.get(
                "right_upper_status",
                data.get(
                    "upper_kanan"
                )
            ) == "NG"

            else "OK"

        )


        lower_kanan = (

            "NG"

            if data.get(
                "right_lower_status",
                data.get(
                    "lower_kanan"
                )
            ) == "NG"

            else "OK"

        )


        upper_ng = (

            upper_kiri == "NG"

            or

            upper_kanan == "NG"

        )


        lower_ng = (

            lower_kiri == "NG"

            or

            lower_kanan == "NG"

        )


        if (
            not upper_ng
            and
            not lower_ng
        ):

            hasil = "GOOD"

        elif (
            upper_ng
            and
            lower_ng
        ):

            hasil = (
                "NG UPPER + LOWER"
            )

        elif upper_ng:

            hasil = "NG UPPER"

        else:

            hasil = "NG LOWER"


    # ======================================================
    # SIMPAN
    # ======================================================

    with latest_detection_lock:

        latest_detection = {

            "found":
                found,

            "tinggi_kiri":
                left_height,

            "tinggi_kanan":
                right_height,

            "upper_kiri":
                upper_kiri,

            "lower_kiri":
                lower_kiri,

            "upper_kanan":
                upper_kanan,

            "lower_kanan":
                lower_kanan,

            "hasil":
                hasil,

            "status":
                (
                    "OBJECT_DETECTED"
                    if found
                    else
                    "NO_OBJECT"
                )
        }


# ==========================================================
# PROSES FRAME
# ==========================================================

def proses_frame(
    frame
):

    if (
        frame is None
        or
        detector is None
    ):

        return frame


    try:

        with detector_lock:

            output, detection = (
                detector.process(
                    frame
                )
            )


        if detection is not None:

            update_detection(
                detection
            )


        if output is None:

            return frame


        return output


    except Exception as error:

        print(
            "Detector error:",
            error
        )


        return frame


# ==========================================================
# AMBIL FRAME
# ==========================================================

def ambil_frame():

    global latest_frame


    # ======================================================
    # BACA CAMERA
    # ======================================================

    with camera_lock:

        frame = camera.read()


    if frame is None:

        return None


    # ======================================================
    # PROSES DETECTOR
    # ======================================================

    output = proses_frame(
        frame
    )


    if output is None:

        return None


    # ======================================================
    # SIMPAN FRAME OVERLAY
    # ======================================================

    with latest_frame_lock:

        latest_frame = (
            output.copy()
        )


    return output


# ==========================================================
# GENERATOR CAMERA
# ==========================================================

def generate_camera():

    while True:

        frame = ambil_frame()


        if frame is None:

            time.sleep(
                0.05
            )

            continue


        # ==================================================
        # JPEG
        # ==================================================

        success, buffer = (
            cv2.imencode(
                ".jpg",
                frame,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    80
                ]
            )
        )


        if success:

            yield (

                b"--frame\r\n"

                b"Content-Type: "
                b"image/jpeg\r\n\r\n"

                +
                buffer.tobytes()

                +
                b"\r\n"
            )


        time.sleep(
            0.03
        )


# ==========================================================
# SIMPAN FOTO FRAME TERAKHIR
# ==========================================================

def simpan_foto_terakhir(
    tanggal,
    waktu
):

    # ======================================================
    # COPY FRAME
    # ======================================================

    with latest_frame_lock:

        if latest_frame is None:

            print(
                "Tidak ada frame "
                "untuk disimpan."
            )

            return None


        frame = (
            latest_frame.copy()
        )


    # ======================================================
    # FOLDER TANGGAL
    # ======================================================

    folder = (
        excel.PHOTO_DIR /
        str(tanggal)
    )


    folder.mkdir(
        parents=True,
        exist_ok=True
    )


    # ======================================================
    # NAMA FILE
    # ======================================================

    safe_waktu = (
        str(waktu)
        .replace(
            ":",
            "-"
        )
        .replace(
            "/",
            "-"
        )
        .replace(
            "\\",
            "-"
        )
    )


    nama_file = (
        f"{tanggal}_"
        f"{safe_waktu}.jpg"
    )


    path_foto = (
        folder /
        nama_file
    )


    # ======================================================
    # SIMPAN JPEG
    # ======================================================

    berhasil = cv2.imwrite(

        str(path_foto),

        frame

    )


    if not berhasil:

        print(
            "Gagal menyimpan foto:",
            path_foto
        )


        return None


    # ======================================================
    # PATH RELATIF TERHADAP data/foto
    # ======================================================

    relative_path = (
        path_foto.relative_to(
            excel.PHOTO_DIR
        )
    )


    relative_path = str(
        relative_path
    ).replace(
        "\\",
        "/"
    )


    print(
        "Foto tersimpan:",
        path_foto
    )


    return relative_path


# ==========================================================
# FRONTEND
# ==========================================================

@app.route("/")
def index():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# ==========================================================
# CSS
# ==========================================================

@app.route(
    "/css/<path:filename>"
)
def css(filename):

    return send_from_directory(
        FRONTEND_DIR / "css",
        filename
    )


# ==========================================================
# JAVASCRIPT
# ==========================================================

@app.route(
    "/js/<path:filename>"
)
def javascript(filename):

    return send_from_directory(
        FRONTEND_DIR / "js",
        filename
    )


# ==========================================================
# FOTO
# ==========================================================

@app.route(
    "/foto/<path:nama_file>"
)
def foto(nama_file):

    root = (
        excel.PHOTO_DIR.resolve()
    )


    path = (
        excel.PHOTO_DIR /
        nama_file
    ).resolve()


    # ======================================================
    # KEAMANAN PATH
    # ======================================================

    if (
        not path.is_file()
        or
        root not in path.parents
    ):

        return jsonify({

            "message":
                "Foto tidak ditemukan"

        }), 404


    return send_file(
        path
    )


# ==========================================================
# TEST API
# ==========================================================

@app.route(
    "/api/test"
)
def api_test():

    return jsonify({

        "status":
            "ok",

        "message":
            "Web QC terhubung "
            "ke Raspberry Pi"

    })


# ==========================================================
# DATA
# ==========================================================

@app.route(
    "/api/data"
)
def api_data():

    try:

        return jsonify(
            excel.baca_data()
        )


    except Exception as error:

        return jsonify({

            "status":
                "error",

            "message":
                str(error)

        }), 500


# ==========================================================
# REKAP
# ==========================================================

@app.route(
    "/api/rekap"
)
def api_rekap():

    try:

        return jsonify(
            excel.hitung_rekap()
        )


    except Exception as error:

        return jsonify({

            "status":
                "error",

            "message":
                str(error)

        }), 500


# ==========================================================
# CURRENT
# ==========================================================

@app.route(
    "/api/current"
)
def api_current():

    with latest_detection_lock:

        return jsonify(
            latest_detection.copy()
        )


# ==========================================================
# DETECTION
# ==========================================================

@app.route(
    "/api/detection"
)
def api_detection():

    with latest_detection_lock:

        return jsonify({

            "status":
                "ok",

            "data":
                latest_detection.copy()

        })


# ==========================================================
# SAVE
# ==========================================================

@app.route(
    "/api/save",
    methods=["POST"]
)
def api_save():

    try:

        data = (
            request.get_json(
                silent=True
            )
            or
            {}
        )


        # ==================================================
        # AMBIL DETEKSI TERBARU
        # ==================================================

        with latest_detection_lock:

            detection = (
                latest_detection.copy()
            )


        # ==================================================
        # WAJIB ADA OBJEK
        # ==================================================

        if (
            not detection.get(
                "found"
            )

            or

            detection.get(
                "status"
            ) == "NO_OBJECT"
        ):

            return jsonify({

                "status":
                    "error",

                "message":
                    "Objek belum "
                    "terdeteksi. "
                    "Data tidak disimpan."

            }), 400


        # ==================================================
        # TINGGI
        # ==================================================

        try:

            tinggi_kiri = float(

                data.get(

                    "tinggi_kiri",

                    detection.get(
                        "tinggi_kiri",
                        0
                    )

                )

            )


            tinggi_kanan = float(

                data.get(

                    "tinggi_kanan",

                    detection.get(
                        "tinggi_kanan",
                        0
                    )

                )

            )


        except Exception:

            return jsonify({

                "status":
                    "error",

                "message":
                    "Nilai tinggi "
                    "kiri/kanan "
                    "tidak valid"

            }), 400


        # ==================================================
        # CEK NILAI
        # ==================================================

        if (
            tinggi_kiri <= 0
            or
            tinggi_kanan <= 0
        ):

            return jsonify({

                "status":
                    "error",

                "message":
                    "Nilai pengukuran "
                    "belum valid"

            }), 400


        # ==================================================
        # STATUS
        # ==================================================

        status_fields = [

            "upper_kiri",

            "lower_kiri",

            "upper_kanan",

            "lower_kanan"

        ]


        for field in status_fields:

            value = str(

                data.get(

                    field,

                    detection.get(
                        field,
                        "NG"
                    )

                )

            ).upper()


            if value not in (
                "OK",
                "NG"
            ):

                value = "NG"


            data[field] = value


        # ==================================================
        # HITUNG HASIL
        # ==================================================

        upper_ng = (

            data["upper_kiri"]
            == "NG"

            or

            data["upper_kanan"]
            == "NG"

        )


        lower_ng = (

            data["lower_kiri"]
            == "NG"

            or

            data["lower_kanan"]
            == "NG"

        )


        if (
            not upper_ng
            and
            not lower_ng
        ):

            hasil = "GOOD"

        elif (
            upper_ng
            and
            lower_ng
        ):

            hasil = (
                "NG UPPER + LOWER"
            )

        elif upper_ng:

            hasil = "NG UPPER"

        else:

            hasil = "NG LOWER"


        # ==================================================
        # TANGGAL / WAKTU
        # ==================================================

        tanggal = str(

            data.get(
                "tanggal"
            )

            or

            time.strftime(
                "%Y-%m-%d"
            )

        )


        waktu = str(

            data.get(
                "waktu"
            )

            or

            time.strftime(
                "%H:%M:%S"
            )

        )


        # ==================================================
        # SIMPAN FOTO OVERLAY
        # ==================================================

        foto_path = (
            simpan_foto_terakhir(
                tanggal,
                waktu
            )
        )


        if not foto_path:

            return jsonify({

                "status":
                    "error",

                "message":
                    "Frame kamera terakhir "
                    "tidak tersedia. "
                    "Pastikan camera stream aktif."

            }), 500


        # ==================================================
        # DATA YANG DISIMPAN
        # ==================================================

        data_simpan = {

            "tanggal":
                tanggal,

            "waktu":
                waktu,

            "foto":
                foto_path,

            "tinggi_kiri":
                tinggi_kiri,

            "tinggi_kanan":
                tinggi_kanan,

            "upper_kiri":
                data["upper_kiri"],

            "lower_kiri":
                data["lower_kiri"],

            "upper_kanan":
                data["upper_kanan"],

            "lower_kanan":
                data["lower_kanan"],

            "hasil":
                hasil
        }


        # ==================================================
        # SIMPAN EXCEL
        # ==================================================

        data_id = (
            excel.simpan_data(
                data_simpan
            )
        )


        print(
            f"Data tersimpan: "
            f"{data_id}"
        )


        print(
            f"Foto: "
            f"{foto_path}"
        )


        return jsonify({

            "status":
                "ok",

            "message":
                "Data QC berhasil "
                "disimpan",

            "id":
                data_id,

            "foto":
                foto_path,

            "data":
                data_simpan

        })


    except Exception as error:

        print(
            "ERROR SIMPAN DATA:",
            error
        )


        return jsonify({

            "status":
                "error",

            "message":
                "Gagal menyimpan "
                "data: "
                + str(error)

        }), 500


# ==========================================================
# EDIT
# ==========================================================

@app.route(
    "/api/edit",
    methods=["POST"]
)
def api_edit():

    try:

        data = (
            request.get_json(
                silent=True
            )
            or
            {}
        )


        if not data.get(
            "id"
        ):

            return jsonify({

                "status":
                    "error",

                "message":
                    "ID data "
                    "tidak ditemukan"

            }), 400


        # ==================================================
        # NORMALISASI STATUS
        # ==================================================

        for field in [

            "upper_kiri",

            "lower_kiri",

            "upper_kanan",

            "lower_kanan"

        ]:

            value = str(
                data.get(
                    field,
                    "NG"
                )
            ).upper()


            if value not in (
                "OK",
                "NG"
            ):

                value = "NG"


            data[field] = value


        # ==================================================
        # HITUNG HASIL
        # ==================================================

        upper_ng = (

            data["upper_kiri"]
            == "NG"

            or

            data["upper_kanan"]
            == "NG"

        )


        lower_ng = (

            data["lower_kiri"]
            == "NG"

            or

            data["lower_kanan"]
            == "NG"

        )


        if (
            not upper_ng
            and
            not lower_ng
        ):

            data["hasil"] = "GOOD"

        elif (
            upper_ng
            and
            lower_ng
        ):

            data["hasil"] = (
                "NG UPPER + LOWER"
            )

        elif upper_ng:

            data["hasil"] = (
                "NG UPPER"
            )

        else:

            data["hasil"] = (
                "NG LOWER"
            )


        # ==================================================
        # EDIT
        # ==================================================

        berhasil = (
            excel.edit_data(
                data
            )
        )


        if berhasil:

            return jsonify({

                "status":
                    "ok",

                "message":
                    "Data berhasil "
                    "diubah"

            })


        return jsonify({

            "status":
                "error",

            "message":
                "Data tidak ditemukan"

        }), 404


    except Exception as error:

        return jsonify({

            "status":
                "error",

            "message":
                "Gagal mengubah "
                "data: "
                + str(error)

        }), 500


# ==========================================================
# DELETE
# ==========================================================

@app.route(
    "/api/delete",
    methods=["POST"]
)
def api_delete():

    try:

        data = (
            request.get_json(
                silent=True
            )
            or
            {}
        )


        berhasil = (
            excel.hapus_data(
                data.get(
                    "id"
                )
            )
        )


        if berhasil:

            return jsonify({

                "status":
                    "ok",

                "success":
                    True,

                "message":
                    "Data QC berhasil "
                    "dihapus"

            })


        return jsonify({

            "status":
                "error",

            "success":
                False,

            "message":
                "Data tidak ditemukan"

        }), 404


    except Exception as error:

        return jsonify({

            "status":
                "error",

            "success":
                False,

            "message":
                str(error)

        }), 500


# ==========================================================
# DELETE DAY
# ==========================================================

@app.route(
    "/api/delete-day",
    methods=["POST"]
)
def api_delete_day():

    try:

        data = (
            request.get_json(
                silent=True
            )
            or
            {}
        )


        tanggal = data.get(
            "tanggal"
        )


        berhasil = (
            excel.hapus_tanggal(
                tanggal
            )
        )


        if berhasil:

            return jsonify({

                "status":
                    "ok",

                "success":
                    True,

                "message":
                    "Semua data pada "
                    "tanggal berhasil "
                    "dihapus",

                "tanggal":
                    tanggal

            })


        return jsonify({

            "status":
                "error",

            "success":
                False,

            "message":
                "Tidak ada data "
                "pada tanggal tersebut"

        }), 404


    except Exception as error:

        return jsonify({

            "status":
                "error",

            "success":
                False,

            "message":
                str(error)

        }), 500


# ==========================================================
# CAMERA STREAM
# ==========================================================

@app.route(
    "/camera"
)
def camera_stream():

    return Response(

        generate_camera(),

        mimetype=(
            "multipart/"
            "x-mixed-replace;"
            " boundary=frame"
        )

    )


# ==========================================================
# CAMERA STATUS
# ==========================================================

@app.route(
    "/api/camera"
)
def camera_status():

    if camera.cap is not None:

        return jsonify({

            "status":
                "ok",

            "camera":
                camera.index

        })


    return jsonify({

        "status":
            "error",

        "message":
            "Camera belum dibuka"

    })


# ==========================================================
# GET IP
# ==========================================================

def get_ip_address():

    try:

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )


        sock.connect(
            (
                "8.8.8.8",
                80
            )
        )


        ip = sock.getsockname()[0]


        sock.close()


        return ip


    except Exception:

        return "127.0.0.1"


# ==========================================================
# SHUTDOWN / RESTART
# ==========================================================

@app.route(
    "/api/shutdown",
    methods=["POST"]
)
def api_shutdown():

    try:

        data = (
            request.get_json(
                silent=True
            )
            or
            {}
        )


        action = data.get(
            "action",
            "shutdown"
        )


        if action not in (
            "shutdown",
            "restart"
        ):

            action = "shutdown"


        # ==================================================
        # POWER THREAD
        # ==================================================

        def power():

            time.sleep(
                1
            )


            camera.release()


            # ----------------------------------------------
            # RASPBERRY / LINUX
            # ----------------------------------------------

            if os.name != "nt":

                command = (

                    "-r"

                    if action == "restart"

                    else

                    "-h"

                )


                subprocess.Popen([

                    "sudo",

                    "shutdown",

                    command,

                    "now"

                ])


            # ----------------------------------------------
            # WINDOWS
            # ----------------------------------------------

            else:

                print(
                    "Perintah power "
                    "tidak dijalankan "
                    "karena sistem Windows."
                )


        threading.Thread(
            target=power,
            daemon=True
        ).start()


        return jsonify({

            "status":
                "ok",

            "message":
                f"Perintah "
                f"{action} diterima"

        })


    except Exception as error:

        return jsonify({

            "status":
                "error",

            "message":
                str(error)

        }), 500


# ==========================================================
# MAIN
# ==========================================================

def main():

    global detector


    print(
        "\n" +
        "=" * 60
    )


    print(
        "          SISTEM QUALITY CONTROL"
    )


    print(
        "=" * 60
    )


    # ======================================================
    # EXCEL
    # ======================================================

    excel.buat_excel()


    excel.update_rekap()


    # ======================================================
    # DETECTOR
    # ======================================================

    detector = buat_detector()


    # ======================================================
    # CAMERA
    # ======================================================

    try:

        camera.open()


    except Exception as error:

        print(
            "CAMERA TIDAK BERHASIL "
            "DIBUKA:",
            error
        )


    # ======================================================
    # IP
    # ======================================================

    ip = get_ip_address()


    print(
        "\nRaspberry Pi : "
        "http://localhost:5000"
    )


    print(
        f"HP / Laptop  : "
        f"http://{ip}:5000"
    )


    print(
        f"Excel        : "
        f"{excel.lokasi_excel()}"
    )


    print(
        f"Camera       : "
        f"{camera.index}"
    )


    print(
        "Detector     : "
        +
        (
            "AKTIF"
            if detector
            else
            "TIDAK AKTIF"
        )
    )


    # ======================================================
    # FLASK
    # ======================================================

    try:

        app.run(

            host="0.0.0.0",

            port=5000,

            debug=False,

            threaded=True

        )


    finally:

        camera.release()


# ==========================================================
# START
# ==========================================================

if __name__ == "__main__":

    main()