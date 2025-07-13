from flask import Flask, render_template, request, session, redirect
import os
import qrcode
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'concert_secret_key'

# Organizer UPI details
YOUR_UPI_ID = "9998143506@ybl"
RECEIVER_NAME = "Ame Mitro Concert"

# Ticket categories with prices
CATEGORY_PRICES = {
    "fan": 2999,
    "general": 1499,
    "gold": 799
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/book')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    session['name'] = request.form.get('name')
    session['phone'] = request.form.get('phone')
    session['email'] = request.form.get('email')
    category = request.form.get('category')
    session['tickets'] = int(request.form.get('tickets', 0))

    if session['tickets'] > 10:
        return "You can only book up to 10 tickets."

    if not category or category not in CATEGORY_PRICES:
        return "Invalid or missing ticket category."

    session['category'] = category
    session['amount'] = session['tickets'] * CATEGORY_PRICES[category]
    return redirect('/payment')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        method = request.form.get("payment_method")
        promo_code = request.form.get("promo_code", "").strip().lower()
        user_upi_id = request.form.get("upi_id")

        # Base amount
        tickets = session.get("tickets", 1)
        category = session.get("category")
        base_amount = CATEGORY_PRICES.get(category, 0) * tickets

        # Apply promo code
        if promo_code == "enjoy":
            amount = int(base_amount * 0.9)
            session['promo'] = 'enjoy'
            session['discount'] = base_amount - amount
        else:
            amount = base_amount
            session['promo'] = ''
            session['discount'] = 0
            if promo_code != "":
                return render_template("payment.html", amount=amount, error="❌ Invalid promo code")

        session['amount'] = amount

        if method in ["phonepe", "gpay"]:
            if not user_upi_id:
                return render_template("payment.html", amount=amount, error="Please enter your UPI ID.")

            upi_url = f"upi://pay?pa={YOUR_UPI_ID}&pn={RECEIVER_NAME}&am={amount}&cu=INR"
            session['upi_url'] = upi_url
            return redirect('/pending')

        elif method == "card":
            if not request.form.get("card_number") or not request.form.get("expiry") or not request.form.get("cvv"):
                return render_template("payment.html", amount=amount, error="Please fill in all card details.")
            return redirect("/success")

        elif method == "other":
            if not request.form.get("other_option"):
                return render_template("payment.html", amount=amount, error="Please select a valid payment option.")
            return f"<h2>🔧 '{request.form.get('other_option')}' payment method coming soon. Please use UPI for now.</h2>"

        else:
            return render_template("payment.html", amount=amount, error="Please select a payment method.")
    else:
        return render_template("payment.html", amount=session.get('amount', 0))

@app.route('/pending')
def pending():
    upi_url = session.get('upi_url')
    return render_template("pending.html", upi_url=upi_url)

@app.route('/success')
def success():
    name = session.get('name')
    tickets = session.get('tickets')
    category = session.get('category')
    amount = session.get('amount')

    qr_data = f"Name: {name}\nCategory: {category}\nTickets: {tickets}\nAmount: ₹{amount}"
    qr_img = qrcode.make(qr_data)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render_template(
        'success.html',
        name=name,
        tickets=tickets,
        category=category,
        amount=amount,
        qr_code=qr_base64
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
