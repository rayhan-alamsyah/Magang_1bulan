// ==========================================================
// POWER.JS
// SISTEM QUALITY CONTROL
// ==========================================================


// ==========================================================
// SCROLL
// ==========================================================

window.addEventListener(
    "load",
    function () {

        try {

            window.scrollTo(
                0,
                0
            );

        } catch (error) {

            console.log(
                "Scroll error:",
                error
            );

        }

    }
);


// ==========================================================
// CAMERA STREAM
// ==========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const cameraStream =
            document.getElementById(
                "camera-stream"
            );


        if (!cameraStream) {

            return;

        }


        cameraStream.onload =
            function () {

                console.log(
                    "Camera stream aktif."
                );

            };


        cameraStream.onerror =
            function () {

                console.log(
                    "Camera stream error."
                );

            };

    }
);


// ==========================================================
// TANGGAL
// ==========================================================

function ambilTanggalSekarang() {

    const sekarang =
        new Date();


    const tahun =
        sekarang.getFullYear();


    const bulan =
        String(
            sekarang.getMonth() + 1
        ).padStart(
            2,
            "0"
        );


    const tanggal =
        String(
            sekarang.getDate()
        ).padStart(
            2,
            "0"
        );


    return (
        tahun +
        "-" +
        bulan +
        "-" +
        tanggal
    );
}


// ==========================================================
// WAKTU
// ==========================================================

function ambilWaktuSekarang() {

    const sekarang =
        new Date();


    const jam =
        String(
            sekarang.getHours()
        ).padStart(
            2,
            "0"
        );


    const menit =
        String(
            sekarang.getMinutes()
        ).padStart(
            2,
            "0"
        );


    const detik =
        String(
            sekarang.getSeconds()
        ).padStart(
            2,
            "0"
        );


    return (
        jam +
        ":" +
        menit +
        ":" +
        detik
    );
}


// ==========================================================
// TENTUKAN HASIL QC
// ==========================================================

function tentukanHasilQC(
    data
) {

    const upperKiri =
        String(
            data.upper_kiri || "NG"
        ).toUpperCase();


    const lowerKiri =
        String(
            data.lower_kiri || "NG"
        ).toUpperCase();


    const upperKanan =
        String(
            data.upper_kanan || "NG"
        ).toUpperCase();


    const lowerKanan =
        String(
            data.lower_kanan || "NG"
        ).toUpperCase();


    const semuaOK = (

        upperKiri === "OK" &&

        lowerKiri === "OK" &&

        upperKanan === "OK" &&

        lowerKanan === "OK"

    );


    if (semuaOK) {

        return "GOOD";

    }


    const upperNG = (

        upperKiri === "NG" ||

        upperKanan === "NG"

    );


    const lowerNG = (

        lowerKiri === "NG" ||

        lowerKanan === "NG"

    );


    if (
        upperNG &&
        lowerNG
    ) {

        return "NG UPPER + LOWER";

    }


    if (upperNG) {

        return "NG UPPER";

    }


    if (lowerNG) {

        return "NG LOWER";

    }


    return "NG";
}


// ==========================================================
// NORMALISASI STATUS
// ==========================================================

function normalisasiStatus(
    status
) {

    const value =
        String(
            status || ""
        ).trim().toUpperCase();


    if (value === "OK") {

        return "OK";

    }


    return "NG";
}


// ==========================================================
// SIMPAN HASIL QC
// ==========================================================

