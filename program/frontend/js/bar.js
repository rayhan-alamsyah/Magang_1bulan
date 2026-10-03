/* ==========================================================
   BAR ATAS DAN BAR BAWAH
   ========================================================== */

const topBar = document.getElementById("top-bar");
const bottomBar = document.getElementById("bottom-bar");

let hideBarTimer = null;


/* ==========================================================
   TAMPILKAN BAR
   ========================================================== */

function tampilkanBar() {

    if (topBar) {
        topBar.classList.remove("hidden");
    }

    if (bottomBar) {
        bottomBar.classList.remove("hidden");
    }

    mulaiTimerBar();
}


/* ==========================================================
   SEMBUNYIKAN BAR
   ========================================================== */

function sembunyikanBar() {

    if (topBar) {
        topBar.classList.add("hidden");
    }

    if (bottomBar) {
        bottomBar.classList.add("hidden");
    }
}


/* ==========================================================
   TIMER
   ========================================================== */

function mulaiTimerBar() {

    clearTimeout(hideBarTimer);

    hideBarTimer = setTimeout(function() {

        sembunyikanBar();

    }, 2500);
}


/* ==========================================================
   DETEKSI SCROLL
   ========================================================== */

let posisiScrollSebelumnya = window.scrollY;


window.addEventListener(
    "scroll",
    function() {

        const posisiSekarang = window.scrollY;


        /*
         * Scroll ke bawah
         */

        if (posisiSekarang > posisiScrollSebelumnya) {

            tampilkanBar();

        }


        /*
         * Scroll ke atas
         */

        else if (posisiSekarang < posisiScrollSebelumnya) {

            tampilkanBar();

        }


        posisiScrollSebelumnya = posisiSekarang;

    },
    {
        passive: true
    }
);


/* ==========================================================
   MOUSE BERGERAK
   ========================================================== */

window.addEventListener(
    "mousemove",
    function() {

        tampilkanBar();

    }
);


/* ==========================================================
   TOUCH HP
   ========================================================== */

window.addEventListener(
    "touchstart",
    function() {

        tampilkanBar();

    },
    {
        passive: true
    }
);


/* ==========================================================
   AWAL
   ========================================================== */

tampilkanBar();