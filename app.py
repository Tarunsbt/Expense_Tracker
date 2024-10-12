from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# User model for login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    expenses = db.relationship('Expense', backref='owner', lazy=True)


# Expense model for storing expenses
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Route: Home/Dashboard
@app.route('/')
@login_required
def dashboard():
    expenses = Expense.query.filter_by(owner=current_user).all()
    categories = [exp.category for exp in expenses]
    amounts = [exp.amount for exp in expenses]

    # Create bar chart for expense analytics
    plt.bar(categories, amounts)
    plt.savefig('static/expense_chart.png')
    plt.close()

    return render_template('dashboard.html', expenses=expenses)


# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and password.')

    return render_template('login.html')


# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


# Route: Add Expense
@app.route('/add-expense', methods=['POST'])
@login_required
def add_expense():
    title = request.form['title']
    amount = request.form['amount']
    category = request.form['category']

    expense = Expense(title=title, amount=amount, category=category, owner=current_user)
    db.session.add(expense)
    db.session.commit()

    return redirect(url_for('dashboard'))


# Route: Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    print("Starting application...")
    with app.app_context():
        print("Creating database if it doesn't exist...")
        if not os.path.exists('expenses.db'):
            db.create_all()
            print("Database created.")
        else:
            print("Database already exists.")
    app.run(debug=True)

