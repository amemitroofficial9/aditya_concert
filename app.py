from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)
app.secret_key = 'concert_secret_key'

TICKET_PRICE = 500
YOUR_UPI_ID = "9998143506@ybl"
RECEIVER_NAME = "Ame Mitro Concert"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    session['name'] = request.form['name']
    session['phone'] = request.form['phone']
    session['email'] = request.form['email']
    session['tickets'] = int(request.form['tickets'])

    if session['tickets'] > 10:
        return "You can only book up to 10 tickets."

    session['amount'] = session['tickets'] * TICKET_PRICE
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
    return render_template('success.html', name=name, tickets=tickets)

if __name__ == '__main__':
    app.run(debug=True)
