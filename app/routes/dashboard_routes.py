from flask import Blueprint, Response, current_app, request, jsonify
from collections import OrderedDict
from datetime import datetime
import json
import jwt
from functools import wraps

dashboard_blueprint = Blueprint('dashboard', __name__)

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
@dashboard_blueprint.route('/getdatadashboard', methods=['POST'])
@token_required
def get_data_dashboard():
    try:
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Mendapatkan bulan dan tahun dari request JSON
        request_data = request.get_json()
        p_periode_bulan = request_data.get('p_periode_bulan')
        p_periode_tahun = request_data.get('p_periode_tahun')

        print(p_periode_bulan, p_periode_tahun)
        # Panggil stored procedure untuk total produk terjual
        cursor.callproc('sp_get_total_produk_terjual_periode', [p_periode_bulan, p_periode_tahun])
        result = cursor.fetchall()
        v_total_produk_terjual = result[0][0] if result else 0

        # Panggil stored procedure untuk total transaksi
        cursor.callproc('sp_get_total_transaksi_periode', [p_periode_bulan, p_periode_tahun])
        result = cursor.fetchone()
        v_total_transaksi_periode = result[0] if result else 0

        # Panggil stored procedure untuk total keuntungan
        cursor.callproc('sp_get_profit_perbulan', [p_periode_bulan, p_periode_tahun])
        result = cursor.fetchone()
        v_total_keuntungan_periode = result[0] if result else 0

        # Panggil stored procedure untuk produk terbaik
        cursor.callproc('sp_get_produk_terbaik_periode', [p_periode_bulan, p_periode_tahun])
        result = cursor.fetchone()
        v_produk_best_seller = result[0] if result else 'Tidak Ada Produk Terbaik'

        # Panggil stored procedure untuk produk stok rendah
        cursor.callproc('sp_get_produk_stok_rendah')
        result = cursor.fetchone()
        v_produk_stok_rendah = result[0] if result else 'Tidak Ada Produk dengan Stok Rendah'

        # Panggil stored procedure untuk total pelanggan
        # cursor.callproc('sp_get_total_pelanggan')
        # result = cursor.fetchone()
        # v_total_member = result[0] if result else 0

        cursor.close()

        # Susun response JSON sesuai format yang diinginkan
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Get Data'),
            ('data', {
                'v_total_produk_terjual': v_total_produk_terjual,
                'v_total_transaksi_periode': v_total_transaksi_periode,
                'v_total_keuntungan_periode': v_total_keuntungan_periode,
                'v_produk_stok_rendah': v_produk_stok_rendah,
                'v_produk_best_seller': v_produk_best_seller
            })
        ])

        response_json = json.dumps(response, ensure_ascii=False, indent=4)
        return Response(response_json, content_type='application/json')

    except Exception as e:
        # Handle error and return a failure response
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Get Data Dashboard'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
