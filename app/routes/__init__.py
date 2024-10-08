# routes/__init__.py

from flask import Blueprint
from .pengguna_routes import pengguna_blueprint
from .produk_routes import produk_blueprint
from .logaktifitas_routes import logaktifitas_blueprint
from .pemasok_routes import pemasok_blueprint
from .laporanstok_routes import laporanstok_blueprint
from .kategori_routes import kategori_blueprint
from .transaksi_routes import transaksi_blueprint
from .login_routes import login_blueprint
from .dashboard_routes import dashboard_blueprint

def register_blueprints(app):
    # Daftar semua blueprint di sini
    app.register_blueprint(pengguna_blueprint, url_prefix='/api/pengguna')
    app.register_blueprint(produk_blueprint, url_prefix='/api/produk')
    app.register_blueprint(logaktifitas_blueprint, url_prefix='/api/logaktifitas')
    app.register_blueprint(pemasok_blueprint, url_prefix='/api/pemasok')
    app.register_blueprint(laporanstok_blueprint, url_prefix='/api/laporanstok')
    app.register_blueprint(kategori_blueprint, url_prefix='/api/kategori')
    app.register_blueprint(transaksi_blueprint, url_prefix='/api/transaksi')
    app.register_blueprint(login_blueprint, url_prefix='/api/login')
    app.register_blueprint(dashboard_blueprint, url_prefix='/api/dashboard')
