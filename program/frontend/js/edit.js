// ==========================================================
// EDIT DATA
// ==========================================================


function bukaEdit(item) {

    document.getElementById("edit-id").value =
        item.id ?? "";


    document.getElementById("edit-tanggal").value =
        item.tanggal ?? "";


    document.getElementById("edit-waktu").value =
        item.waktu ?? "";


    document.getElementById("edit-tinggi-kiri").value =
        item.tinggi_kiri ?? "";


    document.getElementById("edit-tinggi-kanan").value =
        item.tinggi_kanan ?? "";


    document.getElementById("edit-upper-kiri").value =
        item.upper_kiri ?? "OK";


    document.getElementById("edit-lower-kiri").value =
        item.lower_kiri ?? "OK";


    document.getElementById("edit-upper-kanan").value =
        item.upper_kanan ?? "OK";


    document.getElementById("edit-lower-kanan").value =
        item.lower_kanan ?? "OK";


    document.getElementById("edit-hasil").value =
        item.hasil ?? "GOOD";


    document.getElementById("edit-popup").style.display =
        "flex";
}


// ==========================================================
// TUTUP POPUP
// ==========================================================

function tutupEdit() {

    document.getElementById("edit-popup").style.display =
        "none";

}


// ==========================================================
// SIMPAN EDIT
// ==========================================================

async function simpanEdit() {

    const data = {

        id:
            document.getElementById(
                "edit-id"
            ).value,

        tanggal:
            document.getElementById(
                "edit-tanggal"
            ).value,

        waktu:
            document.getElementById(
                "edit-waktu"
            ).value,

        tinggi_kiri:
            document.getElementById(
                "edit-tinggi-kiri"
            ).value,

        tinggi_kanan:
            document.getElementById(
                "edit-tinggi-kanan"
            ).value,

        upper_kiri:
            document.getElementById(
                "edit-upper-kiri"
            ).value,

        lower_kiri:
            document.getElementById(
                "edit-lower-kiri"
            ).value,

        upper_kanan:
            document.getElementById(
                "edit-upper-kanan"
            ).value,

        lower_kanan:
            document.getElementById(
                "edit-lower-kanan"
            ).value,

        hasil:
            document.getElementById(
                "edit-hasil"
            ).value
    };


    if (!data.id) {

        alert("ID data tidak ditemukan.");

        return;

    }


    try {

        const response =
            await fetch(
                "/api/edit",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(data)
                }
            );


        const result =
            await response.json();


        if (result.status !== "ok") {

            alert(
                result.message ||
                "Gagal mengubah data."
            );

            return;

        }


        alert(
            "Data berhasil diubah."
        );


        tutupEdit();


        await loadData();

    }
    catch (error) {

        console.error(error);

        alert(
            "Tidak dapat terhubung ke Raspberry."
        );

    }

}


// ==========================================================
// BUTTON
// ==========================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        const saveButton =
            document.getElementById(
                "edit-save"
            );


        const cancelButton =
            document.getElementById(
                "edit-cancel"
            );


        if (saveButton) {

            saveButton.addEventListener(
                "click",
                simpanEdit
            );

        }


        if (cancelButton) {

            cancelButton.addEventListener(
                "click",
                tutupEdit
            );

        }

    }
);