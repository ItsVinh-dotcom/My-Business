# 🚀 Projects Hub — Dự Án Cá Nhân & Demo

> Nơi chứa toàn bộ mã nguồn các dự án phân tích dữ liệu, công cụ tự động hóa và sản phẩm kỹ thuật phục vụ cho hoạt động kinh doanh cũng như portfolio cá nhân.

---

## 🗂️ Danh Sách Dự Án

| Thư mục | Tên dự án | Mô tả | Công nghệ |
|---|---|---|---|
| [`clothing-shop-profitability`](file:///d:/02_business/02_projects/clothing-shop-profitability) | Phân Tích Lợi Nhuận Shop Quần Áo Online | Pipeline tự động tính lãi ròng từng SKU, xuất báo cáo Dashboard trực quan cho chủ shop Shopee/TikTok Shop | Python, Pandas, HTML/JS Dashboard, Pytest |

---

## 📁 Cấu Trúc Khuyến Nghị Cho Dự Án Mới

Khi tạo thêm dự án mới trong thư mục `02_projects/`, hãy tổ chức theo mẫu sau để đảm bảo tính đồng bộ:

```
02_projects/
└── [ten-du-an]/
    ├── data/               # raw (file gốc), processed (đã làm sạch), reference (dữ liệu mẫu)
    ├── scripts/            # source code / pipeline xử lý chính
    ├── analysis/           # kết quả tính toán, model, ranking
    ├── reports/            # báo cáo đầu ra, dashboard html/pdf
    ├── tests/              # unit tests kiểm thử logic
    ├── requirements.txt    # thư viện dependencies
    └── README.md           # hướng dẫn sử dụng dự án
```
