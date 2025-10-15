"""
Script tạo bảng (nếu chưa có) và thêm dữ liệu mẫu.
Chạy: python3 seed.py
"""
from app import create_app
from models import db, LoaiPhong, Tang, NhanVien, KhachHang, Phong, TaiKhoan, DichVu

app = create_app()

with app.app_context():
    # Tạo bảng
    db.create_all()

    # Kiểm tra đã có seed chưa
    if LoaiPhong.query.count() == 0:
        lp1 = LoaiPhong(ten='single')
        lp2 = LoaiPhong(ten='double')
        lp3 = LoaiPhong(ten='suite')
        db.session.add_all([lp1, lp2, lp3])
        db.session.commit()

    if Tang.query.count() == 0:
        t1 = Tang(ten='Tầng 1')
        t2 = Tang(ten='Tầng 2')
        db.session.add_all([t1, t2])
        db.session.commit()

    if NhanVien.query.count() == 0:
        nv1 = NhanVien(ten='Nguyen Van A', gioitinh='Nam', chucvu='Manager', ngaysinh='1985-05-12', cccd='012345678', sdt='0901234567', luong=15000000)
        nv2 = NhanVien(ten='Tran Thi B', gioitinh='Nu', chucvu='Receptionist', ngaysinh='1992-11-02', cccd='987654321', sdt='0907654321', luong=8000000)
        db.session.add_all([nv1, nv2])
        db.session.commit()

    if Phong.query.count() == 0:
        # Need loaiphong and tang ids
        lp_single = LoaiPhong.query.filter_by(ten='single').first()
        lp_double = LoaiPhong.query.filter_by(ten='double').first()
        lp_suite = LoaiPhong.query.filter_by(ten='suite').first()
        t1 = Tang.query.filter_by(ten='Tầng 1').first()
        t2 = Tang.query.filter_by(ten='Tầng 2').first()
        p1 = Phong(ten='101', dongia=200.00, tinhtrang='free', id_loaiphong=lp_single.id, id_tang=t1.id)
        p2 = Phong(ten='102', dongia=350.00, tinhtrang='free', id_loaiphong=lp_double.id, id_tang=t1.id)
        p3 = Phong(ten='201', dongia=800.00, tinhtrang='free', id_loaiphong=lp_suite.id, id_tang=t2.id)
        db.session.add_all([p1, p2, p3])
        db.session.commit()

    if TaiKhoan.query.count() == 0:
        nv_admin = NhanVien.query.filter_by(ten='Nguyen Van A').first()
        nv_recv = NhanVien.query.filter_by(ten='Tran Thi B').first()
        t1 = TaiKhoan(username='admin', id_nhanvien=nv_admin.id)
        t1.set_password('admin123')
        t2 = TaiKhoan(username='reception', id_nhanvien=nv_recv.id)
        t2.set_password('recept123')
        db.session.add_all([t1, t2])
        db.session.commit()

    if KhachHang.query.count() == 0:
        kh = KhachHang(hoten='Le Van C', gioitinh='Nam', ngaysinh='1990-01-01', diachi='Hanoi', sdt='0912345678', cccd='111222333')
        db.session.add(kh)
        db.session.commit()

    print("Seed finished.")