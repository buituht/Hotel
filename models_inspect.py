# Run: python models_inspect.py
from models import db, LoaiPhong, Tang, NhanVien, KhachHang, Phong, TaiKhoan, DichVu, ThietBi, HoaDon, HoaDonCT, DV_HDCT
models = [LoaiPhong, Tang, NhanVien, KhachHang, Phong, TaiKhoan, DichVu, ThietBi, HoaDon, HoaDonCT, DV_HDCT]
for m in models:
    name = getattr(m, '__name__', str(m))
    try:
        mapper_cols = [p.key for p in m.__mapper__.column_attrs]
    except Exception as e:
        mapper_cols = None
    try:
        table_cols = [c.name for c in getattr(m, '__table__').columns] if getattr(m, '__table__', None) is not None else None
    except Exception as e:
        table_cols = None
    print(f"Model: {name}")
    print("  mapper column attrs:", mapper_cols)
    print("  table column names :", table_cols)
    print("  dir sample:", [a for a in dir(m) if not a.startswith('_')][:30])
    print("----")