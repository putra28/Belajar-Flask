from flask import Blueprint, Response, current_app, request
from collections import OrderedDict
from datetime import datetime
import json
import jwt
from functools import wraps

produk_blueprint = Blueprint('produk', __name__)

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

@produk_blueprint.route('/getdataproduk', methods=['GET'])
@token_required
def get_data_produk():
    try:
        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure
        cursor.callproc('sp_get_all_product')

        # Mengambil hasil dari stored procedure
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()

        # Debug print hasil raw
        print("Raw Results: ", results)

        # Format hasil sebagai JSON dengan urutan kolom yang benar
        data_produk = []
        for row in results:
            created_at = row[8].strftime('%Y-%m-%d %H:%M:%S') if row[8] else None
            updated_at = row[9].strftime('%Y-%m-%d %H:%M:%S') if row[9] else None
            produk = OrderedDict([
                ('v_id_produk', row[0]),                     # ID Produk
                ('v_id_kategori', row[1]),                   # ID Kategori Produk
                ('v_id_subkategori', row[2]),                # ID Subkategori Produk
                ('v_kategori_produk', row[3]),               # Kategori Produk
                ('v_subkategori_produk', row[4]),            # Subkategori Produk
                ('v_nama_produk', row[5]),                   # Nama Produk
                ('v_harga_produk', int(row[6])),             # Harga Produk
                ('v_stok_produk', row[7]),                   # Stok Produk
                ('v_created_at', created_at),                # Tanggal Dibuat
                ('v_updated_at', updated_at),                # Tanggal Diubah
            ])
            data_produk.append(produk)

        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, notification_response, dan data
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Get Data Produk'),
            ('data', data_produk)
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
            ('notification_response', 'Gagal Get Data Produk'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)

# Route untuk menambahkan data
@produk_blueprint.route('/adddataproduk', methods=['POST'])
@token_required
def add_data_produk():
    try:
        # Mengambil data dari request JSON
        data = request.get_json()
        id_kategori = data.get('p_id_kategori')
        id_subkategori = data.get('p_id_subkategori')
        nama_produk = data.get('p_nama_produk')
        harga_produk = data.get('p_harga_produk')

        # Validasi input
        if not all([id_kategori, id_subkategori, nama_produk, harga_produk]):
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
        cursor.callproc('sp_produk_add', [id_kategori, id_subkategori, nama_produk, harga_produk])
        conn.commit()  # Commit perubahan

        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, notification_response
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Menambahkan Data Produk'),
            ('data', [])
        ])

        response_json = json.dumps(response, ensure_ascii=False, indent=4)
        return Response(response_json, content_type='application/json')

    except Exception as e:
        # Handle error and return a failure response
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Menambahkan Data Produk'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
    
@produk_blueprint.route('/updatedataproduk', methods=['POST'])
@token_required
def update_data_produk():
    try:
        # Ambil data dari body JSON
        data = request.json
        id_produk = data.get('p_id_produk')
        id_subkategori = data.get('p_id_subkategori')
        nama_produk = data.get('p_nama_produk')
        harga_produk = data.get('p_harga_produk')
        stok_produk = data.get('p_stok_produk')

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk update data
        cursor.callproc('sp_produk_edit', (id_produk, id_subkategori, nama_produk, harga_produk, stok_produk))
        
        # Commit perubahan
        conn.commit()
        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, dan notification_response
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Update Data Produk'),
            ('data', [])
        ])

        response_json = json.dumps(response, ensure_ascii=False, indent=4)

        return Response(response_json, content_type='application/json')

    except Exception as e:
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Update Data Produk'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)

@produk_blueprint.route('/deletedataproduk', methods=['POST'])
@token_required
def delete_produk():
    try:
        # Mengambil data JSON dari request body
        data = request.get_json()
        id_produk = data.get('p_id_produk')

        if not id_produk:
            return Response(
                json.dumps({
                    'status': 400,
                    'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'notification_response': 'ID Produk Required',
                    'data': []
                }),
                content_type='application/json',
                status=400
            )

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk menghapus pengguna
        cursor.callproc('sp_produk_delete', (id_produk,))

        # Commit perubahan ke database
        conn.commit()

        cursor.close()

        # Format hasil akhir
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Hapus Data Produk'),
            ('data', [])
        ])

        return Response(json.dumps(response, ensure_ascii=False, indent=4), content_type='application/json')

    except Exception as e:
        # Handle error dan kembalikan response kegagalan
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Hapus Data Produk'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
