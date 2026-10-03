from pathlib import Path
import subprocess
import sys
import time


# ============================================================
# LOKASI PROJECT
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

RASPBERRY_DIR = (
    ROOT_DIR
    / "program"
    / "rasberry04"
)

RASPBERRY_APP = (
    RASPBERRY_DIR
    / "app.py"
)


# ============================================================
# CEK FILE
# ============================================================

def cek_file():

    print(
        "Memeriksa file program..."
    )

    if not RASPBERRY_APP.exists():

        print()

        print(
            "ERROR: app Raspberry "
            "tidak ditemukan."
        )

        print(
            RASPBERRY_APP
        )

        return False

    print(
        "Semua file utama ditemukan."
    )

    return True


# ============================================================
# JALANKAN RASPBERRY APP
# ============================================================

def jalankan_raspberry():

    print()

    print("=" * 60)

    print(
        "MENJALANKAN SISTEM RASPBERRY"
    )

    print("=" * 60)

    print()

    print(
        f"File : {RASPBERRY_APP}"
    )

    print()


    proses = subprocess.Popen(

        [
            sys.executable,
            str(RASPBERRY_APP)
        ],

        cwd=RASPBERRY_DIR

    )


    return proses


# ============================================================
# MAIN
# ============================================================

def main():

    print()

    print("=" * 60)

    print(
        "          SISTEM QUALITY CONTROL"
    )

    print("=" * 60)

    print()


    # ========================================================
    # CEK
    # ========================================================

    if not cek_file():

        input(
            "\nTekan ENTER untuk keluar..."
        )

        return


    # ========================================================
    # JALANKAN RASPBERRY APP
    # ========================================================

    raspberry = jalankan_raspberry()


    # ========================================================
    # TUNGGU
    # ========================================================

    print(
        "Menunggu sistem Raspberry aktif..."
    )

    time.sleep(3)


    # ========================================================
    # CEK APAKAH PROGRAM MASIH HIDUP
    # ========================================================

    if raspberry.poll() is not None:

        print()

        print("=" * 60)

        print(
            "SISTEM RASPBERRY GAGAL DIJALANKAN"
        )

        print("=" * 60)

        print()

        print(
            f"Kode keluar: "
            f"{raspberry.returncode}"
        )

        print()

        input(
            "Tekan ENTER untuk keluar..."
        )

        return


    # ========================================================
    # SISTEM RUNNING
    # ========================================================

    print()

    print("=" * 60)

    print(
        "SISTEM QC SUDAH BERJALAN"
    )

    print("=" * 60)

    print()

    print(
        "Web server dijalankan dari:"
    )

    print(
        RASPBERRY_APP
    )

    print()

    print(
        "Tekan CTRL + C untuk "
        "menghentikan sistem."
    )

    print()


    # ========================================================
    # TUNGGU
    # ========================================================

    try:

        raspberry.wait()

    except KeyboardInterrupt:

        print()

        print(
            "Menghentikan sistem..."
        )

        raspberry.terminate()

        try:

            raspberry.wait(
                timeout=5
            )

        except subprocess.TimeoutExpired:

            raspberry.kill()

        print(
            "Sistem berhenti."
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()