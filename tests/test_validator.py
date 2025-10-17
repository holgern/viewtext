"""Tests for field validation functionality."""

import pytest

from viewtext.validator import FieldValidator, ValidationError


class TestFieldValidator:
    """Test FieldValidator class."""

    def test_validate_str_type(self):
        """Test string type validation."""
        validator = FieldValidator(
            field_name="name",
            field_type="str",
            on_validation_error="coerce",
        )
        assert validator.validate("hello") == "hello"
        assert validator.validate(123) == "123"

    def test_validate_int_type(self):
        """Test integer type validation."""
        validator = FieldValidator(
            field_name="age",
            field_type="int",
            on_validation_error="coerce",
        )
        assert validator.validate(42) == 42
        assert validator.validate("123") == 123
        assert validator.validate(3.14) == 3

    def test_validate_float_type(self):
        """Test float type validation."""
        validator = FieldValidator(
            field_name="price",
            field_type="float",
            on_validation_error="coerce",
        )
        assert validator.validate(3.14) == 3.14
        assert validator.validate("2.5") == 2.5
        assert validator.validate(42) == 42.0

    def test_validate_bool_type(self):
        """Test boolean type validation."""
        validator = FieldValidator(
            field_name="active",
            field_type="bool",
            on_validation_error="coerce",
        )
        assert validator.validate(True) is True
        assert validator.validate(False) is False
        assert validator.validate(1) is True
        assert validator.validate(0) is False
        assert validator.validate("yes") is True
        assert validator.validate("") is False

    def test_validate_list_type(self):
        """Test list type validation."""
        validator = FieldValidator(
            field_name="items",
            field_type="list",
            on_validation_error="raise",
        )
        assert validator.validate([1, 2, 3]) == [1, 2, 3]
        with pytest.raises(ValidationError):
            validator.validate("abc")

    def test_validate_dict_type(self):
        """Test dict type validation."""
        validator = FieldValidator(
            field_name="data",
            field_type="dict",
        )
        data = {"key": "value"}
        assert validator.validate(data) == data

    def test_validate_any_type(self):
        """Test any type validation."""
        validator = FieldValidator(
            field_name="anything",
            field_type="any",
        )
        assert validator.validate("hello") == "hello"
        assert validator.validate(123) == 123
        assert validator.validate([1, 2]) == [1, 2]

    def test_min_value_constraint(self):
        """Test min_value constraint."""
        validator = FieldValidator(
            field_name="age",
            field_type="int",
            min_value=18,
            on_validation_error="raise",
        )
        assert validator.validate(25) == 25
        with pytest.raises(ValidationError, match="less than minimum"):
            validator.validate(15)

    def test_max_value_constraint(self):
        """Test max_value constraint."""
        validator = FieldValidator(
            field_name="percentage",
            field_type="float",
            max_value=100.0,
            on_validation_error="raise",
        )
        assert validator.validate(75.5) == 75.5
        with pytest.raises(ValidationError, match="greater than maximum"):
            validator.validate(150.0)

    def test_min_length_constraint(self):
        """Test min_length constraint."""
        validator = FieldValidator(
            field_name="username",
            field_type="str",
            min_length=3,
            on_validation_error="raise",
        )
        assert validator.validate("alice") == "alice"
        with pytest.raises(ValidationError, match="less than minimum"):
            validator.validate("ab")

    def test_max_length_constraint(self):
        """Test max_length constraint."""
        validator = FieldValidator(
            field_name="code",
            field_type="str",
            max_length=5,
            on_validation_error="raise",
        )
        assert validator.validate("ABC") == "ABC"
        with pytest.raises(ValidationError, match="greater than maximum"):
            validator.validate("ABCDEF")

    def test_pattern_constraint(self):
        """Test pattern constraint."""
        validator = FieldValidator(
            field_name="email",
            field_type="str",
            pattern=r"^[a-z]+@[a-z]+\.[a-z]+$",
            on_validation_error="raise",
        )
        assert validator.validate("user@example.com") == "user@example.com"
        with pytest.raises(ValidationError, match="does not match pattern"):
            validator.validate("invalid-email")

    def test_allowed_values_constraint(self):
        """Test allowed_values constraint."""
        validator = FieldValidator(
            field_name="status",
            field_type="str",
            allowed_values=["active", "inactive", "pending"],
            on_validation_error="raise",
        )
        assert validator.validate("active") == "active"
        with pytest.raises(ValidationError, match="not in allowed values"):
            validator.validate("unknown")

    def test_min_items_constraint(self):
        """Test min_items constraint."""
        validator = FieldValidator(
            field_name="tags",
            field_type="list",
            min_items=2,
            on_validation_error="raise",
        )
        assert validator.validate([1, 2, 3]) == [1, 2, 3]
        with pytest.raises(ValidationError, match="minimum is"):
            validator.validate([1])

    def test_max_items_constraint(self):
        """Test max_items constraint."""
        validator = FieldValidator(
            field_name="tags",
            field_type="list",
            max_items=3,
            on_validation_error="raise",
        )
        assert validator.validate([1, 2]) == [1, 2]
        with pytest.raises(ValidationError, match="maximum is"):
            validator.validate([1, 2, 3, 4])

    def test_on_validation_error_use_default(self):
        """Test on_validation_error='use_default' strategy."""
        validator = FieldValidator(
            field_name="age",
            field_type="int",
            min_value=18,
            default=18,
            on_validation_error="use_default",
        )
        assert validator.validate(15) == 18
        assert validator.validate(25) == 25

    def test_on_validation_error_raise(self):
        """Test on_validation_error='raise' strategy."""
        validator = FieldValidator(
            field_name="age",
            field_type="int",
            min_value=18,
            on_validation_error="raise",
        )
        with pytest.raises(ValidationError):
            validator.validate(15)

    def test_on_validation_error_skip(self):
        """Test on_validation_error='skip' strategy."""
        validator = FieldValidator(
            field_name="age",
            field_type="int",
            min_value=18,
            on_validation_error="skip",
        )
        assert validator.validate(15) is None
        assert validator.validate(25) == 25

    def test_on_validation_error_coerce(self):
        """Test on_validation_error='coerce' strategy for constraint violations."""
        validator = FieldValidator(
            field_name="age",
            field_type="int",
            min_value=18,
            max_value=100,
            default=50,
            on_validation_error="coerce",
        )
        assert validator.validate(15) == 50  # Returns default on constraint failure
        assert validator.validate(150) == 50  # Returns default on constraint failure
        assert validator.validate(50) == 50

    def test_coerce_min_length(self):
        """Test coercing returns default on length constraint violation."""
        validator = FieldValidator(
            field_name="code",
            field_type="str",
            min_length=5,
            default="     ",
            on_validation_error="coerce",
        )
        assert (
            validator.validate("abc") == "     "
        )  # Returns default on constraint failure

    def test_coerce_max_length(self):
        """Test coercing returns default on length constraint violation."""
        validator = FieldValidator(
            field_name="code",
            field_type="str",
            max_length=5,
            default="abcde",
            on_validation_error="coerce",
        )
        assert (
            validator.validate("abcdefgh") == "abcde"
        )  # Returns default on constraint failure

    def test_invalid_type_conversion(self):
        """Test invalid type conversion."""
        validator = FieldValidator(
            field_name="price",
            field_type="float",
            on_validation_error="raise",
        )
        with pytest.raises(ValidationError, match="expected type"):
            validator.validate("not-a-number")

    def test_dict_type_validation_error(self):
        """Test dict type validation error."""
        validator = FieldValidator(
            field_name="data",
            field_type="dict",
            on_validation_error="raise",
        )
        with pytest.raises(ValidationError, match="expected type 'dict'"):
            validator.validate("not-a-dict")

    def test_combined_constraints(self):
        """Test multiple constraints together."""
        validator = FieldValidator(
            field_name="score",
            field_type="int",
            min_value=0,
            max_value=100,
            allowed_values=[0, 25, 50, 75, 100],
            on_validation_error="raise",
        )
        assert validator.validate(50) == 50
        with pytest.raises(ValidationError, match="not in allowed values"):
            validator.validate(30)

    def test_none_value_handling(self):
        """Test None value handling."""
        validator = FieldValidator(
            field_name="optional",
            field_type="str",
            default="default",
            on_validation_error="use_default",
        )
        assert validator.validate(None) == "default"

    def test_validation_error_message(self):
        """Test ValidationError message format."""
        validator = FieldValidator(
            field_name="age",
            field_type="int",
            min_value=18,
        )
        try:
            validator.validate(15)
        except ValidationError as e:
            assert "age" in str(e)
            assert "must be >= 18" in str(e)


