from flask import Blueprint, request, Response, current_app
from collections import OrderedDict
from datetime import datetime
import json

# Blueprint untuk login
login_blueprint = Blueprint('login', __name__)

@login_blueprint.route('/', methods=['POST'])
def login():
    try:
        # Ambil data dari body request
        body = request.get_json()
        username_login = body.get('p_username_login')
        password_login = body.get('p_password_login')

        # Koneksi ke MySQL
        conn = current_app.config['MYSQL_CONNECTION']
        cursor = conn.cursor()

        # Panggil stored procedure dengan parameter username dan password
        cursor.callproc('sp_login_retiel', (username_login, password_login))

        # Ambil hasil dari stored procedure
        result = []
        for result_set in cursor.stored_results():
            result = result_set.fetchall()

        cursor.close()

        # Debugging hasil raw
        print("Raw Results:", result)

        # Jika hasil hanya mengembalikan 2 kolom (gagal login)
        if len(result) == 1 and len(result[0]) == 2:
            v_status_get = result[0][0]
            v_message_get = result[0][1]
            
            # Kembalikan hasil dengan status gagal
            response_failed = OrderedDict([
                ('status', 200),
                ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                ('notification_response', v_message_get),
                ('data', [{
                    'v_status_get': v_status_get,
                    'v_message_get': v_message_get
                }])
            ])
            response_json = json.dumps(response_failed, ensure_ascii=False, indent=4)
            return Response(response_json, content_type='application/json', status=401)

        # Jika login berhasil dan mengembalikan data pengguna
        else:
            user_data = []
            for row in result:
                created_at = row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else None
                updated_at = row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else None
                user_info = OrderedDict([
                    ('id_pengguna', row[0]),                # ID Pengguna
                    ('name_pengguna', row[1]),              # Nama Pengguna
                    ('username_pengguna', row[2]),          # Username
                    ('role_pengguna', row[3]),              # Role Pengguna
                    ('created_at', created_at),             # Tanggal Dibuat
                    ('updated_at', updated_at)              # Tanggal Diubah
                ])
                user_data.append(user_info)

            # Format response jika berhasil login
            response_success = OrderedDict([
                ('status', 200),
                ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                ('notification_response', f"Berhasil Login"),
                ('data', user_data)
            ])

            response_json = json.dumps(response_success, ensure_ascii=False, indent=4)
            return Response(response_json, content_type='application/json')

    except Exception as e:
        # Penanganan error
        error_response = OrderedDict([
            ('status', 500),
            ('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('notification_response', 'Gagal Login'),
            ('error', str(e))
        ])
        error_json = json.dumps(error_response, ensure_ascii=False, indent=4)
        return Response(error_json, content_type='application/json', status=500)
