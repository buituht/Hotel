"""
Register Flask-Admin ModelViews for your SQLAlchemy models.

This module programmatically creates a ModelView subclass for each model you
import into register_admin_views(). It attempts to:
- Use mapped attribute names for form_columns
- Create form_ajax_refs for relationship attributes so you get dropdown/ajax lookups
- Exclude sensitive columns like password_hash
- Provide CSV export action for each view
"""
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import PasswordField
from flask import current_app
import sqlalchemy as sa
from sqlalchemy import select 

# Import models ở đây để có thể sử dụng cho các lớp tùy chỉnh
# Đã sửa lỗi: Tên lớp phải viết hoa (NhanVien, KhachHang,...)
from models import db, LoaiPhong, Tang, NhanVien, KhachHang, Phong, DichVu, ThietBi, HoaDon, HoaDonCT, DV_HDCT, TaiKhoan

SENSITIVE_COLUMNS = {'password_hash', 'secret', 'token'}

# --- CÁC HÀM TỰ ĐỘNG ---

def _get_mapped_columns(model):
    try:
        # Lấy tên thuộc tính Python (ten, id_nhanvien,...)
        return [prop.key for prop in model.__mapper__.column_attrs]
    except Exception:
        # fallback to table columns
        try:
            return [c.key for c in model.__table__.columns]
        except Exception:
            return []

def _get_relationships(model):
    try:
        return {rel.key: rel for rel in model.__mapper__.relationships}
    except Exception:
        return {}

class BaseModelView(ModelView):
    can_export = True
    page_size = 50

    def scaffold_form(self):
        form_class = super().scaffold_form()
        # Ẩn các trường nhạy cảm
        for s in SENSITIVE_COLUMNS:
            if hasattr(form_class, s):
                try:
                    delattr(form_class, s)
                except Exception:
                    pass
        return form_class

# --------------------------------------------------------------------
# CÁC LỚP MODELVIEW TÙY CHỈNH (Đã sửa lỗi tên thuộc tính)
# --------------------------------------------------------------------

# 1. NHAN VIEN
class NhanVienCustomView(BaseModelView):
    # SỬA LỖI: Dùng tên thuộc tính Python (ten, sdt) thay vì tên cột CSDL (TenNhanVien, SDT)
    form_columns = ('ten', 'gioitinh', 'chucvu', 'ngaysinh', 'cccd', 'sdt', 'luong')
    column_labels = dict(taikhoan='Tài khoản', hoadons='Hóa đơn đã lập', ten='Tên NV', sdt='SĐT', id='ID')
    column_list = ('id', 'ten', 'chucvu', 'sdt', 'luong', 'taikhoan')

# 2. KHACH HANG
class KhachHangCustomView(BaseModelView):
    # SỬA LỖI: Dùng tên thuộc tính Python (hoten, sdt)
    form_columns = ('hoten', 'gioitinh', 'ngaysinh', 'diachi', 'sdt', 'cccd', 'ngaythue')
    column_labels = dict(hoadons='Hóa đơn đã thuê', hoten='Họ tên', sdt='SĐT', id='ID')
    column_list = ('id', 'hoten', 'sdt', 'cccd')

# 3. PHONG
class PhongCustomView(BaseModelView):
    # SỬA LỖI: Dùng tên thuộc tính Python (ten, id_loaiphong, id_tang)
    form_columns = ('ten', 'dongia', 'tinhtrang', 'id_loaiphong', 'id_tang')
    column_labels = dict(loaiphong='Loại phòng', tang='Tầng', ten='Tên phòng', id='ID')
    column_list = ('id', 'ten', 'dongia', 'loaiphong', 'tang')

# 4. HOA DON
class HoaDonCustomView(BaseModelView):
    # SỬA LỖI: Dùng tên thuộc tính Python (id_nhanvien, id_khachhang)
    form_columns = ('id_nhanvien', 'id_khachhang', 'soluong', 'tongtien', 'ngaythanhtoan')
    column_labels = dict(khachhang='Khách hàng', nhanvien='Nhân viên', soluong='SL Phòng', id='ID')
    column_list = ('id', 'nhanvien', 'khachhang', 'tongtien', 'ngaythanhtoan')

# 5. HOA DON CHI TIET
class HoaDonCTCustomView(BaseModelView):
    # SỬA LỖI: Dùng tên thuộc tính Python (id_hoadon, id_phong)
    form_columns = ('id_hoadon', 'id_phong', 'tenphong', 'ngay_checkin', 'gio_checkin', 'ngay_checkout', 'gioc_checkout', 'nhanvienlap', 'tenkhachhang')
    column_labels = dict(hoadon='Hóa đơn', phong='Phòng', ngay_checkin='Check In', ngay_checkout='Check Out', id='ID')
    column_list = ('id', 'hoadon', 'phong', 'ngay_checkin', 'ngay_checkout')

# 6. DV_HDCT
class DV_HDCTCustomView(BaseModelView):
    # SỬA LỖI: Dùng tên thuộc tính Python (id_hoadonct, id_dichvu, soluong)
    form_columns = ('id_hoadonct', 'id_dichvu', 'soluong', 'giatien', 'giatientong')
    column_labels = dict(hoadonct='Hóa đơn chi tiết', dichvu='Dịch vụ', soluong='Số lượng DV', id='ID')
    column_list = ('id', 'hoadonct', 'dichvu', 'soluong', 'giatientong')

