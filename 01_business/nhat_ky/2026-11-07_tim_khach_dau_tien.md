# Nhật ký 07/11/2026: buổi sáng đi tìm khách đầu tiên

Ghi lại buổi làm việc với Claude (khoảng 10:30–11:30). Lần sau mở lại file này để nói tiếp.

---

## 1. Bối cảnh

- **V-Insights:** dịch vụ tính lãi ròng từng sản phẩm cho shop thời trang trên Shopee/TikTok Shop. Khách gửi file đơn và giá vốn, mình trả báo cáo trong 24h kèm lời khuyên (mẫu nào nên đẩy, mẫu nào xem lại giá).
- Phần chuẩn bị đã đủ: tool Python, landing page (file `website/index.html`, **chưa đưa lên mạng**), logo, page Facebook, tài liệu quy trình.
- **Vấn đề chính: chưa có khách nào.** Nên quyết định không build thêm, tập trung tìm 3 shop dùng thử miễn phí.
- Mục tiêu tuần này: **có 1 shop gửi file thật.**

---

## 2. Con số hôm nay

**Page Facebook V-Insights** (Meta Business Suite, 28 ngày: 9/10–5/11/2026)

| Chỉ số | Số | Ghi chú |
|---|---|---|
| Người xem | 136 | Gần như toàn bộ đến từ đỉnh 30–31/10, ngày đăng bài đầu tiên |
| Lượt xem | 244 | |
| Tương tác | 1 | |
| Click liên kết | 0 | |
| Lượt truy cập page | 19 | Chủ yếu quanh 24/10, khả năng là chính mình lúc dựng page |
| Người theo dõi | 0–1 | |

- Bài đầu tiên đăng 30/10 lúc 21:57, có 1 lượt chia sẻ. Có thể lần chia sẻ này mang về phần lớn lượt xem, **cần kiểm tra đã chia sẻ vào đâu.**

**Nhắn shop trên Shopee**
- Đã nhắn một số shop (chưa đếm chính xác).
- Tin bản dài gửi BraLune Store lúc 10:37–10:39 bị Shopee cảnh báo "không phù hợp Tiêu Chuẩn Cộng Đồng", nhưng shop vẫn đọc được.
- **1 shop trả lời bằng người thật:** BraLune Store, "dạ" lúc 11:26, chưa có bước tiếp theo.

**Group Facebook**
- Page đã vào group "Chuyện Nhà… Shopee / TikTok Shop" (công khai) và "Cộng Đồng Nhà Bán Hàng Việt Nam" (khoảng 6.947 thành viên).
- Đã soạn bài group để đăng. *Cập nhật lại ở đây xem bài đã đăng thành công vào group nào.*

---

## 3. Bài học

1. **Nhắn khách lạ có tỉ lệ thấp nhất.** Người ta mua vì tin người, mà họ chưa biết mình là ai. "Dạ" thường chỉ là lịch sự.
2. **Chat Shopee không phải chỗ chào dịch vụ.** Tránh các từ "file", "dữ liệu", số điện thoại, Zalo, link. Mỗi ngày tối đa 3–5 shop. Ai quan tâm thì rủ sang page Facebook.
3. **Kênh nên ưu tiên:** người quen (nhắn riêng vài người tin tưởng), bài đăng và bình luận hữu ích trong group seller, rồi để khách tự inbox.
4. **Đăng nhiều nhóm:** chỉ dùng tính năng của Meta Business Suite, mỗi lần 3–4 nhóm, đổi câu mở đầu. Không dùng tool hay bot bên ngoài (dễ bị khoá).
   - Bài đăng vào nhóm **không được** bật "Tạo bài viết quảng cáo" hay "Thu hút tin nhắn", nếu không ô chọn nhóm sẽ bị khoá.
5. **Bản thân:** thích build hơn bán, hay nhảy việc khi thấy cái mới. Mẹo: mỗi tuần chỉ theo dõi 1 con số (số shop gửi file). Việc mới nào giúp con số đó tăng thì làm, không thì để tuần sau.
6. **Ẩn danh:** người ngoài không thấy ai quản lý page. Mời bạn bè thích trang hoặc chia sẻ lên trang cá nhân thì sẽ lộ là của mình.

---

## 4. Việc tiếp theo

- [ ] BraLune: nhắn thêm đúng 1 câu (mẫu 5c bên dưới), im lặng thì bỏ qua
- [ ] Cài app Meta Business Suite, bật thông báo tin nhắn và bình luận
- [ ] Bật trả lời tự động cho page (mẫu 5e)
- [ ] Sửa page: thêm số điện thoại/Zalo vào thông tin liên hệ, đặt tên người dùng (ví dụ `vinsights.vn`), ghim bài đầu tiên
- [ ] Cho page xin vào thêm 5 group seller (tránh group affiliate, vì họ không phải người bán)
- [ ] Mỗi ngày đăng 2–3 group, dùng bản A/B bên dưới
- [ ] Bình luận giúp người khác trong group về phí và lãi, khoảng 15 phút mỗi ngày
- [ ] Chạy thử tool với một file xuất đơn Shopee thật trước khi có khách
- [ ] (Để sau) đưa landing page lên Netlify; luồng tự động: form nhận file → tool → báo cáo

