// ==========================================================
// TABEL.JS
// REKAP HARIAN + DATA QC
// ==========================================================

let semuaDataQC = [];
let tanggalAktif = null;


// ==========================================================
// TAMPILKAN DATA QC
// ==========================================================

function tampilkanData(data, tanggalFilter = null) {

    const tbody =
        document.querySelector(
            "#data-table tbody"
        );

    if (!tbody) {
        console.error(
            "tbody #data-table tidak ditemukan."
        );
        return;
    }


    // ------------------------------------------------------
    // Simpan semua data
    // ------------------------------------------------------

    semuaDataQC =
        Array.isArray(data)
            ? data
            : [];

    window.semuaDataQC =
        semuaDataQC;


    // ------------------------------------------------------
    // Simpan tanggal aktif
    // ------------------------------------------------------

    tanggalAktif =
        tanggalFilter;


    // ------------------------------------------------------
    // Bersihkan tabel
    // ------------------------------------------------------

    tbody.innerHTML = "";


    // ------------------------------------------------------
    // FILTER DATA
    // ------------------------------------------------------

    let dataTampil =
        semuaDataQC;

    if (tanggalFilter) {

        dataTampil =
            semuaDataQC.filter(
                item =>
                    String(
                        item.tanggal ?? ""
                    ) ===
                    String(
                        tanggalFilter
                    )
            );
    }


    // ------------------------------------------------------
    // JIKA TIDAK ADA DATA
    // ------------------------------------------------------

    if (dataTampil.length === 0) {

        const tr =
            document.createElement("tr");

        tr.innerHTML = `
            <td colspan="12"
                class="data-kosong">

                ${
                    tanggalFilter
                    ? `Tidak ada Data QC pada tanggal ${tanggalFilter}.`
                    : "Belum ada data QC."
                }

            </td>
        `;

        tbody.appendChild(tr);

        updateJudulDataQC(
            tanggalFilter
        );

        return;
    }


    // ------------------------------------------------------
    // URUTKAN DATA
    // TERBARU DI ATAS
    // ------------------------------------------------------

    dataTampil =
        [...dataTampil].sort(
            (a, b) => {

                const tanggalA =
                    String(
                        a.tanggal ?? ""
                    );

                const tanggalB =
                    String(
                        b.tanggal ?? ""
                    );

                if (
                    tanggalA !==
                    tanggalB
                ) {

                    return tanggalB.localeCompare(
                        tanggalA
                    );
                }


                const waktuA =
                    String(
                        a.waktu ?? ""
                    );

                const waktuB =
                    String(
                        b.waktu ?? ""
                    );

                return waktuB.localeCompare(
                    waktuA
                );
            }
        );


    // ------------------------------------------------------
    // BUAT BARIS
    // ------------------------------------------------------

    dataTampil.forEach(
        (item, index) => {

            const tr =
                document.createElement(
                    "tr"
                );


            // --------------------------------------------------
            // FOTO
            // --------------------------------------------------

            let fotoHTML = "-";

            if (
                item.foto &&
                item.foto !== "-"
            ) {

                let fotoURL =
                    String(
                        item.foto
                    );


                if (
                    !fotoURL.startsWith(
                        "http://"
                    ) &&
                    !fotoURL.startsWith(
                        "https://"
                    ) &&
                    !fotoURL.startsWith(
                        "/"
                    )
                ) {

                    fotoURL =
                        "/foto/" +
                        fotoURL;
                }


                fotoHTML = `
                    <img
                        src="${fotoURL}"
                        class="foto-hasil"
                        alt="Foto hasil QC"
                        onclick="bukaFoto(this.src)"
                        style="cursor: pointer;"
                        onerror="
                            this.style.display='none';
                            this.parentElement.innerHTML =
                            '<span class=\\'foto-error\\'>Foto tidak ditemukan</span>';
                        "
                    >
                `;
            }


            // --------------------------------------------------
            // STATUS
            // --------------------------------------------------

            const upperKiri =
                String(
                    item.upper_kiri ?? "-"
                ).toUpperCase();

            const lowerKiri =
                String(
                    item.lower_kiri ?? "-"
                ).toUpperCase();

            const upperKanan =
                String(
                    item.upper_kanan ?? "-"
                ).toUpperCase();

            const lowerKanan =
                String(
                    item.lower_kanan ?? "-"
                ).toUpperCase();


            // --------------------------------------------------
            // HASIL
            // --------------------------------------------------

            const hasil =
                String(
                    item.hasil ?? "-"
                ).toUpperCase();


            // --------------------------------------------------
            // HTML BARIS
            // --------------------------------------------------

            tr.innerHTML = `

                <td class="kolom-no">
                    ${index + 1}
                </td>

                <td>
                    ${item.tanggal ?? "-"}
                </td>

                <td>
                    ${item.waktu ?? "-"}
                </td>

                <td class="kolom-foto">
                    ${fotoHTML}
                </td>

                <td>
                    ${formatAngka(
                        item.tinggi_kiri
                    )} mm
                </td>

                <td>
                    ${formatAngka(
                        item.tinggi_kanan
                    )} mm
                </td>

                <td class="${kelasStatus(
                    upperKiri
                )}">
                    ${upperKiri}
                </td>

                <td class="${kelasStatus(
                    lowerKiri
                )}">
                    ${lowerKiri}
                </td>

                <td class="${kelasStatus(
                    upperKanan
                )}">
                    ${upperKanan}
                </td>

                <td class="${kelasStatus(
                    lowerKanan
                )}">
                    ${lowerKanan}
                </td>

                <td class="${kelasHasil(
                    hasil
                )}">
                    ${hasil}
                </td>

                <td class="kolom-aksi">

                    <button
                        class="btn-edit"
                        onclick='bukaEdit(${JSON.stringify(item)})'
                    >
                        EDIT
                    </button>

                    <button
                        class="btn-hapus"
                        onclick='hapusData(${JSON.stringify(item.id)})'
                    >
                        HAPUS
                    </button>

                </td>

            `;

            tbody.appendChild(tr);
        }
    );


    // ------------------------------------------------------
    // UPDATE JUDUL
    // ------------------------------------------------------

    updateJudulDataQC(
        tanggalFilter
    );
}


