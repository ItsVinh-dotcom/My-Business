"""
clean_data.py
-------------
Chuyển đổi file export thật từ Shopee / TikTok Shop (.xlsx, .xls, .csv)
về định dạng CSV chuẩn để run_analysis.py xử lý.

Đầu vào : File export gốc từ Seller Center (Shopee hoặc TikTok Shop)
Đầu ra  : data/processed/orders_cleaned.csv  (hoặc đường dẫn tùy chọn)

Cách chạy:
    python scripts/clean_data.py <file_export> [--platform shopee|tiktok] [--output path]

Ví dụ:
    python scripts/clean_data.py data/raw/shopee_export.xlsx --platform shopee
    python scripts/clean_data.py data/raw/tiktok_export.xlsx --platform tiktok
    python scripts/clean_data.py data/raw/export.csv --platform shopee --output clients/ShopABC/orders.csv

Yêu cầu: pip install pandas openpyxl
"""

import pandas as pd
from pathlib import Path
import argparse
import sys
import re

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── Cấu hình ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = BASE_DIR / "data" / "processed" / "orders_cleaned.csv"

# ── Column mapping cho từng sàn ─────────────────────────────────────────────
# Mỗi sàn có thể dùng nhiều tên cột khác nhau → map tất cả về chuẩn.
# Cập nhật thêm nếu sàn đổi tên cột.

SHOPEE_COLUMN_MAP = {
    # Mã đơn hàng
    "Mã đơn hàng":                      "order_id",
    "Order ID":                          "order_id",
    "order_id":                          "order_id",
    # Tên sản phẩm
    "Tên sản phẩm":                     "product_name",
    "Product Name":                      "product_name",
    "product_name":                      "product_name",
    "Tên Sản Phẩm":                     "product_name",
    # SKU
    "SKU sản phẩm":                     "sku",
    "SKU":                               "sku",
    "sku":                               "sku",
    "Mã SKU":                            "sku",
    "SKU phân loại hàng":                "sku",
    "Phân loại hàng":                    "sku",
    # Số lượng
    "Số lượng":                          "quantity",
    "Quantity":                          "quantity",
    "quantity":                          "quantity",
    "SL":                                "quantity",
    # Doanh thu
    "Tổng giá bán":                      "revenue",
    "Tổng tiền đơn hàng":               "revenue",
    "Thành tiền":                        "revenue",
    "Giá gốc":                           "revenue",
    "Người mua thanh toán":              "revenue",
    "Order Amount":                      "revenue",
    "Total Amount":                      "revenue",
    "revenue":                           "revenue",
    "Tổng số tiền (VNĐ)":               "revenue",
    "Doanh số đơn hàng":                "revenue",
    # Phí vận chuyển (shop chịu)
    "Phí vận chuyển":                    "shipping_fee",
    "Phí vận chuyển thực tế":            "shipping_fee",
    "Phí vận chuyển (người bán chịu)":   "shipping_fee",
    "Shipping Fee":                      "shipping_fee",
    "shipping_fee":                      "shipping_fee",
    "Phí ship":                          "shipping_fee",
    "Phí giao hàng người bán trả":       "shipping_fee",
    # Trạng thái
    "Trạng thái đơn hàng":              "status",
    "Order Status":                      "status",
    "status":                            "status",
    "Tình trạng đơn hàng":               "status",
    "Trạng thái":                        "status",
    # Ngày đặt hàng
    "Ngày đặt hàng":                     "order_date",
    "Thời gian đặt hàng":               "order_date",
    "Ngày tạo đơn":                      "order_date",
    "Order Creation Date":               "order_date",
    "order_date":                        "order_date",
    "Created Time":                      "order_date",
    "Thời gian tạo đơn":                "order_date",
}

