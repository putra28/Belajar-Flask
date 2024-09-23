from flask import Blueprint, Response, current_app, request, jsonify
from collections import OrderedDict
from datetime import datetime
import json
import jwt
from functools import wraps
import hashlib

pengguna_blueprint = Blueprint('pengguna', __name__)

# Decorator untuk validasi token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            # Token tidak ditemukan di header
            error_response = OrderedDict([
                ('status', 500),
                ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                ('notification_response', 'Token Required'),
                ('data', [])
            ])
            error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
            return Response(error_json, content_type='application/json', status=500)

        try:
            # Menghapus prefix "Bearer " jika ada
            token = token.replace('Bearer ', '')
            # Decode token JWT
            jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            # Token sudah kadaluwarsa
            error_response = OrderedDict([
                ('status', 500),
                ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                ('notification_response', 'Token Expired'),
                ('data', [])
            ])
            error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
            return Response(error_json, content_type='application/json', status=500)
        except jwt.InvalidTokenError:
            # Token tidak valid (mungkin telah dimodifikasi)
            error_response = OrderedDict([
                ('status', 500),
                ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                ('notification_response', 'Token Invalid'),
                ('data', [])
            ])
            error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
            return Response(error_json, content_type='application/json', status=500)

        return f(*args, **kwargs)
    return decorated

# Route untuk mendapatkan data pengguna
@pengguna_blueprint.route('/getdatapengguna', methods=['GET'])
@token_required
def get_data_pengguna():
    try:
        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure
        cursor.callproc('sp_get_all_pengguna')

        # Mengambil hasil dari stored procedure
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()

        # Debug print hasil raw
        print("Raw Results: ", results)

        # Format hasil sebagai JSON dengan urutan kolom yang benar
        data_pengguna = []
        for row in results:
            created_at = row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else None
            updated_at = row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None
            pengguna = OrderedDict([
                ('v_id_pengguna', row[0]),                 # ID Pengguna
                ('v_nama_pengguna', row[1]),               # Nama Pengguna
                ('v_username_pengguna', row[2]),           # Username Pengguna
                ('v_password_pengguna', row[3]),           # Password Pengguna
                ('v_role_pengguna', row[4]),               # Role Pengguna
                ('v_created_at', created_at),              # Tanggal Dibuat
                ('v_updated_at', updated_at),              # Tanggal Diubah
            ])
            data_pengguna.append(pengguna)

        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, notification_response, dan data
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Get Data Pengguna'),
            ('data', data_pengguna)
        ])

        # Use json.dumps to preserve the order of keys
        response_json = json.dumps(response, ensure_ascii=False, indent=4)

        # Return response with proper content type and status code
        return Response(response_json, content_type='application/json')

    except Exception as e:
        # Handle error and return a failure response
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Get Data Pengguna'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)

# Route untuk menambahkan data pengguna
@pengguna_blueprint.route('/adddatapengguna', methods=['POST'])
@token_required
def add_data_pengguna():
    try:
        # Mengambil data dari request JSON
        data = request.get_json()
        nama_pengguna = data.get('p_nama_pengguna')
        username_pengguna = data.get('p_username_pengguna')
        password_pengguna = data.get('p_password_pengguna')
        role_pengguna = data.get('p_role_pengguna')

        # Validasi input
        if not all([nama_pengguna, username_pengguna, password_pengguna, role_pengguna]):
            return Response(
                json.dumps(OrderedDict([
                    ('status', 400),
                    ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    ('notification_response', 'Semua field harus diisi!'),
                    ('data', [])
                ]))
                , content_type='application/json',
                status=400
            )

        # Hashing password dengan SHA-256
        sha256password = hashlib.sha256(password_pengguna.encode()).hexdigest()
        # Kemudian hash SHA-256 dengan MD5
        md5password = hashlib.md5(sha256password.encode()).hexdigest()

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk menambahkan pengguna
        cursor.callproc('sp_pengguna_add', [nama_pengguna, username_pengguna, md5password, role_pengguna])
        conn.commit()  # Commit perubahan

        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, notification_response
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Menambahkan Data Pengguna'),
            ('data', [])
        ])

        response_json = json.dumps(response, ensure_ascii=False, indent=4)
        return Response(response_json, content_type='application/json')

    except Exception as e:
        # Handle error and return a failure response
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Menambahkan Data Pengguna'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
    
@pengguna_blueprint.route('/updatedatapengguna', methods=['POST'])
@token_required
def update_data_pengguna():
    try:
        # Ambil data dari body JSON
        data = request.json
        id_pengguna = data.get('p_id_pengguna')
        nama_pengguna = data.get('p_nama_pengguna')
        username_pengguna = data.get('p_username_pengguna')
        password_pengguna = data.get('p_password_pengguna')
        role_pengguna = data.get('p_role_pengguna')

        # Hash password menggunakan SHA256 dan MD5
        hashed_password = hashlib.md5(hashlib.sha256(password_pengguna.encode()).hexdigest().encode()).hexdigest()

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk update pengguna
        cursor.callproc('sp_pengguna_edit', (id_pengguna, nama_pengguna, username_pengguna, hashed_password, role_pengguna))
        
        # Commit perubahan
        conn.commit()
        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, dan notification_response
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Update Data Pengguna'),
            ('data', [])
        ])

        response_json = json.dumps(response, ensure_ascii=False, indent=4)

        return Response(response_json, content_type='application/json')

    except Exception as e:
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Update Data Pengguna'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)

@pengguna_blueprint.route('/deletedatapengguna', methods=['POST'])
@token_required
def delete_pengguna():
    try:
        # Mengambil data JSON dari request body
        data = request.get_json()
        p_id_pengguna = data.get('p_id_pengguna')

        if not p_id_pengguna:
            return Response(
                json.dumps({
                    'status': 400,
                    'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'notification_response': 'ID Pengguna Required',
                    'data': []
                }),
                content_type='application/json',
                status=400
            )

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk menghapus pengguna
        cursor.callproc('sp_pengguna_delete', (p_id_pengguna,))

        # Commit perubahan ke database
        conn.commit()

        cursor.close()

        # Format hasil akhir
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Hapus Pengguna'),
            ('data', [])
        ])

        return Response(json.dumps(response, ensure_ascii=False, indent=4), content_type='application/json')

    except Exception as e:
        # Handle error dan kembalikan response kegagalan
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Hapus Pengguna'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)