---

## 5. Tin nhắn mẫu đã dùng hoặc đã soạn

**a. Chat Shopee (bản tự nhiên, đã chỉnh)**
> Hello shop ạ. Em làm phân tích lãi lỗ cho seller thời trang. Cho em hỏi shop mình hiện đang tính lãi theo từng sản phẩm và cả shop bằng cách nào ạ?
>
> Em đang tính miễn phí lãi thật (sau phí sàn, ship, ads) cho vài shop dùng thử. Shop quan tâm thì cứ rep em nhé ạ!

**b. Khi shop Shopee trả lời, rủ sang Facebook**
> Dạ em cảm ơn shop đã phản hồi ạ! Shop có muốn thử nhận báo cáo lãi từng mẫu miễn phí không ạ? Nếu có, shop tìm "V-Insights" trên Facebook rồi nhắn page giúp em, em hướng dẫn chi tiết bên đó cho tiện ạ.

**c. Nhắc lại 1 lần (cho BraLune)**
> Dạ shop có muốn em tính thử miễn phí lãi từng mẫu không ạ? Nếu bận thì không sao đâu ạ, em cảm ơn shop!

**d. Bài group, bản A (mở bằng con số)**
> Bán áo 150k trên Shopee, anh/chị nghĩ mình lãi bao nhiêu?
>
> Nhiều shop tính: giá bán trừ giá nhập 75k là lãi 75k. Nhưng sau khi trừ phí sàn (khoảng 17% + 3.000đ/đơn), đóng gói và quảng cáo, lãi thật chỉ còn khoảng 31k, chưa tới một nửa.
>
> Mình là người làm phân tích dữ liệu cho seller. Mình đang tìm 3 shop quần áo trên Shopee hoặc TikTok Shop để làm miễn phí báo cáo lãi ròng từng sản phẩm, xem mẫu nào lãi thật, mẫu nào đang "bán lỗ mà không biết". Đổi lại anh/chị góp ý thật lòng giúp mình.
>
> Ai quan tâm comment hoặc inbox page nhé. Dữ liệu chỉ dùng để phân tích và xoá sau khi xong.

**Bài group, bản B (mở bằng câu chuyện)**
> Có một chuyện mình gặp khá nhiều: shop dồn tiền ads cho mẫu bán chạy nhất, cuối tháng doanh thu tăng mà tiền về tay không tăng.
>
> Lý do thường là mẫu bán chạy nhất lại không phải mẫu lãi nhất. Trong ví dụ bên dưới, áo thun bán gấp đôi áo sơ mi, nhưng biên lãi chỉ 24,7% so với 36,9%.
>
> Mình đang tìm 3 shop thời trang trên Shopee/TikTok Shop để làm miễn phí báo cáo lãi ròng từng sản phẩm (đã trừ phí sàn, ship, đóng gói, ads). Anh/chị nào muốn biết shop mình đang lãi thật ở đâu thì comment hoặc inbox page nhé. Đổi lại chỉ cần góp ý thật lòng.

(Bản gốc của bài group nằm ở `marketing/2026-10_facebook_launch/bai_dang_facebook.md`. Ảnh dùng kèm: `img_group.png`.)

**e. Trả lời tự động trên Messenger của page**
> Dạ V-Insights chào anh/chị ạ! Em đã nhận được tin nhắn và sẽ phản hồi trong ít phút. Anh/chị cho em biết shop mình đang bán trên Shopee hay TikTok Shop, và bán khoảng bao nhiêu mẫu nhé ạ.

**f. Khi shop đồng ý, hướng dẫn gửi file (qua Messenger, không qua chat Shopee)**
> Dạ em cảm ơn anh/chị nhiều ạ! Anh/chị gửi giúp em 2 thứ:
> 1. File đơn hàng 1 tháng gần nhất (Shopee: Kênh Người Bán → Đơn hàng → Xuất; TikTok Shop: Seller Center → Quản lý đơn hàng → Xuất)
> 2. Giá nhập của từng mẫu: file Excel, ảnh chụp sổ hoặc gõ tin nhắn đều được, ví dụ "Áo thun đen: 85k".
>
> Nếu có thì gửi thêm chi phí quảng cáo trong tháng và chi phí đóng gói mỗi đơn, không có cũng không sao ạ. Em gửi báo cáo trong khoảng 24 giờ sau khi nhận đủ file ạ.

*(Đường dẫn menu xuất file cần kiểm tra lại trên Seller Center.)*
