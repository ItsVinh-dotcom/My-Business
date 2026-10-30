# 👗 Clothing Shop Profitability — Phân Tích Lợi Nhuận Shop Quần Áo Online

> **Productized Service** dành cho chủ shop quần áo online tại Việt Nam (Shopee, TikTok Shop)
> Phân tích lợi nhuận theo từng sản phẩm — rõ ràng, nhanh chóng, dễ hiểu.

---

## 📌 Mục Tiêu Dự Án

Nhiều chủ shop bán hàng online nhưng không biết **sản phẩm nào thực sự có lãi**, sản phẩm nào đang "bán nhiều nhưng lỗ". Dịch vụ này giúp:

- ✅ Xác định **lợi nhuận ròng** từng sản phẩm (sau khi trừ phí sàn, phí ship, giá vốn...)
- ✅ Phân loại sản phẩm theo nhóm: **Ngôi sao / Tiềm năng / Cần loại bỏ**
- ✅ Đưa ra **báo cáo trực quan** để chủ shop ra quyết định nhanh hơn

---

## 🗂️ Cấu Trúc Thư Mục (thực tế)

```
clothing-shop-profitability/
│
├── data/
│   ├── raw/                     # File gốc của khách — KHÔNG chỉnh sửa, KHÔNG đưa lên Git
│   │   ├── sample_orders.csv    # Đơn hàng mẫu (minh họa) — định dạng chuẩn đầu vào
│   │   └── product_cost.csv     # Bảng giá vốn theo SKU
│   ├── processed/
│   │   └── orders_cleaned.csv   # Đơn hàng đã làm sạch + đã tính lãi từng đơn
│   └── reference/
│       ├── platform_fees.csv    # Biểu phí sàn 2026 (% + phí cố định/đơn, cột apply bật/tắt)
│       └── shipping_rates.csv   # Bảng phí vận chuyển tham khảo
│
├── analysis/
│   ├── product_ranking.csv      # Xếp hạng sản phẩm theo lợi nhuận
│   └── dashboard_data.json      # Dữ liệu cho dashboard
│
├── reports/
│   ├── dashboard.html           # Dashboard báo cáo (được pipeline tự nhúng dữ liệu mới)
│   ├── templates/               # (trống) mẫu báo cáo
│   └── delivered/
│       └── bao_cao_loi_nhuan.txt
│
├── scripts/
│   ├── run_analysis.py          # ✅ PIPELINE CHÍNH — chạy 1 lệnh ra toàn bộ kết quả
│   ├── clean_data.py            # Bản đọc & làm sạch dữ liệu sàn
│   ├── calculate_profit.py      # Module tính toán lợi nhuận
│   └── export_report.py         # Module xuất báo cáo
│
├── tests/                       # Unit tests & pipeline tests (50 tests passed)
│   ├── test_clean_data.py
│   └── test_pipeline.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

> 💡 **Ghi chú:** Các tài liệu kinh doanh (`docs/`), thông tin khách hàng (`clients/`), thương hiệu (`brand/`) và landing page (`website/`) được quản lý tập trung tại thư mục `01_business/`.

---

## 🧮 Công Thức Tính Lợi Nhuận

```
Lợi nhuận ròng = Doanh thu − Giá vốn − Phí sàn − Phí ship shop chịu − Đóng gói − Ads
Phí sàn       = Doanh thu × (tổng % phí) + phí cố định mỗi đơn
```

Biểu phí mặc định (người bán thường, ngành thời trang — cập nhật 10/2026, xem `data/reference/platform_fees.csv`):

| Sàn         | Các khoản tính                                                                 | Tổng ước tính        |
|-------------|--------------------------------------------------------------------------------|----------------------|
| Shopee      | Phí cố định 9,82% + Phí xử lý giao dịch 6% + Thuế TMĐT 1,5% + Phí hạ tầng 3.000đ | ~17,3% + 3.000đ/đơn |
| TikTok Shop | Hoa hồng 14% + Phí giao dịch 6% + Thuế TMĐT 1,5% + Phí xử lý đơn 3.000đ          | ~21,5% + 3.000đ/đơn |

> ⚠️ Mức thực tế phụ thuộc ngành hàng cấp 3, shop Mall hay thường, chương trình đang tham gia (Voucher Xtra…). Với khách thật, ưu tiên lấy **phí thực tế từ báo cáo đối soát/doanh thu của sàn**.

---

## 🚀 Hướng Dẫn Sử Dụng

### 1. Nhận dữ liệu từ khách hàng
- Khách export báo cáo đơn hàng từ Shopee / TikTok Shop + bảng giá vốn
- Chuyển về đúng định dạng của `data/raw/sample_orders.csv`
  (cột: `order_id, product_name, sku, quantity, revenue, shipping_fee, status, order_date, platform, ads_cost`)
- Kiểm tra lại `data/reference/platform_fees.csv` (Mall/thường, có Voucher Xtra không, hộ KD hay DN)

### 2. Chạy phân tích
```bash
pip install pandas
python scripts/run_analysis.py
# hoặc chỉ định file & tên shop:
python scripts/run_analysis.py --orders data/raw/shop_abc_orders.csv --cost data/raw/shop_abc_cost.csv --shop "Shop ABC"
```

### 3. Kết quả
- `reports/dashboard.html` — mở bằng trình duyệt, gửi khách (đã nhúng dữ liệu mới)
- `reports/delivered/bao_cao_loi_nhuan.txt` — bản tóm tắt text
- `analysis/product_ranking.csv` — bảng xếp hạng để mở bằng Excel

> Lưu ý: khi giao cho khách, **copy dashboard.html ra file riêng** (vd. `reports/delivered/ShopABC_2026-10.html`) vì lần chạy sau sẽ ghi đè. `reports/dashboard.html` gốc đang được landing page dùng làm *báo cáo mẫu*.

---

## 📊 Phân Loại Sản Phẩm

| Nhóm            | Tiêu chí                        | Hành động đề xuất            |
|-----------------|---------------------------------|------------------------------|
| ⭐ Ngôi sao     | Margin > 30%, Volume cao        | Tăng tồn kho, đẩy quảng cáo |
| 💛 Tiềm năng    | Margin > 15%, Volume thấp       | Tối ưu giá, thêm voucher     |
| ⚠️ Cần xem lại  | Margin 0–15%                    | Giảm chi phí hoặc tăng giá  |
| ❌ Cần loại bỏ  | Margin âm hoặc < 0%             | Ngừng kinh doanh sản phẩm   |

---

## 🔒 Bảo Mật & Quyền Riêng Tư

- Toàn bộ dữ liệu khách hàng **KHÔNG được đưa lên Git** (xem `.gitignore`)
- Thư mục `clients/` và `data/raw/` đã được loại trừ
- Mỗi khách hàng được lưu trữ riêng biệt, không trộn lẫn

---

## 📞 Liên Hệ

> Dịch vụ được cung cấp bởi **Lê Gia Tiến Vinh** — V-Insights
> 📧 Email: legiatienvinh@gmail.com
> 💬 Zalo: 0356 177 552

---

*Cập nhật lần cuối: Tháng 10/2026*
