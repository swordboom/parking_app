from flask import Blueprint, render_template, request, redirect, url_for, session, make_response
from models.parking_model import get_user_by_email, add_user
from functools import wraps
from datetime import timedelta
import bcrypt

auth_bp = Blueprint('auth', __name__)

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "$2b$12$kqbu0btoXGkbuC8wdtZhIuzz8GuAiduYiSugTv17P8dhFqTuTQvWe"  # bcrypt hash for 'admin'

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return no_cache

@auth_bp.route('/')
@nocache
def index():
    return render_template('index.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
@nocache
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        address = request.form['address']
        pincode = request.form['pincode']
        add_user(name, email, hashed_password, address, pincode)
        return redirect(url_for('auth.login'))
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
@nocache
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == ADMIN_EMAIL and bcrypt.checkpw(password.encode(), ADMIN_PASSWORD.encode()):
            session['user_id'] = -1
            session['username'] = ADMIN_EMAIL
            session.permanent = True
            return redirect(url_for('admin.admin_dashboard'))

        user = get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = user['user_id']
            session['username'] = user['email']
            session.permanent = True
            return redirect(url_for('user.user_dashboard'))

        return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@auth_bp.route('/logout')
@nocache
def logout():
    session.clear()
    return redirect(url_for('auth.index'))