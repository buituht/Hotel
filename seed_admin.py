"""
Seed an admin account for local development.

Run once (or re-run) to create an admin user if it doesn't exist.

Default:
    username: admin
    password: Admin@123

If your TaiKhoan model uses different field names, adjust accordingly.
"""
import os
from models import db, TaiKhoan, NhanVien
from app import create_app

DEFAULT_USER = os.environ.get('ADMIN_USER', 'admin')
DEFAULT_PASS = os.environ.get('ADMIN_PASS', 'Admin@123')

app = create_app()
app.app_context().push()

def ensure_admin(username=DEFAULT_USER, password=DEFAULT_PASS):
    # check existing user
    u = TaiKhoan.query.filter_by(username=username).first()
    if u:
        print(f"Admin user '{username}' already exists.")
        return u
    # create linked NhanVien (Manager role)
    nv = NhanVien.query.filter_by(ten='Administrator').first()
    if not nv:
        nv = NhanVien(ten='Administrator', chucvu='Manager')
        db.session.add(nv)
        db.session.flush()
    # create account
    acc = TaiKhoan(username=username, id_nhanvien=getattr(nv, 'id', getattr(nv, 'ID_NhanVien', None)))
    # set password using model helper if exists
    if hasattr(acc, 'set_password'):
        acc.set_password(password)
    else:
        # fallback: set password_hash if attribute exists
        try:
            import werkzeug.security as ws
            acc.password_hash = ws.generate_password_hash(password)
        except Exception:
            pass
    # attempt to mark as admin if field exists
    if hasattr(acc, 'is_admin'):
        setattr(acc, 'is_admin', True)
    try:
        db.session.add(acc)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Failed to create admin user:", e)
        raise
    print(f"Created admin user '{username}' with password '{password}' (development only).")
    return acc

if __name__ == '__main__':
    ensure_admin()