# 📐 Phương Pháp Tính Lợi Nhuận (Methodology)

## Công Thức Cốt Lõi

```
Lợi nhuận ròng (Net Profit) = Doanh thu - Giá vốn - Phí sàn - Phí vận chuyển - Chi phí khác
Biên lợi nhuận (Margin %)  = (Lợi nhuận ròng / Doanh thu) × 100
```

---

## Chi Tiết Từng Thành Phần

### 1. Doanh Thu (Revenue)
- Lấy từ cột "Tổng tiền đơn hàng" hoặc "Số tiền thanh toán" trên báo cáo sàn
- **Lưu ý:** Chỉ tính đơn hàng trạng thái **Hoàn thành** (bỏ qua Hủy/Hoàn trả)

### 2. Giá Vốn (Cost of Goods)
- Khách hàng cung cấp bảng giá vốn từng SKU
- Nếu không có: ước tính = Giá bán × (1 - Margin mong muốn)

### 3. Phí Sàn (Platform Fee) — cập nhật 10/2026
Người bán thường, ngành thời trang:

| Sàn         | Khoản phí                         | Mức             | Hiệu lực     |
|-------------|-----------------------------------|-----------------|--------------|
| Shopee      | Phí cố định (Thời trang nữ)       | 9,82% (9,82–10,80% tùy ngành cấp 3; Mall 7–8,1%) | 01/07/2025 |
| Shopee      | Phí xử lý giao dịch               | 6%              | 01/05/2026   |
| Shopee      | Phí hạ tầng                       | 3.000đ/đơn      | 01/07/2025   |
| Shopee      | Phí Voucher Xtra (nếu tham gia)   | 2% (tối đa 50.000đ/SP) | 06/06/2025 |
| TikTok Shop | Phí hoa hồng (Trang phục nữ)      | 14–15% (nam 13–15%; Mall 16–17,1%) | 03/07/2026 |
| TikTok Shop | Phí giao dịch                     | 6%              | 09/05/2026   |
| TikTok Shop | Phí xử lý đơn hàng                | 3.000đ/đơn      | 27/10/2025   |
| Cả hai      | Thuế TMĐT sàn khấu trừ (hộ KD)    | 1,5% (1% GTGT + 0,5% TNCN) | 01/07/2025 |

> Sàn đổi phí vài lần mỗi năm. Trước mỗi dự án: kiểm tra Seller Center và cập nhật `data/reference/platform_fees.csv`.
> Tốt nhất là lấy số phí thực tế từ báo cáo đối soát/doanh thu của khách thay vì ước tính.

### 4. Phí Vận Chuyển (Shipping)
- Lấy từ báo cáo "Phí vận chuyển người bán chịu" trên sàn
- Nếu shop dùng gói freeship: tính phần shop đang trợ giá

### 5. Chi Phí Khác (Other Costs)
- Quảng cáo Shopee Ads / TikTok Ads (phân bổ theo sản phẩm)
- Chi phí đóng gói (bao bì, băng keo, túi)
- Nhân công (nếu có, phân bổ theo số đơn)

---

## Phân Loại Sản Phẩm

| Nhóm            | Margin         | Chiến lược                   |
|-----------------|----------------|------------------------------|
| ⭐ Ngôi sao     | > 30%          | Scale up, tăng ngân sách ads |
| 💛 Tiềm năng    | 15% – 30%      | Tối ưu chi phí, test giá     |
| ⚠️ Cần xem lại  | 0% – 15%       | Review toàn bộ cost structure |
| ❌ Cần loại bỏ  | < 0%           | Ngừng hoặc tái định giá      |
