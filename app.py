from flask import Flask, render_template, request, redirect, session, url_for
import os
import pytesseract
from PIL import Image

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

        return redirect("/payment")

    return render_template("index.html")

@app.route('/payment', methods=["GET", "POST"])
def payment():
    error = None
    amount = session.get("amount", 0)

    if request.method == "POST":
        promo_code = request.form.get("promo_code", "").strip().lower()
        method = request.form.get("payment_method")

        # Apply promo logic
        if promo_code:
            if promo_code == "enjoy":
                discount = int(amount * 0.10)
                session["promo"] = "enjoy"
                session["discount"] = discount
                session["amount"] = amount - discount
                amount = amount - discount
            else:
                error = "❌ Invalid promo code"
                session.pop("promo", None)
                session.pop("discount", None)

        if method:
            session["payment_method"] = method
            if method in ["phonepe", "gpay", "other"]:
                return redirect("/pending")
            elif method == "card":
                return redirect("/card")

    return render_template("payment.html", amount=session.get("amount", 0), error=error)

@app.route('/pending', methods=["GET", "POST"])
def pending():
    if request.method == "POST":
        file = request.files.get("payment_screenshot")
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Use pytesseract to extract text from the image
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
    return render_template("card_payment.html")

@app.route('/success')
def success():
    return render_template("success.html", name=session.get("name"),
                           category=session.get("category"),
                           tickets=session.get("tickets"),
                           amount=session.get("amount"))

if __name__ == "__main__":
    app.run(debug=True)
