import pytest

from viewtext import BaseFieldRegistry


class TestBaseFieldRegistry:
    def test_register_and_get_field(self):
        registry = BaseFieldRegistry()

        def getter(ctx):
            return ctx["temperature"]

        registry.register("temp", getter)

        assert registry.get("temp") == getter

    def test_get_nonexistent_field_raises_error(self):
        registry = BaseFieldRegistry()

        with pytest.raises(ValueError, match="Unknown field: nonexistent"):
            registry.get("nonexistent")

    def test_has_field_returns_true_for_registered_field(self):
        registry = BaseFieldRegistry()

        def getter(ctx):
            return ctx["temperature"]

        registry.register("temp", getter)

        assert registry.has_field("temp") is True

    def test_has_field_returns_false_for_unregistered_field(self):
        registry = BaseFieldRegistry()

        assert registry.has_field("temp") is False

    def test_register_multiple_fields(self):
        registry = BaseFieldRegistry()

        def temp_getter(ctx):
            return ctx["temp"]

        def humidity_getter(ctx):
            return ctx["humidity"]

        registry.register("temp", temp_getter)
        registry.register("humidity", humidity_getter)

        assert registry.get("temp") == temp_getter
        assert registry.get("humidity") == humidity_getter
        assert registry.has_field("temp") is True
        assert registry.has_field("humidity") is True

    def test_register_overwrites_existing_field(self):
        registry = BaseFieldRegistry()

        def first_getter(ctx):
            return ctx["first"]

        def second_getter(ctx):
            return ctx["second"]

        registry.register("field", first_getter)
        registry.register("field", second_getter)

        assert registry.get("field") == second_getter
