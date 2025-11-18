import random
from flask import (
    Flask, request, jsonify,
    render_template, session, redirect, url_for, flash
)

app = Flask(__name__)
app.secret_key = "kel1cripto"

# ==========================
#  KONSTAN PESAN AKHIR (RANDOM FACTS)
# ==========================

FACT_MESSAGES = [
    "Nihilist Cipher pernah dipakai oleh kelompok revolusioner Rusia (Nihilists) pada akhir abad ke-19 untuk mengatur aksi rahasia termasuk rencana yang berhasil membantu menembus pengawasan polisi Tsar.",
    "Hangman pernah dianggap terlalu gelap untuk anak sekolah di Amerika pada tahun 1970-an, sehingga beberapa sekolah melarang game ini dan menggantinya dengan versi lucu bernama Snowman.",
    "Pemecahan sandi Enigma oleh tim Alan Turing membuat Sekutu bisa membaca pesan rahasia Jerman. Banyak ahli bilang hal ini mempercepat akhir perang hingga 2 tahun."
]

# ==========================
#  KONFIGURASI POLYBIUS 5x5
# ==========================

# Nihilist cipher klasik pakai Polybius 5x5 (I dan J digabung)
ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # tidak ada J


def build_polybius_square():
    """
    Bangun mapping huruf <-> angka (11..55) untuk Polybius square.
    Contoh: A=11, B=12, ..., E=15, F=21, ..., Z=55
    """
    letter_to_num = {}
    num_to_letter = {}
    idx = 0
    for row in range(1, 6):
        for col in range(1, 6):
            letter = ALPHABET[idx]
            num = int(f"{row}{col}")
            letter_to_num[letter] = num
            num_to_letter[num] = letter
            idx += 1
    return letter_to_num, num_to_letter


LETTER_TO_NUM, NUM_TO_LETTER = build_polybius_square()


def prepare_text(text: str) -> str:
    """
    - Uppercase
    - Hapus karakter non huruf
    - Gabungkan J -> I karena pakai 5x5 square
    """
    text = text.upper()
    cleaned = []
    for ch in text:
        if ch == "J":
            ch = "I"
        if ch.isalpha():
            cleaned.append(ch)
    return "".join(cleaned)


def text_to_numbers(text: str):
    """
    Ubah teks (huruf saja) jadi list angka Polybius (misal: "AB" -> [11, 12])
    """
    text = prepare_text(text)
    numbers = []
    for ch in text:
        numbers.append(LETTER_TO_NUM[ch])
    return numbers


def numbers_to_text(numbers):
    """
    Ubah list angka Polybius (11..55) jadi teks (misal: [11, 12] -> "AB").
    """
    chars = []
    for num in numbers:
        letter = NUM_TO_LETTER.get(num)
        if letter is None:
            continue
        chars.append(letter)
    return "".join(chars)


def expand_key_numbers(key_numbers, length):
    """
    Ulangi key_numbers sampai panjangnya >= length, lalu dipotong pas.
    """
    expanded = []
    while len(expanded) < length:
        expanded.extend(key_numbers)
    return expanded[:length]


# ==========================
#  NIHILIST CIPHER
# ==========================

def nihilist_encrypt(plaintext: str, key: str) -> str:
    """
    Encrypt Nihilist cipher.
    Output: string angka dipisah spasi, misal: "53 66 81 ..."
    """
    pt_nums = text_to_numbers(plaintext)
    key_nums = text_to_numbers(key)

    if not key_nums:
        raise ValueError("Key tidak boleh kosong atau tidak mengandung huruf.")

    key_nums_expanded = expand_key_numbers(key_nums, len(pt_nums))

    cipher_nums = []
    for p, k in zip(pt_nums, key_nums_expanded):
        cipher_nums.append(p + k)

    return " ".join(str(n) for n in cipher_nums)


