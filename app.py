#!/usr/bin/env python3
"""
Main Flask app: registers both the custom Bootstrap admin UI (admin-ui blueprint)
and Flask-Admin (for quick CRUD on all models).

Usage:
- Ensure models.py and forms.py exist and are compatible.
- Run: python seed_admin.py   # optional, to create default admin user
- Run: python app.py
- Custom UI: http://127.0.0.1:5000/admin-ui/
- Flask-Admin: http://127.0.0.1:5000/flask-admin/
"""
import os
import logging
from flask import Flask, redirect, url_for, render_template, flash, request
from flask_migrate import Migrate
from sqlalchemy.exc import OperationalError
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_admin import Admin

# Import your models and forms
from models import (
    db, LoaiPhong, Tang, NhanVien, KhachHang, Phong,
    TaiKhoan, DichVu, ThietBi, HoaDon, HoaDonCT, DV_HDCT
)
from forms import LoginForm, RegisterForm

# Custom admin UI blueprint
from admin_views import admin_bp

# Flask-Admin ModelView registrations (in separate module)
from admin_modelviews import register_admin_views

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, template_folder='templates')
    # DEVELOPMENT DB connection string you requested
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3307/khachsan'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')

    # Convenience: expose getattr safely to templates (optional)
    app.jinja_env.globals['getattr'] = getattr

    db.init_app(app)
    Migrate(app, db)

    # Login manager
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return TaiKhoan.query.get(int(user_id))
        except Exception:
            return None

    # Register custom admin UI (Bootstrap)
    app.register_blueprint(admin_bp)

    # Register Flask-Admin at /flask-admin/
    admin = Admin(app, name='Flask Admin', template_mode='bootstrap4', url='/flask-admin/')
    # register ModelViews for all models
    register_admin_views(admin, db, app)

    # Index route redirect to custom admin UI dashboard
    @app.route('/')
    def index():
        return redirect(url_for('admin_ui.dashboard'))

    # Auth routes (using existing forms.py)
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            try:
                user = TaiKhoan.query.filter_by(username=form.username.data).first()
            except OperationalError:
                flash("Không thể kết nối đến database. Kiểm tra cấu hình kết nối và quyền truy cập.", "danger")
                return render_template('login.html', form=form)
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                flash('Đăng nhập thành công.', 'success')
                next_page = request.args.get('next') or url_for('admin_ui.dashboard')
                return redirect(next_page)
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Đã đăng xuất.', 'info')
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            if TaiKhoan.query.filter_by(username=form.username.data).first():
                flash('Tên đăng nhập đã tồn tại.', 'danger')
                return render_template('register.html', form=form)
            nv = NhanVien.query.filter_by(ten=form.employee_name.data).first()
            if not nv:
                nv = NhanVien(ten=form.employee_name.data, chucvu=form.employee_role.data)
                db.session.add(nv)
                db.session.flush()
            acc = TaiKhoan(username=form.username.data, id_nhanvien=nv.id)
            acc.set_password(form.password.data)
            db.session.add(acc)
            db.session.commit()
            flash('Đăng ký thành công. Bạn có thể đăng nhập.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    # Simple debug route to see current user
    @app.route('/_whoami')
    @login_required
    def whoami():
        acc = current_user
        username = acc.username if hasattr(acc, 'username') else getattr(acc, 'TenDangNhap', '')
        try:
            nv = acc.nhanvien
            nv_name = getattr(nv, 'ten', getattr(nv, 'TenNhanVien', ''))
            nv_role = getattr(nv, 'chucvu', getattr(nv, 'ChucVu', ''))
            nvinfo = f"{nv_name} / {nv_role}"
        except Exception:
            nvinfo = "No linked NhanVien"
        return f"Logged in as: {username} — Linked: {nvinfo}"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)