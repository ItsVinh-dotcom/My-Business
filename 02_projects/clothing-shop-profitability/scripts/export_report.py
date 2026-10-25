"""
export_report.py
----------------
Tạo báo cáo tóm tắt điều hành (Executive Summary) cho khách hàng dưới dạng:
1. Markdown (.md)
2. HTML in / xuất PDF (.html)

Cách chạy:
    python scripts/export_report.py
    python scripts/export_report.py --shop "Min Boutique" --output reports/delivered/executive_summary.html
"""

import json
from pathlib import Path
from datetime import datetime
import argparse
import sys

# Đảm bảo UTF-8 trên Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_JSON = BASE_DIR / "analysis" / "dashboard_data.json"
DEFAULT_MD = BASE_DIR / "reports" / "delivered" / "executive_summary.md"
DEFAULT_HTML = BASE_DIR / "reports" / "delivered" / "executive_summary.html"


def generate_executive_markdown(data: dict, shop_name: str) -> str:
    overview = data.get("overview", {})
    products = data.get("products", [])
    platforms = data.get("by_platform", [])
    period = data.get("period", "Tháng gần nhất")

    stars = [p for p in products if "Ngôi sao" in p.get("classification", "")]
    warnings = [p for p in products if any(k in p.get("classification", "") for k in ["Cần xem lại", "Cần loại bỏ"])]
    potentials = [p for p in products if "Tiềm năng" in p.get("classification", "")]

    rev = overview.get("total_revenue", 0)
    profit = overview.get("total_profit", 0)
    margin = overview.get("avg_margin_pct", 0)
    orders = overview.get("total_orders", 0)

    md = f"""# 📊 BÁO CÁO PHÂN TÍCH LỢI NHUẬN THỰC TẾ
**Khách hàng:** {shop_name}  
**Kỳ phân tích:** {period}  
**Thời gian tạo:** {datetime.now().strftime('%d/%m/%Y %H:%M')}  

---

## 1. TỔNG QUAN HIỆU QUẢ KINH DOANH
- **Tổng doanh thu:** {rev:,.0f} đ
- **Lợi nhuận ròng thực tế:** {profit:,.0f} đ
- **Biên lợi nhuận ròng (Net Margin):** {margin:.1f}%
- **Tổng đơn hoàn thành:** {orders} đơn

### Hiệu quả theo sàn:
"""
    for pdata in platforms:
        plat = pdata.get("platform", "Khác")
        p_rev = pdata.get("revenue", 0)
        p_profit = pdata.get("profit", 0)
        p_margin = (p_profit / p_rev * 100) if p_rev else 0
        p_orders = pdata.get("orders", 0)
        md += f"- **{plat}:** {p_orders} đơn | Doanh thu: {p_rev:,.0f} đ | Lãi ròng: {p_profit:,.0f} đ ({p_margin:.1f}%)\n"

    md += """
---

## 2. PHÂN LOẠI & ĐÁNH GIÁ SẢN PHẨM

### ⭐ Sản phẩm Ngôi sao (Ưu tiên số 1: Tăng tồn kho & chạy Ads)
"""
    if stars:
        for p in stars:
            md += f"- **{p['name']}:** Lãi {p['net_profit']:,.0f} đ (Biên lãi: {p['margin_pct']:.1f}%) — Đã bán {p['quantity']} cái\n"
    else:
        md += "_Chưa có sản phẩm đạt tiêu chuẩn Ngôi sao (Margin > 30%)_\n"

    md += """
### 💛 Sản phẩm Tiềm năng (Tối ưu giá & combo để nâng margin)
"""
    for p in potentials:
        md += f"- **{p['name']}:** Lãi {p['net_profit']:,.0f} đ ({p['margin_pct']:.1f}%)\n"

    if warnings:
        md += """
### ⚠️ Sản phẩm Cần xem lại / Nguy cơ lỗ
"""
        for p in warnings:
            md += f"- **{p['name']}:** Lãi {p['net_profit']:,.0f} đ ({p['margin_pct']:.1f}%) ➔ Cân nhắc tăng giá hoặc dừng chạy Ads\n"

    md += """
---

## 3. KHUYẾN NGHỊ HÀNH ĐỘNG CỤ THỂ
1. **Tập trung nguồn vốn:** Dồn 60-70% ngân sách nhập hàng vào nhóm **Ngôi sao**.
2. **Kiểm soát chi phí sàn 2026:** Định giá bán mới phải cộng tối thiểu 18-22% phí sàn để tránh lãi ảo.
3. **Tối ưu đơn hàng combo:** Thiết lập combo 2 sản phẩm để tiết kiệm phí cố định mỗi đơn (3.000đ/đơn).

---
*Báo cáo được tạo bởi dịch vụ Shop Analytics VN.*
"""
    return md


