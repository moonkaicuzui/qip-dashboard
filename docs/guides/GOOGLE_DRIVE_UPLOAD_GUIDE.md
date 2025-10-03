# Google Drive File Upload Guide for QIP Dashboard
# Hướng dẫn Tải lên Tệp Google Drive cho Bảng điều khiển QIP

---

## 🌐 English Version

### Overview
This guide explains which files the QIP Dashboard system retrieves from Google Drive and the rules for uploading files to ensure successful synchronization.

### Google Drive Folder Structure

```
📁 Root Folder (ID: 1PwmT0di7w2_iz-iA8Llza_h0oT4l4Q9D)
├── 📁 monthly_data/
│   └── 📁 YYYY_MM/ (e.g., 2025_08 for August 2025)
│       ├── basic_manpower_data.csv
│       ├── attendance_data.csv
│       ├── 5prs_data.csv
│       └── YYYY년 M월 인센티브 지급 세부 정보.csv
├── 📁 aql_history/
│   └── AQL_REPORT_MONTH_YYYY.csv
└── 📁 configs/
    ├── auditor_trainer_area_mapping.json
    └── type2_position_mapping.json
```

### Files Retrieved from Google Drive

#### Required Files (Must be present)
1. **Basic Manpower Data**
   - Location: `monthly_data/YYYY_MM/basic_manpower_data.csv`
   - File name: Must be exactly `basic_manpower_data.csv`

2. **Attendance Data**
   - Location: `monthly_data/YYYY_MM/attendance_data.csv`
   - File name: Must be exactly `attendance_data.csv`

3. **5PRS Data**
   - Location: `monthly_data/YYYY_MM/5prs_data.csv`
   - File name: Must be exactly `5prs_data.csv`

4. **AQL Reports** (Last 3 months)
   - Location: `aql_history/AQL_REPORT_MONTH_YYYY.csv`
   - Example: `AQL_REPORT_AUGUST_2025.csv`
   - Month name must be in UPPERCASE English

#### Optional Files
5. **Current Month Incentive Data**
   - Location: `monthly_data/YYYY_MM/YYYY년 M월 인센티브 지급 세부 정보.csv`
   - Example: `2025년 8월 인센티브 지급 세부 정보.csv`

6. **Previous Month Incentive Data** (for comparison)
   - Automatically retrieved from previous month's folder

7. **Configuration Files**
   - `configs/auditor_trainer_area_mapping.json`
   - `configs/type2_position_mapping.json`

### Upload Rules and Naming Conventions

#### Folder Naming Rules
- **Monthly folders**: Use format `YYYY_MM`
  - ✅ Correct: `2025_08` (August 2025)
  - ✅ Correct: `2025_12` (December 2025)
  - ❌ Wrong: `2025_8` (missing leading zero)
  - ❌ Wrong: `2025-08` (wrong separator)

#### File Naming Rules

**For Basic Data Files:**
- Must use exact English names (no variations allowed)
- ✅ `basic_manpower_data.csv`
- ❌ `basic_manpower.csv`
- ❌ `manpower_data.csv`

**For AQL Reports:**
- Format: `AQL_REPORT_MONTH_YYYY.csv`
- Month must be full name in UPPERCASE
- ✅ `AQL_REPORT_JANUARY_2025.csv`
- ✅ `AQL_REPORT_DECEMBER_2025.csv`
- ❌ `AQL_REPORT_JAN_2025.csv` (abbreviated)
- ❌ `AQL_REPORT_january_2025.csv` (lowercase)

**For Incentive Files:**
- Format: `YYYY년 M월 인센티브 지급 세부 정보.csv`
- Month should NOT have leading zero
- ✅ `2025년 8월 인센티브 지급 세부 정보.csv`
- ❌ `2025년 08월 인센티브 지급 세부 정보.csv`

### Upload Checklist
- [ ] Created monthly folder with format `YYYY_MM`
- [ ] All CSV files are in UTF-8 encoding
- [ ] File names match exactly as specified
- [ ] AQL report month name is in UPPERCASE
- [ ] Incentive file uses single-digit month (1-9) without leading zero
- [ ] All required files are present in the monthly folder