# 7. DICH VU (Custom View để kiểm soát form_columns)
class DichVuCustomView(BaseModelView):
    # SỬA LỖI: Dùng tên thuộc tính Python (ten, id_loaiphong, id_phong)
    form_columns = ('ten', 'gia', 'id_loaiphong', 'id_phong')
    column_labels = dict(ten='Tên DV', gia='Giá', loaiphong='Loại phòng', phong='Phòng', id='ID')
    column_list = ('id', 'ten', 'gia', 'loaiphong', 'phong')


# --------------------------------------------------------------------
# HÀM ĐĂNG KÝ ADMIN VIEWS
# --------------------------------------------------------------------

# Mapping các model cần tùy chỉnh
CUSTOM_VIEWS = {
    NhanVien: NhanVienCustomView,
    KhachHang: KhachHangCustomView,
    Phong: PhongCustomView,
    HoaDon: HoaDonCustomView,
    HoaDonCT: HoaDonCTCustomView,
    DV_HDCT: DV_HDCTCustomView,
    DichVu: DichVuCustomView, 
}
# Các model cơ bản có thể dùng tự động hóa
BASIC_MODELS = [LoaiPhong, Tang, ThietBi, TaiKhoan]

def register_admin_views(admin, db, app=None):
    
    # 1. Đăng ký các ModelView tùy chỉnh (để tránh lỗi AJAX/ID)
    for model, ViewCls in CUSTOM_VIEWS.items():
        model_name = getattr(model, '__name__', str(model))
        try:
            # Phân loại cho dễ quản lý
            category = 'Hóa đơn & Nghiệp vụ' if model in [HoaDon, HoaDonCT, DV_HDCT, Phong, DichVu] else 'Quản lý nhân sự'
            admin.add_view(ViewCls(model, db.session, category=category))
            if app:
                app.logger.info("Registered Flask-Admin custom view for model: %s", model_name)
        except Exception as e:
            if app:
                app.logger.exception("Failed to register Custom ModelView for %s: %s", model_name, e)
            else:
                print(f"Failed to register Custom ModelView for {model_name}: {e}")

    # 2. Đăng ký các ModelView tự động (cho các model đơn giản)
    models_to_auto_register = BASIC_MODELS
    
    for model in models_to_auto_register:
        model_name = getattr(model, '__name__', str(model))
        cols = _get_mapped_columns(model)
        
        # loại bỏ sensitive columns
        cols = [c for c in cols if c not in SENSITIVE_COLUMNS]
        
        if not cols:
            if app:
                app.logger.warning("Model %s: no form columns detected; view will be registered but forms may be empty.", model_name)
        
        # Xây dựng form_ajax_refs
        relationships = _get_relationships(model)
        form_ajax_refs = {}
        for rel_name, rel in relationships.items():
            target = rel.mapper.class_
            # Bỏ qua nếu model đích là CUSTOM_VIEWS (đã được xử lý thủ công)
            if target in CUSTOM_VIEWS:
                 continue

            label_fields = []
            for candidate in ('ten', 'name', 'title', 'username'):
                if hasattr(target, candidate):
                    label_fields.append(candidate)
            
            if not label_fields:
                try:
                    pk = [p.key for p in target.__mapper__.primary_key][0]
                    label_fields = [pk]
                except Exception:
                    label_fields = []
            
            if label_fields:
                form_ajax_refs[rel_name] = {'fields': label_fields}

        # Tạo dynamic ModelView subclass
        view_attrs = {
            # Sử dụng cols tự động tìm thấy
            'form_columns': tuple(cols) if cols else None,
            'form_ajax_refs': form_ajax_refs or None,
            'column_list': tuple(cols[:8]) if cols else None,
        }

        # Xử lý mật khẩu cho TaiKhoan
        if 'password_hash' in _get_mapped_columns(model):
            view_attrs['form_extra_fields'] = {'password': PasswordField('Mật khẩu mới')}
            # Loại bỏ cột hash
            view_attrs['form_excluded_columns'] = tuple(set(view_attrs.get('form_excluded_columns', ()) ) | {'password_hash'})

            # Logic thay đổi mật khẩu
            def on_model_change_password(self, form, model_obj, is_created):
                pwd = getattr(form, 'password', None)
                if pwd and getattr(pwd, 'data', None):
                    if hasattr(model_obj, 'set_password'):
                        # Dùng set_password từ models.py
                        model_obj.set_password(pwd.data)
                    else:
                        # Fallback nếu không có set_password
                        try:
                            import werkzeug.security as ws
                            model_obj.password_hash = ws.generate_password_hash(pwd.data)
                        except Exception:
                            pass
                
                # Gọi hàm gốc
                try:
                    return super(self.__class__, self).on_model_change(form, model_obj, is_created)
                except Exception:
                    return None

            view_attrs['on_model_change'] = on_model_change_password
            
        # Build the ModelView subclass
        # Đảm bảo view_attrs không chứa None
        ViewCls = type(f'{model_name}ModelView', (BaseModelView,), {k: v for k, v in view_attrs.items() if v is not None})

        try:
            # Đăng ký View tự động
            admin.add_view(ViewCls(model, db.session, category='Hệ thống'))
            if app:
                app.logger.info("Registered Flask-Admin auto view for model: %s", model_name)
        except Exception as e:
            if app:
                app.logger.exception("Failed to register ModelView for %s: %s", model_name, e)
            else:
                print(f"Failed to register ModelView for {model_name}: {e}")


