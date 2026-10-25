"""
⚠️ FILE DEPRECATED — KHÔNG SỬ DỤNG.

Phí sàn cố định 4% đã lỗi thời (thực tế 2026: Shopee ~17.3%, TikTok ~21.5%).
File này chỉ giữ lại để tham khảo lịch sử.

═══════════════════════════════════════════════════════════════
  THAY THẾ BẰNG: scripts/run_analysis.py
  Pipeline hoàn chỉnh: tính phí sàn từ file tham chiếu,
  xuất dashboard, báo cáo text, JSON — chạy 1 lệnh.

  python scripts/run_analysis.py
═══════════════════════════════════════════════════════════════

calculate_profit.py (cũ)
-------------------
Tính lợi nhuận ròng với phí sàn cố định 4% — SAI SO VỚI THỰC TẾ.
"""

import warnings
warnings.warn(
    "calculate_profit.py đã lỗi thời (phí sàn 4% không đúng thực tế 2026). "
    "Dùng scripts/run_analysis.py thay thế.",
    DeprecationWarning,
    stacklevel=2,
)

import pandas as pd
from pathlib import Path
import sys

# ── Cấu hình ────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).resolve().parent.parent
PROCESSED    = BASE_DIR / "data" / "processed" / "orders_cleaned.csv"
COST_FILE    = BASE_DIR / "data" / "raw" / "product_cost.xlsx"
OUTPUT_FILE  = BASE_DIR / "analysis" / "product_ranking.xlsx"

# ⚠️ Tỷ lệ phí sàn (%) — SAI, CHỈ 4% thay vì ~17-22%
PLATFORM_FEE_RATE = 0.04   # ← LỖI THỜI

# ── Phân loại sản phẩm ──────────────────────────────────────────────────────
def classify_product(margin: float) -> str:
    if margin > 30:
        return "⭐ Ngôi sao"
    elif margin > 15:
        return "💛 Tiềm năng"
    elif margin >= 0:
        return "⚠️ Cần xem lại"
    else:
        return "❌ Cần loại bỏ"


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("⚠️  FILE NÀY ĐÃ LỖI THỜI — ĐỪNG DÙNG!")
    print("   Phí sàn 4% không đúng thực tế (2026: ~17-22%)")
    print()
    print("   Thay thế bằng:")
    print("   python scripts/run_analysis.py")
    print("=" * 60)
    sys.exit(1)