### Month Names Reference
| Number | English (for AQL) | Korean (for Incentive) |
|--------|------------------|----------------------|
| 01 | JANUARY | 1월 |
| 02 | FEBRUARY | 2월 |
| 03 | MARCH | 3월 |
| 04 | APRIL | 4월 |
| 05 | MAY | 5월 |
| 06 | JUNE | 6월 |
| 07 | JULY | 7월 |
| 08 | AUGUST | 8월 |
| 09 | SEPTEMBER | 9월 |
| 10 | OCTOBER | 10월 |
| 11 | NOVEMBER | 11월 |
| 12 | DECEMBER | 12월 |

---

## 🇻🇳 Phiên bản Tiếng Việt

### Tổng quan
Hướng dẫn này giải thích những tệp nào hệ thống Bảng điều khiển QIP lấy từ Google Drive và các quy tắc tải lên tệp để đảm bảo đồng bộ hóa thành công.

### Cấu trúc Thư mục Google Drive

```
📁 Thư mục Gốc (ID: 1PwmT0di7w2_iz-iA8Llza_h0oT4l4Q9D)
├── 📁 monthly_data/
│   └── 📁 YYYY_MM/ (ví dụ: 2025_08 cho tháng 8 năm 2025)
│       ├── basic_manpower_data.csv
│       ├── attendance_data.csv
│       ├── 5prs_data.csv
│       └── YYYY년 M월 인센티브 지급 세부 정보.csv
├── 📁 aql_history/
│   └── AQL_REPORT_MONTH_YYYY.csv
└── 📁 configs/
    ├── auditor_trainer_area_mapping.json
    └── type2_position_mapping.json
```

### Các Tệp Được Lấy từ Google Drive

#### Tệp Bắt buộc (Phải có)
1. **Dữ liệu Nhân lực Cơ bản**
   - Vị trí: `monthly_data/YYYY_MM/basic_manpower_data.csv`
   - Tên tệp: Phải chính xác là `basic_manpower_data.csv`

2. **Dữ liệu Chấm công**
   - Vị trí: `monthly_data/YYYY_MM/attendance_data.csv`
   - Tên tệp: Phải chính xác là `attendance_data.csv`

3. **Dữ liệu 5PRS**
   - Vị trí: `monthly_data/YYYY_MM/5prs_data.csv`
   - Tên tệp: Phải chính xác là `5prs_data.csv`

4. **Báo cáo AQL** (3 tháng gần nhất)
   - Vị trí: `aql_history/AQL_REPORT_MONTH_YYYY.csv`
   - Ví dụ: `AQL_REPORT_AUGUST_2025.csv`
   - Tên tháng phải viết HOA bằng tiếng Anh

#### Tệp Tùy chọn
5. **Dữ liệu Khuyến khích Tháng hiện tại**
   - Vị trí: `monthly_data/YYYY_MM/YYYY년 M월 인센티브 지급 세부 정보.csv`
   - Ví dụ: `2025년 8월 인센티브 지급 세부 정보.csv`

6. **Dữ liệu Khuyến khích Tháng trước** (để so sánh)
   - Tự động lấy từ thư mục tháng trước

7. **Tệp Cấu hình**
   - `configs/auditor_trainer_area_mapping.json`
   - `configs/type2_position_mapping.json`

### Quy tắc Tải lên và Quy ước Đặt tên

#### Quy tắc Đặt tên Thư mục
- **Thư mục hàng tháng**: Sử dụng định dạng `YYYY_MM`
  - ✅ Đúng: `2025_08` (Tháng 8 năm 2025)
  - ✅ Đúng: `2025_12` (Tháng 12 năm 2025)
  - ❌ Sai: `2025_8` (thiếu số 0 đầu)
  - ❌ Sai: `2025-08` (dấu phân cách sai)

#### Quy tắc Đặt tên Tệp

**Cho Tệp Dữ liệu Cơ bản:**
- Phải sử dụng tên tiếng Anh chính xác (không cho phép biến thể)
- ✅ `basic_manpower_data.csv`
- ❌ `basic_manpower.csv`
- ❌ `manpower_data.csv`

