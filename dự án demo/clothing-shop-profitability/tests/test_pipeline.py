"""
tests/test_pipeline.py
----------------------
Unit tests cho pipeline phân tích lợi nhuận.

Chạy: pytest tests/ -v
Hoặc: python -m pytest tests/ -v
"""

import pytest
import pandas as pd
from pathlib import Path
import sys
import json

# Thêm thư mục scripts vào path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from run_analysis import (
    load_platform_fees,
    clean_orders,
    calculate_profit,
    summarize_by_product,
    classify,
    detect_period,
    export_dashboard_json,
    compare_periods,
    margin_alerts,
)

# ── Fixtures ─────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent


@pytest.fixture
def sample_orders_path():
    return BASE / "data" / "raw" / "sample_orders.csv"


@pytest.fixture
def product_cost_path():
    return BASE / "data" / "raw" / "product_cost.csv"


@pytest.fixture
def platform_fees_path():
    return BASE / "data" / "reference" / "platform_fees.csv"


@pytest.fixture
def sample_orders(sample_orders_path):
    return clean_orders(sample_orders_path)


@pytest.fixture
def cost_df(product_cost_path):
    return pd.read_csv(product_cost_path, encoding="utf-8-sig")


@pytest.fixture
def fee_rates(platform_fees_path):
    return load_platform_fees(platform_fees_path)


@pytest.fixture
def orders_full(sample_orders, cost_df, fee_rates):
    return calculate_profit(sample_orders, cost_df, fee_rates)


@pytest.fixture
def summary(orders_full):
    return summarize_by_product(orders_full)


# ── Test: Load Platform Fees ────────────────────────────────────────────────
class TestLoadPlatformFees:
    def test_loads_from_file(self, platform_fees_path):
        fees = load_platform_fees(platform_fees_path)
        assert "Shopee" in fees
        assert "TikTok" in fees
        assert "pct" in fees["Shopee"]
        assert "fixed" in fees["Shopee"]

    def test_shopee_fee_reasonable(self, fee_rates):
        """Phí Shopee 2026 nên khoảng 15-20%."""
        assert 10 < fee_rates["Shopee"]["pct"] < 25

    def test_tiktok_fee_reasonable(self, fee_rates):
        """Phí TikTok 2026 nên khoảng 18-25%."""
        assert 15 < fee_rates["TikTok"]["pct"] < 30

    def test_fixed_fee_is_3000(self, fee_rates):
        """Phí cố định / đơn nên là 3.000đ."""
        assert fee_rates["Shopee"]["fixed"] == 3000
        assert fee_rates["TikTok"]["fixed"] == 3000

    def test_fallback_when_file_missing(self, tmp_path):
        fees = load_platform_fees(tmp_path / "nonexistent.csv")
        assert "Shopee" in fees
        assert "TikTok" in fees


# ── Test: Clean Orders ──────────────────────────────────────────────────────
class TestCleanOrders:
    def test_returns_dataframe(self, sample_orders):
        assert isinstance(sample_orders, pd.DataFrame)

    def test_only_completed_orders(self, sample_orders):
        assert all(
            "hoàn thành" in str(s).lower() or "completed" in str(s).lower()
            for s in sample_orders["status"]
        )

    def test_no_duplicate_order_ids(self, sample_orders):
        assert sample_orders["order_id"].is_unique

    def test_numeric_columns(self, sample_orders):
        for col in ["revenue", "shipping_fee", "quantity"]:
            assert pd.api.types.is_numeric_dtype(sample_orders[col])

    def test_has_required_columns(self, sample_orders):
        required = ["order_id", "product_name", "sku", "quantity", "revenue",
                     "shipping_fee", "status", "order_date", "platform"]
        for col in required:
            assert col in sample_orders.columns, f"Thiếu cột: {col}"

    def test_order_count(self, sample_orders):
        """Dữ liệu mẫu có 46 dòng, 1 trùng → 45 đơn hợp lệ."""
        assert len(sample_orders) == 45


