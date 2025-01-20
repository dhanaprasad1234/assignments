import hashlib
from flask import Flask, request, jsonify, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import validators
import socket

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/url_shortener'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class URL(db.Model):
    __tablename__ = 'url'
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expiration_time = db.Column(db.DateTime, nullable=False,default=24)
    password = db.Column(db.Text, nullable=True)

class AccessLog(db.Model):
    __tablename__ = 'access_log'
    id = db.Column(db.Integer, primary_key=True)
    short_url = db.Column(db.String(255), db.ForeignKey('url.short_url', ondelete="CASCADE"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(255), nullable=False)

def generate_hashed_short_url(original_url):
    return hashlib.sha256(original_url.encode()).hexdigest()[:6]

def validate_url(url):
    return validators.url(url)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    data = request.form
    original_url = data.get('url')
    expiration_hours = int(data.get('expiration_hours', 24))
    password = data.get('password')

    if not validate_url(original_url):
        return jsonify({'error': 'Invalid URL'}), 400

    short_url = generate_hashed_short_url(original_url)

    if password:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    else:
        hashed_password = None

    expiration_time = datetime.utcnow() + timedelta(hours=expiration_hours)

    existing_url = URL.query.filter_by(short_url=short_url).first()
    if existing_url:
        return jsonify({'short_url': f"https://127.0.0.1:5000/{short_url}"})

    new_url = URL(
        original_url=original_url,
        short_url=short_url,
        expiration_time=expiration_time,
        password=hashed_password
    )
    db.session.add(new_url)
    db.session.commit()

    return render_template('index.html', short_url=f"https://127.0.0.1:5000/{short_url}")

@app.route('/<short_url>', methods=['GET'])
def redirect_to_original(short_url):
    password = request.args.get('password')
    url_entry = URL.query.filter_by(short_url=short_url).first()

    if not url_entry:
        return jsonify({'error': 'URL not found'}), 404

    if datetime.utcnow() > url_entry.expiration_time:
        return jsonify({'error': 'URL has expired'}), 410


    if url_entry.password:
        if password:
            return jsonify({'error': 'Password is required to access this URL'}), 401
        if not bcrypt.check_password_hash(url_entry.password, password):
                return jsonify({'error': 'Incorrect password. Please try again.'}), 401

        else:
            pass

    ip_address = request.remote_addr or socket.gethostbyname(socket.gethostname())
    access_log = AccessLog(short_url=url_entry.short_url, ip_address=ip_address)
    db.session.add(access_log)
    db.session.commit()

    return redirect(url_entry.original_url)

@app.route('/analytics/<short_url>', methods=['GET'])
def get_analytics(short_url):
    url_entry = URL.query.filter_by(short_url=short_url).first()

    if not url_entry:
        return jsonify({'error': 'URL not found'}), 404

    access_logs = AccessLog.query.filter_by(short_url=url_entry.short_url).all()

    analytics = {
        'original_url': url_entry.original_url,
        'short_url': f"https://127.0.0.1:5000/{short_url} ",
        'visit_count': len(access_logs),
        'access_logs': [{'timestamp': log.timestamp, 'ip_address': log.ip_address} for log in access_logs]
    }

    return render_template('analytics.html', analytics=analytics)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

