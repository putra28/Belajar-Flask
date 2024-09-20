from flask import Blueprint, Response, current_app
from collections import OrderedDict
from datetime import datetime
import json

laporanstok_blueprint = Blueprint('laporanstok', __name__)

@laporanstok_blueprint.route('/getlaporanstok', methods=['GET'])
def get_data_stok():
    try:
        # Mengambil koneksi MySQL dari konfigurasi Flask
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure
        cursor.callproc('sp_get_all_laporan_stok')

        # Mengambil hasil dari stored procedure
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()

        # Debug print hasil raw
        print("Raw Results: ", results)

        # Format hasil sebagai JSON dengan urutan kolom yang benar
        laporan_stok = []
        for row in results:
            created_at = row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else None
            lapstok = OrderedDict([
                ('id_stok', row[0]),                        # ID pemasok
                ('nama_produk', row[1]),                    # Nama pemasok
                ('stok_semula', row[2]),                    # Kontak pemasok
                ('perubahan_stok', row[3]),                 # Alamat pemasok
                ('aksi_stok', row[4]),                      # Alamat pemasok
                ('v_created_at', created_at),               # Tanggal Laporan
            ])
            laporan_stok.append(lapstok)

        cursor.close()

        # Format hasil akhir dengan tanggal saat ini, status, notification_response, dan data
        response = OrderedDict([
            ('status', 200),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Berhasil Get Laporan Stok'),
            ('data', laporan_stok)
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
            ('notification_response', 'Gagal Get Laporan Stok'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