TIKTOK_COLUMN_MAP = {
    # Mã đơn hàng
    "Order ID":                          "order_id",
    "Mã đơn hàng":                      "order_id",
    "order_id":                          "order_id",
    "ID đơn hàng":                       "order_id",
    # Tên sản phẩm
    "Product Name":                      "product_name",
    "Tên sản phẩm":                      "product_name",
    "product_name":                      "product_name",
    "SKU Name":                          "product_name",
    # SKU
    "Seller SKU":                        "sku",
    "SKU":                               "sku",
    "sku":                               "sku",
    "SKU ID":                            "sku",
    "Mã SKU người bán":                 "sku",
    # Số lượng
    "Quantity":                          "quantity",
    "Số lượng":                          "quantity",
    "quantity":                          "quantity",
    # Doanh thu
    "SKU Subtotal After Discount":       "revenue",
    "Total Settlement Amount":           "revenue",
    "Order Amount":                      "revenue",
    "Tổng thanh toán":                   "revenue",
    "Tổng tiền hàng":                    "revenue",
    "Total Amount":                      "revenue",
    "revenue":                           "revenue",
    "Tổng giá trị sản phẩm":            "revenue",
    "Doanh số sản phẩm":                "revenue",
    # Phí vận chuyển
    "Shipping Fee Paid by Seller":       "shipping_fee",
    "Phí vận chuyển người bán chịu":     "shipping_fee",
    "Shipping Fee":                      "shipping_fee",
    "shipping_fee":                      "shipping_fee",
    "Phí vận chuyển":                    "shipping_fee",
    # Trạng thái
    "Order Status":                      "status",
    "Trạng thái đơn hàng":              "status",
    "status":                            "status",
    "Trạng thái":                        "status",
    # Ngày
    "Created Time":                      "order_date",
    "Order Creation Date":               "order_date",
    "Thời gian tạo đơn":                "order_date",
    "Ngày tạo đơn":                      "order_date",
    "order_date":                        "order_date",
    "Thời gian đặt hàng":               "order_date",
}

# Trạng thái coi là "hoàn thành" trên từng sàn
COMPLETED_STATUSES = [
    "hoàn thành", "completed", "đã giao", "delivered",
    "giao thành công", "hoàn tất",
]


# ── Hàm đọc file ────────────────────────────────────────────────────────────
def read_file(filepath: Path) -> pd.DataFrame:
    """Đọc file export (xlsx, xls, csv) và trả về DataFrame thô."""
    suffix = filepath.suffix.lower()
    if suffix in (".xlsx", ".xls"):
        # Thử đọc từ sheet đầu tiên; nhiều file Shopee/TikTok có header ở dòng 1
        try:
            df = pd.read_excel(filepath, engine="openpyxl" if suffix == ".xlsx" else "xlrd")
        except Exception:
            # Thử bỏ dòng đầu (một số file sàn có dòng tiêu đề thừa)
            df = pd.read_excel(filepath, header=1,
                               engine="openpyxl" if suffix == ".xlsx" else "xlrd")
    elif suffix == ".csv":
        # Thử utf-8-sig (BOM) trước, fallback sang cp1252
        try:
            df = pd.read_csv(filepath, encoding="utf-8-sig")
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding="cp1252")
    else:
        raise ValueError(f"Định dạng file không hỗ trợ: {suffix}. Dùng .xlsx, .xls, hoặc .csv")
    return df


# ── Hàm phát hiện sàn tự động ───────────────────────────────────────────────
def detect_platform(df: pd.DataFrame) -> str:
    """Đoán sàn dựa trên tên cột."""
    cols_str = " ".join(str(c) for c in df.columns).lower()
    tiktok_hints = ["seller sku", "sku subtotal", "tiktok", "created time",
                    "mã sku người bán", "id đơn hàng"]
    shopee_hints = ["sku phân loại", "phân loại hàng", "shopee",
                    "sku sản phẩm", "mã đơn hàng"]
    tiktok_score = sum(1 for h in tiktok_hints if h in cols_str)
    shopee_score = sum(1 for h in shopee_hints if h in cols_str)
    if tiktok_score > shopee_score:
        return "tiktok"
    return "shopee"