class TestValidationWithRegistryBuilder:
    """Test validation integration with RegistryBuilder."""

    def test_registry_builder_with_validation(self, tmp_path):
        """Test RegistryBuilder with field validation."""
        from viewtext.loader import LayoutLoader
        from viewtext.registry_builder import RegistryBuilder

        config_path = tmp_path / "test.toml"
        config_path.write_text("""
[fields.age]
context_key = "age"
type = "int"
min_value = 0
max_value = 120
on_validation_error = "use_default"
default = 0

[fields.name]
context_key = "name"
type = "str"
min_length = 1
max_length = 50
on_validation_error = "raise"

[layouts.test]
name = "Test Layout"

[[layouts.test.lines]]
field = "age"
index = 0
""")

        loader = LayoutLoader(str(config_path))
        registry = RegistryBuilder.build_from_config(loader=loader)

        age_getter = registry.get("age")
        assert age_getter({"age": 25}) == 25
        assert age_getter({"age": -5}) == 0
        assert age_getter({"age": 200}) == 0

        name_getter = registry.get("name")
        assert name_getter({"name": "Alice"}) == "Alice"

        with pytest.raises(ValidationError) as exc_info:
            name_getter({"name": "x" * 100})
        assert "name" in str(exc_info.value)
        assert "greater than maximum" in str(exc_info.value)

    def test_validation_with_computed_fields(self, tmp_path):
        """Test validation with computed fields."""
        from viewtext.loader import LayoutLoader
        from viewtext.registry_builder import RegistryBuilder

        config_path = tmp_path / "test.toml"
        config_path.write_text("""
[fields.total]
operation = "add"
sources = ["price", "tax"]
type = "float"
min_value = 0
on_validation_error = "use_default"
default = 0.0

[layouts.test]
name = "Test Layout"

[[layouts.test.lines]]
field = "total"
index = 0
""")

        loader = LayoutLoader(str(config_path))
        registry = RegistryBuilder.build_from_config(loader=loader)

        total_getter = registry.get("total")
        assert total_getter({"price": 10, "tax": 2}) == 12.0
        assert total_getter({"price": -10, "tax": -5}) == 0.0
