from flask import Blueprint, Response, current_app, request
from collections import OrderedDict
from datetime import datetime
import json
import jwt
from functools import wraps
kategori_blueprint = Blueprint('kategori', __name__)

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

@kategori_blueprint.route('/getdatakategori', methods=['GET'])
@token_required
def get_data_kategori():
    try:
        # Mengamsbil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure
        cursor.callproc('sp_get_all_kategori')

        # Mengambil hasil dari stored procedure
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()

        # Debug print hasil raw
        print("Raw Results: ", results)

        # Format hasil sebagai JSON dengan urutan kolom yang benar
        data_kategori = []
        for row in results:
            created_at = row[3].strftime('%Y-%m-%d %H:%M:%S') if row[3] else None
            updated_at = row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else None
            kategori = OrderedDict([
                ('id_kategori', row[0]),                    # ID Kategori
                ('name_kategori', row[1]),                  # Nama Kategori 
                ('name_subkategori', row[2]),               # Nama Subkategori
                ('v_created_at', created_at),               # Tanggal Dibuat
                ('v_updated_at', updated_at),               # Tanggal Diubah
            ])
            data_kategori.append(kategori)

        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, notification_response, dan data
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Get Data Kategori'),
            ('data', data_kategori)
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
            ('notification_response', 'Gagal Get Data Kategori'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)

# Route untuk menambahkan data
@kategori_blueprint.route('/adddatakategori', methods=['POST'])
@token_required
def add_data_kategori():
    try:
        # Mengambil data dari request JSON
        data = request.get_json()
        nama_kategori = data.get('p_nama_kategori')

        # Validasi input
        if not all([nama_kategori]):
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
        cursor.callproc('sp_kategori_add', [nama_kategori])
        conn.commit()  # Commit perubahan

        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, notification_response
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Menambahkan Data Kategori'),
            ('data', [])
        ])

        response_json = json.dumps(response, ensure_ascii=False, indent=4)
        return Response(response_json, content_type='application/json')

    except Exception as e:
        # Handle error and return a failure response
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Menambahkan Data Kategori'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
    
@kategori_blueprint.route('/updatedatakategori', methods=['POST'])
@token_required
def update_data_kategori():
    try:
        # Ambil data dari body JSON
        data = request.json
        id_kategori = data.get('p_id_kategori')
        nama_kategori = data.get('p_nama_kategori')

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk update data
        cursor.callproc('sp_kategori_edit', (id_kategori, nama_kategori))
        
        # Commit perubahan
        conn.commit()
        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, dan notification_response
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Update Data Kategori'),
            ('data', [])
        ])

        response_json = json.dumps(response, ensure_ascii=False, indent=4)

        return Response(response_json, content_type='application/json')

    except Exception as e:
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Update Data Kategori'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)

@kategori_blueprint.route('/deletedatakategori', methods=['POST'])
@token_required
def delete_kategori():
    try:
        # Mengambil data JSON dari request body
        data = request.get_json()
        id_kategori = data.get('p_id_kategori')

        if not id_kategori:
            return Response(
                json.dumps({
                    'status': 400,
                    'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'notification_response': 'ID Kategori Required',
                    'data': []
                }),
                content_type='application/json',
                status=400
            )

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk menghapus pengguna
        cursor.callproc('sp_kategori_delete', (id_kategori))

        # Commit perubahan ke database
        conn.commit()

        cursor.close()

        # Format hasil akhir
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Hapus Data Kategori'),
            ('data', [])
        ])

        return Response(json.dumps(response, ensure_ascii=False, indent=4), content_type='application/json')

    except Exception as e:
        # Handle error dan kembalikan response kegagalan
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Hapus Data Kategori'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)

# Route untuk menambahkan data
@kategori_blueprint.route('/adddatasubkategori', methods=['POST'])
@token_required
def add_data_subkategori():
    try:
        # Mengambil data dari request JSON
        data = request.get_json()
        id_kategori = data.get('p_id_kategori')
        nama_subkategori = data.get('p_nama_subkategori')

        # Validasi input
        if not all([id_kategori, nama_subkategori]):
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
        cursor.callproc('sp_subkategori_add', [id_kategori, nama_subkategori])
        conn.commit()  # Commit perubahan

        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, notification_response
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Menambahkan Data Sub-Kategori'),
            ('data', [])
        ])

        response_json = json.dumps(response, ensure_ascii=False, indent=4)
        return Response(response_json, content_type='application/json')

    except Exception as e:
        # Handle error and return a failure response
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Menambahkan Data Sub-Kategori'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
    
@kategori_blueprint.route('/updatedatasubkategori', methods=['POST'])
@token_required
def update_data_subkategori():
    try:
        # Ambil data dari body JSON
        data = request.json
        id_subkategori = data.get('p_id_subkategori')
        nama_subkategori = data.get('p_nama_subkategori')

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk update data
        cursor.callproc('sp_subkategori_edit', (id_subkategori, nama_subkategori))
        
        # Commit perubahan
        conn.commit()
        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, dan notification_response
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Update Data Sub-Kategori'),
            ('data', [])
        ])

        response_json = json.dumps(response, ensure_ascii=False, indent=4)

        return Response(response_json, content_type='application/json')

    except Exception as e:
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Update Data Sub-Kategori'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)

@kategori_blueprint.route('/deletedatasubkategori', methods=['POST'])
@token_required
def delete_subkategori():
    try:
        # Mengambil data JSON dari request body
        data = request.get_json()
        id_subkategori = data.get('p_id_subkategori')

        if not id_subkategori:
            return Response(
                json.dumps({
                    'status': 400,
                    'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'notification_response': 'ID Sub-Kategori Required',
                    'data': []
                }),
                content_type='application/json',
                status=400
            )

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk menghapus pengguna
        cursor.callproc('sp_subkategori_delete', (id_subkategori))

        # Commit perubahan ke database
        conn.commit()

        cursor.close()

        # Format hasil akhir
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Hapus Data Sub-Kategori'),
            ('data', [])
        ])

        return Response(json.dumps(response, ensure_ascii=False, indent=4), content_type='application/json')

    except Exception as e:
        # Handle error dan kembalikan response kegagalan
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Hapus Data Sub-Kategori'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
