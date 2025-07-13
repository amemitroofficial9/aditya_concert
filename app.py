from flask import Flask, render_template, request, redirect, session, url_for
import os
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "concert_secret_key"

# Folder to store uploaded screenshots
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CATEGORY_PRICES = {
    "fan": 2999,
    "general": 1499,
    "gold": 799
}

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/book', methods=["GET", "POST"])
def book():
    if request.method == "POST":
        session["name"] = request.form.get("name")
        session["phone"] = request.form.get("phone")
        session["email"] = request.form.get("email")
        category = request.form.get("category")
        session["tickets"] = int(request.form.get("tickets", 1))

        if category not in CATEGORY_PRICES:
            return "Invalid category selected."

        amount = CATEGORY_PRICES[category] * session["tickets"]
        session["category"] = category
        session["amount"] = amount

        # Clear previous promo on new booking
        session.pop("promo", None)
        session.pop("discount", None)

        return redirect("/payment")

    return render_template("index.html")

@app.route('/payment', methods=["GET", "POST"])
def payment():
    error = None
    amount = session.get("amount", 0)
    promo_code_input = ""  # Start empty by default

    if request.method == "POST":
        if 'apply_promo' in request.form:
            # User clicked Apply promo button
            promo_code_input = request.form.get("promo_code", "").strip()

            if promo_code_input.lower() == "enjoy":
                discount = int(amount * 0.10)
                session["promo"] = "enjoy"
                session["discount"] = discount
                session["amount"] = amount - discount
                amount = session["amount"]
            else:
                error = "❌ Invalid promo code"
                session.pop("promo", None)
                session.pop("discount", None)
        else:
            # Normal payment submission
            method = request.form.get("payment_method")
            session["payment_method"] = method

            if method in ["phonepe", "gpay", "other"]:
                return redirect("/pending")
            elif method == "card":
                return redirect("/card")

    return render_template("payment.html", amount=amount, error=error, promo_code=promo_code_input)

@app.route('/pending', methods=["GET", "POST"])
def pending():
    if request.method == "POST":
        file = request.files.get("payment_screenshot")
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # If on Windows, uncomment and update path:
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

            try:
                text = pytesseract.image_to_string(Image.open(filepath))
                if "shah priyal shripal bhai" in text.lower():
                    return redirect("/success")
                else:
                    return "❌ Payment not verified. Name not found in screenshot."
            except Exception as e:
                return f"Error reading image: {e}"

    return render_template("pending.html")

@app.route('/card', methods=["GET", "POST"])
def card():
    # Implement real card payment logic if needed
    return render_template("card_payment.html")

@app.route('/success')
def success():
    return render_template("success.html", name=session.get("name"),
                           category=session.get("category"),
                           tickets=session.get("tickets"),
                           amount=session.get("amount"))

if __name__ == "__main__":
    app.run(debug=True)
