```markdown
# Khách sạn - Trang quản lý (Flask + Flask-Admin)

Mô tả nhanh:
- Giao diện quản trị CRUD cho các bảng chính của database `khachsan`.
- Dùng Flask, SQLAlchemy, Flask-Admin để dựng nhanh các trang quản lý.

Yêu cầu:
- Python 3.8+
- MySQL/MariaDB (ở ví dụ dùng host 127.0.0.1:3307)
- Cài dependencies:
  pip install -r requirements.txt

Cấu hình:
- Mở file app.py và sửa chuỗi kết nối:
  app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@127.0.0.1:3307/khachsan'

Khởi tạo và seed dữ liệu mẫu:
- Tạo database `khachsan` (nếu chưa có) trong MySQL.
- Chạy: python3 seed.py

Chạy ứng dụng:
- python3 app.py
- Mở trình duyệt: http://127.0.0.1:5000/admin/

Gợi ý mở rộng:
- Thêm authentication/role-based access (Flask-Login + roles).
- Tùy chỉnh ModelView để ẩn cột mật khẩu, và biểu mẫu lưu mật khẩu bằng hash.
- Thêm báo cáo (doanh thu theo ngày), export CSV, filter, etc.
```