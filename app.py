from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)

app = Flask(__name__)
app.secret_key = "ganti_ini_dengan_secret_key_yang_aman"

# sementara: password yang benar
CORRECT_PASSWORD = "datascience"   # nanti bisa diganti hasil dekripsi nihilis
PLAINTEXT_MESSAGE = "Selamat, kamu berhasil memecahkan sandi Nihilist Cipher!"
### PASSWORD BERDASARKAN HASIL PANJANG X LEBAR PIXEL GAMBAR YANG AKAN DIBERIKAN ###


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/hangman")
def hangman():
    # nanti di sini bisa inisialisasi kata dsb, sekarang render dulu
    return render_template("hangman.html")


@app.route("/set_hangman_word", methods=["POST"])
def set_hangman_word():
    """
    Dipanggil dari JavaScript ketika pemain sudah lolos hangman.
    Kata yang berhasil ditebak akan dikirim ke server dan disimpan di session.
    """
    word = request.form.get("word", "").strip().lower()
    if not word:
        return "no word", 400

    session["hangman_success"] = True
    session["hangman_word"] = word
    return ("", 204)  # No Content, tapi menandakan berhasil


@app.route("/cipher", methods=["GET", "POST"])
def cipher():
    # cek apakah user sudah lewat hangman
    if not session.get("hangman_success"):
        return redirect(url_for("hangman"))

    # kata kunci yang berhasil ditebak di hangman
    key_word = session.get("hangman_word", "")

    # nanti ciphertext ini akan di-generate dari Nihilist cipher
    # menggunakan key_word
    # contoh placeholder:
    ciphertext = f"nihilist(ciphertext) dari kata: {key_word}"
    ### RISKA HARUS BIKIN FUNGSI DI SINI BUAT NGENCRYP DECRYPT NIHILIST CIPHER ###

    if request.method == "POST":
        password = request.form.get("password", "").strip()

        if password.lower() == CORRECT_PASSWORD.lower():
            session["cipher_unlocked"] = True
            return redirect(url_for("message_page"))
        else:
            flash("Password salah. Coba lagi ya.")

    return render_template("nihilist.html", ciphertext=ciphertext, key_word=key_word)


@app.route("/message")
def message_page():
    # hanya boleh diakses kalau password sudah benar
    if not session.get("cipher_unlocked"):
        return redirect(url_for("home"))

    return render_template("message.html", plaintext=PLAINTEXT_MESSAGE)


if __name__ == "__main__":
    app.run(debug=True)