async function simpanHasilQC() {

    const tombol =
        document.getElementById(
            "save-button"
        );


    if (tombol) {

        tombol.disabled = true;

    }


    try {

        // ==================================================
        // AMBIL HASIL TERBARU DARI RASPBERRY
        // ==================================================

        const response =
            await fetch(
                "/api/detection",
                {
                    method: "GET",
                    cache: "no-store"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Gagal mengambil hasil deteksi."
            );

        }


        const responseData =
            await response.json();


        const data =
            responseData.data;


        if (!data) {

            throw new Error(
                "Data deteksi kosong."
            );

        }


        // ==================================================
        // WAJIB ADA OBJEK
        // ==================================================

        if (
            data.found !== true ||
            data.status === "NO_OBJECT"
        ) {

            alert(
                "Objek belum terdeteksi.\n\n" +
                "Data tidak disimpan."
            );

            return;

        }


        // ==================================================
        // TINGGI
        // ==================================================

        const tinggiKiri =
            Number(
                data.tinggi_kiri ??
                data.left_height ??
                0
            );


        const tinggiKanan =
            Number(
                data.tinggi_kanan ??
                data.right_height ??
                0
            );


        if (
            !Number.isFinite(
                tinggiKiri
            ) ||
            !Number.isFinite(
                tinggiKanan
            ) ||
            tinggiKiri <= 0 ||
            tinggiKanan <= 0
        ) {

            alert(
                "Nilai pengukuran belum valid.\n\n" +
                "Data tidak disimpan."
            );

            return;

        }


        // ==================================================
        // STATUS
        // ==================================================

        const upperKiri =
            normalisasiStatus(
                data.upper_kiri ??
                data.left_upper_status
            );


        const lowerKiri =
            normalisasiStatus(
                data.lower_kiri ??
                data.left_lower_status
            );


        const upperKanan =
            normalisasiStatus(
                data.upper_kanan ??
                data.right_upper_status
            );


        const lowerKanan =
            normalisasiStatus(
                data.lower_kanan ??
                data.right_lower_status
            );


        // ==================================================
        // HASIL
        // ==================================================

        const hasil =
            tentukanHasilQC({

                upper_kiri:
                    upperKiri,

                lower_kiri:
                    lowerKiri,

                upper_kanan:
                    upperKanan,

                lower_kanan:
                    lowerKanan

            });


        // ==================================================
        // DATA
        // ==================================================

        const dataSimpan = {

            tanggal:
                ambilTanggalSekarang(),

            waktu:
                ambilWaktuSekarang(),

            tinggi_kiri:
                tinggiKiri,

            tinggi_kanan:
                tinggiKanan,

            upper_kiri:
                upperKiri,

            lower_kiri:
                lowerKiri,

            upper_kanan:
                upperKanan,

            lower_kanan:
                lowerKanan,

            hasil:
                hasil

        };


        console.log(
            "Data yang dikirim:",
            dataSimpan
        );


        // ==================================================
        // KIRIM KE RASPBERRY
        //
        // FOTO TIDAK DIAMBIL DARI BROWSER.
        //
        // app.py yang akan mengambil latest_frame
        // dan menyimpannya sebagai JPG.
        // ==================================================

        const saveResponse =
            await fetch(
                "/api/save",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            dataSimpan
                        )

                }
            );


        const hasilSave =
            await saveResponse.json();


        if (!saveResponse.ok) {

            throw new Error(

                hasilSave.message ||
                "Gagal menyimpan data."

            );

        }


        if (
            hasilSave.status !== "ok"
        ) {

            throw new Error(

                hasilSave.message ||
                "Data gagal disimpan."

            );

        }


        // ==================================================
        // SUKSES
        // ==================================================

        alert(

            "Data QC berhasil disimpan.\n\n" +

            "Foto hasil pengukuran juga berhasil disimpan."

        );


        console.log(
            "Foto:",
            hasilSave.foto
        );


        // ==================================================
        // REFRESH DATA
        // ==================================================

        if (
            typeof loadData === "function"
        ) {

            await loadData();

        }


    } catch (error) {

        console.error(
            "Simpan QC error:",
            error
        );


        alert(

            "Gagal menyimpan data QC.\n\n" +
            error.message

        );


    } finally {

        if (tombol) {

            tombol.disabled = false;

        }

    }
}


// ==========================================================
// PASANG EVENT TOMBOL SIMPAN
// ==========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const tombol =
            document.getElementById(
                "save-button"
            );


        if (!tombol) {

            console.log(
                "Tombol save-button tidak ditemukan."
            );

            return;

        }


        tombol.addEventListener(

            "click",

            simpanHasilQC

        );

    }
);


// ==========================================================
// MODAL POWER
// ==========================================================

function bukaModalPower() {

    const modal =
        document.getElementById(
            "power-modal"
        );


    if (modal) {

        modal.style.display =
            "flex";

    }

}


// ==========================================================
// TUTUP MODAL POWER
// ==========================================================

function tutupModalPower() {

    const modal =
        document.getElementById(
            "power-modal"
        );


    if (modal) {

        modal.style.display =
            "none";

    }

}


// ==========================================================
// SHUTDOWN / RESTART
// ==========================================================

async function jalankanShutdown(
    action
) {

    if (
        action !== "shutdown" &&
        action !== "restart"
    ) {

        return;

    }


    let pesan;


    if (action === "shutdown") {

        pesan =
            "Yakin ingin mematikan Raspberry Pi?";

    } else {

        pesan =
            "Yakin ingin restart Raspberry Pi?";

    }


    const yakin =
        confirm(
            pesan
        );


    if (!yakin) {

        return;

    }


    try {

        const response =
            await fetch(
                "/api/shutdown",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            action:
                                action
                        })

                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(

                result.message ||
                "Perintah gagal."

            );

        }


        alert(
            result.message ||
            "Perintah berhasil dikirim."
        );


    } catch (error) {

        console.error(
            "Power error:",
            error
        );


        alert(

            "Gagal menjalankan perintah.\n\n" +
            error.message

        );

    }

}


// ==========================================================
// TUTUP MODAL JIKA KLIK LUAR
// ==========================================================

document.addEventListener(
    "click",
    function (event) {

        const modal =
            document.getElementById(
                "power-modal"
            );


        if (!modal) {

            return;

        }


        if (
            event.target === modal
        ) {

            modal.style.display =
                "none";

        }

    }
);