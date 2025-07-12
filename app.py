from flask import Flask, render_template, request, session, redirect
import os

app = Flask(__name__)
app.secret_key = 'concert_secret_key'

YOUR_UPI_ID = "9998143506@ybl"
RECEIVER_NAME = "Ame Mitro Concert"

# Ticket price mapping
CATEGORY_PRICES = {
    "fan": 1500,
    "general": 1000,
    "gold": 599
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    session['name'] = request.form['name']
    session['phone'] = request.form['phone']
    session['email'] = request.form['email']
    session['category'] = request.form['category']
    session['tickets'] = int(request.form['tickets'])

    if session['tickets'] > 10:
        return "You can only book up to 10 tickets."

    category = session['category']
    if category not in CATEGORY_PRICES:
        return "Invalid ticket category selected."

    price = CATEGORY_PRICES[category]
    session['amount'] = session['tickets'] * price
    return redirect('/payment')

@app.route('/payment')
def payment():
    return render_template('payment.html', amount=session.get('amount', 0))

@app.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    upi_id = request.form.get('upi_id')
    if not upi_id:
        return render_template('payment.html', amount=session.get('amount', 0), error="❌ Please enter your UPI ID.")

    # Redirect to UPI payment request
    amount = session.get('amount', 0)
    upi_url = f"upi://pay?pa={YOUR_UPI_ID}&pn={RECEIVER_NAME}&am={amount}&cu=INR"
    return redirect(upi_url)

@app.route('/success')
def success():
    name = session.get('name')
    tickets = session.get('tickets')
    category = session.get('category')
    return render_template('success.html', name=name, tickets=tickets, category=category)

# ✅ Required for Render deployment
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
