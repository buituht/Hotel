-- khachsan_import.sql
-- Import-ready SQL for database `khachsan`
-- Adds CREATE DATABASE, DROP TABLE IF EXISTS, AUTO_INCREMENT and some sample seed data.

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE DATABASE IF NOT EXISTS `khachsan` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `khachsan`;

SET FOREIGN_KEY_CHECKS = 0;

-- Drop tables if they exist (reverse dependency order)
DROP TABLE IF EXISTS `dv_hdct`;
DROP TABLE IF EXISTS `dichvu`;
DROP TABLE IF EXISTS `hoadonct`;
DROP TABLE IF EXISTS `hoadon`;
DROP TABLE IF EXISTS `thietbi`;
DROP TABLE IF EXISTS `phong`;
DROP TABLE IF EXISTS `taikhoan`;
DROP TABLE IF EXISTS `nhanvien`;
DROP TABLE IF EXISTS `khachhang`;
DROP TABLE IF EXISTS `loaiphong`;
DROP TABLE IF EXISTS `tang`;

-- Table: loaiphong
CREATE TABLE `loaiphong` (
  `ID_LoaiPhong` int(11) NOT NULL AUTO_INCREMENT,
  `TenLoaiPhong` varchar(255) NOT NULL,
  PRIMARY KEY (`ID_LoaiPhong`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table: tang
CREATE TABLE `tang` (
  `ID_Tang` int(11) NOT NULL AUTO_INCREMENT,
  `TenTang` varchar(255) NOT NULL,
  PRIMARY KEY (`ID_Tang`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table: nhanvien
CREATE TABLE `nhanvien` (
  `IDNhanVien` int(11) NOT NULL AUTO_INCREMENT,
  `TenNhanVien` varchar(255) NOT NULL,
  `GioiTinh` varchar(10) DEFAULT NULL,
  `ChucVu` varchar(100) DEFAULT NULL,
  `NgaySinh` date DEFAULT NULL,
  `Cccd` varchar(20) DEFAULT NULL,
  `SDT` varchar(15) DEFAULT NULL,
  `Luong` decimal(12,2) DEFAULT NULL,
  PRIMARY KEY (`IDNhanVien`),
  UNIQUE KEY `TenNhanVien` (`TenNhanVien`),
  UNIQUE KEY `Cccd` (`Cccd`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table: khachhang
CREATE TABLE `khachhang` (
  `IDKhachHang` int(11) NOT NULL AUTO_INCREMENT,
  `HoTen` varchar(255) NOT NULL,
  `GioiTinh` varchar(10) DEFAULT NULL,
  `NgaySinh` date DEFAULT NULL,
  `DiaChi` varchar(255) DEFAULT NULL,
  `SoDienThoai` varchar(15) DEFAULT NULL,
  `CCCD` varchar(20) DEFAULT NULL,
  `NgayThue` date DEFAULT NULL,
  PRIMARY KEY (`IDKhachHang`),
  UNIQUE KEY `CCCD` (`CCCD`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table: phong
CREATE TABLE `phong` (
  `ID_Phong` int(11) NOT NULL AUTO_INCREMENT,
  `TenPhong` varchar(255) NOT NULL,
  `DonGia` decimal(10,2) NOT NULL,
  `TinhTrang` varchar(50) DEFAULT NULL,
  `ID_LoaiPhong` int(11) NOT NULL,
  `ID_Tang` int(11) NOT NULL,
  PRIMARY KEY (`ID_Phong`),
  KEY `ID_LoaiPhong` (`ID_LoaiPhong`),
  KEY `ID_Tang` (`ID_Tang`),
  CONSTRAINT `phong_ibfk_1` FOREIGN KEY (`ID_LoaiPhong`) REFERENCES `loaiphong` (`ID_LoaiPhong`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `phong_ibfk_2` FOREIGN KEY (`ID_Tang`) REFERENCES `tang` (`ID_Tang`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table: taikhoan
CREATE TABLE `taikhoan` (
  `IDTaiKhoan` int(11) NOT NULL AUTO_INCREMENT,
  `TenDangNhap` varchar(100) NOT NULL,
  `MatKhau` varchar(255) NOT NULL,
  `IDNhanVien` int(11) NOT NULL,
  PRIMARY KEY (`IDTaiKhoan`),
  UNIQUE KEY `TenDangNhap` (`TenDangNhap`),
  UNIQUE KEY `IDNhanVien` (`IDNhanVien`),
  CONSTRAINT `taikhoan_ibfk_1` FOREIGN KEY (`IDNhanVien`) REFERENCES `nhanvien` (`IDNhanVien`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table: dichvu
CREATE TABLE `dichvu` (
  `ID_DichVu` int(11) NOT NULL AUTO_INCREMENT,
  `TenDichVu` varchar(255) NOT NULL,
  `GiaDichVu` decimal(10,2) NOT NULL,
  `ID_LoaiPhong` int(11) NOT NULL,
  `ID_Phong` int(11) NOT NULL,
  PRIMARY KEY (`ID_DichVu`),
  KEY `ID_Phong` (`ID_Phong`),
  KEY `fk_dichvu_loaiphong` (`ID_LoaiPhong`),
  CONSTRAINT `dichvu_ibfk_1` FOREIGN KEY (`ID_Phong`) REFERENCES `phong` (`ID_Phong`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_dichvu_loaiphong` FOREIGN KEY (`ID_LoaiPhong`) REFERENCES `loaiphong` (`ID_LoaiPhong`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table: thietbi
CREATE TABLE `thietbi` (
  `ID_ThietBi` int(11) NOT NULL AUTO_INCREMENT,
  `TenThietBi` varchar(255) NOT NULL,
  `GiaThietBi` decimal(10,2) DEFAULT NULL,
  `TrangThai` varchar(50) DEFAULT NULL,
  `ID_LoaiPhong` int(11) NOT NULL,
  `ID_Phong` int(11) NOT NULL,
  PRIMARY KEY (`ID_ThietBi`),
  KEY `ID_LoaiPhong` (`ID_LoaiPhong`),
  KEY `ID_Phong` (`ID_Phong`),
  CONSTRAINT `thietbi_ibfk_1` FOREIGN KEY (`ID_LoaiPhong`) REFERENCES `loaiphong` (`ID_LoaiPhong`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `thietbi_ibfk_2` FOREIGN KEY (`ID_Phong`) REFERENCES `phong` (`ID_Phong`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table: hoadon
CREATE TABLE `hoadon` (
  `IDHoaDon` int(11) NOT NULL AUTO_INCREMENT,
  `SoLuong` int(11) NOT NULL,
  `TongTien` decimal(12,2) NOT NULL,
  `NgayThanhToan` datetime DEFAULT NULL,
  `IDNhanVien` int(11) NOT NULL,
  `IDKhacHang` int(11) NOT NULL,
  PRIMARY KEY (`IDHoaDon`),
  KEY `IDNhanVien` (`IDNhanVien`),
  KEY `IDKhacHang` (`IDKhacHang`),
  CONSTRAINT `hoadon_ibfk_1` FOREIGN KEY (`IDNhanVien`) REFERENCES `nhanvien` (`IDNhanVien`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `hoadon_ibfk_2` FOREIGN KEY (`IDKhacHang`) REFERENCES `khachhang` (`IDKhachHang`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table: hoadonct
CREATE TABLE `hoadonct` (
  `IDHoaDonCT` int(11) NOT NULL AUTO_INCREMENT,
  `TenPhong` varchar(255) DEFAULT NULL,
  `NgayCheckIn` datetime NOT NULL,
  `NgayCheckOut` datetime DEFAULT NULL,
  `NhanVienLap` varchar(255) DEFAULT NULL,
  `TenKhachHang` varchar(255) DEFAULT NULL,
  `GiocCheckOut` datetime DEFAULT NULL,
  `GioCheckIn` datetime DEFAULT NULL,
  `IDHoaDon` int(11) NOT NULL,
  `ID_Phong` int(11) NOT NULL,
  PRIMARY KEY (`IDHoaDonCT`),
  KEY `IDHoaDon` (`IDHoaDon`),
  KEY `ID_Phong` (`ID_Phong`),
  CONSTRAINT `hoadonct_ibfk_1` FOREIGN KEY (`IDHoaDon`) REFERENCES `hoadon` (`IDHoaDon`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `hoadonct_ibfk_2` FOREIGN KEY (`ID_Phong`) REFERENCES `phong` (`ID_Phong`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table: dv_hdct
CREATE TABLE `dv_hdct` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `IDHoaDonCT` int(11) NOT NULL,
  `IDDichVu` int(11) NOT NULL,
  `SoLuongDV` int(11) NOT NULL,
  `GiaTien` decimal(10,2) NOT NULL,
  `GiaTienTong` decimal(12,2) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `IDHoaDonCT` (`IDHoaDonCT`),
  KEY `IDDichVu` (`IDDichVu`),
  CONSTRAINT `dv_hdct_ibfk_1` FOREIGN KEY (`IDHoaDonCT`) REFERENCES `hoadonct` (`IDHoaDonCT`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `dv_hdct_ibfk_2` FOREIGN KEY (`IDDichVu`) REFERENCES `dichvu` (`ID_DichVu`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

SET FOREIGN_KEY_CHECKS = 1;

-- Sample seed data (minimal) ------------------------------------------------

INSERT INTO `loaiphong` (`TenLoaiPhong`) VALUES
('single'), ('double'), ('suite');

INSERT INTO `tang` (`TenTang`) VALUES
('Tầng 1'), ('Tầng 2');

INSERT INTO `nhanvien` (`TenNhanVien`, `GioiTinh`, `ChucVu`, `NgaySinh`, `Cccd`, `SDT`, `Luong`) VALUES
('Nguyen Van A', 'Nam', 'Manager', '1985-05-12', '012345678', '0901234567', 15000000.00),
('Tran Thi B', 'Nu', 'Receptionist', '1992-11-02', '987654321', '0907654321', 8000000.00);

INSERT INTO `khachhang` (`HoTen`, `GioiTinh`, `NgaySinh`, `DiaChi`, `SoDienThoai`, `CCCD`, `NgayThue`) VALUES
('Le Van C', 'Nam', '1990-01-01', 'Hanoi', '0912345678', '111222333', NULL);

INSERT INTO `phong` (`TenPhong`, `DonGia`, `TinhTrang`, `ID_LoaiPhong`, `ID_Tang`) VALUES
('101', 200.00, 'free', 1, 1),
('102', 350.00, 'free', 2, 1),
('201', 800.00, 'free', 3, 2);

INSERT INTO `taikhoan` (`TenDangNhap`, `MatKhau`, `IDNhanVien`) VALUES
('admin', 'admin_password_hash_here', 1),
('reception', 'reception_password_hash_here', 2);

INSERT INTO `dichvu` (`TenDichVu`, `GiaDichVu`, `ID_LoaiPhong`, `ID_Phong`) VALUES
('Giặt ủi', 50.00, 1, 101),
('Ăn sáng', 30.00, 2, 102);

-- End of file
COMMIT;