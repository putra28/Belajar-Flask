from flask import Blueprint, Response, current_app, request
from collections import OrderedDict
from datetime import datetime
import json
import jwt
from functools import wraps

transaksi_blueprint = Blueprint('transaksi', __name__)

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

@transaksi_blueprint.route('/getalldatatransaksi', methods=['GET'])
@token_required
def get_data_transaksi():
    try:
        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure 
        cursor.callproc('sp_get_all_histori_transaksi')
        transaksi_results = []
        for result in cursor.stored_results():
            transaksi_results = result.fetchall()

        cursor.callproc('sp_get_all_detail_transaksi')
        detail_results = []
        for result in cursor.stored_results():
            detail_results = result.fetchall()

        # Debug print hasil raw
        print("Transaksi Raw Results: ", transaksi_results)
        print("Detail Raw Results: ", detail_results)

        # Format hasil sebagai JSON dengan urutan kolom yang benar
        transaksi_data = []

         # Loop through the transaksi_results and build transaksi with corresponding detail_transaksi
        for transaksi_row in transaksi_results:
            # Filter details for this transaksi (matching M_idTransaksi)
            detail_transaksi = []
            for detail_row in detail_results:
                if detail_row[1] == transaksi_row[0]:  # detail_row[1] is M_idTransaksi
                    detail = OrderedDict([
                        ('v_id_detail_transaksi', detail_row[0]), # ID Detail Transaksi
                        ('v_id_transaksi', detail_row[1]),        # ID Transaksi
                        ('v_name_kategori', detail_row[2]),       # Nama Kategori
                        ('v_name_subkategori', detail_row[3]),    # Nama Subkategori
                        ('v_name_produk', detail_row[4]),         # Nama Produk
                        ('v_price_produk', int(detail_row[5])),   # Harga Produk
                        ('v_quantity_produk', detail_row[6])      # Jumlah Produk
                    ])
                    detail_transaksi.append(detail)

            # Build transaksi object
            transaksi = OrderedDict([
                ('v_id_transaksi', transaksi_row[0]),              # ID Transaksi
                ('v_id_pengguna', transaksi_row[1]),               # ID Pengguna
                ('v_nama_pengguna', transaksi_row[2]),             # Nama Pengguna
                ('v_nama_pelanggan', transaksi_row[3]),            # Nama Pelanggan
                ('v_quantity_transaksi', transaksi_row[4]),        # Jumlah Transaksi
                ('v_total_payment', int(transaksi_row[5])),        # Total Pembayaran
                ('v_total_price', int(transaksi_row[6])),          # Total Harga
                ('v_total_change', int(transaksi_row[7])),         # Total Kembalian
                ('v_date_transaksi', transaksi_row[8].strftime('%Y-%m-%d %H:%M:%S')),  # Tanggal Transaksi
                ('v_detail_transaksi', detail_transaksi)           # Detail Transaksi (from above)
            ])

            transaksi_data.append(transaksi)

        cursor.close()

        # Format final response
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Mengambil Data Transaksi'),
            ('data', transaksi_data)
        ])

        # Use json.dumps to preserve the order of keys
        response_json = json.dumps(response, ensure_ascii=False, indent=4)

        # Return response with proper content type and status code
        return Response(response_json, content_type='application/json')

    except Exception as e:
        # Handle error and return a failure response
        error_response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Mengambil Data Transaksi ini.'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
    

@transaksi_blueprint.route('/getdatatransaksibykasir', methods=['POST'])
@token_required
def get_data_transaksi_by_kasir():
    try:
        # Mengambil parameter dari request JSON
        request_data = request.get_json()
        p_id_pengguna = request_data.get('p_id_pengguna')

        # Validasi ID Pengguna
        if not p_id_pengguna:
            return Response(json.dumps({
                'status': 400,
                'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'notification_response': 'p_id_pengguna tidak disediakan'
            }), content_type='application/json', status=400)

        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure untuk mengambil data transaksi berdasarkan p_id_pengguna
        cursor.callproc('sp_get_pengguna_histrori_transaksi', [p_id_pengguna])

        # Mengambil hasil dari stored procedure
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()

        cursor.close()

        # Cek jumlah kolom dalam hasil
        if len(results) == 0:
            return Response(json.dumps({
                'status': 500,
                'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'notification_response': 'Gagal Mengambil Data Transaksi',
                'error': 'Tidak ada hasil dari stored procedure'
            }), content_type='application/json', status=500)

        # Jika hasil hanya berisi 2 kolom (status_get dan message_get)
        if len(results[0]) == 2:
            status_get, message_get = results[0]
            response = OrderedDict([
                ('status', 200),
                ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                ('notification_response', message_get),
                ('data', [{
                    'v_status_get': status_get,
                    'v_message_get': message_get
                }])
            ])
            return Response(json.dumps(response, ensure_ascii=False, indent=4), content_type='application/json')

        # Jika hasil berisi data transaksi
        transaksi_data = []
        for transaksi_row in results:
            # Ambil detail transaksi (kamu perlu melakukan query untuk detail transaksi di sini)
            # Misalnya, detail_transaksi = get_detail_transaksi(transaksi_row[0])

            transaksi = OrderedDict([
                ('v_id_transaksi', transaksi_row[0]),
                ('v_id_pengguna', transaksi_row[1]),
                ('v_nama_pengguna', transaksi_row[2]),
                ('v_nama_pelanggan', transaksi_row[3]),
                ('v_quantity_transaksi', transaksi_row[4]),
                ('v_total_payment', int(transaksi_row[5])),
                ('v_total_price', int(transaksi_row[6])),
                ('v_total_change', int(transaksi_row[7])),
                ('v_date_transaksi', transaksi_row[8].strftime('%Y-%m-%dT%H:%M:%S')),
                # ('v_detail_transaksi', detail_transaksi)  # Uncomment when detail retrieval is implemented
            ])
            transaksi_data.append(transaksi)

        # Format hasil akhir
        if transaksi_data:
            username = transaksi_data[0]['v_nama_pengguna']  # Ambil nama pengguna dari transaksi pertama
            response = OrderedDict([
                ('status', 200),
                ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                ('notification_response', f'Berhasil Mengambil Data Transaksi By {username}'),
                ('data', transaksi_data)
            ])
        else:
            response = OrderedDict([
                ('status', 200),
                ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                ('notification_response', 'Tidak ada data transaksi untuk pengguna ini.'),
                ('data', [])
            ])

        response_json = json.dumps(response, ensure_ascii=False, indent=4)

        return Response(response_json, content_type='application/json')

    except Exception as e:
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Mengambil Data Transaksi'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
