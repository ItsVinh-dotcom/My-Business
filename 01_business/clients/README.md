# 📁 Thư Mục Khách Hàng (`clients/`)

> ⚠️ **Thư mục này đã được loại trừ khỏi Git** (xem `.gitignore`).

## Cấu Trúc Gợi Ý

Mỗi khách hàng tạo 1 thư mục con:

```
clients/
├── ShopABC_2026-10/
│   ├── raw/                    # File gốc khách gửi (Excel, CSV)
│   │   ├── shopee_orders.xlsx
│   │   ├── tiktok_orders.xlsx
│   │   └── bang_gia_von.xlsx
│   ├── processed/              # Dữ liệu đã chuẩn hóa
│   │   └── orders_cleaned.csv
│   ├── reports/                # Báo cáo đã xuất
│   │   ├── dashboard.html
│   │   └── bao_cao_loi_nhuan.txt
│   └── notes.txt               # Ghi chú riêng (biểu phí đặc biệt, yêu cầu)
├── ShopXYZ_2026-09/
│   └── ...
```

## Quy Tắc

1. **Đặt tên thư mục:** `TenShop_YYYY-MM` (ví dụ: `ShopABC_2026-10`)
2. **Không sửa file gốc** trong `raw/` — luôn xử lý rồi lưu vào `processed/`
3. **Xóa dữ liệu** sau khi giao báo cáo xong (cam kết bảo mật)
4. **Chạy pipeline:** Dùng `--orders` và `--cost` trỏ vào file trong thư mục khách

```bash
python 02_projects/clothing-shop-profitability/scripts/run_analysis.py \
  --orders 01_business/clients/ShopABC_2026-10/processed/orders.csv \
  --cost 01_business/clients/ShopABC_2026-10/raw/bang_gia_von.csv \
  --shop "Shop ABC"
```
