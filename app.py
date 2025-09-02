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


# ---------------- NO TIMEOUT BLOCK FOR RENDER ----------------
import threading
import time
import requests

@app.route("/ping")
def ping():
    return "pong"

def keep_alive():
    while True:
        try:
            url = os.environ.get("RENDER_EXTERNAL_URL")
            if url:
                requests.get(f"{url}/ping")
        except Exception:
            pass
        time.sleep(600)  # 10 minutes


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host="0.0.0.0", port=port, debug=False)