// ==========================================================
// FORMAT ANGKA
// ==========================================================

function formatAngka(value) {

    const number =
        Number(value);

    if (
        !Number.isFinite(number)
    ) {

        return "0.00";
    }

    return number.toFixed(2);
}


// ==========================================================
// KELAS STATUS
// ==========================================================

function kelasStatus(status) {

    if (
        status === "NG"
    ) {

        return "status-ng";
    }

    if (
        status === "OK"
    ) {

        return "status-ok";
    }

    return "";
}


// ==========================================================
// KELAS HASIL
// ==========================================================

function kelasHasil(hasil) {

    if (
        hasil === "GOOD"
    ) {

        return "hasil-good";
    }

    return "hasil-ng";
}


// ==========================================================
// UPDATE JUDUL DATA QC
// ==========================================================

function updateJudulDataQC(
    tanggal
) {

    const info =
        document.querySelector(
            "#data-qc-info"
        );

    if (!info) {
        return;
    }


    if (tanggal) {

        info.innerHTML = `
            Menampilkan Data QC tanggal
            <strong>${tanggal}</strong>.

            <button
                class="btn-reset-filter"
                onclick="tampilkanSemuaData()"
            >
                TAMPILKAN SEMUA
            </button>
        `;

    } else {

        info.innerHTML = `
            Menampilkan semua Data QC dari semua tanggal.
        `;
    }
}


// ==========================================================
// TAMPILKAN SEMUA DATA
// ==========================================================

