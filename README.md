# 🏢 My Business & Projects Workspace

Chào mừng bạn đến với trung tâm quản lý hoạt động kinh doanh và các dự án cá nhân. Workspace được tổ chức khoa học theo mô hình phân tách rõ ràng giữa **Thông tin kinh doanh** và **Dự án kỹ thuật**.

---

## 🧭 Cấu Trúc Tổng Quan

```
d:\02_business\
│
├── 📁 01_business/                     # 💼 THÔNG TIN KINH DOANH & VẬN HÀNH DỊCH VỤ
│   ├── 📁 brand/                       # Bộ nhận diện thương hiệu (Logo, Cover Facebook, SVG, PNG, Icon)
│   ├── 📁 website/                     # Website & Landing page giới thiệu dịch vụ (index.html)
│   ├── 📁 clients/                     # Quản lý khách hàng, quy tắc lưu trữ & bảo mật dữ liệu
│   ├── 📁 docs/                        # Tài liệu nghiệp vụ: Methodology, Onboarding checklist, FAQ
│   └── 📄 README.md                    # Chi tiết phân hệ Business
│
├── 📁 02_projects/                     # 🚀 CÁC DỰ ÁN CÁ NHÂN & PORTFOLIO KỸ THUẬT
│   ├── 📁 clothing-shop-profitability/ # Dự án demo: Phân tích lợi nhuận shop thời trang online
│   │   ├── 📁 data/                    # Dữ liệu mẫu (raw, processed, reference platform fees)
│   │   ├── 📁 scripts/                 # Source code pipeline xử lý & tính toán lãi ròng
│   │   ├── 📁 analysis/                # Bảng xếp hạng sản phẩm & dữ liệu phân tích JSON
│   │   ├── 📁 reports/                 # Báo cáo kết quả & Dashboard tương tác HTML
│   │   ├── 📁 tests/                   # Bộ kiểm thử tự động (50/50 tests passed)
│   │   ├── 📄 requirements.txt         # Thư viện phụ thuộc (pandas, pytest, ...)
│   │   └── 📄 README.md                # Hướng dẫn chi tiết dự án
│   └── 📄 README.md                    # Danh mục & quy chuẩn thêm dự án mới
│
├── 📄 .gitignore                       # Cấu hình bảo mật & loại trừ file rác, dữ liệu khách hàng
└── 📄 README.md                        # Mục lục điều hướng workspace (file này)
```

---

## 📌 Hướng Dẫn Nhanh

### 1. 💼 Về phần Business
- **Xem Landing Page:** Mở file [`01_business/website/index.html`](file:///d:/02_business/01_business/website/index.html) trên trình duyệt để trải nghiệm landing page giới thiệu dịch vụ và công cụ tính lãi.
- **Tài nguyên Thương hiệu:** Xem các file vector SVG / PNG tại [`01_business/brand/`](file:///d:/02_business/01_business/brand).
- **Quy trình làm việc với khách:** Xem checklist tiếp nhận tại [`01_business/docs/onboarding_checklist.md`](file:///d:/02_business/01_business/docs/onboarding_checklist.md).

### 2. 🚀 Về phần Dự án cá nhân
- **Chạy thử pipeline phân tích lợi nhuận:**
  ```bash
  cd 02_projects/clothing-shop-profitability
  python scripts/run_analysis.py
  ```
- **Chạy bộ kiểm thử (Unit tests):**
  ```bash
  cd 02_projects/clothing-shop-profitability
  pytest
  ```
- **Thêm dự án mới:** Bạn chỉ cần tạo một thư mục mới trong [`02_projects/`](file:///d:/02_business/02_projects) theo chuẩn đã được hướng dẫn tại [`02_projects/README.md`](file:///d:/02_business/02_projects/README.md).

---

## 🔒 Quy Định Bảo Mật Dữ Liệu
- Dữ liệu thô và thông tin nhạy cảm của khách hàng (`raw/*.csv`, `raw/*.xlsx`, `clients/*/`) luôn được loại trừ khỏi Git theo [.gitignore](file:///d:/02_business/.gitignore).
- Chỉ những dữ liệu mẫu (sample data) và mã nguồn phục vụ mục đích demo mới được lưu trữ trên Git.