# ── Test: Calculate Profit ──────────────────────────────────────────────────
class TestCalculateProfit:
    def test_has_profit_columns(self, orders_full):
        expected_cols = ["platform_fee", "packaging_cost", "total_cogs",
                         "total_cost", "net_profit", "margin_pct"]
        for col in expected_cols:
            assert col in orders_full.columns, f"Thiếu cột: {col}"

    def test_profit_formula(self, orders_full):
        """Lợi nhuận = Doanh thu - Tổng chi phí."""
        for _, row in orders_full.head(5).iterrows():
            expected = row["revenue"] - row["total_cost"]
            assert abs(row["net_profit"] - expected) < 1, \
                f"Công thức sai cho đơn {row['order_id']}"

    def test_platform_fee_positive(self, orders_full):
        """Phí sàn phải > 0 khi doanh thu > 0."""
        has_revenue = orders_full[orders_full["revenue"] > 0]
        assert (has_revenue["platform_fee"] > 0).all()

    def test_total_revenue_reasonable(self, orders_full):
        """Tổng doanh thu phải > 0."""
        assert orders_full["revenue"].sum() > 0

    def test_packaging_cost_per_order(self, orders_full):
        """Mỗi đơn có chi phí đóng gói 5.000đ."""
        assert (orders_full["packaging_cost"] == 5000).all()


# ── Test: Summarize by Product ──────────────────────────────────────────────
class TestSummarizeByProduct:
    def test_returns_8_products(self, summary):
        """Dữ liệu mẫu có 8 sản phẩm."""
        assert len(summary) == 8

    def test_sorted_by_profit(self, summary):
        """Phải sắp xếp giảm dần theo lợi nhuận."""
        profits = list(summary["loi_nhuan_rong"])
        assert profits == sorted(profits, reverse=True)

    def test_has_classification(self, summary):
        """Mỗi sản phẩm phải có phân loại."""
        assert summary["phan_loai"].notna().all()
        valid = ["⭐ Ngôi sao", "💛 Tiềm năng", "⚠️ Cần xem lại", "❌ Cần loại bỏ"]
        for _, row in summary.iterrows():
            assert row["phan_loai"] in valid, f"Phân loại không hợp lệ: {row['phan_loai']}"

    def test_margin_calculation(self, summary):
        """Margin = Lợi nhuận / Doanh thu * 100."""
        for _, row in summary.iterrows():
            if row["doanh_thu"] > 0:
                expected = round(row["loi_nhuan_rong"] / row["doanh_thu"] * 100, 1)
                assert abs(row["margin_pct"] - expected) < 0.2


# ── Test: Classify ──────────────────────────────────────────────────────────
class TestClassify:
    def test_star(self):
        assert classify(35) == "⭐ Ngôi sao"

    def test_potential(self):
        assert classify(20) == "💛 Tiềm năng"

    def test_warning(self):
        assert classify(10) == "⚠️ Cần xem lại"

    def test_drop(self):
        assert classify(-5) == "❌ Cần loại bỏ"

    def test_boundary_30(self):
        assert classify(30) == "💛 Tiềm năng"  # > 30 mới là ngôi sao

    def test_boundary_15(self):
        assert classify(15) == "⚠️ Cần xem lại"  # > 15 mới là tiềm năng

    def test_boundary_0(self):
        assert classify(0) == "⚠️ Cần xem lại"  # >= 0 là cần xem lại


# ── Test: Detect Period ─────────────────────────────────────────────────────
class TestDetectPeriod:
    def test_sample_data_period(self, sample_orders):
        period = detect_period(sample_orders)
        assert "9/2026" in period or "09/2026" in period

    def test_empty_date(self):
        df = pd.DataFrame({"order_date": [None, None]})
        assert detect_period(df) == "Không rõ kỳ"


# ── Test: Export Dashboard JSON ─────────────────────────────────────────────
class TestExportDashboardJSON:
    def test_json_structure(self, summary, orders_full, fee_rates, tmp_path):
        output = tmp_path / "test_dashboard.json"
        data = export_dashboard_json(
            summary, orders_full, output, "Tháng 9/2026", "Test Shop", fee_rates
        )
        assert "overview" in data
        assert "products" in data
        assert "daily_trend" in data
        assert "by_platform" in data

    def test_json_overview(self, summary, orders_full, fee_rates, tmp_path):
        output = tmp_path / "test_dashboard.json"
        data = export_dashboard_json(
            summary, orders_full, output, "Tháng 9/2026", "Test Shop", fee_rates
        )
        ov = data["overview"]
        assert ov["total_revenue"] > 0
        assert ov["total_orders"] == 45
        assert 0 < ov["avg_margin_pct"] < 100

    def test_json_file_valid(self, summary, orders_full, fee_rates, tmp_path):
        output = tmp_path / "test_dashboard.json"
        export_dashboard_json(
            summary, orders_full, output, "Tháng 9/2026", "Test Shop", fee_rates
        )
        content = json.loads(output.read_text(encoding="utf-8"))
        assert isinstance(content, dict)


# ── Test: Compare Periods ───────────────────────────────────────────────────
class TestComparePeriods:
    def test_compare_same_data(self, summary):
        """So sánh kỳ giống nhau → thay đổi = 0."""
        changes = compare_periods(summary, summary)
        assert len(changes) == len(summary)
        for c in changes:
            assert c["revenue_change_pct"] == 0
            assert c["margin_change"] == 0

    def test_compare_structure(self, summary):
        changes = compare_periods(summary, summary)
        for c in changes:
            assert "product" in c
            assert "revenue_now" in c
            assert "margin_change" in c


# ── Test: Margin Alerts ─────────────────────────────────────────────────────
class TestMarginAlerts:
    def test_no_alerts_for_healthy_margins(self, summary):
        """Dữ liệu mẫu không có margin âm → không có cảnh báo đỏ."""
        alerts = margin_alerts(summary)
        red_alerts = [a for a in alerts if "NGHIÊM TRỌNG" in a["level"]]
        assert len(red_alerts) == 0

    def test_detects_negative_margin(self):
        """Phát hiện sản phẩm margin âm."""
        fake = pd.DataFrame({
            "product_base": ["SP Lỗ"],
            "margin_pct": [-10.0],
        })
        alerts = margin_alerts(fake)
        assert len(alerts) == 1
        assert "NGHIÊM TRỌNG" in alerts[0]["level"]

    def test_detects_low_margin(self):
        """Phát hiện sản phẩm margin thấp < 10%."""
        fake = pd.DataFrame({
            "product_base": ["SP Thấp"],
            "margin_pct": [5.0],
        })
        alerts = margin_alerts(fake)
        assert len(alerts) == 1
        assert "CẢNH BÁO" in alerts[0]["level"]

    def test_detects_margin_drop(self):
        """Phát hiện margin giảm so với kỳ trước."""
        current = pd.DataFrame({
            "product_base": ["SP Test"],
            "margin_pct": [20.0],
        })
        prev = pd.DataFrame({
            "product_base": ["SP Test"],
            "margin_pct": [30.0],
        })
        alerts = margin_alerts(current, prev, drop_threshold=5.0)
        drop_alerts = [a for a in alerts if "THEO DÕI" in a["level"]]
        assert len(drop_alerts) == 1


# ── Test: Integration ───────────────────────────────────────────────────────
class TestIntegration:
    def test_full_pipeline(self, sample_orders_path, product_cost_path, platform_fees_path, tmp_path):
        """Test toàn bộ pipeline từ đầu đến cuối."""
        fee_rates = load_platform_fees(platform_fees_path)
        orders = clean_orders(sample_orders_path)
        cost_df = pd.read_csv(product_cost_path, encoding="utf-8-sig")
        orders_full = calculate_profit(orders, cost_df, fee_rates)
        summary = summarize_by_product(orders_full)

        # Kiểm tra kết quả cuối
        assert len(summary) == 8
        assert summary["loi_nhuan_rong"].sum() > 0
        assert (summary["doanh_thu"] > 0).all()

        # Export JSON
        output_json = tmp_path / "test.json"
        data = export_dashboard_json(
            summary, orders_full, output_json, "Test", "Test Shop", fee_rates
        )
        assert output_json.exists()
        assert len(data["products"]) == 8

    def test_output_files_exist(self):
        """Kiểm tra các file output mẫu đã được tạo."""
        assert (BASE / "analysis" / "product_ranking.csv").exists()
        assert (BASE / "analysis" / "dashboard_data.json").exists()
        assert (BASE / "reports" / "delivered" / "bao_cao_loi_nhuan.txt").exists()
        assert (BASE / "reports" / "dashboard.html").exists()
