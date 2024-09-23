# app/__init__.py
from flask import Flask, current_app, send_from_directory
import mysql.connector
from app.routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object('instance.config.Config')

    # Setup koneksi MySQL secara manual
    app.config['MYSQL_CONNECTION'] = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    # Route untuk favicon
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(current_app.static_folder, 'angry.ico')
    # Daftarkan semua blueprint yang didefinisikan di routes/__init__.py
    register_blueprints(app)

    return app