**Cho Báo cáo AQL:**
- Định dạng: `AQL_REPORT_MONTH_YYYY.csv`
- Tháng phải là tên đầy đủ viết HOA
- ✅ `AQL_REPORT_JANUARY_2025.csv`
- ✅ `AQL_REPORT_DECEMBER_2025.csv`
- ❌ `AQL_REPORT_JAN_2025.csv` (viết tắt)
- ❌ `AQL_REPORT_january_2025.csv` (chữ thường)

**Cho Tệp Khuyến khích:**
- Định dạng: `YYYY년 M월 인센티브 지급 세부 정보.csv`
- Tháng KHÔNG có số 0 đầu
- ✅ `2025년 8월 인센티브 지급 세부 정보.csv`
- ❌ `2025년 08월 인센티브 지급 세부 정보.csv`

### Danh sách Kiểm tra Tải lên
- [ ] Đã tạo thư mục hàng tháng với định dạng `YYYY_MM`
- [ ] Tất cả tệp CSV đều ở mã hóa UTF-8
- [ ] Tên tệp khớp chính xác như đã chỉ định
- [ ] Tên tháng báo cáo AQL viết HOA
- [ ] Tệp khuyến khích sử dụng tháng một chữ số (1-9) không có số 0 đầu
- [ ] Tất cả tệp bắt buộc đều có trong thư mục hàng tháng

### Bảng Tham khảo Tên Tháng
| Số | Tiếng Anh (cho AQL) | Tiếng Hàn (cho Khuyến khích) | Tiếng Việt |
|----|-------------------|----------------------------|------------|
| 01 | JANUARY | 1월 | Tháng 1 |
| 02 | FEBRUARY | 2월 | Tháng 2 |
| 03 | MARCH | 3월 | Tháng 3 |
| 04 | APRIL | 4월 | Tháng 4 |
| 05 | MAY | 5월 | Tháng 5 |
| 06 | JUNE | 6월 | Tháng 6 |
| 07 | JULY | 7월 | Tháng 7 |
| 08 | AUGUST | 8월 | Tháng 8 |
| 09 | SEPTEMBER | 9월 | Tháng 9 |
| 10 | OCTOBER | 10월 | Tháng 10 |
| 11 | NOVEMBER | 11월 | Tháng 11 |
| 12 | DECEMBER | 12월 | Tháng 12 |

### Ví dụ Thực tế

#### Tải lên dữ liệu Tháng 9 năm 2025:

1. **Tạo thư mục trong Google Drive:**
   ```
   monthly_data/2025_09/
   ```

2. **Tải lên các tệp sau vào thư mục `2025_09`:**
   - `basic_manpower_data.csv` (Dữ liệu nhân lực)
   - `attendance_data.csv` (Dữ liệu chấm công)
   - `5prs_data.csv` (Dữ liệu 5PRS)
   - `2025년 9월 인센티브 지급 세부 정보.csv` (Dữ liệu khuyến khích)

3. **Tải lên vào thư mục `aql_history`:**
   - `AQL_REPORT_SEPTEMBER_2025.csv`

### Lưu ý Quan trọng

⚠️ **Chú ý:**
- Tên tệp phải chính xác 100% - một ký tự sai sẽ khiến đồng bộ hóa thất bại
- Luôn sử dụng số 0 đầu cho tháng trong tên thư mục (01, 02, ..., 09)
- KHÔNG sử dụng số 0 đầu cho tháng trong tên tệp khuyến khích tiếng Hàn
- Tên tháng AQL phải là tiếng Anh VIẾT HOA đầy đủ

### Hỗ trợ

Nếu gặp vấn đề với việc đồng bộ hóa tệp:
1. Kiểm tra tên thư mục và tệp có chính xác không
2. Xác nhận mã hóa tệp CSV là UTF-8
3. Đảm bảo tất cả tệp bắt buộc đều có mặt
4. Kiểm tra quyền truy cập Google Drive

---

## 📞 Contact / Liên hệ

For technical support regarding file uploads, please contact the system administrator.
Để được hỗ trợ kỹ thuật về việc tải lên tệp, vui lòng liên hệ quản trị viên hệ thống.

---

*Last updated: August 2025 / Cập nhật lần cuối: Tháng 8 năm 2025*