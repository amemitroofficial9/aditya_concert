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

# 🎯 Landing page (home)
@app.route('/')
def home():
    return render_template('home.html')

# Booking form
@app.route('/book')
def index():
    return render_template('index.html')

# Handle booking submission
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

# Show payment method form
@app.route('/payment')
def payment():
    return render_template('payment.html', amount=session.get('amount', 0), error=None)

# Handle payment
@app.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    method = request.form.get("payment_method")
    original_amount = session.get("amount", 0)

    # 🎁 Promo Code Logic
    promo_code = request.form.get("promo_code", "").strip().lower()
    if promo_code == "enjoy":
        discount = int(original_amount * 0.10)
        amount = int(original_amount - discount)
        session['promo'] = promo_code
        session['discount'] = discount
    elif promo_code:
        return render_template("payment.html", amount=original_amount, error="❌ Invalid promo code")
    else:
        amount = original_amount
        session['discount'] = 0

    session['amount'] = amount

    # UPI Payment
    if method in ["phonepe", "gpay"]:
        user_upi_id = request.form.get("upi_id")
        if not user_upi_id:
            return render_template("payment.html", amount=amount, error="Please enter your UPI ID.")
        session['payer_upi'] = user_upi_id

        upi_url = f"upi://pay?pa={YOUR_UPI_ID}&pn={RECEIVER_NAME}&am={amount}&cu=INR"
        return redirect(upi_url)

    # Card Payment
    elif method == "card":
        if not request.form.get("card_number") or not request.form.get("expiry") or not request.form.get("cvv"):
            return render_template("payment.html", amount=amount, error="Please fill in all card details.")
        return redirect("/success")

    # Other Payment Method
    elif method == "other":
        if not request.form.get("other_option"):
            return render_template("payment.html", amount=amount, error="Please select a valid payment option.")
        return f"<h2>🔧 '{request.form.get('other_option')}' payment method coming soon. Please use UPI for now.</h2>"

    else:
        return render_template("payment.html", amount=amount, error="Please select a payment method.")

# Success page with QR code
@app.route('/success')
def success():
    name = session.get('name')
    tickets = session.get('tickets')
    category = session.get('category')
    amount = session.get('amount')
    discount = session.get('discount', 0)

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
        discount=discount,
        qr_code=qr_base64
    )

# Render-compatible run
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