function tampilkanSemuaData() {

    tanggalAktif = null;

    tampilkanData(
        semuaDataQC,
        null
    );


    const bagianDataQC =
        document.querySelector(
            "#bagian-data-qc"
        );

    if (bagianDataQC) {

        bagianDataQC.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
}


// ==========================================================
// KLIK REKAP HARIAN
// ==========================================================

function pilihTanggalRekap(
    tanggal
) {

    if (!tanggal) {
        return;
    }

    tanggalAktif =
        tanggal;


    tampilkanData(
        semuaDataQC,
        tanggal
    );


    const bagianDataQC =
        document.querySelector(
            "#bagian-data-qc"
        );

    if (bagianDataQC) {

        bagianDataQC.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
}


// ==========================================================
// TAMPILKAN REKAP HARIAN
//
// DATA QC DIKELOMPOKKAN BERDASARKAN TANGGAL
// ==========================================================

function tampilkanRekap(data) {

    const tbody =
        document.querySelector(
            "#rekap-table tbody"
        );

    if (!tbody) {

        console.error(
            "tbody #rekap-table tidak ditemukan."
        );

        return;
    }


    tbody.innerHTML = "";


    // ======================================================
    // CEK DATA
    // ======================================================

    if (
        !Array.isArray(data) ||
        data.length === 0
    ) {

        const tr =
            document.createElement(
                "tr"
            );

        tr.innerHTML = `
            <td colspan="7"
                class="data-kosong">

                Belum ada rekap data.

            </td>
        `;

        tbody.appendChild(tr);

        return;
    }


    // ======================================================
    // KELOMPOKKAN BERDASARKAN TANGGAL
    // ======================================================

    const rekapMap =
        {};


    data.forEach(item => {

        const tanggal =
            String(
                item.tanggal ?? ""
            ).trim();


        if (!tanggal) {
            return;
        }


        // --------------------------------------------------
        // Jika tanggal belum ada
        // --------------------------------------------------

        if (!rekapMap[tanggal]) {

            rekapMap[tanggal] = {

                tanggal: tanggal,

                good: 0,

                ng_upper_kiri: 0,

                ng_upper_kanan: 0,

                ng_lower_kiri: 0,

                ng_lower_kanan: 0

            };
        }


        const rekap =
            rekapMap[tanggal];


        // --------------------------------------------------
        // HASIL GOOD
        // --------------------------------------------------

        const hasil =
            String(
                item.hasil ?? ""
            ).toUpperCase();


        if (
            hasil === "GOOD"
        ) {

            rekap.good++;
        }


        // --------------------------------------------------
        // UPPER KIRI
        // --------------------------------------------------

        if (
            String(
                item.upper_kiri ?? ""
            ).toUpperCase()
            === "NG"
        ) {

            rekap.ng_upper_kiri++;
        }


        // --------------------------------------------------
        // UPPER KANAN
        // --------------------------------------------------

        if (
            String(
                item.upper_kanan ?? ""
            ).toUpperCase()
            === "NG"
        ) {

            rekap.ng_upper_kanan++;
        }


        // --------------------------------------------------
        // LOWER KIRI
        // --------------------------------------------------

        if (
            String(
                item.lower_kiri ?? ""
            ).toUpperCase()
            === "NG"
        ) {

            rekap.ng_lower_kiri++;
        }


        // --------------------------------------------------
        // LOWER KANAN
        // --------------------------------------------------

        if (
            String(
                item.lower_kanan ?? ""
            ).toUpperCase()
            === "NG"
        ) {

            rekap.ng_lower_kanan++;
        }

    });


    // ======================================================
    // UBAH OBJECT MENJADI ARRAY
    // ======================================================

    const dataUrut =
        Object.values(
            rekapMap
        ).sort(
            (a, b) =>
                String(
                    b.tanggal
                ).localeCompare(
                    String(
                        a.tanggal
                    )
                )
        );


    // ======================================================
    // BUAT BARIS REKAP
    // ======================================================

    dataUrut.forEach(
        item => {

            const tanggal =
                item.tanggal;


            const tr =
                document.createElement(
                    "tr"
                );


            tr.classList.add(
                "baris-rekap"
            );


            tr.title =
                `Klik untuk melihat Data QC ${tanggal}`;


            tr.onclick =
                function(event) {

                    if (
                        event.target.closest(
                            ".btn-hapus-hari"
                        )
                    ) {

                        return;
                    }


                    pilihTanggalRekap(
                        tanggal
                    );
                };


            tr.innerHTML = `

                <td class="tanggal-rekap">

                    <span class="tanggal-link">
                        ${tanggal}
                    </span>

                </td>

                <td>
                    ${item.good}
                </td>

                <td>
                    ${item.ng_upper_kiri}
                </td>

                <td>
                    ${item.ng_upper_kanan}
                </td>

                <td>
                    ${item.ng_lower_kiri}
                </td>

                <td>
                    ${item.ng_lower_kanan}
                </td>

                <td>

                    <button
                        class="btn-hapus-hari"
                        onclick="event.stopPropagation(); hapusHari('${tanggal}')"
                    >
                        HAPUS HARI
                    </button>

                </td>

            `;


            tbody.appendChild(
                tr
            );
        }
    );
}


// ==========================================================
// BUKA FOTO
// ==========================================================

function bukaFoto(url) {

    let popup =
        document.querySelector(
            "#foto-popup"
        );


    if (!popup) {

        popup =
            document.createElement(
                "div"
            );

        popup.id =
            "foto-popup";

        popup.className =
            "foto-popup";


        popup.innerHTML = `

            <div
                class="foto-popup-overlay"
                onclick="tutupFoto()"
            >

                <div
                    class="foto-popup-content"
                    onclick="event.stopPropagation()"
                >

                    <button
                        class="foto-popup-close"
                        onclick="tutupFoto()"
                    >
                        ×
                    </button>

                    <img
                        id="foto-popup-image"
                        src=""
                        alt="Foto hasil QC"
                    >

                </div>

            </div>

        `;


        document.body.appendChild(
            popup
        );
    }


    const image =
        document.querySelector(
            "#foto-popup-image"
        );


    if (image) {

        image.src =
            url;
    }


    popup.classList.add(
        "aktif"
    );
}


// ==========================================================
// TUTUP FOTO
// ==========================================================

function tutupFoto() {

    const popup =
        document.querySelector(
            "#foto-popup"
        );

    if (popup) {

        popup.classList.remove(
            "aktif"
        );
    }
}


// ==========================================================
// HAPUS DATA QC
// ==========================================================

async function hapusData(id) {

    if (
        id === null ||
        id === undefined ||
        id === ""
    ) {
        alert(
            "ID data tidak ditemukan."
        );
        return;
    }


    const yakin =
        confirm(
            "Apakah data QC ini ingin dihapus?"
        );


    if (!yakin) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/delete",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        id: id
                    })
                }
            );


        const result =
            await response.json();


        if (
            response.ok &&
            result.success
        ) {

            alert(
                "Data QC berhasil dihapus."
            );


            if (
                typeof loadData ===
                "function"
            ) {

                await loadData();
            }

        } else {

            alert(
                result.message ||
                "Gagal menghapus data."
            );
        }


    } catch (error) {

        console.error(
            "Error hapus data:",
            error
        );

        alert(
            "Terjadi kesalahan saat menghapus data."
        );
    }
}


// ==========================================================
// HAPUS SATU HARI
// ==========================================================

async function hapusHari(
    tanggal
) {

    if (!tanggal) {
        return;
    }


    const yakin =
        confirm(
            `Hapus SEMUA Data QC pada tanggal ${tanggal}?`
        );


    if (!yakin) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/delete-day",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        tanggal: tanggal
                    })
                }
            );


        const result =
            await response.json();


        if (
            response.ok &&
            result.success
        ) {

            alert(
                `Data tanggal ${tanggal} berhasil dihapus.`
            );


            tanggalAktif =
                null;


            if (
                typeof loadData ===
                "function"
            ) {

                await loadData();
            }

        } else {

            alert(
                result.message ||
                "Gagal menghapus data hari."
            );
        }


    } catch (error) {

        console.error(
            "Error hapus hari:",
            error
        );

        alert(
            "Terjadi kesalahan saat menghapus hari."
        );
    }
}