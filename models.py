from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()



class LoaiPhong(db.Model):
    __tablename__ = 'loaiphong'
    id = db.Column('ID_LoaiPhong', db.Integer, primary_key=True, autoincrement=True)
    ten = db.Column('TenLoaiPhong', db.String(255), nullable=False)
    phongs = db.relationship('Phong', backref='loaiphong', lazy=True)
    dichvus = db.relationship('DichVu', backref='loaiphong', lazy=True)
    thietbis = db.relationship('ThietBi', backref='loaiphong', lazy=True)

class Tang(db.Model):
    __tablename__ = 'tang'
    id = db.Column('ID_Tang', db.Integer, primary_key=True, autoincrement=True)
    ten = db.Column('TenTang', db.String(255), nullable=False)
    phongs = db.relationship('Phong', backref='tang', lazy=True)

class NhanVien(db.Model):
    __tablename__ = 'nhanvien'
    id = db.Column('IDNhanVien', db.Integer, primary_key=True, autoincrement=True)
    ten = db.Column('TenNhanVien', db.String(255), nullable=False, unique=True)
    gioitinh = db.Column('GioiTinh', db.String(10))
    chucvu = db.Column('ChucVu', db.String(100))
    ngaysinh = db.Column('NgaySinh', db.Date)
    cccd = db.Column('Cccd', db.String(20), unique=True)
    sdt = db.Column('SDT', db.String(15))
    luong = db.Column('Luong', db.Numeric(12,2))
    taikhoan = db.relationship('TaiKhoan', backref='nhanvien', uselist=False)
    hoadons = db.relationship('HoaDon', backref='nhanvien', lazy=True)

class KhachHang(db.Model):
    __tablename__ = 'khachhang'
    id = db.Column('IDKhachHang', db.Integer, primary_key=True, autoincrement=True)
    hoten = db.Column('HoTen', db.String(255), nullable=False)
    gioitinh = db.Column('GioiTinh', db.String(10))
    ngaysinh = db.Column('NgaySinh', db.Date)
    diachi = db.Column('DiaChi', db.String(255))
    sdt = db.Column('SoDienThoai', db.String(15))
    cccd = db.Column('CCCD', db.String(20), unique=True)
    ngaythue = db.Column('NgayThue', db.Date)
    hoadons = db.relationship('HoaDon', backref='khachhang', lazy=True)

class Phong(db.Model):
    __tablename__ = 'phong'
    id = db.Column('ID_Phong', db.Integer, primary_key=True, autoincrement=True)
    ten = db.Column('TenPhong', db.String(255), nullable=False)
    dongia = db.Column('DonGia', db.Numeric(10,2), nullable=False)
    tinhtrang = db.Column('TinhTrang', db.String(50))
    id_loaiphong = db.Column('ID_LoaiPhong', db.Integer, db.ForeignKey('loaiphong.ID_LoaiPhong'), nullable=False)
    id_tang = db.Column('ID_Tang', db.Integer, db.ForeignKey('tang.ID_Tang'), nullable=False)
    dichvus = db.relationship('DichVu', backref='phong', lazy=True)
    thietbis = db.relationship('ThietBi', backref='phong', lazy=True)
    hoadoncts = db.relationship('HoaDonCT', backref='phong', lazy=True)

