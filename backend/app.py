# ===== MEDICARE CLOUD - PYTHON FLASK BACKEND =====
# Azure App Service deployment
# Install requirements: pip install flask flask-cors bcrypt pyodbc

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import bcrypt
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'medicare-cloud-secret-2026')
CORS(app, supports_credentials=True)

# ── In-memory store (replace with Azure SQL in production) ─────
# In Azure production, connect using pyodbc + Azure SQL connection string:
# conn_str = os.environ.get('AZURE_SQL_CONNECTION_STRING')

users_db     = {}   # { email: { name, email, password_hash } }
medicines_db = {}   # { email: [ {name, dosage, frequency, time, instructions} ] }
records_db   = {}   # { email: [ {name, type, notes, size, date, blob_url} ] }


# ── Helper ─────────────────────────────────────────────────────
def get_user():
    return session.get('user_email')

def require_auth(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not get_user():
            return jsonify({'error': 'Unauthorized'}), 401
        return fn(*args, **kwargs)
    return wrapper


# ── AUTH ROUTES ────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data     = request.get_json()
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if email in users_db:
        return jsonify({'error': 'Email already registered'}), 409

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users_db[email] = { 'name': name, 'email': email, 'password_hash': password_hash }
    medicines_db[email] = []
    records_db[email]   = []

    session['user_email'] = email
    return jsonify({'message': 'Registered successfully', 'name': name, 'email': email}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data     = request.get_json()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    user = users_db.get(email)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    if not bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return jsonify({'error': 'Invalid email or password'}), 401

    session['user_email'] = email
    return jsonify({'message': 'Login successful', 'name': user['name'], 'email': email}), 200


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_email', None)
    return jsonify({'message': 'Logged out'}), 200


# ── MEDICINES ROUTES ────────────────────────────────────────────

@app.route('/api/medicines', methods=['GET'])
@require_auth
def get_medicines():
    email = get_user()
    return jsonify(medicines_db.get(email, [])), 200


@app.route('/api/medicines', methods=['POST'])
@require_auth
def add_medicine():
    email = get_user()
    data  = request.get_json()
    name         = data.get('name', '').strip()
    dosage       = data.get('dosage', '').strip()
    frequency    = data.get('frequency', '').strip()
    time         = data.get('time', '').strip()
    instructions = data.get('instructions', '').strip()

    if not name or not dosage or not frequency or not time:
        return jsonify({'error': 'Name, dosage, frequency, and time are required'}), 400

    medicine = {
        'id':           len(medicines_db.get(email, [])),
        'name':         name,
        'dosage':       dosage,
        'frequency':    frequency,
        'time':         time,
        'instructions': instructions,
        'created_at':   datetime.now().isoformat()
    }
    medicines_db.setdefault(email, []).append(medicine)
    return jsonify({'message': 'Medicine added', 'medicine': medicine}), 201


@app.route('/api/medicines/<int:med_id>', methods=['PUT'])
@require_auth
def update_medicine(med_id):
    email = get_user()
    meds  = medicines_db.get(email, [])
    if med_id >= len(meds):
        return jsonify({'error': 'Medicine not found'}), 404

    data = request.get_json()
    meds[med_id].update({
        'name':         data.get('name', meds[med_id]['name']),
        'dosage':       data.get('dosage', meds[med_id]['dosage']),
        'frequency':    data.get('frequency', meds[med_id]['frequency']),
        'time':         data.get('time', meds[med_id]['time']),
        'instructions': data.get('instructions', meds[med_id].get('instructions', '')),
    })
    return jsonify({'message': 'Medicine updated', 'medicine': meds[med_id]}), 200


@app.route('/api/medicines/<int:med_id>', methods=['DELETE'])
@require_auth
def delete_medicine(med_id):
    email = get_user()
    meds  = medicines_db.get(email, [])
    if med_id >= len(meds):
        return jsonify({'error': 'Medicine not found'}), 404
    deleted = meds.pop(med_id)
    return jsonify({'message': 'Medicine deleted', 'medicine': deleted}), 200


# ── HEALTH RECORDS ROUTES ───────────────────────────────────────

@app.route('/api/records', methods=['GET'])
@require_auth
def get_records():
    email = get_user()
    return jsonify(records_db.get(email, [])), 200


@app.route('/api/records', methods=['POST'])
@require_auth
def add_record():
    """
    In Azure deployment:
    1. Receive file via multipart form
    2. Upload to Azure Blob Storage using azure-storage-blob SDK
    3. Get blob URL and save metadata to Azure SQL Database
    """
    email     = get_user()
    file_name = request.form.get('file_name', '')
    file_type = request.form.get('type', '')
    notes     = request.form.get('notes', '')
    file_size = request.form.get('size', '')

    # Simulate Azure Blob Storage URL
    blob_url  = f"https://medicarecloud.blob.core.windows.net/records/{email}/{file_name}"

    record = {
        'id':       len(records_db.get(email, [])),
        'name':     file_name,
        'type':     file_type,
        'notes':    notes,
        'size':     file_size,
        'blob_url': blob_url,
        'date':     datetime.now().strftime('%d %b %Y'),
        'uploaded_at': datetime.now().isoformat()
    }
    records_db.setdefault(email, []).append(record)
    return jsonify({'message': 'Record uploaded to Azure Blob Storage', 'record': record}), 201


@app.route('/api/records/<int:rec_id>', methods=['DELETE'])
@require_auth
def delete_record(rec_id):
    """
    In Azure deployment: also delete the blob from Azure Blob Storage
    """
    email   = get_user()
    records = records_db.get(email, [])
    if rec_id >= len(records):
        return jsonify({'error': 'Record not found'}), 404
    deleted = records.pop(rec_id)
    return jsonify({'message': 'Record deleted', 'record': deleted}), 200


# ── CONTACT ROUTE ───────────────────────────────────────────────

@app.route('/api/contact', methods=['POST'])
def contact():
    """
    In Azure deployment:
    Send email via Azure Communication Services SDK:
    from azure.communication.email import EmailClient
    client = EmailClient.from_connection_string(os.environ['AZURE_COMM_CONNECTION_STRING'])
    """
    data    = request.get_json()
    name    = data.get('name', '').strip()
    email   = data.get('email', '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    if not name or not email or not subject or not message:
        return jsonify({'error': 'All fields are required'}), 400

    # Log message (in production: send via Azure Communication Services)
    print(f"[CONTACT] From: {name} <{email}> | Subject: {subject} | Message: {message}")
    return jsonify({'message': 'Message received. We will get back to you soon.'}), 200


# ── DASHBOARD STATS ─────────────────────────────────────────────

@app.route('/api/dashboard', methods=['GET'])
@require_auth
def dashboard():
    email = get_user()
    meds    = medicines_db.get(email, [])
    records = records_db.get(email, [])
    return jsonify({
        'total_medicines': len(meds),
        'total_records':   len(records),
        'today_medicines': meds,
        'recent_records':  records[-5:][::-1]
    }), 200


# ── HEALTH CHECK ────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status':   'running',
        'service':  'MediCare Cloud API',
        'platform': 'Microsoft Azure App Service',
        'version':  '1.0.0'
    }), 200


# ── RUN ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    # Azure App Service uses PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
