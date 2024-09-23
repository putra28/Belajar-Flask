import jwt
from datetime import datetime, timedelta
from flask import current_app

def create_token(username):
    # Waktu sekarang
    now = datetime.utcnow()

    # Hitung waktu sampai jam 12 malam (UTC)
    midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
    expiration_time = midnight - now  # Selisih waktu dari sekarang hingga 12 malam

    # Buat token JWT dengan waktu kedaluwarsa di jam 12 malam
    token = jwt.encode({
        'username': username,
        'exp': now + expiration_time  # Set waktu expired sesuai jam 12 malam
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return token

def verify_token(token):
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        return data
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
