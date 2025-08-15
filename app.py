from flask import Flask, render_template, request, redirect, session, url_for, g
import sqlite3
import os
import secrets
from datetime import timedelta

from controllers.admin_controller import admin_bp
from controllers.user_controller import user_bp
from controllers.auth_controller import auth_bp
from models.parking_model import init_db

#using flask 
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Initialize the database
with app.app_context():
    init_db()

# Register the blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