def nihilist_decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypt Nihilist cipher.
    ciphertext diasumsikan berupa angka dipisah spasi, contoh: "53 66 81 ..."
    """
    cipher_nums = []
    for part in ciphertext.strip().split():
        if part.isdigit():
            cipher_nums.append(int(part))

    key_nums = text_to_numbers(key)
    if not key_nums:
        raise ValueError("Key tidak boleh kosong atau tidak mengandung huruf.")

    key_nums_expanded = expand_key_numbers(key_nums, len(cipher_nums))

    pt_nums = []
    for c, k in zip(cipher_nums, key_nums_expanded):
        pt_nums.append(c - k)

    plaintext = numbers_to_text(pt_nums)
    return plaintext


# ==========================
#  PESAN DEFAULT & RANDOM KEY
# ==========================

# Pesan yang DIENKRIP di dalam kotak
DEFAULT_MESSAGES = [
    "selamat datang. kata sandi untuk masuk ke halaman berikutnya adalah "
    "panjang pixel foto ini dikali lebarnya. semoga beruntung"
]


def generate_random_key(length: int = 6) -> str:
    """Generate key random dari ALPHABET (tanpa J)."""
    return "".join(random.choice(ALPHABET) for _ in range(length))


# ==========================
#  UTIL FLASK: BOX
# ==========================

def generate_box_size():
    width = random.randint(200, 800)
    height = random.randint(200, 500)
    return width, height


# ==========================
#  ROUTES NIHILIST API (OPSIONAL, MASIH ADA)
# ==========================

@app.route("/api/random-key-and-messages", methods=["GET"])
def api_random_key_and_messages():
    key = generate_random_key()

    cipher_list = []
    for msg in DEFAULT_MESSAGES:
        cipher = nihilist_encrypt(msg, key)
        cipher_list.append({
            "plaintext": msg,
            "cipher": cipher
        })

    return jsonify({
        "key": key,
        "cipher_messages": cipher_list
    })


@app.route("/api/encrypt", methods=["POST"])
def api_encrypt():
    data = request.get_json(silent=True) or {}
    key = data.get("key", "")
    message = data.get("message", "")

    if not key or not message:
        return jsonify({"error": "key dan message wajib diisi"}), 400

    try:
        cipher = nihilist_encrypt(message, key)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"cipher": cipher})


@app.route("/api/decrypt", methods=["POST"])
def api_decrypt():
    data = request.get_json(silent=True) or {}
    key = data.get("key", "")
    cipher = data.get("cipher", "")

    if not key or not cipher:
        return jsonify({"error": "key dan cipher wajib diisi"}), 400

    try:
        plaintext = nihilist_decrypt(cipher, key)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"plaintext": plaintext})


# ==========================
#  ROUTES FLOW GAME
#  home -> hangman -> cipher -> message
# ==========================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/hangman")
def hangman():
    # di template hangman.html kamu mainkan game-nya
    # dan kalau sudah benar, JS panggil /set_hangman_word
    return render_template("hangman.html")


@app.route("/set_hangman_word", methods=["POST"])
def set_hangman_word():
    """
    Dipanggil dari JavaScript ketika pemain sudah lolos hangman.
    Kata yang berhasil ditebak akan dikirim ke server dan disimpan di session.
    """
    word = request.form.get("word", "").strip()
    if not word:
        return "no word", 400

    session["hangman_success"] = True
    session["hangman_word"] = word.upper()   # biar cocok untuk cipher
    return ("", 204)  # No Content, tapi menandakan berhasil


@app.route("/cipher", methods=["GET", "POST"])
def cipher():
    # 1) pastikan user sudah beres Hangman
    if not session.get("hangman_success"):
        return redirect(url_for("hangman"))

    # 2) key = kata dari hangman
    key_word = session.get("hangman_word", "")
    if not key_word:
        # fallback kalau ada error
        key_word = generate_random_key()
        session["hangman_word"] = key_word

    session["nihilist_key"] = key_word  # simpan kalau-kalau perlu lagi

    # 3) pesan yang akan dienkripsi dan ditaruh di dalam kotak
    message = DEFAULT_MESSAGES[0]

    # 4) POST: user submit luas kotak
    if request.method == "POST":
        guess = request.form.get("password", "").strip()
        width = session.get("box_width")
        height = session.get("box_height")

        # regenerate cipher_text untuk ditampilkan lagi
        cipher_text = nihilist_encrypt(message, key_word)

        if width is None or height is None:
            flash("There's an error with the session. Generating a new puzzle.")
            width, height = generate_box_size()
            session["box_width"] = width
            session["box_height"] = height
            return render_template(
                "cipher.html",
                width=width, height=height,
                key=key_word,
                cipher_text=cipher_text
            )

        try:
            guess_int = int(guess)
        except ValueError:
            flash("Password is wrong.")
            return render_template(
                "cipher.html",
                width=width, height=height,
                key=key_word,
                cipher_text=cipher_text
            )

        correct_area = width * height

        if guess_int == correct_area:
            # buka akses ke message
            session["cipher_unlocked"] = True
            return redirect(url_for("message_page"))
        else:
            flash("Password is wrong.")
            return render_template(
                "cipher.html",
                width=width, height=height,
                key=key_word,
                cipher_text=cipher_text
            )

    # 5) GET: generate puzzle baru (ukuran kotak random + cipher baru)
    width, height = generate_box_size()
    session["box_width"] = width
    session["box_height"] = height

    cipher_text = nihilist_encrypt(message, key_word)

    return render_template(
        "cipher.html",
        width=width, height=height,
        key=key_word,
        cipher_text=cipher_text
    )


@app.route("/message")
def message_page():
    # hanya boleh diakses kalau cipher sudah berhasil dibuka
    if not session.get("cipher_unlocked"):
        return redirect(url_for("home"))

    random_fact = random.choice(FACT_MESSAGES)
    return render_template("message.html", message=random_fact)


if __name__ == "__main__":
    app.run(debug=True)