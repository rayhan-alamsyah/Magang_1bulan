// ==========================================================
// API.JS
// Sistem Quality Control
// ==========================================================


// ==========================================================
// TEST KONEKSI
// ==========================================================

async function testConnection() {

    try {

        const response = await fetch("/api/test");

        if (!response.ok) {
            throw new Error("Server tidak merespons");
        }

        const data = await response.json();

        const status =
            document.getElementById("system-status");

        if (status) {

            status.textContent = "TERHUBUNG";

            status.classList.remove("offline");
            status.classList.add("online");
        }

    } catch (error) {

        console.error(
            "Koneksi gagal:",
            error
        );

        const status =
            document.getElementById("system-status");

        if (status) {

            status.textContent =
                "TIDAK TERHUBUNG";

            status.classList.remove("online");
            status.classList.add("offline");
        }
    }
}


// ==========================================================
// LOAD DATA QC
// ==========================================================

async function loadData() {

    try {

        const response =
            await fetch("/api/data");

        if (!response.ok) {

            throw new Error(
                "Gagal mengambil data QC"
            );
        }

        const data =
            await response.json();

        console.log(
            "DATA QC:",
            data
        );


        // --------------------------------------------------
        // Simpan semua data secara global
        // --------------------------------------------------

        window.semuaDataQC =
            Array.isArray(data)
                ? data
                : [];


        // --------------------------------------------------
        // Tampilkan DATA QC
        // --------------------------------------------------

        if (
            typeof tampilkanData ===
            "function"
        ) {

            tampilkanData(
                window.semuaDataQC
            );
        }


        // --------------------------------------------------
        // Tampilkan REKAP
        //
        // Rekap menggunakan data QC yang sama.
        // --------------------------------------------------

        if (
            typeof tampilkanRekap ===
            "function"
        ) {

            tampilkanRekap(
                window.semuaDataQC
            );
        }


    } catch (error) {

        console.error(
            "Gagal load data:",
            error
        );

        window.semuaDataQC = [];


        if (
            typeof tampilkanData ===
            "function"
        ) {

            tampilkanData([]);
        }


        if (
            typeof tampilkanRekap ===
            "function"
        ) {

            tampilkanRekap([]);
        }
    }
}


// ==========================================================
// LOAD HASIL PENGUKURAN SEKARANG
// ==========================================================

async function loadCurrentResult() {

    try {

        const response =
            await fetch(
                "/api/current"
            );

        if (!response.ok) {

            throw new Error(
                "Gagal mengambil hasil sekarang"
            );
        }

        const result =
            await response.json();

        console.log(
            "HASIL SEKARANG:",
            result
        );


        if (
            typeof tampilkanHasilSekarang ===
            "function"
        ) {

            tampilkanHasilSekarang(
                result
            );
        }

    } catch (error) {

        console.error(
            "Gagal mengambil hasil sekarang:",
            error
        );
    }
}


// ==========================================================
// TAMPILKAN HASIL SEKARANG
// ==========================================================

function tampilkanHasilSekarang(result) {

    if (!result) {
        return;
    }


    // ------------------------------------------------------
    // Tinggi kiri
    // ------------------------------------------------------

    const kiri =
        document.getElementById(
            "hasil-tinggi-kiri"
        );

    if (kiri) {

        const nilai =
            Number(
                result.tinggi_kiri
            );

        kiri.textContent =
            Number.isFinite(nilai)
                ? `${nilai.toFixed(2)} mm`
                : "0.00 mm";
    }


    // ------------------------------------------------------
    // Tinggi kanan
    // ------------------------------------------------------

    const kanan =
        document.getElementById(
            "hasil-tinggi-kanan"
        );

    if (kanan) {

        const nilai =
            Number(
                result.tinggi_kanan
            );

        kanan.textContent =
            Number.isFinite(nilai)
                ? `${nilai.toFixed(2)} mm`
                : "0.00 mm";
    }


    // ------------------------------------------------------
    // Hasil QC
    // ------------------------------------------------------

    const hasil =
        document.getElementById(
            "hasil-qc"
        );

    if (hasil) {

        hasil.textContent =
            result.hasil ?? "-";
    }
}


// ==========================================================
// SIMPAN DATA
//
// Fungsi utama tombol SIMPAN berada di power.js.
// Fungsi ini tetap dipertahankan agar kode lama tidak rusak.
// ==========================================================

async function simpanData() {

    if (
        typeof simpanHasilQC ===
        "function"
    ) {

        await simpanHasilQC();

        return;
    }

    console.warn(
        "Fungsi simpanHasilQC() tidak ditemukan."
    );
}


// ==========================================================
// INITIAL LOAD
// ==========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        // --------------------------------------------------
        // Cek koneksi
        // --------------------------------------------------

        testConnection();


        // --------------------------------------------------
        // Ambil data QC SATU KALI ketika halaman dibuka
        // --------------------------------------------------

        loadData();


        // --------------------------------------------------
        // Ambil hasil pengukuran saat ini
        // --------------------------------------------------

        loadCurrentResult();


        // --------------------------------------------------
        // Update hasil pengukuran setiap 500 ms
        //
        // Ini tetap diperlukan supaya angka pengukuran
        // kiri/kanan dan hasil QC selalu terbaru.
        // --------------------------------------------------

        setInterval(
            loadCurrentResult,
            500
        );


        // --------------------------------------------------
        // TIDAK ADA:
        //
        // setInterval(loadData, 5000);
        //
        // Data QC tidak refresh sendiri.
        // Data berubah setelah SIMPAN / HAPUS.
        // --------------------------------------------------

    }
);