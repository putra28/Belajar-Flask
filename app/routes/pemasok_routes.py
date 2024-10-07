from flask import Blueprint, Response, current_app, request
from collections import OrderedDict
from datetime import datetime
import json
import jwt
from functools import wraps

pemasok_blueprint = Blueprint('pemasok', __name__)

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

@pemasok_blueprint.route('/getdatapemasok', methods=['GET'])
@token_required
def get_data_pemasok():
    try:
        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure
        cursor.callproc('sp_get_all_pemasok')

        # Mengambil hasil dari stored procedure
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()

        # Format hasil sebagai JSON dengan urutan kolom yang benar
        data_pemasok = []
        for row in results:
            created_at = row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else None
            updated_at = row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else None
            pemasok = OrderedDict([
                ('v_id_pemasok', row[0]),                   # ID pemasok
                ('v_nama_pemasok', row[1]),                 # Nama pemasok
                ('v_kontak_pemasok', row[2]),               # Kontak pemasok
                ('v_alamat_pemasok', row[3]),               # Alamat pemasok
                ('v_created_at', created_at),               # Tanggal Dibuat
                ('v_updated_at', updated_at),               # Tanggal Diubah
            ])
            data_pemasok.append(pemasok)

        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, notification_response, dan data
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Get Data Pemasok'),
            ('data', data_pemasok)
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
            ('notification_response', 'Gagal Get Data Pemasok'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)

# Route untuk menambahkan data
@pemasok_blueprint.route('/adddatapemasok', methods=['POST'])
@token_required
def add_data_pemasok():
    try:
        # Mengambil data dari request JSON
        data = request.get_json()
        nama_pemasok = data.get('p_nama_pemasok')
        kontak_pemasok = data.get('p_kontak_pemasok')
        alamat_pemasok = data.get('p_alamat_pemasok')

        # Validasi input
        if not all([nama_pemasok, kontak_pemasok, alamat_pemasok]):
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

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk menambahkan data
        cursor.callproc('sp_pemasok_add', [nama_pemasok, kontak_pemasok, alamat_pemasok])
        conn.commit()  # Commit perubahan

        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, notification_response
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Menambahkan Data Pemasok'),
            ('data', [])
        ])

        response_json = json.dumps(response, ensure_ascii=False, indent=4)
        return Response(response_json, content_type='application/json')

    except Exception as e:
        # Handle error and return a failure response
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Menambahkan Data Pemasok'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
    
@pemasok_blueprint.route('/updatedatapemasok', methods=['POST'])
@token_required
def update_data_pemasok():
    try:
        # Ambil data dari body JSON
        data = request.json
        id_pemasok = data.get('p_id_pemasok')
        nama_pemasok = data.get('p_nama_pemasok')
        kontak_pemasok = data.get('p_kontak_pemasok')
        alamat_pemasok = data.get('p_alamat_pemasok')

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk update data
        cursor.callproc('sp_pemasok_edit', (id_pemasok, nama_pemasok, kontak_pemasok, alamat_pemasok))
        
        # Commit perubahan
        conn.commit()
        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, dan notification_response
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Update Data Pemasok'),
            ('data', [])
        ])

        response_json = json.dumps(response, ensure_ascii=False, indent=4)

        return Response(response_json, content_type='application/json')

    except Exception as e:
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Update Data Pemasok'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)

@pemasok_blueprint.route('/deletedatapemasok', methods=['POST'])
@token_required
def delete_pemasok():
    try:
        # Mengambil data JSON dari request body
        data = request.get_json()
        id_pemasok = data.get('p_id_pemasok')

        if not id_pemasok:
            return Response(
                json.dumps({
                    'status': 400,
                    'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'notification_response': 'ID Pemasok Required',
                    'data': []
                }),
                content_type='application/json',
                status=400
            )

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk menghapus pengguna
        cursor.callproc('sp_pemasok_delete', (id_pemasok))

        # Commit perubahan ke database
        conn.commit()

        cursor.close()

        # Format hasil akhir
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Hapus Data Pemasok'),
            ('data', [])
        ])

        return Response(json.dumps(response, ensure_ascii=False, indent=4), content_type='application/json')

    except Exception as e:
        # Handle error dan kembalikan response kegagalan
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Hapus Data Pemasok'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
