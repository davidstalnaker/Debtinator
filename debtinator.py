from flask import Flask, render_template, request, session, escape, redirect, url_for, g
from database import db_session, init_db
from models import User, Bill, Debt, parseMoney, addDebt
app = Flask(__name__)
app.secret_key = "\xb2\xd8c\xaf+S4+\xec\x90\x1e\xd6g\xd1\xce)\x06\xf9\x7f'\xadi\x99n"

@app.route('/')
def index():
	return render_template('index.html', user = g.user)

@app.route('/createUserTable')
def createUserTable():
	init_db()
	return "Created user table"
	
@app.route('/register', methods=['GET', 'POST'])
def register():
	errors = []
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		
		newUser = User(username, password)
		isValid, errors = newUser.validate()
		
		if isValid:
			db_session.add(newUser)
			db_session.commit()
			session['username'] = newUser.name
			session.permanent = True
			return redirect(url_for('index'))
		else:
			return render_template('register.html', user = g.user, errors=errors)
	else:
		return render_template('register.html', user = g.user, errors=errors)
		
@app.route('/login', methods=['GET', 'POST'])
def login():
	errors = []
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		
		user = User.query.filter(User.name == username).first()
		if user:
			if user.testPassword(password):
				session['username'] = user.name
				session.permanent = True
				return redirect(url_for('index'))
			else:
				errors.append('Incorrect password')
				
		else:
			errors.append('User doesn\'t exist')
		
	return render_template('login.html', user = g.user, errors=errors)
	
@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))
	
@app.route('/createbill', methods=['GET', 'POST'])
def create_bill():
	if request.method == 'POST':
		amount = request.form['amount']
		participants = map(lambda username: User.query.filter(User.name == username).first(), request.form.getlist('participants'))
		payer = User.query.filter(User.name == request.form['payer']).first()
		
		bill = Bill(amount, participants, payer)
		amountPer = (float(bill.amount) / 100) / len(participants)
		for user in bill.participants:
			if user != payer:
				print(user)
				debt = addDebt(payer, user, amountPer, db_session)

		
		db_session.add(bill)
		db_session.commit()
		return redirect(url_for('index'))
	else:
		users = User.query.all()
		return render_template('createbill.html', user = g.user, users = users)



	
@app.before_request
def get_user():
	g.user = None;
	if 'username' in session:
		try:
			g.user = User.query.filter(User.name == session['username']).first()
		except:
			pass
	
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)