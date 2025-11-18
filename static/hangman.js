document.addEventListener("DOMContentLoaded", function () {
    // --- CONFIG GAME ---
    const MAX_WRONG = 6;        // salah maksimal per kata
    const MAX_LIVES = 3;        // total nyawa

    // semua kata huruf kecil
    const wordList = [
        "overdispersion",
        "frequentist",
        "asymptotic",
        "generalized",
        "embedding",
        "transformer",
        "inference",
        "neighbors",
        "convolutional",
        "gaussian",
        "recognition",
        "lemmatization",
        "kumaraswamy",
        "gompertz",
        "mahalanobis",
        "equipartition",
        "hierarchical",
        "experimental",
        "bidirectional",
        "homogenous"
    ];

    // --- STATE GAME ---
    let lives = MAX_LIVES;
    let wrongGuesses = 0;
    let currentWord = "";   // selalu lowercase
    let guessedLetters = new Set();
    let gameOver = false;
    let alreadySentToServer = false;

    // --- DOM ELEMENTS ---
    const gameArea = document.getElementById("game-area");
    const wordContainer = document.getElementById("word-container");
    const livesSpan = document.getElementById("lives");
    const wrongCountSpan = document.getElementById("wrong-count");
    const usedLettersDiv = document.getElementById("used-letters");
    const messageDiv = document.getElementById("message");
    const letterInput = document.getElementById("letter-input");
    const guessButton = document.getElementById("guess-button");

    // URL dari data-attribute (diisi sama Jinja di HTML)
    const setHangmanUrl = gameArea.dataset.setHangmanUrl;
    const cipherUrl = gameArea.dataset.cipherUrl;

    // --- FUNGSI UTAMA ---

    function pickRandomWord() {
        const idx = Math.floor(Math.random() * wordList.length);
        currentWord = wordList[idx];  // sudah lowercase
        guessedLetters.clear();
        wrongGuesses = 0;
        updateUI();
        setMessage("");
    }

    function updateUI() {
        livesSpan.textContent = lives;
        wrongCountSpan.textContent = wrongGuesses;

        const displayChars = [];
        for (let i = 0; i < currentWord.length; i++) {
            const ch = currentWord[i];
            if (ch === " " || ch === "-") {
                displayChars.push(ch);
            } else if (guessedLetters.has(ch)) {
                displayChars.push(ch.toUpperCase());
            } else {
                displayChars.push("_");
            }
        }
        wordContainer.textContent = displayChars.join(" ");

        // tampilan huruf terpakai
        if (guessedLetters.size > 0) {
            const used = Array.from(guessedLetters).sort().join(" ");
            usedLettersDiv.textContent = used.toUpperCase();
        } else {
            usedLettersDiv.textContent = "-";
        }
    }

    function setMessage(msg, type = "info") {
        messageDiv.textContent = msg;
        messageDiv.className = "text-center fw-semibold";
        if (type === "success") {
            messageDiv.classList.add("text-success");
        } else if (type === "error") {
            messageDiv.classList.add("text-danger");
        } else if (type === "warning") {
            messageDiv.classList.add("text-warning");
        } else {
            messageDiv.classList.add("text-light");
        }
    }

    function isWordSolved() {
        for (let i = 0; i < currentWord.length; i++) {
            const ch = currentWord[i];
            if (ch !== " " && ch !== "-" && !guessedLetters.has(ch)) {
                return false;
            }
        }
        return true;
    }

    function sendWordToServerAndGoToCipher() {
        if (alreadySentToServer) return;
        alreadySentToServer = true;

        const formData = new URLSearchParams();
        formData.append("word", currentWord);

        fetch(setHangmanUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData.toString()
        })
        .then(function (res) {
            if (!res.ok) {
                throw new Error("Server error: " + res.status);
            }
            window.location.href = cipherUrl;
        })
        .catch(function (err) {
            console.error(err);
            alreadySentToServer = false;
            setMessage("Gagal mengirim kata ke server. Coba lagi atau refresh halaman.", "error");
        });
    }

    function handleGuess() {
        if (gameOver || alreadySentToServer) {
            return;
        }

        const raw = letterInput.value.trim().toLowerCase();
        letterInput.value = "";

        if (!raw || raw.length !== 1 || !/[a-z]/.test(raw)) {
            setMessage("Masukkan satu huruf a-z.", "warning");
            return;
        }

        if (guessedLetters.has(raw)) {
            setMessage("Huruf itu sudah kamu coba.", "warning");
            return;
        }

        guessedLetters.add(raw);

        if (currentWord.includes(raw)) {
            setMessage("Betul! Lanjut tebak huruf lain.", "success");
        } else {
            wrongGuesses += 1;
            setMessage("Salah tebak. Hati-hati, maksimal 6 salah per kata.", "error");
        }

        updateUI();

        // Cek menang / kalah untuk kata ini
        if (isWordSolved()) {
            // lolos hangman: kata berhasil, wrongGuesses < 6, lives >= 1
            if (wrongGuesses < MAX_WRONG && lives >= 1) {
                setMessage("Keren! Kamu berhasil menebak: " + currentWord, "success");
                sendWordToServerAndGoToCipher();
            }
        } else if (wrongGuesses >= MAX_WRONG) {
            // Kalah untuk kata ini
            lives -= 1;

            if (lives > 0) {
                updateUI();
                setMessage(
                    "Kamu kehabisan percobaan untuk kata: " + currentWord +
                    ". Nyawa berkurang 1. Kata baru muncul!", "error"
                );
                setTimeout(function () {
                    pickRandomWord();
                }, 1500);
            } else {
                // Game over total
                updateUI();
                setMessage(
                    "Game over. Nyawa habis.",
                    "error"
                );
                endGame();
            }
        }
    }

    function endGame() {
        gameOver = true;
        letterInput.disabled = true;
        guessButton.disabled = true;
    }

    // --- EVENT LISTENER ---
    guessButton.addEventListener("click", handleGuess);

    letterInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            handleGuess();
        }
    });

    letterInput.focus();
    pickRandomWord();
});
