# 💼 Business Hub — V-Insights

> Trung tâm quản lý thông tin kinh doanh, dịch vụ phân tích lợi nhuận cho các chủ shop online (Shopee, TikTok Shop).

---

## 🧭 Cấu Trúc Phân Hệ Kinh Doanh

```
01_business/
├── brand/        # Bộ nhận diện thương hiệu (Logo, Cover Facebook, SVG, PNG, Icons)
├── website/      # Landing page chính thức giới thiệu dịch vụ (index.html)
├── clients/      # Quản lý thông tin & dữ liệu khách hàng (được bảo mật khỏi Git)
└── docs/         # Tài liệu nghiệp vụ & dịch vụ
    ├── methodology.md           # Phương pháp luận tính toán chi phí, phí sàn & lợi nhuận
    ├── onboarding_checklist.md  # Checklist tiếp nhận shop mới
    └── faq.md                   # Câu hỏi thường gặp khi tư vấn khách hàng
```

---

## 🎯 Chi Tiết Từng Phần

### 1. 🎨 Thương Hiệu (`brand/`)
- Chứa các phiên bản logo chính thức của **V-Insights**:
  - `v-insights-logo.svg`, `v-insights-logo.png`: Logo nhận diện chuẩn
  - `v-insights-horizontal-*.svg/png`: Logo ngang cho dark mode / light mode
  - `v-insights-facebook-cover.html/png`: Banner / Cover Facebook chuẩn kích thước
  - `v-insights-icon.svg/png`: Icon ứng dụng / favicon

### 2. 🌐 Website & Landing Page (`website/`)
- File `index.html`: Landing page bán dịch vụ được tối ưu chuyển đổi, bao gồm:
  - Máy tính lợi nhuận nhanh cho chủ shop
  - Bảng so sánh phí sàn Shopee vs TikTok Shop cập nhật mới nhất
  - Các gói dịch vụ & cam kết bảo mật
  - Nút kêu gọi hành động (CTA) dẫn về Messenger của Fanpage

### 3. 👥 Quản Lý Khách Hàng (`clients/`)
- Quản lý quy trình nhận dữ liệu và bàn giao báo cáo cho từng khách hàng theo từng tháng.
- Thư mục tuân thủ chính sách bảo mật: các thư mục con chứa dữ liệu thật của khách được tự động loại trừ khỏi Git theo `.gitignore`.

### 4. 📚 Tài Liệu Dịch Vụ (`docs/`)
- **`methodology.md`**: Chi tiết công thức tính toán lợi nhuận ròng, tỷ lệ hoa hồng, phí giao dịch, phí hạ tầng và thuế TMĐT.
- **`onboarding_checklist.md`**: Quy trình 3 bước từ tiếp nhận, thu thập dữ liệu đến bàn giao kết quả.
- **`faq.md`**: Kịch bản giải đáp các thắc mắc thường gặp của khách hàng.
