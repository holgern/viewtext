from datetime import datetime

import pytest

from viewtext.formatters import FormatterRegistry


class TestFormatterRegistry:
    def test_register_custom_formatter(self):
        registry = FormatterRegistry()

        def custom_formatter(value, **kwargs):
            return f"custom_{value}"

        registry.register("custom", custom_formatter)

        formatter = registry.get("custom")
        assert formatter("test") == "custom_test"

    def test_get_nonexistent_formatter_raises_error(self):
        registry = FormatterRegistry()

        with pytest.raises(ValueError, match="Unknown formatter: nonexistent"):
            registry.get("nonexistent")

    def test_builtin_formatters_are_registered(self):
        registry = FormatterRegistry()

        assert registry.get("text") is not None
        assert registry.get("text_uppercase") is not None
        assert registry.get("price") is not None
        assert registry.get("number") is not None
        assert registry.get("datetime") is not None
        assert registry.get("relative_time") is not None


class TestTextFormatter:
    def test_format_text_basic(self):
        registry = FormatterRegistry()
        formatter = registry.get("text")

        assert formatter("hello") == "hello"
        assert formatter(123) == "123"

    def test_format_text_with_prefix(self):
        registry = FormatterRegistry()
        formatter = registry.get("text")

        assert formatter("world", prefix="hello ") == "hello world"

    def test_format_text_with_suffix(self):
        registry = FormatterRegistry()
        formatter = registry.get("text")

        assert formatter("hello", suffix=" world") == "hello world"

    def test_format_text_with_prefix_and_suffix(self):
        registry = FormatterRegistry()
        formatter = registry.get("text")

        assert formatter("test", prefix="[", suffix="]") == "[test]"


class TestTextUppercaseFormatter:
    def test_format_text_uppercase(self):
        registry = FormatterRegistry()
        formatter = registry.get("text_uppercase")

        assert formatter("hello") == "HELLO"
        assert formatter("World") == "WORLD"
        assert formatter(123) == "123"


class TestPriceFormatter:
    def test_format_price_basic(self):
        registry = FormatterRegistry()
        formatter = registry.get("price")

        assert formatter(123.45) == "123.45"
        assert formatter(123) == "123.00"

    def test_format_price_with_symbol_prefix(self):
        registry = FormatterRegistry()
        formatter = registry.get("price")

        assert formatter(123.45, symbol="$") == "$123.45"

    def test_format_price_with_symbol_suffix(self):
        registry = FormatterRegistry()
        formatter = registry.get("price")

        assert formatter(123.45, symbol="EUR", symbol_position="suffix") == "123.45EUR"

    def test_format_price_with_decimals(self):
        registry = FormatterRegistry()
        formatter = registry.get("price")

        assert formatter(123.456, decimals=3) == "123.456"
        assert formatter(123.456, decimals=1) == "123.5"

    def test_format_price_with_thousands_separator(self):
        registry = FormatterRegistry()
        formatter = registry.get("price")

        assert formatter(1234.56, thousands_sep=",") == "1,234.56"
        assert formatter(1234567.89, thousands_sep=",") == "1,234,567.89"

    def test_format_price_with_custom_thousands_separator(self):
        registry = FormatterRegistry()
        formatter = registry.get("price")

        assert formatter(1234.56, thousands_sep=".") == "1.234.56"
        assert formatter(1234567.89, thousands_sep=".") == "1.234.567.89"
        assert formatter(1234567.89, thousands_sep=" ") == "1 234 567.89"

    def test_format_price_with_european_format(self):
        registry = FormatterRegistry()
        formatter = registry.get("price")

        assert (
            formatter(1234567.89, thousands_sep=".", decimal_sep=",") == "1.234.567,89"
        )
        assert formatter(1234.56, thousands_sep=".", decimal_sep=",") == "1.234,56"
        assert formatter(100.5, thousands_sep=".", decimal_sep=",") == "100,50"
        assert (
            formatter(1234567.89, thousands_sep=" ", decimal_sep=",") == "1 234 567,89"
        )

    def test_format_price_none_value(self):
        registry = FormatterRegistry()
        formatter = registry.get("price")

        assert formatter(None) == ""

    def test_format_price_invalid_value(self):
        registry = FormatterRegistry()
        formatter = registry.get("price")

        assert formatter("invalid") == "invalid"


class TestNumberFormatter:
    def test_format_number_basic(self):
        registry = FormatterRegistry()
        formatter = registry.get("number")

        assert formatter(123) == "123"
        assert formatter(123.456) == "123"

    def test_format_number_with_decimals(self):
        registry = FormatterRegistry()
        formatter = registry.get("number")

        assert formatter(123.456, decimals=2) == "123.46"
        assert formatter(123.456, decimals=1) == "123.5"

    def test_format_number_with_prefix(self):
        registry = FormatterRegistry()
        formatter = registry.get("number")

        assert formatter(123, prefix="Value: ") == "Value: 123"

    def test_format_number_with_suffix(self):
        registry = FormatterRegistry()
        formatter = registry.get("number")

        assert formatter(123, suffix=" units") == "123 units"

    def test_format_number_with_thousands_separator(self):
        registry = FormatterRegistry()
        formatter = registry.get("number")

        assert formatter(1234, thousands_sep=",") == "1,234"
        assert formatter(1234567, thousands_sep=",") == "1,234,567"

    def test_format_number_with_custom_thousands_separator(self):
        registry = FormatterRegistry()
        formatter = registry.get("number")

        assert formatter(1234, thousands_sep=".") == "1.234"
        assert formatter(1234567, thousands_sep=".") == "1.234.567"
        assert formatter(100000, thousands_sep=".") == "100.000"
        assert formatter(1234567, thousands_sep=" ") == "1 234 567"

    def test_format_number_with_european_format(self):
        registry = FormatterRegistry()
        formatter = registry.get("number")

        assert (
            formatter(1234567.89, decimals=2, thousands_sep=".", decimal_sep=",")
            == "1.234.567,89"
        )
        assert (
            formatter(1234.56, decimals=2, thousands_sep=".", decimal_sep=",")
            == "1.234,56"
        )
        assert (
            formatter(100.5, decimals=1, thousands_sep=".", decimal_sep=",") == "100,5"
        )
        assert (
            formatter(1234567, decimals=0, thousands_sep=".", decimal_sep=",")
            == "1.234.567"
        )

    def test_format_number_none_value(self):
        registry = FormatterRegistry()
        formatter = registry.get("number")

        assert formatter(None) == ""

    def test_format_number_invalid_value(self):
        registry = FormatterRegistry()
        formatter = registry.get("number")

        assert formatter("invalid") == "invalid"


class TestDatetimeFormatter:
    def test_format_datetime_from_datetime_object(self):
        registry = FormatterRegistry()
        formatter = registry.get("datetime")

        dt = datetime(2023, 5, 15, 14, 30, 45)
        assert formatter(dt) == "2023-05-15 14:30:45"

    def test_format_datetime_from_timestamp(self):
        registry = FormatterRegistry()
        formatter = registry.get("datetime")

        timestamp = 1684162245
        result = formatter(timestamp)
        assert "2023" in result

    def test_format_datetime_with_custom_format(self):
        registry = FormatterRegistry()
        formatter = registry.get("datetime")

        dt = datetime(2023, 5, 15, 14, 30, 45)
        assert formatter(dt, format="%Y-%m-%d") == "2023-05-15"
        assert formatter(dt, format="%H:%M") == "14:30"

    def test_format_datetime_from_string(self):
        registry = FormatterRegistry()
        formatter = registry.get("datetime")

        assert formatter("2023-05-15") == "2023-05-15"

    def test_format_datetime_none_value(self):
        registry = FormatterRegistry()
        formatter = registry.get("datetime")

        assert formatter(None) == ""


