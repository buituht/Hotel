from flask import redirect, url_for, request
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

# Lớp kiểm tra quyền (giữ nguyên logic is_admin của bạn)
class AuthModelView(ModelView):
    def is_accessible(self):
        try:
            return current_user.is_authenticated and current_user.is_admin
        except Exception:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

# SafeModelView loại trừ các attribute relationship/phức tạp khỏi form tự động
class SafeModelView(AuthModelView):
    # Các tên attribute này là tên thuộc tính Python trong model (không phải tên cột DB).
    # Nếu model của bạn có tên khác (ví dụ 'hoadons' thay vì 'hoadons'), hãy chỉnh ở đây.
    form_excluded_columns = (
        # chung
        'phongs', 'dichvus', 'thietbis', 'taikhoan', 'hoadons',
        'hoadoncts', 'dv_hdcts', 'phongs',
        # specific names used in models.py — giữ để an toàn
        'phongs', 'dichvus', 'thietbis', 'taikhoan',
        'hoadons', 'hoadoncts', 'dv_hdcts', 'phong', 'nhanvien'
    )