class TaiKhoan(UserMixin, db.Model):
    __tablename__ = 'taikhoan'
    id = db.Column('IDTaiKhoan', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column('TenDangNhap', db.String(100), nullable=False, unique=True)
    password_hash = db.Column('MatKhau', db.String(255), nullable=False)
    id_nhanvien = db.Column('IDNhanVien', db.Integer, db.ForeignKey('nhanvien.IDNhanVien'), nullable=False, unique=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        # Determine admin by linked Nhân Viên chức vụ 'Manager' or 'Admin' (case-insensitive)
        try:
            cv = (self.nhanvien.chucvu or "").lower()
            return cv in ('manager', 'admin')
        except Exception:
            return False

class DichVu(db.Model):
    __tablename__ = 'dichvu'
    id = db.Column('ID_DichVu', db.Integer, primary_key=True, autoincrement=True)
    ten = db.Column('TenDichVu', db.String(255), nullable=False)
    gia = db.Column('GiaDichVu', db.Numeric(10,2), nullable=False)
    id_loaiphong = db.Column('ID_LoaiPhong', db.Integer, db.ForeignKey('loaiphong.ID_LoaiPhong'), nullable=False)
    id_phong = db.Column('ID_Phong', db.Integer, db.ForeignKey('phong.ID_Phong'), nullable=False)
    dv_hdcts = db.relationship('DV_HDCT', backref='dichvu', lazy=True)

class ThietBi(db.Model):
    __tablename__ = 'thietbi'
    id = db.Column('ID_ThietBi', db.Integer, primary_key=True, autoincrement=True)
    ten = db.Column('TenThietBi', db.String(255), nullable=False)
    gia = db.Column('GiaThietBi', db.Numeric(10,2))
    trangthai = db.Column('TrangThai', db.String(50))
    id_loaiphong = db.Column('ID_LoaiPhong', db.Integer, db.ForeignKey('loaiphong.ID_LoaiPhong'), nullable=False)
    id_phong = db.Column('ID_Phong', db.Integer, db.ForeignKey('phong.ID_Phong'), nullable=False)

class HoaDon(db.Model):
    __tablename__ = 'hoadon'
    id = db.Column('IDHoaDon', db.Integer, primary_key=True, autoincrement=True)
    soluong = db.Column('SoLuong', db.Integer, nullable=False, default=0)
    tongtien = db.Column('TongTien', db.Numeric(12,2), nullable=False, default=0)
    ngaythanhtoan = db.Column('NgayThanhToan', db.DateTime)
    id_nhanvien = db.Column('IDNhanVien', db.Integer, db.ForeignKey('nhanvien.IDNhanVien'), nullable=False)
    id_khachhang = db.Column('IDKhacHang', db.Integer, db.ForeignKey('khachhang.IDKhachHang'), nullable=False)  # note: original name kept
    hoadoncts = db.relationship('HoaDonCT', backref='hoadon', lazy=True)

class HoaDonCT(db.Model):
    __tablename__ = 'hoadonct'
    id = db.Column('IDHoaDonCT', db.Integer, primary_key=True, autoincrement=True)
    tenphong = db.Column('TenPhong', db.String(255))
    ngay_checkin = db.Column('NgayCheckIn', db.DateTime, nullable=False, default=datetime.utcnow)
    ngay_checkout = db.Column('NgayCheckOut', db.DateTime)
    nhanvienlap = db.Column('NhanVienLap', db.String(255))
    tenkhachhang = db.Column('TenKhachHang', db.String(255))
    gioc_checkout = db.Column('GiocCheckOut', db.DateTime)
    gio_checkin = db.Column('GioCheckIn', db.DateTime)
    id_hoadon = db.Column('IDHoaDon', db.Integer, db.ForeignKey('hoadon.IDHoaDon'), nullable=False)
    id_phong = db.Column('ID_Phong', db.Integer, db.ForeignKey('phong.ID_Phong'), nullable=False)
    dv_hdcts = db.relationship('DV_HDCT', backref='hoadonct', lazy=True)

class DV_HDCT(db.Model):
    __tablename__ = 'dv_hdct'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    id_hoadonct = db.Column('IDHoaDonCT', db.Integer, db.ForeignKey('hoadonct.IDHoaDonCT'), nullable=False)
    id_dichvu = db.Column('IDDichVu', db.Integer, db.ForeignKey('dichvu.ID_DichVu'), nullable=False)
    soluong = db.Column('SoLuongDV', db.Integer, nullable=False, default=1)
    giatien = db.Column('GiaTien', db.Numeric(10,2), nullable=False, default=0)
    giatientong = db.Column('GiaTienTong', db.Numeric(12,2), nullable=False, default=0)