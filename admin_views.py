from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, EqualTo
from functools import wraps

from sqlalchemy import select

from wtforms import DateField #thu vien ngay thang
from wtforms.validators import Regexp 
from models import KhachHang # Form KhachHangForm 

from models import db, Phong, LoaiPhong, Tang
from models import db, Phong, LoaiPhong, Tang, TaiKhoan, NhanVien 
admin_bp = Blueprint('admin_ui', __name__, template_folder='templates', url_prefix='/admin-ui')

from chartdashboard import create_floor_chart 






def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        # allow if is_admin property exists and true; otherwise block
        if hasattr(current_user, 'is_admin') and not current_user.is_admin:
            flash('Bạn không có quyền truy cập trang quản trị.', 'danger')
            return redirect(url_for('index'))
        return fn(*args, **kwargs)
    return wrapper

class PhongForm(FlaskForm):
    ten = StringField('Tên phòng', validators=[DataRequired(), Length(max=255)])
    dongia = DecimalField('Đơn giá', validators=[DataRequired()], places=2)
    tinhtrang = StringField('Tình trạng', validators=[Optional(), Length(max=50)])
    id_loaiphong = SelectField('Loại phòng', coerce=int, validators=[Optional()])
    id_tang = SelectField('Tầng', coerce=int, validators=[Optional()])
    submit = SubmitField('Lưu')

# Thêm class Form cho TaiKhoan
class TaiKhoanForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(max=100)])
    id_nhanvien = SelectField('Nhân viên liên kết', coerce=int, validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[Optional(), EqualTo('confirm', message='Mật khẩu không khớp')])
    confirm = PasswordField('Xác nhận Mật khẩu', validators=[Optional()])
    submit = SubmitField('Lưu')

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_phong = Phong.query.count()
    total_loaiphong = LoaiPhong.query.count()
    total_tang = Tang.query.count()
    chart_data = create_floor_chart() 
    return render_template('admin/dashboard.html', total_phong=total_phong,
                           total_loaiphong=total_loaiphong, total_tang=total_tang,chart_data=chart_data)

@admin_bp.route('/phong')
@login_required
@admin_required
def phong_list():
    phongs = Phong.query.order_by(Phong.id).all()
    return render_template('admin/rooms_list.html', phongs=phongs)

@admin_bp.route('/phong/create', methods=['GET', 'POST'])
@login_required
@admin_required
def phong_create():
    form = PhongForm()
    # populate choices
    form.id_loaiphong.choices = [(lp.id, lp.ten) for lp in LoaiPhong.query.order_by(LoaiPhong.ten).all()]
    form.id_tang.choices = [(t.id, t.ten) for t in Tang.query.order_by(Tang.ten).all()]
    if form.validate_on_submit():
        p = Phong(
            ten=form.ten.data,
            dongia=form.dongia.data,
            tinhtrang=form.tinhtrang.data,
            id_loaiphong=form.id_loaiphong.data or None,
            id_tang=form.id_tang.data or None
        )
        db.session.add(p)
        db.session.commit()
        flash('Tạo phòng mới thành công.', 'success')
        return redirect(url_for('admin_ui.phong_list'))
    return render_template('admin/room_form.html', form=form, action='create')

@admin_bp.route('/phong/edit/<int:phong_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def phong_edit(phong_id):
    p = Phong.query.get_or_404(phong_id)
    form = PhongForm(obj=p)
    form.id_loaiphong.choices = [(lp.id, lp.ten) for lp in LoaiPhong.query.order_by(LoaiPhong.ten).all()]
    form.id_tang.choices = [(t.id, t.ten) for t in Tang.query.order_by(Tang.ten).all()]
    # set selected if GET
    if request.method == 'GET':
        form.id_loaiphong.data = p.id_loaiphong
        form.id_tang.data = p.id_tang
    if form.validate_on_submit():
        p.ten = form.ten.data
        p.dongia = form.dongia.data
        p.tinhtrang = form.tinhtrang.data
        p.id_loaiphong = form.id_loaiphong.data or None
        p.id_tang = form.id_tang.data or None
        db.session.commit()
        flash('Cập nhật phòng thành công.', 'success')
        return redirect(url_for('admin_ui.phong_list'))
    return render_template('admin/room_form.html', form=form, action='edit', phong=p)

@admin_bp.route('/phong/delete/<int:phong_id>', methods=['POST'])
@login_required
@admin_required
def phong_delete(phong_id):
    p = Phong.query.get_or_404(phong_id)
    db.session.delete(p)
    db.session.commit()
    flash('Đã xóa phòng.', 'info')
    return redirect(url_for('admin_ui.phong_list'))



# --------------------------------------------------------------------
# QUẢN LÝ TÀI KHOẢN (TaiKhoan)
# --------------------------------------------------------------------

@admin_bp.route('/taikhoan')
@login_required
@admin_required
def taikhoan_list():
    """Hiển thị danh sách Tài khoản."""
    stmt = select(TaiKhoan).order_by(TaiKhoan.id)
    taikhoans = db.session.scalars(stmt).all()
    return render_template('admin/taikhoan_list.html', taikhoans=taikhoans)

@admin_bp.route('/taikhoan/create', methods=['GET', 'POST'])
@login_required
@admin_required
def taikhoan_create():
    """Tạo Tài khoản mới."""
    form = TaiKhoanForm()
    
    # Lấy danh sách Nhân viên chưa có tài khoản
    # 1. Tìm ID Nhân viên đã có tài khoản
    stmt_existing_nv = select(TaiKhoan.id_nhanvien)
    existing_nv_ids = db.session.scalars(stmt_existing_nv).all()
    
    # 2. Lấy danh sách Nhân viên chưa có tài khoản
    stmt_nv = select(NhanVien).filter(NhanVien.id.not_in(existing_nv_ids)).order_by(NhanVien.ten)
    form.id_nhanvien.choices = [(nv.id, nv.ten) for nv in db.session.scalars(stmt_nv).all()]
    
    # Thêm lựa chọn placeholder nếu không có nhân viên nào
    if not form.id_nhanvien.choices:
        flash('Không có Nhân viên nào chưa có tài khoản để tạo.', 'warning')
        return redirect(url_for('admin_ui.taikhoan_list'))

    # Bắt buộc nhập mật khẩu khi tạo mới
    form.password.validators = [DataRequired(), EqualTo('confirm', message='Mật khẩu không khớp')]
    form.confirm.validators = [DataRequired()]

    if form.validate_on_submit():
        tk = TaiKhoan(
            username=form.username.data,
            id_nhanvien=form.id_nhanvien.data
        )
        # Hash và lưu mật khẩu
        tk.set_password(form.password.data)
        
        db.session.add(tk)
        db.session.commit()
        flash('Tạo tài khoản mới thành công.', 'success')
        return redirect(url_for('admin_ui.taikhoan_list'))
        
    return render_template('admin/taikhoan_form.html', form=form, action='create')

@admin_bp.route('/taikhoan/edit/<int:taikhoan_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def taikhoan_edit(taikhoan_id):
    """Chỉnh sửa Tài khoản."""
    # Lấy đối tượng TaiKhoan
    tk = db.get_or_404(TaiKhoan, taikhoan_id)
    
    # Khởi tạo form với dữ liệu hiện tại (trừ mật khẩu)
    form = TaiKhoanForm(obj=tk)
    
    # Bỏ buộc nhập mật khẩu khi chỉnh sửa (chỉ nhập khi muốn đổi)
    form.password.validators = [Optional(), EqualTo('confirm', message='Mật khẩu không khớp')]
    form.confirm.validators = [Optional()]
    
    # Lấy danh sách Nhân viên (bao gồm nhân viên hiện tại)
    # 1. Tìm ID Nhân viên đã có tài khoản (trừ nhân viên hiện tại)
    stmt_existing_nv = select(TaiKhoan.id_nhanvien).filter(TaiKhoan.id != taikhoan_id)
    existing_nv_ids = db.session.scalars(stmt_existing_nv).all()
    
    # 2. Lấy danh sách Nhân viên chưa có tài khoản + Nhân viên hiện tại
    stmt_nv = select(NhanVien).filter(NhanVien.id.not_in(existing_nv_ids)).order_by(NhanVien.ten)
    
    form.id_nhanvien.choices = [(nv.id, nv.ten) for nv in db.session.scalars(stmt_nv).all()]

    if request.method == 'GET':
        # Đặt giá trị mặc định cho SelectField
        form.id_nhanvien.data = tk.id_nhanvien
    
    if form.validate_on_submit():
        tk.username = form.username.data
        tk.id_nhanvien = form.id_nhanvien.data
        
        # Chỉ cập nhật mật khẩu nếu người dùng nhập mật khẩu mới
        if form.password.data:
            tk.set_password(form.password.data)
            
        db.session.commit()
        flash('Cập nhật tài khoản thành công.', 'success')
        return redirect(url_for('admin_ui.taikhoan_list'))
        
    return render_template('admin/taikhoan_form.html', form=form, action='edit', taikhoan=tk)

@admin_bp.route('/taikhoan/delete/<int:taikhoan_id>', methods=['POST'])
@login_required
@admin_required
def taikhoan_delete(taikhoan_id):
    """Xóa Tài khoản."""
    tk = db.get_or_404(TaiKhoan, taikhoan_id)
    db.session.delete(tk)
    db.session.commit()
    flash('Đã xóa tài khoản.', 'info')
    return redirect(url_for('admin_ui.taikhoan_list'))




# --------------------------------------------------------------------
# QUẢN LÝ NHÂN VIÊN (NhanVien)
# --------------------------------------------------------------------

class NhanVienForm(FlaskForm):
    ten = StringField('Tên Nhân Viên', validators=[DataRequired(), Length(max=255)])
    gioitinh = SelectField('Giới Tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')], validators=[Optional()])
    chucvu = StringField('Chức Vụ', validators=[DataRequired(), Length(max=100)])
    ngaysinh = DateField('Ngày Sinh (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    cccd = StringField('CCCD/CMND', validators=[DataRequired(), Length(max=20), 
                                                Regexp(r'^[0-9]+$', message='CCCD chỉ chứa chữ số')])
    sdt = StringField('Số Điện Thoại', validators=[Optional(), Length(max=15)])
    luong = DecimalField('Lương (VND)', validators=[Optional()], places=2)
    submit = SubmitField('Lưu')

from models import NhanVien

@admin_bp.route('/nhanvien')
@login_required
@admin_required
def nhanvien_list():
    """Hiển thị danh sách Nhân viên."""
    nhanviens = NhanVien.query.order_by(NhanVien.id).all()
    return render_template('admin/nhanvien_list.html', nhanviens=nhanviens)

@admin_bp.route('/nhanvien/create', methods=['GET', 'POST'])
@login_required
@admin_required
def nhanvien_create():
    """Tạo hồ sơ Nhân viên mới."""
    form = NhanVienForm()
    if form.validate_on_submit():
        # Kiểm tra tính duy nhất của CCCD
        if NhanVien.query.filter_by(cccd=form.cccd.data).first():
            flash('CCCD đã tồn tại trong hệ thống.', 'danger')
            return render_template('admin/nhanvien_form.html', form=form, action='create')
            
        nv = NhanVien(
            ten=form.ten.data,
            gioitinh=form.gioitinh.data,
            chucvu=form.chucvu.data,
            ngaysinh=form.ngaysinh.data,
            cccd=form.cccd.data,
            sdt=form.sdt.data,
            luong=form.luong.data
        )
        db.session.add(nv)
        db.session.commit()
        flash('Tạo hồ sơ nhân viên thành công.', 'success')
        return redirect(url_for('admin_ui.nhanvien_list'))
        
    return render_template('admin/nhanvien_form.html', form=form, action='create')

@admin_bp.route('/nhanvien/edit/<int:nv_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def nhanvien_edit(nv_id):
    """Chỉnh sửa hồ sơ Nhân viên."""
    nv = db.get_or_404(NhanVien, nv_id)
    form = NhanVienForm(obj=nv) # obj=nv điền sẵn dữ liệu cũ

    if form.validate_on_submit():
        # Kiểm tra CCCD duy nhất (loại trừ chính nhân viên đang sửa)
        if NhanVien.query.filter(NhanVien.cccd == form.cccd.data, NhanVien.id != nv_id).first():
            flash('CCCD đã tồn tại trong hệ thống cho nhân viên khác.', 'danger')
            return render_template('admin/nhanvien_form.html', form=form, action='edit', nhanvien=nv)

        nv.ten = form.ten.data
        nv.gioitinh = form.gioitinh.data
        nv.chucvu = form.chucvu.data
        nv.ngaysinh = form.ngaysinh.data
        nv.cccd = form.cccd.data
        nv.sdt = form.sdt.data
        nv.luong = form.luong.data
        
        db.session.commit()
        flash('Cập nhật hồ sơ nhân viên thành công.', 'success')
        return redirect(url_for('admin_ui.nhanvien_list'))
        
    return render_template('admin/nhanvien_form.html', form=form, action='edit', nhanvien=nv)

@admin_bp.route('/nhanvien/delete/<int:nv_id>', methods=['POST'])
@login_required
@admin_required
def nhanvien_delete(nv_id):
    """Xóa hồ sơ Nhân viên."""
    nv = db.get_or_404(NhanVien, nv_id)
    
    # Kỹ thuật: Kiểm tra nếu nhân viên có liên kết tài khoản/hóa đơn
    if nv.taikhoan or nv.hoadons:
        flash('Không thể xóa nhân viên này vì đang có Tài khoản hoặc Hóa đơn liên quan.', 'danger')
        return redirect(url_for('admin_ui.nhanvien_list'))
        
    db.session.delete(nv)
    db.session.commit()
    flash('Đã xóa hồ sơ nhân viên.', 'info')
    return redirect(url_for('admin_ui.nhanvien_list'))



from wtforms import DateField 
from wtforms.validators import Regexp 
from models import KhachHang 

class KhachHangForm(FlaskForm):
    hoten = StringField('Họ và Tên', validators=[DataRequired(), Length(max=255)])
    gioitinh = SelectField('Giới Tính', 
                           choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')], 
                           validators=[Optional()])
    ngaysinh = DateField('Ngày Sinh (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    diachi = StringField('Địa Chỉ', validators=[Optional(), Length(max=255)])
    sdt = StringField('Số Điện Thoại', validators=[Optional(), Length(max=15)])
    cccd = StringField('CCCD/CMND', 
                       validators=[DataRequired(), Length(max=20), 
                                   Regexp(r'^[0-9]+$', message='CCCD chỉ chứa chữ số')])
    ngaythue = DateField('Ngày Thuê (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Lưu')


# --------------------------------------------------------------------
# QUẢN LÝ KHÁCH HÀNG (KhachHang)
# --------------------------------------------------------------------

@admin_bp.route('/khachhang')
@login_required
@admin_required
def khachhang_list():
    """Hiển thị danh sách Khách hàng."""
    khachhangs = KhachHang.query.order_by(KhachHang.id).all()
    # Chú ý: Cần có template admin/khachhang_list.html
    return render_template('admin/khachhang_list.html', khachhangs=khachhangs)

@admin_bp.route('/khachhang/create', methods=['GET', 'POST'])
@login_required
@admin_required
def khachhang_create():
    """Tạo hồ sơ Khách hàng mới."""
    form = KhachHangForm()
    if form.validate_on_submit():
        # Kiểm tra tính duy nhất của CCCD
        if KhachHang.query.filter_by(cccd=form.cccd.data).first():
            flash('CCCD đã tồn tại trong hệ thống.', 'danger')
            return render_template('admin/khachhang_form.html', form=form, action='create')
            
        kh = KhachHang(
            hoten=form.hoten.data,
            gioitinh=form.gioitinh.data,
            ngaysinh=form.ngaysinh.data,
            diachi=form.diachi.data,
            sdt=form.sdt.data,
            cccd=form.cccd.data,
            ngaythue=form.ngaythue.data
        )
        db.session.add(kh)
        db.session.commit()
        flash('Tạo hồ sơ khách hàng thành công.', 'success')
        return redirect(url_for('admin_ui.khachhang_list'))
        
    return render_template('admin/khachhang_form.html', form=form, action='create')

@admin_bp.route('/khachhang/edit/<int:kh_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def khachhang_edit(kh_id):
    """Chỉnh sửa hồ sơ Khách hàng."""
    kh = db.get_or_404(KhachHang, kh_id)
    form = KhachHangForm(obj=kh) # obj=kh điền sẵn dữ liệu cũ

    if form.validate_on_submit():
        # Kiểm tra CCCD duy nhất (loại trừ chính khách hàng đang sửa)
        if KhachHang.query.filter(KhachHang.cccd == form.cccd.data, KhachHang.id != kh_id).first():
            flash('CCCD đã tồn tại trong hệ thống cho khách hàng khác.', 'danger')
            return render_template('admin/khachhang_form.html', form=form, action='edit', khachhang=kh)

        kh.hoten = form.hoten.data
        kh.gioitinh = form.gioitinh.data
        kh.ngaysinh = form.ngaysinh.data
        kh.diachi = form.diachi.data
        kh.sdt = form.sdt.data
        kh.cccd = form.cccd.data
        kh.ngaythue = form.ngaythue.data
        
        db.session.commit()
        flash('Cập nhật hồ sơ khách hàng thành công.', 'success')
        return redirect(url_for('admin_ui.khachhang_list'))
        
    return render_template('admin/khachhang_form.html', form=form, action='edit', khachhang=kh)

@admin_bp.route('/khachhang/delete/<int:kh_id>', methods=['POST'])
@login_required
@admin_required
def khachhang_delete(kh_id):
    """Xóa hồ sơ Khách hàng."""
    kh = db.get_or_404(KhachHang, kh_id)
    
    # Kiểm tra nếu khách hàng có liên kết hóa đơn
    if kh.hoadons:
        flash('Không thể xóa khách hàng này vì đang có Hóa đơn liên quan.', 'danger')
        return redirect(url_for('admin_ui.khachhang_list'))
        
    db.session.delete(kh)
    db.session.commit()
    flash('Đã xóa hồ sơ khách hàng.', 'info')
    return redirect(url_for('admin_ui.khachhang_list'))


class LoaiPhongForm(FlaskForm):
    ten = StringField('Tên Loại Phòng', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Lưu')

# --------------------------------------------------------------------
# QUẢN LÝ LOẠI PHÒNG (LoaiPhong)
# --------------------------------------------------------------------

@admin_bp.route('/loaiphong')
@login_required
@admin_required
def loaiphong_list():
    """Hiển thị danh sách Loại phòng."""
    loaiphongs = LoaiPhong.query.order_by(LoaiPhong.id).all()
    # Chú ý: Cần có template admin/loaiphong_list.html
    return render_template('admin/loaiphong_list.html', loaiphongs=loaiphongs)

@admin_bp.route('/loaiphong/create', methods=['GET', 'POST'])
@login_required
@admin_required
def loaiphong_create():
    """Tạo Loại phòng mới."""
    form = LoaiPhongForm()
    if form.validate_on_submit():
        # Kiểm tra Tên Loại Phòng duy nhất
        if LoaiPhong.query.filter_by(ten=form.ten.data).first():
            flash('Tên loại phòng này đã tồn tại.', 'danger')
            return render_template('admin/loaiphong_form.html', form=form, action='create')
            
        lp = LoaiPhong(
            ten=form.ten.data
        )
        db.session.add(lp)
        db.session.commit()
        flash('Tạo loại phòng mới thành công.', 'success')
        return redirect(url_for('admin_ui.loaiphong_list'))
        
    return render_template('admin/loaiphong_form.html', form=form, action='create')

@admin_bp.route('/loaiphong/edit/<int:lp_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def loaiphong_edit(lp_id):
    """Chỉnh sửa Loại phòng."""
    lp = db.get_or_404(LoaiPhong, lp_id)
    form = LoaiPhongForm(obj=lp) # obj=lp điền sẵn dữ liệu cũ

    if form.validate_on_submit():
        # Kiểm tra Tên Loại Phòng duy nhất (loại trừ chính đối tượng đang sửa)
        if LoaiPhong.query.filter(LoaiPhong.ten == form.ten.data, LoaiPhong.id != lp_id).first():
            flash('Tên loại phòng này đã tồn tại cho loại phòng khác.', 'danger')
            return render_template('admin/loaiphong_form.html', form=form, action='edit', loaiphong=lp)

        lp.ten = form.ten.data
        
        db.session.commit()
        flash('Cập nhật loại phòng thành công.', 'success')
        return redirect(url_for('admin_ui.loaiphong_list'))
        
    return render_template('admin/loaiphong_form.html', form=form, action='edit', loaiphong=lp)

@admin_bp.route('/loaiphong/delete/<int:lp_id>', methods=['POST'])
@login_required
@admin_required
def loaiphong_delete(lp_id):
    """Xóa Loại phòng."""
    lp = db.get_or_404(LoaiPhong, lp_id)
    
    # Kiểm tra liên kết: Nếu loại phòng đang được sử dụng bởi bất kỳ phòng nào
    if lp.phongs:
        flash(f'Không thể xóa loại phòng "{lp.ten}" vì có {len(lp.phongs)} phòng đang sử dụng loại này.', 'danger')
        return redirect(url_for('admin_ui.loaiphong_list'))
        
    db.session.delete(lp)
    db.session.commit()
    flash('Đã xóa loại phòng.', 'info')
    return redirect(url_for('admin_ui.loaiphong_list'))


class TangForm(FlaskForm):
    ten = StringField('Tên Tầng', validators=[DataRequired(), Length(max=100)])
    # mota đã được loại bỏ
    submit = SubmitField('Lưu')

# --------------------------------------------------------------------
# QUẢN LÝ TẦNG (Tang) - Đã sửa lỗi: Loại bỏ 'mota'
# --------------------------------------------------------------------

@admin_bp.route('/tang')
@login_required
@admin_required
def tang_list():
    """Hiển thị danh sách Tầng."""
    tangs = Tang.query.order_by(Tang.id).all()
    return render_template('admin/tang_list.html', tangs=tangs)

@admin_bp.route('/tang/create', methods=['GET', 'POST'])
@login_required
@admin_required
def tang_create():
    """Tạo Tầng mới."""
    form = TangForm()
    if form.validate_on_submit():
        # Kiểm tra Tên Tầng duy nhất
        if Tang.query.filter_by(ten=form.ten.data).first():
            flash('Tên tầng này đã tồn tại.', 'danger')
            return render_template('admin/tang_form.html', form=form, action='create')
            
        t = Tang(
            ten=form.ten.data,
            # Loại bỏ mota: không truyền vào hàm khởi tạo
        )
        db.session.add(t)
        db.session.commit()
        flash('Tạo tầng mới thành công.', 'success')
        return redirect(url_for('admin_ui.tang_list'))
        
    return render_template('admin/tang_form.html', form=form, action='create')

@admin_bp.route('/tang/edit/<int:t_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def tang_edit(t_id):
    """Chỉnh sửa Tầng."""
    t = db.get_or_404(Tang, t_id)
    form = TangForm(obj=t)

    if form.validate_on_submit():
        # Kiểm tra Tên Tầng duy nhất
        if Tang.query.filter(Tang.ten == form.ten.data, Tang.id != t_id).first():
            flash('Tên tầng này đã tồn tại cho tầng khác.', 'danger')
            return render_template('admin/tang_form.html', form=form, action='edit', tang=t)

        t.ten = form.ten.data
        # Loại bỏ mota: không gán giá trị
        
        db.session.commit()
        flash('Cập nhật tầng thành công.', 'success')
        return redirect(url_for('admin_ui.tang_list'))
        
    return render_template('admin/tang_form.html', form=form, action='edit', tang=t)

@admin_bp.route('/tang/delete/<int:t_id>', methods=['POST'])
@login_required
@admin_required
def tang_delete(t_id):
    """Xóa Tầng."""
    t = db.get_or_404(Tang, t_id)
    
    # Kiểm tra liên kết
    if t.phongs:
        flash(f'Không thể xóa tầng "{t.ten}" vì có {len(t.phongs)} phòng đang ở tầng này.', 'danger')
        return redirect(url_for('admin_ui.tang_list'))
        
    db.session.delete(t)
    db.session.commit()
    flash('Đã xóa tầng.', 'info')
    return redirect(url_for('admin_ui.tang_list'))


from wtforms import DecimalField, SelectField 
from models import LoaiPhong, Phong 
from models import db, Phong, LoaiPhong, Tang, TaiKhoan, NhanVien, KhachHang, DichVu, DV_HDCT
from models import (
    db, 
    Phong, 
    LoaiPhong, 
    Tang, 
    TaiKhoan, 
    NhanVien, 
    KhachHang, 
    DichVu, 
    ThietBi, 
    HoaDon, 
    HoaDonCT,    
    DV_HDCT      
)

class DichVuForm(FlaskForm):
    ten = StringField('Tên Dịch Vụ', validators=[DataRequired(), Length(max=255)])
    
    # Sửa: Dùng 'gia' thay cho 'dongia'
    gia = DecimalField('Giá Dịch Vụ (VND)', validators=[DataRequired()], places=2)
    
    # Thêm khóa ngoại
    id_loaiphong = SelectField('Loại Phòng', coerce=int, validators=[Optional()])
    id_phong = SelectField('Phòng (Cụ thể)', coerce=int, validators=[Optional()])
    
    submit = SubmitField('Lưu')

# --------------------------------------------------------------------
# QUẢN LÝ DỊCH VỤ (DichVu) 
# --------------------------------------------------------------------

@admin_bp.route('/dichvu')
@login_required
@admin_required
def dichvu_list():
    """Hiển thị danh sách Dịch vụ."""
    dichvus = DichVu.query.order_by(DichVu.id).all()
    return render_template('admin/dichvu_list.html', dichvus=dichvus)

@admin_bp.route('/dichvu/create', methods=['GET', 'POST'])
@login_required
@admin_required
def dichvu_create():
    """Tạo Dịch vụ mới."""
    form = DichVuForm()
    
    # Nạp danh sách cho SelectField
    form.id_loaiphong.choices = [(0, '--- Không áp dụng ---')] + [(lp.id, lp.ten) for lp in LoaiPhong.query.all()]
    form.id_phong.choices = [(0, '--- Không áp dụng ---')] + [(p.id, p.ten) for p in Phong.query.all()]

    if form.validate_on_submit():
        if DichVu.query.filter_by(ten=form.ten.data).first():
            flash('Tên dịch vụ này đã tồn tại.', 'danger')
            return render_template('admin/dichvu_form.html', form=form, action='create')
            
        dv = DichVu(
            ten=form.ten.data,
            gia=form.gia.data, # Sửa: Dùng 'gia'
            # Gán khóa ngoại (dùng None nếu người dùng chọn 'Không áp dụng' (ID=0))
            id_loaiphong=form.id_loaiphong.data if form.id_loaiphong.data != 0 else None, 
            id_phong=form.id_phong.data if form.id_phong.data != 0 else None
        )
        db.session.add(dv)
        db.session.commit()
        flash('Tạo dịch vụ mới thành công.', 'success')
        return redirect(url_for('admin_ui.dichvu_list'))
        
    return render_template('admin/dichvu_form.html', form=form, action='create')

@admin_bp.route('/dichvu/edit/<int:dv_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def dichvu_edit(dv_id):
    """Chỉnh sửa Dịch vụ."""
    dv = db.get_or_404(DichVu, dv_id)
    form = DichVuForm(obj=dv)

    # Nạp danh sách cho SelectField
    form.id_loaiphong.choices = [(0, '--- Không áp dụng ---')] + [(lp.id, lp.ten) for lp in LoaiPhong.query.all()]
    form.id_phong.choices = [(0, '--- Không áp dụng ---')] + [(p.id, p.ten) for p in Phong.query.all()]

    if request.method == 'GET':
        # Đặt giá trị mặc định cho SelectField khi GET
        form.id_loaiphong.data = dv.id_loaiphong or 0
        form.id_phong.data = dv.id_phong or 0

    if form.validate_on_submit():
        if DichVu.query.filter(DichVu.ten == form.ten.data, DichVu.id != dv_id).first():
            flash('Tên dịch vụ này đã tồn tại cho dịch vụ khác.', 'danger')
            return render_template('admin/dichvu_form.html', form=form, action='edit', dichvu=dv)

        dv.ten = form.ten.data
        dv.gia = form.gia.data # Sửa: Dùng 'gia'
        dv.id_loaiphong = form.id_loaiphong.data if form.id_loaiphong.data != 0 else None
        dv.id_phong = form.id_phong.data if form.id_phong.data != 0 else None
        
        db.session.commit()
        flash('Cập nhật dịch vụ thành công.', 'success')
        return redirect(url_for('admin_ui.dichvu_list'))
        
    return render_template('admin/dichvu_form.html', form=form, action='edit', dichvu=dv)

@admin_bp.route('/dichvu/delete/<int:dv_id>', methods=['POST'])
@login_required
@admin_required
def dichvu_delete(dv_id):
    """Xóa Dịch vụ."""
    dv = db.get_or_404(DichVu, dv_id)
    
    # Kiểm tra liên kết: Nếu dịch vụ đang được sử dụng trong bất kỳ DV_HDCT nào
    if dv.dv_hdcts: 
        flash(f'Không thể xóa dịch vụ "{dv.ten}" vì đang có hóa đơn chi tiết sử dụng dịch vụ này.', 'danger')
        return redirect(url_for('admin_ui.dichvu_list'))
        
    db.session.delete(dv)
    db.session.commit()
    flash('Đã xóa dịch vụ.', 'info')
    return redirect(url_for('admin_ui.dichvu_list'))


from wtforms import StringField, DecimalField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from models import ThietBi, LoaiPhong, Phong # Đảm bảo đã import

class ThietBiForm(FlaskForm):
    ten = StringField('Tên Thiết Bị', validators=[DataRequired(), Length(max=255)])
    
    # Dùng 'gia' thay vì 'dongia'
    gia = DecimalField('Giá Thiết Bị (VND)', validators=[Optional()], places=2)
    
    trangthai = StringField('Trạng Thái', validators=[Optional(), Length(max=50)])
    
    # Khóa ngoại
    id_loaiphong = SelectField('Loại Phòng', coerce=int, validators=[Optional()])
    id_phong = SelectField('Phòng (Cụ thể)', coerce=int, validators=[Optional()])
    
    submit = SubmitField('Lưu')

# --------------------------------------------------------------------
# QUẢN LÝ THIẾT BỊ (ThietBi)
# --------------------------------------------------------------------

@admin_bp.route('/thietbi')
@login_required
@admin_required
def thietbi_list():
    """Hiển thị danh sách Thiết bị."""
    thietbis = ThietBi.query.order_by(ThietBi.id).all()
    # Chú ý: Cần có template admin/thietbi_list.html
    return render_template('admin/thietbi_list.html', thietbis=thietbis)

@admin_bp.route('/thietbi/create', methods=['GET', 'POST'])
@login_required
@admin_required
def thietbi_create():
    """Tạo Thiết bị mới."""
    form = ThietBiForm()
    
    # Nạp danh sách cho SelectField (ID=0 là giá trị 'Không áp dụng')
    form.id_loaiphong.choices = [(0, '--- Không áp dụng ---')] + [(lp.id, lp.ten) for lp in LoaiPhong.query.all()]
    form.id_phong.choices = [(0, '--- Không áp dụng ---')] + [(p.id, p.ten) for p in Phong.query.all()]

    if form.validate_on_submit():
        # Kiểm tra Tên Thiết Bị duy nhất (tùy chọn, nên kiểm tra nếu thiết bị là duy nhất)
        # if ThietBi.query.filter_by(ten=form.ten.data).first():
        #     flash('Tên thiết bị này đã tồn tại.', 'danger')
        #     return render_template('admin/thietbi_form.html', form=form, action='create')
            
        tb = ThietBi(
            ten=form.ten.data,
            gia=form.gia.data,
            trangthai=form.trangthai.data,
            # Gán khóa ngoại (dùng None nếu người dùng chọn 'Không áp dụng' (ID=0))
            id_loaiphong=form.id_loaiphong.data if form.id_loaiphong.data != 0 else None, 
            id_phong=form.id_phong.data if form.id_phong.data != 0 else None
        )
        db.session.add(tb)
        db.session.commit()
        flash('Tạo thiết bị mới thành công.', 'success')
        return redirect(url_for('admin_ui.thietbi_list'))
        
    return render_template('admin/thietbi_form.html', form=form, action='create')

@admin_bp.route('/thietbi/edit/<int:tb_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def thietbi_edit(tb_id):
    """Chỉnh sửa Thiết bị."""
    tb = db.get_or_404(ThietBi, tb_id)
    form = ThietBiForm(obj=tb)

    # Nạp danh sách cho SelectField
    form.id_loaiphong.choices = [(0, '--- Không áp dụng ---')] + [(lp.id, lp.ten) for lp in LoaiPhong.query.all()]
    form.id_phong.choices = [(0, '--- Không áp dụng ---')] + [(p.id, p.ten) for p in Phong.query.all()]

    if request.method == 'GET':
        # Đặt giá trị mặc định cho SelectField khi GET
        form.id_loaiphong.data = tb.id_loaiphong or 0
        form.id_phong.data = tb.id_phong or 0

    if form.validate_on_submit():
        # Kiểm tra Tên Thiết Bị duy nhất (tùy chọn)
        # if ThietBi.query.filter(ThietBi.ten == form.ten.data, ThietBi.id != tb_id).first():
        #     flash('Tên thiết bị này đã tồn tại cho thiết bị khác.', 'danger')
        #     return render_template('admin/thietbi_form.html', form=form, action='edit', thietbi=tb)

        tb.ten = form.ten.data
        tb.gia = form.gia.data
        tb.trangthai = form.trangthai.data
        tb.id_loaiphong = form.id_loaiphong.data if form.id_loaiphong.data != 0 else None
        tb.id_phong = form.id_phong.data if form.id_phong.data != 0 else None
        
        db.session.commit()
        flash('Cập nhật thiết bị thành công.', 'success')
        return redirect(url_for('admin_ui.thietbi_list'))
        
    return render_template('admin/thietbi_form.html', form=form, action='edit', thietbi=tb)

@admin_bp.route('/thietbi/delete/<int:tb_id>', methods=['POST'])
@login_required
@admin_required
def thietbi_delete(tb_id):
    """Xóa Thiết bị."""
    tb = db.get_or_404(ThietBi, tb_id)
    
    # Thiết bị thường không có khóa ngoại ngược, nên không cần kiểm tra liên kết phức tạp.
    
    db.session.delete(tb)
    db.session.commit()
    flash('Đã xóa thiết bị.', 'info')
    return redirect(url_for('admin_ui.thietbi_list'))


#xử lý hóa đơn
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from wtforms import IntegerField, DecimalField, DateField
from models import HoaDon, NhanVien, KhachHang

class HoaDonForm(FlaskForm):
    soluong = IntegerField('Số Lượng Dịch Vụ/Phòng', validators=[DataRequired(), NumberRange(min=0)])
    tongtien = DecimalField('Tổng Tiền (VND)', validators=[DataRequired()], places=2)
    ngaythanhtoan = DateField('Ngày Thanh Toán (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    
    # Khóa ngoại
    id_nhanvien = SelectField('Nhân Viên Lập', coerce=int, validators=[DataRequired()])
    id_khachhang = SelectField('Khách Hàng', coerce=int, validators=[DataRequired()])
    
    submit = SubmitField('Lưu')

# --------------------------------------------------------------------
# QUẢN LÝ HÓA ĐƠN (HoaDon)
# --------------------------------------------------------------------

@admin_bp.route('/hoadon')
@login_required
@admin_required
def hoadon_list():
    """Hiển thị danh sách Hóa đơn."""
    hoadons = HoaDon.query.order_by(HoaDon.id.desc()).all()
    return render_template('admin/hoadon_list.html', hoadons=hoadons)

@admin_bp.route('/hoadon/create', methods=['GET', 'POST'])
@login_required
@admin_required
def hoadon_create():
    """Tạo Hóa đơn mới."""
    form = HoaDonForm()
    
    # Nạp danh sách cho SelectField
    form.id_nhanvien.choices = [(nv.id, nv.ten) for nv in NhanVien.query.all()]
    form.id_khachhang.choices = [(kh.id, kh.hoten) for kh in KhachHang.query.all()]

    if form.validate_on_submit():
        hd = HoaDon(
            soluong=form.soluong.data,
            tongtien=form.tongtien.data,
            ngaythanhtoan=form.ngaythanhtoan.data,
            id_nhanvien=form.id_nhanvien.data, 
            id_khachhang=form.id_khachhang.data
        )
        db.session.add(hd)
        db.session.commit()
        flash('Tạo hóa đơn thành công. Thêm chi tiết hóa đơn ngay bây giờ!', 'success')
        # Chuyển hướng đến trang chỉnh sửa hóa đơn để thêm chi tiết
        return redirect(url_for('admin_ui.hoadon_edit', hd_id=hd.id)) 
        
    return render_template('admin/hoadon_form.html', form=form, action='create')

@admin_bp.route('/hoadon/edit/<int:hd_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def hoadon_edit(hd_id):
    """Chỉnh sửa Hóa đơn và Chi tiết."""
    hd = db.get_or_404(HoaDon, hd_id)
    form = HoaDonForm(obj=hd)

    form.id_nhanvien.choices = [(nv.id, nv.ten) for nv in NhanVien.query.all()]
    form.id_khachhang.choices = [(kh.id, kh.hoten) for kh in KhachHang.query.all()]

    if request.method == 'GET':
        form.id_nhanvien.data = hd.id_nhanvien
        form.id_khachhang.data = hd.id_khachhang

    if form.validate_on_submit():
        hd.soluong = form.soluong.data
        hd.tongtien = form.tongtien.data
        hd.ngaythanhtoan = form.ngaythanhtoan.data
        hd.id_nhanvien = form.id_nhanvien.data
        hd.id_khachhang = form.id_khachhang.data
        
        db.session.commit()
        flash('Cập nhật hóa đơn thành công.', 'success')
        return redirect(url_for('admin_ui.hoadon_list'))
        
    return render_template('admin/hoadon_form.html', form=form, action='edit', hoadon=hd)

@admin_bp.route('/hoadon/delete/<int:hd_id>', methods=['POST'])
@login_required
@admin_required
def hoadon_delete(hd_id):
    """Xóa Hóa đơn."""
    hd = db.get_or_404(HoaDon, hd_id)
    
    # Xóa tất cả HoaDonCT và DV_HDCT liên quan trước
    for hdct in hd.hoadoncts:
        for dv_hdct in hdct.dv_hdcts:
            db.session.delete(dv_hdct)
        db.session.delete(hdct)
        
    db.session.delete(hd)
    db.session.commit()
    flash('Đã xóa hóa đơn và tất cả chi tiết liên quan.', 'info')
    return redirect(url_for('admin_ui.hoadon_list'))

# form hoa don chi tiet
from wtforms import DateTimeField
from models import Phong
from datetime import datetime

class HoaDonCTForm(FlaskForm):
    tenphong = StringField('Tên Phòng', validators=[Optional(), Length(max=255)])
    tenkhachhang = StringField('Tên Khách Hàng', validators=[Optional(), Length(max=255)])
    nhanvienlap = StringField('Nhân Viên Lập', validators=[Optional(), Length(max=255)])
    
    # Lưu ý: DateTimeField cần dữ liệu dạng datetime object, không phải string date
    ngay_checkin = DateField('Ngày Check-In (YYYY-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])
    gio_checkin = StringField('Giờ Check-In (HH:MM)', validators=[Optional()]) 
    
    ngay_checkout = DateField('Ngày Check-Out (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    gioc_checkout = StringField('Giờ Check-Out (HH:MM)', validators=[Optional()])
    
    # Khóa ngoại
    id_phong = SelectField('Phòng Thuê', coerce=int, validators=[DataRequired()]) 
    
    submit = SubmitField('Lưu Chi Tiết')

# --------------------------------------------------------------------
# QUẢN LÝ CHI TIẾT HÓA ĐƠN (HoaDonCT)
# --------------------------------------------------------------------

@admin_bp.route('/hoadon/<int:hd_id>/ct/create', methods=['GET', 'POST'])
@login_required
@admin_required
def hoadonct_create(hd_id):
    """Thêm Chi tiết Hóa đơn (Phòng) vào Hóa đơn."""
    hd = db.get_or_404(HoaDon, hd_id)
    form = HoaDonCTForm()
    
    form.id_phong.choices = [(p.id, p.ten) for p in Phong.query.all()]

    if form.validate_on_submit():
        # Kết hợp ngày và giờ (để tạo datetime object, dù mô hình DB là DateTime)
        checkin_dt_str = f"{form.ngay_checkin.data} {form.gio_checkin.data or '00:00'}"
        checkin_dt = datetime.strptime(checkin_dt_str, '%Y-%m-%d %H:%M')
        
        checkout_dt = None
        if form.ngay_checkout.data:
            checkout_dt_str = f"{form.ngay_checkout.data} {form.gioc_checkout.data or '00:00'}"
            checkout_dt = datetime.strptime(checkout_dt_str, '%Y-%m-%d %H:%M')
        
        ct = HoaDonCT(
            tenphong=form.tenphong.data,
            tenkhachhang=form.tenkhachhang.data,
            nhanvienlap=form.nhanvienlap.data,
            ngay_checkin=checkin_dt,
            gio_checkin=checkin_dt, # Lưu lại datetime object
            ngay_checkout=checkout_dt,
            gioc_checkout=checkout_dt, # Lưu lại datetime object
            id_hoadon=hd_id,
            id_phong=form.id_phong.data
        )
        db.session.add(ct)
        db.session.commit()
        flash(f'Đã thêm chi tiết phòng "{ct.tenphong}" vào hóa đơn.', 'success')
        return redirect(url_for('admin_ui.hoadon_edit', hd_id=hd_id))
        
    return render_template('admin/hoadonct_form.html', form=form, action='create', hoadon=hd)

@admin_bp.route('/hoadonct/edit/<int:ct_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def hoadonct_edit(ct_id):
    """Chỉnh sửa Chi tiết Hóa đơn."""
    ct = db.get_or_404(HoaDonCT, ct_id)
    
    # Khởi tạo form với dữ liệu cũ
    # Ta phải tách datetime thành date và time string để form hiển thị đúng
    initial_data = {
        'ngay_checkin': ct.ngay_checkin.date() if ct.ngay_checkin else None,
        'gio_checkin': ct.gio_checkin.strftime('%H:%M') if ct.gio_checkin else '',
        'ngay_checkout': ct.ngay_checkout.date() if ct.ngay_checkout else None,
        'gioc_checkout': ct.gioc_checkout.strftime('%H:%M') if ct.gioc_checkout else '',
    }
    form = HoaDonCTForm(obj=ct, **initial_data)
    form.id_phong.choices = [(p.id, p.ten) for p in Phong.query.all()]

    if form.validate_on_submit():
        checkin_dt_str = f"{form.ngay_checkin.data} {form.gio_checkin.data or '00:00'}"
        ct.ngay_checkin = datetime.strptime(checkin_dt_str, '%Y-%m-%d %H:%M')
        ct.gio_checkin = ct.ngay_checkin # Cập nhật lại gio_checkin
        
        if form.ngay_checkout.data:
            checkout_dt_str = f"{form.ngay_checkout.data} {form.gioc_checkout.data or '00:00'}"
            ct.ngay_checkout = datetime.strptime(checkout_dt_str, '%Y-%m-%d %H:%M')
            ct.gioc_checkout = ct.ngay_checkout # Cập nhật lại gioc_checkout
        else:
            ct.ngay_checkout = None
            ct.gioc_checkout = None

        ct.tenphong = form.tenphong.data
        ct.tenkhachhang = form.tenkhachhang.data
        ct.nhanvienlap = form.nhanvienlap.data
        ct.id_phong = form.id_phong.data
        
        db.session.commit()
        flash('Cập nhật chi tiết hóa đơn thành công.', 'success')
        return redirect(url_for('admin_ui.hoadon_edit', hd_id=ct.id_hoadon))
        
    return render_template('admin/hoadonct_form.html', form=form, action='edit', hoadonct=ct)

@admin_bp.route('/hoadonct/delete/<int:ct_id>', methods=['POST'])
@login_required
@admin_required
def hoadonct_delete(ct_id):
    """Xóa Chi tiết Hóa đơn."""
    ct = db.get_or_404(HoaDonCT, ct_id)
    hd_id = ct.id_hoadon
    
    # Xóa tất cả DV_HDCT liên quan trước
    for dv_hdct in ct.dv_hdcts:
        db.session.delete(dv_hdct)
        
    db.session.delete(ct)
    db.session.commit()
    flash('Đã xóa chi tiết hóa đơn.', 'info')
    return redirect(url_for('admin_ui.hoadon_edit', hd_id=hd_id))