from flask import Flask, send_from_directory, jsonify
from pathlib import Path
import socket


# ============================================================
# KONFIGURASI DASAR
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)


# ============================================================
# HALAMAN UTAMA
# ============================================================

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


# ============================================================
# FILE CSS
# ============================================================

@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory(
        BASE_DIR / "css",
        filename
    )


# ============================================================
# FILE JAVASCRIPT
# ============================================================

@app.route("/js/<path:filename>")
def javascript(filename):
    return send_from_directory(
        BASE_DIR / "js",
        filename
    )


# ============================================================
# TEST KONEKSI
# ============================================================

@app.route("/api/test")
def api_test():

    return jsonify({
        "status": "ok",
        "message": "Web QC terhubung ke Raspberry Pi"
    })


# ============================================================
# MENCARI IP RASPBERRY PI
# ============================================================

def get_ip_address():

    try:

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        # Tidak mengirim data.
        # Hanya digunakan untuk mengetahui
        # alamat IP jaringan yang sedang aktif.
        sock.connect(("8.8.8.8", 80))

        ip = sock.getsockname()[0]

        sock.close()

        return ip

    except Exception:

        return "127.0.0.1"


# ============================================================
# MENJALANKAN SERVER
# ============================================================

if __name__ == "__main__":

    ip = get_ip_address()

    print()
    print("=" * 55)
    print("              SISTEM QUALITY CONTROL")
    print("=" * 55)
    print()
    print("Web server aktif")
    print()
    print("Buka di Raspberry Pi:")
    print("http://localhost:5000")
    print()
    print("Buka dari HP / Laptop:")
    print(f"http://{ip}:5000")
    print()
    print("Pastikan HP / Laptop berada di jaringan")
    print("yang sama dengan Raspberry Pi.")
    print()
    print("=" * 55)
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )