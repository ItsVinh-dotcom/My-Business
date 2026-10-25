"""
tests/test_clean_data.py
------------------------
Unit tests cho module clean_data.py (chuyển đổi file xuất từ Shopee/TikTok).
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Thêm thư mục scripts vào path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from clean_data import (
    detect_platform,
    map_columns,
    clean_orders,
    _parse_number,
    _generate_sku,
)


class TestPlatformDetection:
    def test_detect_shopee(self):
        df = pd.DataFrame(columns=["Mã đơn hàng", "Tên sản phẩm", "SKU phân loại hàng", "Tổng giá bán", "Trạng thái đơn hàng"])
        assert detect_platform(df) == "shopee"

    def test_detect_tiktok(self):
        df = pd.DataFrame(columns=["Order ID", "Product Name", "Seller SKU", "SKU Subtotal", "Order Status", "Created Time"])
        assert detect_platform(df) == "tiktok"


class TestNumberParsing:
    def test_integer(self):
        assert _parse_number(150000) == 150000

    def test_string_with_commas(self):
        assert _parse_number("150,000") == 150000

    def test_string_with_dots(self):
        assert _parse_number("150.000") == 150000

    def test_none_or_empty(self):
        assert _parse_number(None) == 0
        assert _parse_number("") == 0


class TestSkuGeneration:
    def test_generate_from_title(self):
        sku = _generate_sku("Áo Thun Nam Cotton Cổ Tròn")
        assert len(sku) > 0
        assert "-" in sku
        assert sku.replace("-", "").isalnum()


class TestCleanOrders:
    @pytest.fixture
    def raw_shopee_df(self):
        return pd.DataFrame({
            "Mã đơn hàng": ["SP001", "SP002", "SP003", "SP001"],  # SP001 is duplicate
            "Tên sản phẩm": ["Áo Thun Trơn", "Quần Jean Slim", "Váy Hoa", "Áo Thun Trơn"],
            "SKU phân loại hàng": ["AT01", "QJ01", "VH01", "AT01"],
            "Số lượng": [1, 2, 1, 1],
            "Tổng giá bán": ["150.000", "350.000", "280.000", "150.000"],
            "Trạng thái đơn hàng": ["Hoàn thành", "Đã hủy", "Hoàn thành", "Hoàn thành"],
            "Ngày đặt hàng": ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-01"],
            "Phí vận chuyển": ["15.000", "20.000", "0", "15.000"]
        })

    def test_filters_uncompleted_and_duplicates(self, raw_shopee_df):
        cleaned = clean_orders(raw_shopee_df, "shopee")
        # SP002 cancelled, SP001 duplicated -> only SP001 and SP003 should remain
        assert len(cleaned) == 2
        assert set(cleaned["order_id"]) == {"SP001", "SP003"}

    def test_standard_columns_present(self, raw_shopee_df):
        cleaned = clean_orders(raw_shopee_df, "shopee")
        expected_cols = ["order_id", "product_name", "sku", "quantity", "revenue", "platform", "status"]
        for col in expected_cols:
            assert col in cleaned.columns

    def test_revenue_numeric(self, raw_shopee_df):
        cleaned = clean_orders(raw_shopee_df, "shopee")
        assert cleaned.loc[cleaned["order_id"] == "SP001", "revenue"].values[0] == 150000
