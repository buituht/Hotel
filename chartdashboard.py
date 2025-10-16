import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import base64
# import model tầng
from models import Tang, db 
from flask import current_app # Cần thiết để lấy ngữ cảnh ứng dụng

def create_floor_chart():
    # SỬ DỤNG BLOC TRY...EXCEPT CÓ GẮN NGỮ CẢNH
    try:
        # Bắt buộc: Truy vấn DB phải nằm trong ngữ cảnh ứng dụng
        with current_app.app_context():
            # 1. Lấy dữ liệu từ DB
            tangs = Tang.query.all()
            labels = [t.ten for t in tangs]
            sizes = [len(t.phongs) for t in tangs]
        
        # Xử lý dữ liệu mẫu nếu DB trống (Nằm ngoài khối with app_context)
        if not labels:
            print("INFO: Database không có dữ liệu Tầng. Dùng dữ liệu mẫu.")
            labels = ['Mẫu A', 'Mẫu B', 'Mẫu C']
            sizes = [10, 5, 8]
        
        # 2. Tạo Biểu Đồ Matplotlib
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(labels, sizes, color=['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e'])
        
        ax.set_title('Số Lượng Phòng Theo Tầng')
        ax.set_ylabel('Số Lượng Phòng')
        ax.set_xlabel('Tên Tầng')
        
        plt.tight_layout()
        
        # 3. Lưu và Mã hóa
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True) 
        plt.close(fig) 
        
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return data

    except Exception as e:
        # Lỗi sẽ được in ra console
        import traceback
        print("--------------------------------------------------")
        print("LỖI GỠ LỖI BIỂU ĐỒ MATPLOTLIB:")
        print(traceback.format_exc())
        print("--------------------------------------------------")
        return None