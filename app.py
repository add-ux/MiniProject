# app.py - Main Flask Server
import os
import re
import sqlite3
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
import bcrypt

# Import your analyzer
from multi_lang_analyzer import MultiLanguageAnalyzer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")

# Supported file types
SUPPORTED_EXTENSIONS = {
    '.py': 'Python',
    '.c': 'C',
    '.cpp': 'C++',
    '.cc': 'C++',
    '.cxx': 'C++',
    '.h': 'C/C++ Header',
    '.hpp': 'C++ Header'
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              email TEXT NOT NULL UNIQUE,
              password_hash BLOB NOT NULL,
              created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
)

@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Please enter a valid email address."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username or email already exists."}), 409
    finally:
        conn.close()

    return jsonify({"message": "Signup successful"}), 201

@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    login_id = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not login_id or not password:
        return jsonify({"error": "Username/email and password are required."}), 400

    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, username, email, password_hash FROM users WHERE username = ? OR email = ?",
            (login_id, login_id.lower()),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        return jsonify({"error": "Invalid credentials."}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), row["password_hash"]):
        return jsonify({"error": "Invalid credentials."}), 401

    return (
        jsonify(
            {
                "message": "Login successful",
                "user": {"id": row["id"], "username": row["username"], "email": row["email"]},
            }
        ),
        200,
    )

@app.post("/api/analyze")
def analyze_code():
    """Analyze uploaded code file with ML enhancement"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in SUPPORTED_EXTENSIONS:
            return jsonify({
                'error': f'Unsupported file type. Supported: {", ".join(SUPPORTED_EXTENSIONS.keys())}'
            }), 400
        
        # Save file temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(temp_path)
        
        try:
            # Run analyzer with ML enhancement
            analyzer = MultiLanguageAnalyzer(temp_path, use_ml=True)
            results = analyzer.analyze_with_ml()
            
            # Add metadata
            results['filename'] = file.filename
            results['filesize'] = os.path.getsize(temp_path)
            results['ml_enabled'] = True
            
            # Generate unique ID for this analysis
            analysis_id = hashlib.md5(f"{file.filename}{datetime.now()}".encode()).hexdigest()[:8]
            results['analysis_id'] = analysis_id
            
            return jsonify({
                'success': True,
                'results': results,
                'message': 'ML-enhanced analysis completed successfully'
            })
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.post("/api/analyze-text")
def analyze_text():
    """Analyze code pasted as text with ML enhancement"""
    try:
        data = request.get_json()
        
        if not data or 'code' not in data or 'language' not in data:
            return jsonify({'error': 'Missing code or language'}), 400
        
        code = data['code']
        language = data['language']
        
        # Map language to file extension
        ext_map = {
            'python': '.py',
            'c': '.c',
            'cpp': '.cpp'
        }
        
        if language not in ext_map:
            return jsonify({'error': f'Unsupported language: {language}'}), 400
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix=ext_map[language], delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_path = f.name
        
        try:
            # Run analyzer with ML enhancement
            analyzer = MultiLanguageAnalyzer(temp_path, use_ml=True)
            results = analyzer.analyze_with_ml()
            
            results['language'] = language
            results['ml_enabled'] = True
            results['analysis_id'] = hashlib.md5(f"{code[:100]}{datetime.now()}".encode()).hexdigest()[:8]
            
            return jsonify({
                'success': True,
                'results': results,
                'message': 'ML-enhanced analysis completed successfully'
            })
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.get("/api/languages")
def get_supported_languages():
    """Return list of supported languages"""
    return jsonify({
        'languages': [
            {'name': 'Python', 'extension': '.py', 'icon': '🐍'},
            {'name': 'C', 'extension': '.c', 'icon': '⚙️'},
            {'name': 'C++', 'extension': '.cpp', 'icon': '⚡'}
        ]
    })

@app.get("/api/ml/status")
def ml_status():
    """Get ML model status"""
    try:
        from ml_models import CodeMLAnalyzer
        ml_analyzer = CodeMLAnalyzer()
        
        # Check if real models exist
        real_model_path = Path("models/quality_model_real.pkl")
        
        return jsonify({
            'ml_enabled': True,
            'using_real_data': real_model_path.exists(),
            'quality_model_loaded': ml_analyzer.quality_predictor is not None,
            'bug_model_loaded': ml_analyzer.bug_predictor is not None,
            'security_model_loaded': ml_analyzer.security_predictor is not None,
            'message': 'Using real dataset models' if real_model_path.exists() else 'Using synthetic models (run trainer for better accuracy)'
        })
    except Exception as e:
        return jsonify({'ml_enabled': False, 'error': str(e)}), 200

if __name__ == "__main__":
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    init_db()
    print("\n" + "="*60)
    print("🚀 Code Analyzer Server Starting...")
    print("="*60)
    print("📍 Server URL: http://127.0.0.1:5000")
    print("📊 ML Status: http://127.0.0.1:5000/api/ml/status")
    print("\n⚠️  First time setup: Run 'python train_real_models.py' to train ML models")
    print("="*60 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=True)