class TestRelativeTimeFormatter:
    def test_format_relative_time_seconds(self):
        registry = FormatterRegistry()
        formatter = registry.get("relative_time")

        assert formatter(30) == "30s ago"
        assert formatter(59) == "59s ago"

    def test_format_relative_time_minutes(self):
        registry = FormatterRegistry()
        formatter = registry.get("relative_time")

        assert formatter(60) == "1m ago"
        assert formatter(120) == "2m ago"
        assert formatter(3599) == "59m ago"

    def test_format_relative_time_hours(self):
        registry = FormatterRegistry()
        formatter = registry.get("relative_time")

        assert formatter(3600) == "1h ago"
        assert formatter(7200) == "2h ago"
        assert formatter(86399) == "23h ago"

    def test_format_relative_time_days(self):
        registry = FormatterRegistry()
        formatter = registry.get("relative_time")

        assert formatter(86400) == "1d ago"
        assert formatter(172800) == "2d ago"
        assert formatter(259200) == "3d ago"

    def test_format_relative_time_long_format(self):
        registry = FormatterRegistry()
        formatter = registry.get("relative_time")

        assert formatter(30, format="long") == "30 seconds ago"
        assert formatter(120, format="long") == "2 minutes ago"
        assert formatter(7200, format="long") == "2 hours ago"
        assert formatter(172800, format="long") == "2 days ago"

    def test_format_relative_time_none_value(self):
        registry = FormatterRegistry()
        formatter = registry.get("relative_time")

        assert formatter(None) == ""

    def test_format_relative_time_invalid_value(self):
        registry = FormatterRegistry()
        formatter = registry.get("relative_time")

        assert formatter("invalid") == "invalid"


class TestTemplateFormatter:
    def test_format_template_basic(self):
        registry = FormatterRegistry()
        formatter = registry.get("template")

        context = {"price": 100, "currency": "USD"}
        result = formatter(
            context, template="{price} {currency}", fields=["price", "currency"]
        )
        assert result == "100 USD"

    def test_format_template_with_nested_fields(self):
        registry = FormatterRegistry()
        formatter = registry.get("template")

        context = {"current_price": {"fiat": "€95,000", "usd": 100000, "sat_usd": 1000}}
        template = (
            "{current_price_fiat} - ${current_price_usd} - "
            "{current_price_sat_usd:.0f} /$"
        )
        result = formatter(
            context,
            template=template,
            fields=["current_price.fiat", "current_price.usd", "current_price.sat_usd"],
        )
        assert result == "€95,000 - $100000 - 1000 /$"

    def test_format_template_with_formatting_specs(self):
        registry = FormatterRegistry()
        formatter = registry.get("template")

        context = {"value": 123.456}
        result = formatter(context, template="{value:.2f}", fields=["value"])
        assert result == "123.46"

    def test_format_template_missing_field(self):
        registry = FormatterRegistry()
        formatter = registry.get("template")

        context = {"price": 100}
        result = formatter(
            context, template="{price} {currency}", fields=["price", "currency"]
        )
        assert result == "100 "

    def test_format_template_non_dict_value(self):
        registry = FormatterRegistry()
        formatter = registry.get("template")

        result = formatter("not a dict", template="{price}", fields=["price"])
        assert result == "not a dict"

    def test_format_template_no_fields(self):
        registry = FormatterRegistry()
        formatter = registry.get("template")

        context = {"price": 100}
        result = formatter(context, template="Static text")
        assert result == "Static text"

    def test_format_template_deeply_nested_fields(self):
        registry = FormatterRegistry()
        formatter = registry.get("template")

        context = {"level1": {"level2": {"level3": "deep value"}}}
        result = formatter(
            context, template="{level1_level2_level3}", fields=["level1.level2.level3"]
        )
        assert result == "deep value"