# ── Hàm chuẩn hóa cột ──────────────────────────────────────────────────────
def map_columns(df: pd.DataFrame, platform: str) -> pd.DataFrame:
    """Đổi tên cột về chuẩn, giữ lại cột hữu ích."""
    col_map = TIKTOK_COLUMN_MAP if platform == "tiktok" else SHOPEE_COLUMN_MAP

    # Map cột — chỉ lấy cột đầu tiên khớp cho mỗi target
    rename_dict = {}
    mapped_targets = set()
    for orig_col in df.columns:
        target = col_map.get(orig_col) or col_map.get(str(orig_col).strip())
        if target and target not in mapped_targets:
            rename_dict[orig_col] = target
            mapped_targets.add(target)

    df = df.rename(columns=rename_dict)

    # Kiểm tra các cột bắt buộc
    required = ["order_id", "product_name", "quantity", "revenue", "status"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        available = list(df.columns)
        raise ValueError(
            f"Không tìm thấy các cột bắt buộc: {missing}\n"
            f"Các cột có trong file: {available}\n"
            f"→ Hãy kiểm tra lại file export hoặc cập nhật column mapping trong clean_data.py"
        )

    return df


# ── Hàm làm sạch ────────────────────────────────────────────────────────────
def clean_orders(df: pd.DataFrame, platform: str) -> pd.DataFrame:
    """
    Làm sạch dữ liệu:
    - Map cột về chuẩn
    - Chỉ giữ đơn 'Hoàn thành'
    - Chuẩn hóa kiểu dữ liệu
    - Loại trùng lặp
    - Thêm cột platform
    """
    df = map_columns(df, platform)

    # ── Lọc đơn hoàn thành ──
    if "status" in df.columns:
        status_lower = df["status"].astype(str).str.lower().str.strip()
        mask = status_lower.apply(
            lambda s: any(kw in s for kw in COMPLETED_STATUSES)
        )
        n_before = len(df)
        df = df[mask]
        n_filtered = n_before - len(df)
        if n_filtered > 0:
            print(f"  📋 Lọc trạng thái: bỏ {n_filtered} đơn chưa hoàn thành, giữ {len(df)} đơn")

    # ── Loại trùng ──
    if "order_id" in df.columns:
        n_before = len(df)
        df = df.drop_duplicates(subset=["order_id"])
        n_dup = n_before - len(df)
        if n_dup > 0:
            print(f"  🔄 Loại {n_dup} đơn trùng lặp")

    # ── Chuẩn hóa số ──
    num_cols = ["revenue", "shipping_fee", "quantity", "ads_cost"]
    for c in num_cols:
        if c in df.columns:
            # Xử lý format số kiểu VN: "1.500.000" hoặc "1,500,000"
            df[c] = df[c].apply(_parse_number)

    # ── Đảm bảo cột tồn tại ──
    if "shipping_fee" not in df.columns:
        df["shipping_fee"] = 0
    if "ads_cost" not in df.columns:
        df["ads_cost"] = 0
    if "sku" not in df.columns:
        # Tạo SKU tạm từ tên sản phẩm
        df["sku"] = df["product_name"].apply(_generate_sku)
        print("  ⚠️  File không có cột SKU — đã tạo SKU tạm từ tên sản phẩm")

    # ── Chuẩn hóa ngày ──
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce", dayfirst=True)
        # Chuyển về format YYYY-MM-DD
        df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")

    # ── Thêm cột platform ──
    platform_name = "TikTok" if platform == "tiktok" else "Shopee"
    if "platform" not in df.columns:
        df["platform"] = platform_name

    # ── Chỉ giữ các cột chuẩn ──
    standard_cols = [
        "order_id", "product_name", "sku", "quantity", "revenue",
        "shipping_fee", "status", "order_date", "platform", "ads_cost"
    ]
    existing_cols = [c for c in standard_cols if c in df.columns]
    df = df[existing_cols]

    return df


def _parse_number(val) -> float:
    """Chuyển giá trị (có thể là string format VN) thành float."""
    if pd.isna(val):
        return 0.0
    s = str(val).strip()
    # Loại bỏ ký tự không phải số, dấu chấm, dấu phẩy, dấu trừ
    # Format VN: 1.500.000 hoặc 1,500,000
    # Nếu có cả dấu chấm và dấu phẩy → xác định separator
    if "," in s and "." in s:
        # "1.500.000,50" → VN style: . là hàng nghìn, , là thập phân
        # "1,500,000.50" → EN style: , là hàng nghìn, . là thập phân
        last_dot = s.rfind(".")
        last_comma = s.rfind(",")
        if last_comma > last_dot:
            # VN style
            s = s.replace(".", "").replace(",", ".")
        else:
            # EN style
            s = s.replace(",", "")
    elif "," in s:
        # Chỉ có dấu phẩy → có thể là "1,500" (EN thousands) hoặc "1,5" (VN decimal)
        parts = s.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Likely decimal: "1,5" → "1.5"
            s = s.replace(",", ".")
        else:
            # Likely thousands: "1,500,000"
            s = s.replace(",", "")
    elif "." in s:
        # Chỉ có dấu chấm → "1.500.000" hoặc "150.000" (VN thousands) hoặc "1.5" (EN decimal)
        parts = s.split(".")
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3):
            # VN thousands: "150.000" hoặc "1.500.000"
            s = s.replace(".", "")
        # else: normal decimal, keep as is

    # Loại bỏ các ký tự thừa (đ, VND, ₫, khoảng trắng)
    s = re.sub(r"[^\d.\-]", "", s)
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def _generate_sku(product_name: str) -> str:
    """Tạo SKU tạm từ tên sản phẩm."""
    if pd.isna(product_name):
        return "UNKNOWN"
    # Lấy chữ cái đầu mỗi từ + hash
    words = str(product_name).strip().split()
    prefix = "".join(w[0].upper() for w in words[:4] if w)
    hash_val = abs(hash(product_name)) % 10000
    return f"{prefix}-{hash_val:04d}"


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Chuyển đổi file export Shopee/TikTok Shop về CSV chuẩn",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python scripts/clean_data.py data/raw/shopee_export.xlsx
  python scripts/clean_data.py data/raw/tiktok_orders.csv --platform tiktok
  python scripts/clean_data.py data/raw/export.xlsx -o clients/ShopABC/orders.csv
        """,
    )
    ap.add_argument("input_file", type=Path, help="File export từ sàn (.xlsx, .xls, .csv)")
    ap.add_argument("--platform", "-p", choices=["shopee", "tiktok"],
                    help="Sàn: shopee hoặc tiktok (tự phát hiện nếu bỏ trống)")
    ap.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT,
                    help=f"File CSV đầu ra (mặc định: {DEFAULT_OUTPUT.name})")
    args = ap.parse_args()

    # Kiểm tra file tồn tại
    if not args.input_file.exists():
        print(f"❌ Không tìm thấy file: {args.input_file}")
        sys.exit(1)

    print(f"\n📂 Đang đọc file: {args.input_file.name}")
    raw_df = read_file(args.input_file)
    print(f"  📊 Số dòng thô: {len(raw_df)}")
    print(f"  📋 Các cột: {list(raw_df.columns)}")

    # Phát hiện sàn nếu không chỉ định
    platform = args.platform
    if not platform:
        platform = detect_platform(raw_df)
        print(f"  🔍 Phát hiện sàn: {platform.upper()}")
    else:
        print(f"  🏪 Sàn: {platform.upper()}")

    # Làm sạch
    try:
        cleaned_df = clean_orders(raw_df, platform)
    except ValueError as e:
        print(f"\n❌ Lỗi: {e}")
        sys.exit(1)

    # Lưu file
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(args.output, index=False, encoding="utf-8-sig")

    print(f"\n✅ Đã lưu {len(cleaned_df)} đơn hàng sạch → {args.output}")
    print(f"   Tiếp theo: python scripts/run_analysis.py --orders {args.output}")
