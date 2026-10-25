"""
run_analysis.py
---------------
Pipeline phân tích lợi nhuận hoàn chỉnh — chạy 1 lệnh ra kết quả luôn.

Đầu vào : data/raw/sample_orders.csv
           data/raw/product_cost.csv
           data/reference/platform_fees.csv
Đầu ra  : data/processed/orders_cleaned.csv
           analysis/product_ranking.csv
           reports/delivered/bao_cao_loi_nhuan.txt  (báo cáo text)
           analysis/dashboard_data.json
           reports/dashboard.html  (nhúng lại dữ liệu mới vào dashboard)

Cách chạy:
    python scripts/run_analysis.py

Tùy chọn:
    python scripts/run_analysis.py --orders data/raw/shop_x.csv --cost data/raw/cost_x.csv --shop "Shop X"

So sánh với tháng trước:
    python scripts/run_analysis.py --prev-orders data/raw/thang_truoc.csv

Yêu cầu: pip install pandas
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import re
import argparse
import sys

# Đảm bảo in tiếng Việt và emoji không bị lỗi trên Windows PowerShell / CMD
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── Cấu hình đường dẫn ──────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent

RAW_ORDERS   = BASE / "data" / "raw"       / "sample_orders.csv"
RAW_COST     = BASE / "data" / "raw"       / "product_cost.csv"
FEE_REF      = BASE / "data" / "reference" / "platform_fees.csv"
OUT_CLEAN    = BASE / "data" / "processed" / "orders_cleaned.csv"
OUT_RANK     = BASE / "analysis"           / "product_ranking.csv"
OUT_REPORT   = BASE / "reports" / "delivered" / "bao_cao_loi_nhuan.txt"
OUT_JSON     = BASE / "analysis" / "dashboard_data.json"
DASHBOARD    = BASE / "reports" / "dashboard.html"

# ── Cấu hình phí sàn ────────────────────────────────────────────────────────
def load_platform_fees(path: Path) -> dict:
    """
    Đọc bảng phí sàn từ file tham chiếu, tổng hợp theo sàn.
    Trả về: {"Shopee": {"pct": 17.32, "fixed": 3000}, ...}
      - pct   : tổng % phí tính trên doanh thu
      - fixed : tổng phí cố định (VND) mỗi đơn
    Chỉ cộng các dòng có apply = 1.
    """
    if path.exists():
        fees_df = pd.read_csv(path, encoding="utf-8-sig")
        if "apply" in fees_df.columns:
            fees_df = fees_df[fees_df["apply"].fillna(1).astype(int) == 1]
        if "fixed_vnd_per_order" not in fees_df.columns:
            fees_df["fixed_vnd_per_order"] = 0
        g = fees_df.groupby("platform").agg(
            pct=("rate_pct", "sum"), fixed=("fixed_vnd_per_order", "sum"))
        return {k: {"pct": float(v["pct"]), "fixed": float(v["fixed"])}
                for k, v in g.iterrows()}
    # Fallback nếu chưa có file (ước tính thận trọng 2026)
    print("  ⚠️  Không thấy file phí sàn — dùng mức ước tính 18% + 3.000đ/đơn")
    return {"Shopee": {"pct": 18.0, "fixed": 3000}, "TikTok": {"pct": 21.5, "fixed": 3000}}

DEFAULT_FEE = {"pct": 18.0, "fixed": 3000}

PACKAGING_COST_PER_ORDER = 5_000   # Chi phí đóng gói / đơn (VND)

# ── Step 1: Đọc & làm sạch dữ liệu ─────────────────────────────────────────
def clean_orders(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")

    # Chỉ giữ đơn hoàn thành
    df = df[df["status"].str.contains("Hoàn thành|Completed", case=False, na=False)]
    df = df.drop_duplicates(subset=["order_id"])

    num_cols = ["revenue", "shipping_fee", "quantity", "ads_cost"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # Đảm bảo cột ads_cost tồn tại
    if "ads_cost" not in df.columns:
        df["ads_cost"] = 0

    print(f"  ✅ Đọc xong: {len(df)} đơn hàng hợp lệ")
    return df


# ── Step 2: Tính lợi nhuận từng đơn ─────────────────────────────────────────
def calculate_profit(orders: pd.DataFrame, cost_df: pd.DataFrame, fee_rates: dict) -> pd.DataFrame:
    df = orders.merge(
        cost_df[["sku", "cost_price", "category"]],
        on="sku", how="left"
    )

    # Phí sàn theo platform (từ file tham chiếu): % doanh thu + phí cố định/đơn
    unknown = set(df["platform"].unique()) - set(fee_rates)
    if unknown:
        print(f"  ⚠️  Chưa có biểu phí cho sàn {unknown} — dùng mặc định {DEFAULT_FEE}")
    rate  = df["platform"].map(lambda p: fee_rates.get(p, DEFAULT_FEE)["pct"])
    fixed = df["platform"].map(lambda p: fee_rates.get(p, DEFAULT_FEE)["fixed"])
    df["platform_fee_rate"] = rate / 100
    df["platform_fee"]      = (df["revenue"] * df["platform_fee_rate"] + fixed).round(0)

    missing_cost = df[df["cost_price"].isna()]["sku"].unique()
    if len(missing_cost):
        print(f"  ⚠️  {len(missing_cost)} SKU chưa có giá vốn (đang tính = 0): {list(missing_cost)[:10]}")

    # Các chi phí
    df["packaging_cost"] = PACKAGING_COST_PER_ORDER
    df["cost_price"]     = df["cost_price"].fillna(0)
    df["total_cogs"]     = df["cost_price"] * df["quantity"]
    df["total_cost"]     = (df["total_cogs"] + df["platform_fee"]
                            + df["shipping_fee"] + df["packaging_cost"]
                            + df["ads_cost"])
    df["net_profit"]     = df["revenue"] - df["total_cost"]
    df["margin_pct"]     = (df["net_profit"] / df["revenue"].replace(0, 1) * 100).round(1)

    return df


# ── Step 3: Tổng hợp theo sản phẩm ─────────────────────────────────────────
def summarize_by_product(df: pd.DataFrame) -> pd.DataFrame:
    # Lấy tên sản phẩm cơ bản (bỏ phần size)
    df["product_base"] = df["product_name"]

    summary = df.groupby(["product_base", "category"]).agg(
        so_don         = ("order_id",       "count"),
        tong_so_luong  = ("quantity",       "sum"),
        doanh_thu      = ("revenue",        "sum"),
        gia_von        = ("total_cogs",     "sum"),
        phi_san        = ("platform_fee",   "sum"),
        phi_ship       = ("shipping_fee",   "sum"),
        dong_goi       = ("packaging_cost", "sum"),
        phi_ads        = ("ads_cost",       "sum"),
        loi_nhuan_rong = ("net_profit",     "sum"),
    ).reset_index()

    summary["margin_pct"] = (
        summary["loi_nhuan_rong"] / summary["doanh_thu"].replace(0, 1) * 100
    ).round(1)

    summary = summary.sort_values("loi_nhuan_rong", ascending=False)
    summary["phan_loai"] = summary["margin_pct"].apply(classify)

    return summary


def classify(margin: float) -> str:
    if margin > 30:   return "⭐ Ngôi sao"
    if margin > 15:   return "💛 Tiềm năng"
    if margin >= 0:   return "⚠️ Cần xem lại"
    return "❌ Cần loại bỏ"


def detect_period(orders: pd.DataFrame) -> str:
    """Tự xác định kỳ báo cáo từ cột order_date."""
    d = pd.to_datetime(orders["order_date"], errors="coerce").dropna()
    if d.empty:
        return "Không rõ kỳ"
    months = sorted({(x.year, x.month) for x in d})
    if len(months) == 1:
        return f"Tháng {months[0][1]}/{months[0][0]}"
    return f"{d.min():%d/%m/%Y} – {d.max():%d/%m/%Y}"


# ── Step 3b: So sánh với kỳ trước ───────────────────────────────────────────
def compare_periods(current: pd.DataFrame, prev: pd.DataFrame) -> list:
    """So sánh tổng hợp sản phẩm giữa kỳ hiện tại và kỳ trước.
    Trả về danh sách dict chứa thay đổi từng sản phẩm."""
    merged = current.merge(
        prev[["product_base", "doanh_thu", "loi_nhuan_rong", "margin_pct", "so_don"]],
        on="product_base", how="left", suffixes=("", "_prev")
    )
    changes = []
    for _, row in merged.iterrows():
        rev_now  = float(row["doanh_thu"])
        rev_prev = float(row.get("doanh_thu_prev", 0) or 0)
        pft_now  = float(row["loi_nhuan_rong"])
        pft_prev = float(row.get("loi_nhuan_rong_prev", 0) or 0)
        mgn_now  = float(row["margin_pct"])
        mgn_prev = float(row.get("margin_pct_prev", 0) or 0)
        ord_now  = int(row["so_don"])
        ord_prev = int(row.get("so_don_prev", 0) or 0)

        rev_change = ((rev_now - rev_prev) / rev_prev * 100) if rev_prev else 0
        pft_change = ((pft_now - pft_prev) / abs(pft_prev) * 100) if pft_prev else 0
        mgn_change = mgn_now - mgn_prev

        changes.append({
            "product":       row["product_base"],
            "revenue_now":   rev_now,
            "revenue_prev":  rev_prev,
            "revenue_change_pct": round(rev_change, 1),
            "profit_now":    pft_now,
            "profit_prev":   pft_prev,
            "profit_change_pct": round(pft_change, 1),
            "margin_now":    mgn_now,
            "margin_prev":   mgn_prev,
            "margin_change":  round(mgn_change, 1),
            "orders_now":    ord_now,
            "orders_prev":   ord_prev,
        })
    return changes


def print_comparison(changes: list) -> str:
    """In bảng so sánh tháng ra text."""
    lines = []
    lines.append("")
    lines.append("─" * 62)
    lines.append("📊 SO SÁNH VỚI KỲ TRƯỚC")
    lines.append("─" * 62)

    for c in changes:
        arrow_rev = "📈" if c["revenue_change_pct"] > 0 else "📉" if c["revenue_change_pct"] < 0 else "➡️"
        arrow_pft = "📈" if c["profit_change_pct"] > 0 else "📉" if c["profit_change_pct"] < 0 else "➡️"
        arrow_mgn = "🔺" if c["margin_change"] > 0 else "🔻" if c["margin_change"] < 0 else "➡️"

        lines.append(f"\n  {c['product']}")
        lines.append(f"    Doanh thu : {c['revenue_prev']:>12,.0f} → {c['revenue_now']:>12,.0f}đ  {arrow_rev} {c['revenue_change_pct']:+.1f}%")
        lines.append(f"    Lợi nhuận : {c['profit_prev']:>12,.0f} → {c['profit_now']:>12,.0f}đ  {arrow_pft} {c['profit_change_pct']:+.1f}%")
        lines.append(f"    Margin    : {c['margin_prev']:>11.1f}% → {c['margin_now']:>10.1f}%  {arrow_mgn} {c['margin_change']:+.1f}pp")
        lines.append(f"    Số đơn    : {c['orders_prev']:>12} → {c['orders_now']:>12}")

    text = "\n".join(lines)
    print(text)
    return text


# ── Step 3c: Cảnh báo margin giảm ───────────────────────────────────────────
def margin_alerts(current: pd.DataFrame, prev: pd.DataFrame = None,
                  drop_threshold: float = 5.0) -> list:
    """Phát hiện sản phẩm có margin thấp hoặc giảm so với kỳ trước.
    - Margin âm: cảnh báo đỏ
    - Margin < 10%: cảnh báo cam
    - Margin giảm > drop_threshold pp so với kỳ trước: cảnh báo vàng
    Trả về danh sách cảnh báo.
    """
    alerts = []

    for _, row in current.iterrows():
        name = row["product_base"]
        mgn = float(row["margin_pct"])

        if mgn < 0:
            alerts.append({
                "level": "🔴 NGHIÊM TRỌNG",
                "product": name,
                "margin": mgn,
                "message": f"Margin ÂM ({mgn:.1f}%) — đang LỖ mỗi đơn bán ra!",
            })
        elif mgn < 10:
            alerts.append({
                "level": "🟠 CẢNH BÁO",
                "product": name,
                "margin": mgn,
                "message": f"Margin rất thấp ({mgn:.1f}%) — gần hòa vốn, rủi ro lỗ.",
            })

    # So sánh margin giảm so với kỳ trước
    if prev is not None:
        prev_margins = dict(zip(prev["product_base"], prev["margin_pct"]))
        for _, row in current.iterrows():
            name = row["product_base"]
            mgn_now = float(row["margin_pct"])
            mgn_prev = float(prev_margins.get(name, mgn_now))
            drop = mgn_prev - mgn_now
            if drop >= drop_threshold:
                alerts.append({
                    "level": "🟡 THEO DÕI",
                    "product": name,
                    "margin": mgn_now,
                    "message": f"Margin GIẢM {drop:.1f}pp ({mgn_prev:.1f}% → {mgn_now:.1f}%) so với kỳ trước!",
                })

    return alerts


def print_alerts(alerts: list) -> str:
    """In danh sách cảnh báo."""
    if not alerts:
        return ""
    lines = []
    lines.append("")
    lines.append("─" * 62)
    lines.append("🚨 CẢNH BÁO MARGIN")
    lines.append("─" * 62)
    for a in alerts:
        lines.append(f"  {a['level']}  {a['product']}")
        lines.append(f"    {a['message']}")
    text = "\n".join(lines)
    print(text)
    return text


# ── Step 4: Xuất báo cáo text ────────────────────────────────────────────────
def print_report(summary: pd.DataFrame, orders: pd.DataFrame, period: str, shop: str):
    total_rev    = orders["revenue"].sum()
    total_profit = orders["net_profit"].sum()
    total_ads    = orders["ads_cost"].sum()
    avg_margin   = (total_profit / total_rev * 100) if total_rev else 0

    lines = []
    lines.append("=" * 62)
    lines.append(f"     BÁO CÁO LỢI NHUẬN THEO SẢN PHẨM — {period.upper()}")
    lines.append(f"     Shop: {shop}")
    lines.append(f"     Xuất ngày: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append("=" * 62)
    lines.append("")
    lines.append("📊 TỔNG QUAN")
    lines.append(f"   Tổng doanh thu    : {total_rev:>12,.0f} đ")
    lines.append(f"   Tổng lợi nhuận    : {total_profit:>12,.0f} đ")
    lines.append(f"   Tổng chi phí Ads  : {total_ads:>12,.0f} đ")
    lines.append(f"   Biên lợi nhuận TB : {avg_margin:>11.1f}%")
    lines.append(f"   Tổng số đơn       : {len(orders):>12,} đơn")
    lines.append("")
    lines.append("─" * 62)
    lines.append("📦 CHI TIẾT TỪNG SẢN PHẨM")
    lines.append("─" * 62)

    for _, row in summary.iterrows():
        lines.append(f"\n  {row['phan_loai']}  {row['product_base']}")
        lines.append(f"    Số đơn      : {row['so_don']:>6} đơn  |  Số lượng: {row['tong_so_luong']:>5}")
        lines.append(f"    Doanh thu   : {row['doanh_thu']:>12,.0f} đ")
        lines.append(f"    Giá vốn     : {row['gia_von']:>12,.0f} đ")
        lines.append(f"    Phí sàn     : {row['phi_san']:>12,.0f} đ")
        lines.append(f"    Phí ship    : {row['phi_ship']:>12,.0f} đ")
        lines.append(f"    Đóng gói    : {row['dong_goi']:>12,.0f} đ")
        lines.append(f"    Chi phí Ads : {row['phi_ads']:>12,.0f} đ")
        lines.append(f"    ► Lợi nhuận : {row['loi_nhuan_rong']:>12,.0f} đ  ({row['margin_pct']}%)")

    lines.append("")
    lines.append("─" * 62)
    lines.append("💡 KHUYẾN NGHỊ")
    lines.append("─" * 62)

    stars    = summary[summary["phan_loai"].str.startswith("⭐")]
    potential = summary[summary["phan_loai"].str.startswith("💛")]
    warnings = summary[summary["phan_loai"].str.startswith("⚠")]
    drops    = summary[summary["phan_loai"].str.startswith("❌")]

    if not stars.empty:
        lines.append("\n  🚀 Tăng tồn kho & đẩy ads cho:")
        for _, r in stars.iterrows():
            lines.append(f"     • {r['product_base']} (margin {r['margin_pct']}%)")

    if not potential.empty:
        lines.append("\n  💛 Tối ưu giá / giảm chi phí ads, test voucher:")
        for _, r in potential.iterrows():
            lines.append(f"     • {r['product_base']} (margin {r['margin_pct']}%)")

    if not warnings.empty:
        lines.append("\n  🔧 Cần tối ưu chi phí hoặc tăng giá:")
        for _, r in warnings.iterrows():
            lines.append(f"     • {r['product_base']} (margin {r['margin_pct']}%)")

    if not drops.empty:
        lines.append("\n  🛑 Cân nhắc ngừng kinh doanh:")
        for _, r in drops.iterrows():
            lines.append(f"     • {r['product_base']} (margin {r['margin_pct']}%)")

    lines.append("")
    lines.append("=" * 62)

    report_text = "\n".join(lines)
    print(report_text)
    return report_text


# ── Step 5: Xuất JSON cho Dashboard ─────────────────────────────────────────
def export_dashboard_json(summary: pd.DataFrame, orders: pd.DataFrame, output: Path,
                          period: str, shop: str, fee_rates: dict) -> dict:
    """Xuất dữ liệu JSON để dashboard HTML đọc trực tiếp."""
    total_rev    = float(orders["revenue"].sum())
    total_profit = float(orders["net_profit"].sum())
    total_ads    = float(orders["ads_cost"].sum())
    total_cogs   = float(orders["total_cogs"].sum())
    total_pfee   = float(orders["platform_fee"].sum())
    total_ship   = float(orders["shipping_fee"].sum())
    total_pack   = float(orders["packaging_cost"].sum())
    avg_margin   = round((total_profit / total_rev * 100), 1) if total_rev else 0

    # Sản phẩm chi tiết
    products = []
    for _, row in summary.iterrows():
        products.append({
            "name":       row["product_base"],
            "category":   row["category"],
            "orders":     int(row["so_don"]),
            "quantity":   int(row["tong_so_luong"]),
            "revenue":    float(row["doanh_thu"]),
            "cogs":       float(row["gia_von"]),
            "platform_fee": float(row["phi_san"]),
            "shipping":   float(row["phi_ship"]),
            "packaging":  float(row["dong_goi"]),
            "ads_cost":   float(row["phi_ads"]),
            "net_profit": float(row["loi_nhuan_rong"]),
            "margin_pct": float(row["margin_pct"]),
            "classification": row["phan_loai"],
        })

    # Doanh thu theo ngày
    daily = orders.groupby("order_date").agg(
        revenue    = ("revenue",    "sum"),
        profit     = ("net_profit", "sum"),
        orders_cnt = ("order_id",   "count"),
    ).reset_index()
    daily_data = []
    for _, row in daily.iterrows():
        daily_data.append({
            "date":    str(row["order_date"]),
            "revenue": float(row["revenue"]),
            "profit":  float(row["profit"]),
            "orders":  int(row["orders_cnt"]),
        })

    # Phân bổ theo sàn
    by_platform = orders.groupby("platform").agg(
        revenue = ("revenue",    "sum"),
        profit  = ("net_profit", "sum"),
        orders  = ("order_id",   "count"),
    ).reset_index()
    platform_data = []
    for _, row in by_platform.iterrows():
        platform_data.append({
            "platform": row["platform"],
            "revenue":  float(row["revenue"]),
            "profit":   float(row["profit"]),
            "orders":   int(row["orders"]),
        })

    dashboard = {
        "report_date": datetime.now().strftime("%d/%m/%Y"),
        "period":      period,
        "shop_name":   shop,
        "fee_assumptions": fee_rates,
        "overview": {
            "total_revenue":   total_rev,
            "total_profit":    total_profit,
            "total_ads_cost":  total_ads,
            "total_cogs":      total_cogs,
            "total_platform_fee": total_pfee,
            "total_shipping":  total_ship,
            "total_packaging": total_pack,
            "avg_margin_pct":  avg_margin,
            "total_orders":    len(orders),
        },
        "products":     products,
        "daily_trend":  daily_data,
        "by_platform":  platform_data,
    }

    output.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  📊 Đã xuất dữ liệu dashboard → {output.name}")
    return dashboard


# ── Step 6: Nhúng dữ liệu mới vào dashboard.html ───────────────────────────
def update_dashboard_html(dashboard: dict, html_path: Path):
    """Thay khối `const DATA = {...};` trong dashboard.html bằng dữ liệu mới."""
    if not html_path.exists():
        print(f"  ⚠️  Không thấy {html_path.name} — bỏ qua bước cập nhật dashboard")
        return
    html = html_path.read_text(encoding="utf-8")
    payload = json.dumps(dashboard, ensure_ascii=False, indent=2)
    new_html, n = re.subn(r"const DATA = \{.*?\n\};", lambda m: f"const DATA = {payload};",
                          html, count=1, flags=re.S)
    if n == 0:
        print("  ⚠️  Không tìm thấy khối `const DATA = {...};` trong dashboard.html")
        return
    html_path.write_text(new_html, encoding="utf-8")
    print(f"  🖥️  Đã cập nhật dữ liệu vào → reports/{html_path.name}")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Phân tích lợi nhuận shop online")
    ap.add_argument("--orders", type=Path, default=RAW_ORDERS, help="File đơn hàng (CSV)")
    ap.add_argument("--cost",   type=Path, default=RAW_COST,   help="File giá vốn (CSV)")
    ap.add_argument("--shop",   default="Shop mẫu (dữ liệu minh họa)", help="Tên shop in trên báo cáo")
    ap.add_argument("--prev-orders", type=Path, default=None,
                    help="File đơn hàng kỳ trước (CSV) — để so sánh tháng")
    ap.add_argument("--prev-cost", type=Path, default=None,
                    help="File giá vốn kỳ trước (nếu khác kỳ hiện tại)")
    args = ap.parse_args()

    print("\n🚀 Bắt đầu phân tích lợi nhuận...")
    print(f"  📂 Đọc dữ liệu từ: {args.orders.name}")

    # ── Kiểm tra file tồn tại ──
    if not args.orders.exists():
        print(f"\n❌ Lỗi: Không tìm thấy file đơn hàng: {args.orders}")
        print(f"   Hãy kiểm tra đường dẫn hoặc xem README.md để biết định dạng file cần thiết.")
        sys.exit(1)
    if not args.cost.exists():
        print(f"\n❌ Lỗi: Không tìm thấy file giá vốn: {args.cost}")
        print(f"   Cần file CSV với cột: sku, product_name, cost_price, category")
        sys.exit(1)

    try:
        # Load phí sàn từ file tham chiếu
        fee_rates = load_platform_fees(FEE_REF)
        for p, f in fee_rates.items():
            print(f"  💰 Phí sàn {p}: {f['pct']:.2f}% + {f['fixed']:,.0f}đ/đơn")

        # Step 1 — Clean
        orders_raw = clean_orders(args.orders)
        if orders_raw.empty:
            print("\n❌ Lỗi: Không có đơn hàng nào hợp lệ (trạng thái 'Hoàn thành').")
            sys.exit(1)
        cost_df = pd.read_csv(args.cost, encoding="utf-8-sig")
        period  = detect_period(orders_raw)

        # Step 2 — Calculate
        orders_full = calculate_profit(orders_raw, cost_df, fee_rates)
        OUT_CLEAN.parent.mkdir(parents=True, exist_ok=True)
        orders_full.to_csv(OUT_CLEAN, index=False, encoding="utf-8-sig")
        print(f"  💾 Đã lưu dữ liệu sạch → {OUT_CLEAN.name}")

        # Step 3 — Summarize
        summary = summarize_by_product(orders_full)
        summary.to_csv(OUT_RANK, index=False, encoding="utf-8-sig")
        print(f"  📊 Đã lưu xếp hạng sản phẩm → {OUT_RANK.name}")

        # Step 3b — So sánh với kỳ trước (nếu có)
        comparison_data = None
        prev_summary = None
        if args.prev_orders and args.prev_orders.exists():
            print(f"\n  🔄 So sánh với kỳ trước: {args.prev_orders.name}")
            prev_cost_path = args.prev_cost if args.prev_cost else args.cost
            prev_raw = clean_orders(args.prev_orders)
            if not prev_raw.empty:
                prev_cost_df = pd.read_csv(prev_cost_path, encoding="utf-8-sig")
                prev_full = calculate_profit(prev_raw, prev_cost_df, fee_rates)
                prev_summary = summarize_by_product(prev_full)
                comparison_data = compare_periods(summary, prev_summary)
        elif args.prev_orders:
            print(f"  ⚠️  File kỳ trước không tồn tại: {args.prev_orders} — bỏ qua so sánh")

        # Step 3c — Cảnh báo margin
        alerts_list = margin_alerts(summary, prev_summary)

        # Step 4 — Report
        print(f"\n{'─'*62}")
        report_text = print_report(summary, orders_full, period, args.shop)

        # Thêm so sánh vào báo cáo (nếu có)
        if comparison_data:
            report_text += "\n" + print_comparison(comparison_data)

        # Thêm cảnh báo vào báo cáo (nếu có)
        if alerts_list:
            report_text += "\n" + print_alerts(alerts_list)

        OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
        OUT_REPORT.write_text(report_text, encoding="utf-8")
        print(f"\n  📄 Đã lưu báo cáo → {OUT_REPORT}")

        # Step 5 — Dashboard JSON
        dashboard = export_dashboard_json(summary, orders_full, OUT_JSON, period, args.shop, fee_rates)
        # Thêm dữ liệu so sánh và cảnh báo vào JSON
        if comparison_data:
            dashboard["comparison"] = comparison_data
        if alerts_list:
            dashboard["margin_alerts"] = alerts_list
            OUT_JSON.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8")

        # Step 6 — Dashboard HTML
        update_dashboard_html(dashboard, DASHBOARD)

        print(f"\n✅ Hoàn tất! Kiểm tra thư mục analysis/ và reports/\n")

    except FileNotFoundError as e:
        print(f"\n❌ Lỗi: File không tìm thấy — {e}")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"\n❌ Lỗi: File dữ liệu trống hoặc không có nội dung.")
        sys.exit(1)
    except KeyError as e:
        print(f"\n❌ Lỗi: Thiếu cột bắt buộc trong file dữ liệu — {e}")
        print(f"   Kiểm tra lại format file. Cần có: order_id, product_name, sku, quantity, revenue, shipping_fee, status, order_date, platform")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Lỗi không mong đợi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