def generate_printable_html(data: dict, shop_name: str) -> str:
    md_content = generate_executive_markdown(data, shop_name)
    # Simple clean styling for executive summary
    overview = data.get("overview", {})
    rev = overview.get("total_revenue", 0)
    profit = overview.get("total_profit", 0)
    margin = overview.get("avg_margin_pct", 0)
    orders = overview.get("total_orders", 0)

    rows_html = ""
    for p in data.get("products", []):
        rows_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;"><b>{p.get('name', '')}</b></td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: center;">{p.get('classification', '')}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right;">{p.get('quantity', 0)}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right;">{p.get('revenue', 0):,.0f} đ</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right; color: #16a34a; font-weight: bold;">{p.get('net_profit', 0):,.0f} đ</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold;">{p.get('margin_pct', 0):.1f}%</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Báo Cáo Tóm Tắt Điều Hành — {shop_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1e293b;
            background: #f8fafc;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        .report-card {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            padding: 48px;
        }}
        .header {{
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 24px;
            margin-bottom: 32px;
        }}
        .header h1 {{ margin: 0 0 8px 0; font-size: 26px; color: #0f172a; }}
        .header p {{ margin: 0; color: #64748b; font-size: 14px; }}
        .kpi-row {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 32px;
        }}
        .kpi-box {{
            background: #f1f5f9;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }}
        .kpi-box span {{ display: block; font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase; }}
        .kpi-box strong {{ display: block; font-size: 20px; color: #0f172a; margin-top: 4px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 24px 0;
            font-size: 14px;
        }}
        th {{
            background: #f1f5f9;
            padding: 12px 10px;
            text-align: left;
            border-bottom: 2px solid #cbd5e1;
            font-size: 13px;
        }}
        .btn-print {{
            display: inline-block;
            background: #4f46e5;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            margin-bottom: 24px;
            cursor: pointer;
            border: none;
        }}
        @media print {{
            body {{ background: white; padding: 0; }}
            .report-card {{ box-shadow: none; padding: 0; }}
            .btn-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="report-card">
        <button class="btn-print" onclick="window.print()">🖨️ In / Lưu file PDF (Ctrl+P)</button>
        <div class="header">
            <h1>📊 BÁO CÁO PHÂN TÍCH LỢI NHUẬN THỰC TẾ</h1>
            <p><strong>Khách hàng:</strong> {shop_name} &nbsp;|&nbsp; <strong>Kỳ:</strong> {data.get('period', 'Tháng 9/2026')} &nbsp;|&nbsp; <strong>Ngày xuất:</strong> {datetime.now().strftime('%d/%m/%Y')}</p>
        </div>

        <div class="kpi-row">
            <div class="kpi-box">
                <span>Doanh thu</span>
                <strong>{rev:,.0f} đ</strong>
            </div>
            <div class="kpi-box">
                <span>Lợi nhuận ròng</span>
                <strong style="color: #16a34a;">{profit:,.0f} đ</strong>
            </div>
            <div class="kpi-box">
                <span>Biên lợi nhuận</span>
                <strong>{margin:.1f}%</strong>
            </div>
            <div class="kpi-box">
                <span>Số đơn hàng</span>
                <strong>{orders}</strong>
            </div>
        </div>

        <h3 style="margin-top: 32px; color: #0f172a;">Chi tiết sản phẩm</h3>
        <table>
            <thead>
                <tr>
                    <th>Sản phẩm</th>
                    <th style="text-align: center;">Phân loại</th>
                    <th style="text-align: right;">SL</th>
                    <th style="text-align: right;">Doanh thu</th>
                    <th style="text-align: right;">Lợi nhuận</th>
                    <th style="text-align: right;">Margin</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>

        <div style="background: #f8fafc; border-left: 4px solid #4f46e5; padding: 16px 20px; border-radius: 4px; margin-top: 32px;">
            <h4 style="margin: 0 0 8px 0; color: #0f172a;">💡 Khuyến nghị hành động</h4>
            <p style="margin: 0; font-size: 14px; color: #334155;">
                • Dồn ngân sách đẩy mạnh các sản phẩm <strong>Ngôi sao</strong> có margin &gt; 30%.<br>
                • Đóng gói combo sản phẩm để tối ưu chi phí cố định (3.000đ/đơn) và tăng giá trị trung bình đơn.<br>
                • Rà soát thường xuyên các chương trình trợ giá voucher sàn để không bị âm margin thực tế.
            </p>
        </div>
    </div>
</body>
</html>
"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Xuất báo cáo tóm tắt executive summary")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON, help="Đường dẫn file dashboard_data.json")
    parser.add_argument("--shop", type=str, default="Shop mẫu", help="Tên shop")
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD, help="File Markdown đầu ra")
    parser.add_argument("--out-html", type=Path, default=DEFAULT_HTML, help="File HTML đầu ra")
    args = parser.parse_args()

    if not args.json.exists():
        print(f"❌ Không tìm thấy file JSON: {args.json}")
        sys.exit(1)

    with open(args.json, "r", encoding="utf-8") as f:
        data = json.load(f)

    md = generate_executive_markdown(data, args.shop)
    html = generate_printable_html(data, args.shop)

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write(md)

    args.out_html.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Đã xuất báo cáo Markdown: {args.out_md}")
    print(f"✅ Đã xuất báo cáo HTML in/PDF: {args.out_html}")


if __name__ == "__main__":
    main()
