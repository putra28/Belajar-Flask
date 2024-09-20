from flask import Blueprint, Response, current_app
from collections import OrderedDict
from datetime import datetime
import json

pengguna_blueprint = Blueprint('pengguna', __name__)

@pengguna_blueprint.route('/getdatapengguna', methods=['GET'])
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
