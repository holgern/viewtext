import unittest

from viewtext.loader import FieldMapping
from viewtext.registry_builder import MethodCallParser, RegistryBuilder


class TestMethodCallParser(unittest.TestCase):
    def test_parse_simple_key(self):
        result = MethodCallParser.parse("ticker")
        expected = [("key", "ticker", [])]
        self.assertEqual(result, expected)

    def test_parse_attribute_access(self):
        result = MethodCallParser.parse("ticker.name")
        expected = [("key", "ticker", []), ("attr", "name", [])]
        self.assertEqual(result, expected)

    def test_parse_nested_attribute_access(self):
        result = MethodCallParser.parse("ticker.data.name")
        expected = [
            ("key", "ticker", []),
            ("attr", "data", []),
            ("attr", "name", []),
        ]
        self.assertEqual(result, expected)

    def test_parse_method_call_no_args(self):
        result = MethodCallParser.parse("ticker.get_price()")
        expected = [("key", "ticker", []), ("method", "get_price", [])]
        self.assertEqual(result, expected)

    def test_parse_method_call_with_string_arg(self):
        result = MethodCallParser.parse("ticker.get_price('fiat')")
        expected = [("key", "ticker", []), ("method", "get_price", ["fiat"])]
        self.assertEqual(result, expected)

    def test_parse_method_call_with_int_arg(self):
        result = MethodCallParser.parse("obj.get_value(42)")
        expected = [("key", "obj", []), ("method", "get_value", [42])]
        self.assertEqual(result, expected)

    def test_parse_method_call_with_float_arg(self):
        result = MethodCallParser.parse("obj.get_value(3.14)")
        expected = [("key", "obj", []), ("method", "get_value", [3.14])]
        self.assertEqual(result, expected)

    def test_parse_method_call_with_bool_args(self):
        result = MethodCallParser.parse("obj.set_flag(True)")
        expected = [("key", "obj", []), ("method", "set_flag", [True])]
        self.assertEqual(result, expected)

        result = MethodCallParser.parse("obj.set_flag(false)")
        expected = [("key", "obj", []), ("method", "set_flag", [False])]
        self.assertEqual(result, expected)

    def test_parse_method_call_with_multiple_args(self):
        result = MethodCallParser.parse("obj.process('data', 42, 3.14)")
        expected = [("key", "obj", []), ("method", "process", ["data", 42, 3.14])]
        self.assertEqual(result, expected)

    def test_parse_chained_method_calls(self):
        result = MethodCallParser.parse(
            "portfolio.get_ticker('BTC').get_current_price('fiat')"
        )
        expected = [
            ("key", "portfolio", []),
            ("method", "get_ticker", ["BTC"]),
            ("method", "get_current_price", ["fiat"]),
        ]
        self.assertEqual(result, expected)

    def test_parse_chained_with_attributes(self):
        result = MethodCallParser.parse("obj.data.get_value().result")
        expected = [
            ("key", "obj", []),
            ("attr", "data", []),
            ("method", "get_value", []),
            ("attr", "result", []),
        ]
        self.assertEqual(result, expected)

    def test_parse_array_index(self):
        result = MethodCallParser.parse("items.0")
        expected = [("key", "items", []), ("index", "0", [])]
        self.assertEqual(result, expected)

    def test_parse_array_index_with_attribute(self):
        result = MethodCallParser.parse("items.0.name")
        expected = [
            ("key", "items", []),
            ("index", "0", []),
            ("attr", "name", []),
        ]
        self.assertEqual(result, expected)

    def test_parse_nested_array_indices(self):
        result = MethodCallParser.parse("matrix.0.1")
        expected = [
            ("key", "matrix", []),
            ("index", "0", []),
            ("index", "1", []),
        ]
        self.assertEqual(result, expected)

    def test_parse_array_with_method(self):
        result = MethodCallParser.parse("items.0.get_value()")
        expected = [
            ("key", "items", []),
            ("index", "0", []),
            ("method", "get_value", []),
        ]
        self.assertEqual(result, expected)


class TestRegistryBuilder(unittest.TestCase):
    def test_getter_with_simple_key(self):
        getter = RegistryBuilder._create_getter("name", "name", default="Unknown")
        context = {"name": "Alice"}
        self.assertEqual(getter(context), "Alice")

    def test_getter_with_missing_key_returns_default(self):
        getter = RegistryBuilder._create_getter("name", "name", default="Unknown")
        context = {}
        self.assertEqual(getter(context), "Unknown")

    def test_getter_with_attribute_access(self):
        class Obj:
            name = "Alice"

        getter = RegistryBuilder._create_getter(
            "obj_name", "obj.name", default="Unknown"
        )
        context = {"obj": Obj()}
        self.assertEqual(getter(context), "Alice")

    def test_getter_with_method_call_no_args(self):
        class Obj:
            def get_name(self):
                return "Alice"

        getter = RegistryBuilder._create_getter(
            "name", "obj.get_name()", default="Unknown"
        )
        context = {"obj": Obj()}
        self.assertEqual(getter(context), "Alice")

    def test_getter_with_method_call_with_args(self):
        class Obj:
            def get_value(self, key):
                return {"name": "Alice", "age": 30}.get(key)

        getter = RegistryBuilder._create_getter(
            "name", "obj.get_value('name')", default="???"
        )
        context = {"obj": Obj()}
        self.assertEqual(getter(context), "Alice")

    def test_getter_with_chained_method_calls(self):
        class Ticker:
            def __init__(self, price):
                self.price = price

            def get_price(self):
                return self.price

        class Portfolio:
            def get_ticker(self, symbol):
                return Ticker(50000.0)

        getter = RegistryBuilder._create_getter(
            "btc_price", "portfolio.get_ticker('BTC').get_price()", default=0.0
        )
        context = {"portfolio": Portfolio()}
        self.assertEqual(getter(context), 50000.0)

    def test_getter_with_transform_upper(self):
        getter = RegistryBuilder._create_getter(
            "name", "name", default="unknown", transform="upper"
        )
        context = {"name": "alice"}
        self.assertEqual(getter(context), "ALICE")

    def test_getter_with_transform_lower(self):
        getter = RegistryBuilder._create_getter(
            "name", "name", default="UNKNOWN", transform="lower"
        )
        context = {"name": "ALICE"}
        self.assertEqual(getter(context), "alice")

    def test_getter_with_attribute_error_returns_default(self):
        class Obj:
            pass

        getter = RegistryBuilder._create_getter(
            "missing", "obj.missing", default="default"
        )
        context = {"obj": Obj()}
        self.assertEqual(getter(context), "default")

    def test_getter_with_type_error_returns_default(self):
        class Obj:
            def get_value(self, key):
                return {"name": "Alice"}.get(key)

        getter = RegistryBuilder._create_getter(
            "value", "obj.get_value()", default="default"
        )
        context = {"obj": Obj()}
        self.assertEqual(getter(context), "default")

    def test_getter_with_missing_object_returns_default(self):
        getter = RegistryBuilder._create_getter("name", "obj.name", default="default")
        context = {}
        self.assertEqual(getter(context), "default")

    def test_getter_with_array_index(self):
        getter = RegistryBuilder._create_getter(
            "first_item", "items.0", default="default"
        )
        context = {"items": ["apple", "banana", "cherry"]}
        self.assertEqual(getter(context), "apple")

    def test_getter_with_array_index_and_attribute(self):
        getter = RegistryBuilder._create_getter(
            "first_name", "users.0.name", default="Unknown"
        )
        context = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}
        self.assertEqual(getter(context), "Alice")

    def test_getter_with_nested_array_indices(self):
        getter = RegistryBuilder._create_getter("value", "matrix.0.1", default=0)
        context = {"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
        self.assertEqual(getter(context), 2)

    def test_getter_with_array_index_out_of_bounds(self):
        getter = RegistryBuilder._create_getter("item", "items.10", default="default")
        context = {"items": ["apple", "banana"]}
        self.assertEqual(getter(context), "default")

    def test_getter_with_array_index_on_non_list(self):
        getter = RegistryBuilder._create_getter("value", "obj.0", default="default")
        context = {"obj": "not_a_list"}
        self.assertEqual(getter(context), "default")

    def test_getter_with_nested_dict_access(self):
        getter = RegistryBuilder._create_getter(
            "fastest", "recommended_fees.fastestFee", default=None
        )
        context = {
            "recommended_fees": {"fastestFee": 1, "halfHourFee": 2, "hourFee": 3}
        }
        self.assertEqual(getter(context), 1)

    def test_getter_with_deeply_nested_dict_access(self):
        getter = RegistryBuilder._create_getter(
            "value", "level1.level2.level3", default="not_found"
        )
        context = {"level1": {"level2": {"level3": "found"}}}
        self.assertEqual(getter(context), "found")

    def test_getter_with_array_index_and_dict_access(self):
        getter = RegistryBuilder._create_getter(
            "median", "mempool_blocks_fee.0.medianFee", default=0.0
        )
        context = {
            "mempool_blocks_fee": [
                {"medianFee": 0.75, "totalFees": 1126162},
                {"medianFee": 0.69, "totalFees": 705881},
            ]
        }
        self.assertEqual(getter(context), 0.75)


class TestComputedFields(unittest.TestCase):
    def test_celsius_to_fahrenheit(self):
        mapping = FieldMapping(
            operation="celsius_to_fahrenheit", sources=["temp_c"], default=0.0
        )
        getter = RegistryBuilder._create_operation_getter("temp_f", mapping)
        context = {"temp_c": 0}
        self.assertEqual(getter(context), 32.0)

        context = {"temp_c": 100}
        self.assertEqual(getter(context), 212.0)

        context = {"temp_c": -40}
        self.assertEqual(getter(context), -40.0)

    def test_fahrenheit_to_celsius(self):
        mapping = FieldMapping(
            operation="fahrenheit_to_celsius", sources=["temp_f"], default=0.0
        )
        getter = RegistryBuilder._create_operation_getter("temp_c", mapping)
        context = {"temp_f": 32}
        self.assertAlmostEqual(getter(context), 0.0, places=5)

        context = {"temp_f": 212}
        self.assertAlmostEqual(getter(context), 100.0, places=5)

        context = {"temp_f": -40}
        self.assertEqual(getter(context), -40.0)

    def test_multiply_operation(self):
        mapping = FieldMapping(
            operation="multiply", sources=["price", "quantity"], default=0.0
        )
        getter = RegistryBuilder._create_operation_getter("total", mapping)
        context = {"price": 10.5, "quantity": 3}
        self.assertEqual(getter(context), 31.5)

    def test_divide_operation(self):
        mapping = FieldMapping(
            operation="divide", sources=["total", "count"], default=0.0
        )
        getter = RegistryBuilder._create_operation_getter("average", mapping)
        context = {"total": 100, "count": 4}
        self.assertEqual(getter(context), 25.0)

    def test_divide_by_zero_returns_default(self):
        mapping = FieldMapping(
            operation="divide", sources=["total", "count"], default=0.0
        )
        getter = RegistryBuilder._create_operation_getter("result", mapping)
        context = {"total": 100, "count": 0}
        self.assertEqual(getter(context), 0.0)

    def test_add_operation(self):
        mapping = FieldMapping(operation="add", sources=["a", "b"], default=0.0)
        getter = RegistryBuilder._create_operation_getter("sum", mapping)
        context = {"a": 10, "b": 5}
        self.assertEqual(getter(context), 15)

    def test_subtract_operation(self):
        mapping = FieldMapping(operation="subtract", sources=["a", "b"], default=0.0)
        getter = RegistryBuilder._create_operation_getter("diff", mapping)
        context = {"a": 10, "b": 3}
        self.assertEqual(getter(context), 7)

    def test_average_operation(self):
        mapping = FieldMapping(
            operation="average", sources=["a", "b", "c"], default=0.0
        )
        getter = RegistryBuilder._create_operation_getter("avg", mapping)
        context = {"a": 10, "b": 20, "c": 30}
        self.assertEqual(getter(context), 20.0)

    def test_min_operation(self):
        mapping = FieldMapping(operation="min", sources=["a", "b", "c"], default=0.0)
        getter = RegistryBuilder._create_operation_getter("minimum", mapping)
        context = {"a": 10, "b": 5, "c": 15}
        self.assertEqual(getter(context), 5)

    def test_max_operation(self):
        mapping = FieldMapping(operation="max", sources=["a", "b", "c"], default=0.0)
        getter = RegistryBuilder._create_operation_getter("maximum", mapping)
        context = {"a": 10, "b": 25, "c": 15}
        self.assertEqual(getter(context), 25)

    def test_abs_operation(self):
        mapping = FieldMapping(operation="abs", sources=["value"], default=0.0)
        getter = RegistryBuilder._create_operation_getter("abs_value", mapping)
        context = {"value": -42}
        self.assertEqual(getter(context), 42)

        context = {"value": 42}
        self.assertEqual(getter(context), 42)

    def test_round_operation(self):
        mapping = FieldMapping(operation="round", sources=["value"], default=0.0)
        getter = RegistryBuilder._create_operation_getter("rounded", mapping)
        context = {"value": 3.14159}
        self.assertEqual(getter(context), 3)

        context = {"value": 3.7}
        self.assertEqual(getter(context), 4)

    def test_linear_transform_operation(self):
        mapping = FieldMapping(
            operation="linear_transform",
            sources=["value"],
            multiply=2.5,
            add=10,
            default=0.0,
        )
        getter = RegistryBuilder._create_operation_getter("transformed", mapping)
        context = {"value": 4}
        self.assertEqual(getter(context), 20.0)

    def test_linear_transform_multiply_only(self):
        mapping = FieldMapping(
            operation="linear_transform", sources=["value"], multiply=3, default=0.0
        )
        getter = RegistryBuilder._create_operation_getter("scaled", mapping)
        context = {"value": 5}
        self.assertEqual(getter(context), 15.0)

    def test_linear_transform_add_only(self):
        mapping = FieldMapping(
            operation="linear_transform", sources=["value"], add=100, default=0.0
        )
        getter = RegistryBuilder._create_operation_getter("offset", mapping)
        context = {"value": 25}
        self.assertEqual(getter(context), 125.0)

    def test_linear_transform_divide_only(self):
        mapping = FieldMapping(
            operation="linear_transform", sources=["value"], divide=4, default=0.0
        )
        getter = RegistryBuilder._create_operation_getter("divided", mapping)
        context = {"value": 20}
        self.assertEqual(getter(context), 5.0)

    def test_linear_transform_divide_by_zero_returns_default(self):
        mapping = FieldMapping(
            operation="linear_transform", sources=["value"], divide=0, default=999.0
        )
        getter = RegistryBuilder._create_operation_getter("result", mapping)
        context = {"value": 20}
        self.assertEqual(getter(context), 999.0)

    def test_missing_source_returns_default(self):
        mapping = FieldMapping(
            operation="multiply", sources=["price", "quantity"], default=0.0
        )
        getter = RegistryBuilder._create_operation_getter("total", mapping)
        context = {"price": 10.5}
        self.assertEqual(getter(context), 0.0)

    def test_non_numeric_source_returns_default(self):
        mapping = FieldMapping(
            operation="multiply", sources=["price", "quantity"], default=0.0
        )
        getter = RegistryBuilder._create_operation_getter("total", mapping)
        context = {"price": "not_a_number", "quantity": 3}
        self.assertEqual(getter(context), 0.0)

    def test_invalid_operation_raises_error(self):
        mapping = FieldMapping(operation="invalid_op", sources=["value"], default=0.0)
        with self.assertRaises(ValueError):
            RegistryBuilder._create_operation_getter("result", mapping)

    def test_ceil_operation(self):
        mapping = FieldMapping(operation="ceil", sources=["value"], default=0.0)
        getter = RegistryBuilder._create_operation_getter("ceiled", mapping)
        context = {"value": 3.2}
        self.assertEqual(getter(context), 4)

    def test_ceil_operation_negative(self):
        mapping = FieldMapping(operation="ceil", sources=["value"], default=0.0)
        getter = RegistryBuilder._create_operation_getter("ceiled", mapping)
        context = {"value": -3.7}
        self.assertEqual(getter(context), -3)

    def test_floor_operation(self):
        mapping = FieldMapping(operation="floor", sources=["value"], default=0.0)
        getter = RegistryBuilder._create_operation_getter("floored", mapping)
        context = {"value": 3.8}
        self.assertEqual(getter(context), 3)

    def test_floor_operation_negative(self):
        mapping = FieldMapping(operation="floor", sources=["value"], default=0.0)
        getter = RegistryBuilder._create_operation_getter("floored", mapping)
        context = {"value": -3.2}
        self.assertEqual(getter(context), -4)

    def test_modulo_operation(self):
        mapping = FieldMapping(
            operation="modulo", sources=["value", "divisor"], default=0
        )
        getter = RegistryBuilder._create_operation_getter("remainder", mapping)
        context = {"value": 17, "divisor": 5}
        self.assertEqual(getter(context), 2)

    def test_modulo_by_zero_returns_default(self):
        mapping = FieldMapping(
            operation="modulo", sources=["value", "divisor"], default=999
        )
        getter = RegistryBuilder._create_operation_getter("remainder", mapping)
        context = {"value": 17, "divisor": 0}
        self.assertEqual(getter(context), 999)

    def test_concat_operation(self):
        mapping = FieldMapping(
            operation="concat", sources=["first", "last"], separator=" ", default=""
        )
        getter = RegistryBuilder._create_operation_getter("full_name", mapping)
        context = {"first": "John", "last": "Doe"}
        self.assertEqual(getter(context), "John Doe")

    def test_concat_operation_no_separator(self):
        mapping = FieldMapping(
            operation="concat", sources=["part1", "part2"], default=""
        )
        getter = RegistryBuilder._create_operation_getter("combined", mapping)
        context = {"part1": "Hello", "part2": "World"}
        self.assertEqual(getter(context), "HelloWorld")

    def test_concat_missing_source_returns_default(self):
        mapping = FieldMapping(
            operation="concat", sources=["first", "last"], separator=" ", default="N/A"
        )
        getter = RegistryBuilder._create_operation_getter("full_name", mapping)
        context = {"first": "John"}
        self.assertEqual(getter(context), "N/A")

    def test_concat_with_prefix(self):
        mapping = FieldMapping(
            operation="concat", sources=["price"], prefix="$", default=""
        )
        getter = RegistryBuilder._create_operation_getter("formatted_price", mapping)
        context = {"price": "99.99"}
        self.assertEqual(getter(context), "$99.99")

    def test_concat_with_suffix(self):
        mapping = FieldMapping(
            operation="concat", sources=["temp"], suffix="°C", default=""
        )
        getter = RegistryBuilder._create_operation_getter("formatted_temp", mapping)
        context = {"temp": "25"}
        self.assertEqual(getter(context), "25°C")

    def test_concat_with_prefix_and_suffix(self):
        mapping = FieldMapping(
            operation="concat",
            sources=["value"],
            prefix="[",
            suffix="]",
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("wrapped", mapping)
        context = {"value": "test"}
        self.assertEqual(getter(context), "[test]")

    def test_concat_with_separator_prefix_suffix(self):
        mapping = FieldMapping(
            operation="concat",
            sources=["first", "last"],
            separator=" ",
            prefix="Name: ",
            suffix="!",
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("greeting", mapping)
        context = {"first": "John", "last": "Doe"}
        self.assertEqual(getter(context), "Name: John Doe!")

    def test_concat_with_skip_empty(self):
        mapping = FieldMapping(
            operation="concat",
            sources=["first", "middle", "last"],
            separator=" ",
            skip_empty=True,
            default="N/A",
        )
        getter = RegistryBuilder._create_operation_getter("full_name", mapping)
        context = {"first": "John", "last": "Doe"}
        self.assertEqual(getter(context), "John Doe")

    def test_concat_with_skip_empty_all_missing(self):
        mapping = FieldMapping(
            operation="concat",
            sources=["first", "last"],
            separator=" ",
            skip_empty=True,
            default="N/A",
        )
        getter = RegistryBuilder._create_operation_getter("full_name", mapping)
        context = {}
        self.assertEqual(getter(context), "")

    def test_concat_without_skip_empty_returns_default(self):
        mapping = FieldMapping(
            operation="concat",
            sources=["first", "middle", "last"],
            separator=" ",
            skip_empty=False,
            default="N/A",
        )
        getter = RegistryBuilder._create_operation_getter("full_name", mapping)
        context = {"first": "John", "last": "Doe"}
        self.assertEqual(getter(context), "N/A")

    def test_concat_skip_empty_with_prefix_suffix(self):
        mapping = FieldMapping(
            operation="concat",
            sources=["city", "state", "country"],
            separator=", ",
            prefix="Location: ",
            suffix=".",
            skip_empty=True,
            default="N/A",
        )
        getter = RegistryBuilder._create_operation_getter("location", mapping)
        context = {"city": "San Francisco", "country": "USA"}
        self.assertEqual(getter(context), "Location: San Francisco, USA.")

    def test_split_operation(self):
        mapping = FieldMapping(
            operation="split", sources=["text"], separator=" ", default=[]
        )
        getter = RegistryBuilder._create_operation_getter("words", mapping)
        context = {"text": "Hello World Test"}
        self.assertEqual(getter(context), ["Hello", "World", "Test"])

    def test_split_operation_comma(self):
        mapping = FieldMapping(
            operation="split", sources=["csv"], separator=",", default=[]
        )
        getter = RegistryBuilder._create_operation_getter("items", mapping)
        context = {"csv": "apple,banana,cherry"}
        self.assertEqual(getter(context), ["apple", "banana", "cherry"])

    def test_split_missing_source_returns_default(self):
        mapping = FieldMapping(
            operation="split", sources=["text"], separator=" ", default=["error"]
        )
        getter = RegistryBuilder._create_operation_getter("words", mapping)
        context = {}
        self.assertEqual(getter(context), ["error"])

    def test_substring_operation(self):
        mapping = FieldMapping(
            operation="substring", sources=["text"], start=0, end=5, default=""
        )
        getter = RegistryBuilder._create_operation_getter("substr", mapping)
        context = {"text": "Hello World"}
        self.assertEqual(getter(context), "Hello")

    def test_substring_operation_no_end(self):
        mapping = FieldMapping(
            operation="substring", sources=["text"], start=6, default=""
        )
        getter = RegistryBuilder._create_operation_getter("substr", mapping)
        context = {"text": "Hello World"}
        self.assertEqual(getter(context), "World")

    def test_substring_operation_negative_start(self):
        mapping = FieldMapping(
            operation="substring", sources=["text"], start=-5, default=""
        )
        getter = RegistryBuilder._create_operation_getter("substr", mapping)
        context = {"text": "Hello World"}
        self.assertEqual(getter(context), "World")

    def test_substring_missing_source_returns_default(self):
        mapping = FieldMapping(
            operation="substring", sources=["text"], start=0, end=5, default="N/A"
        )
        getter = RegistryBuilder._create_operation_getter("substr", mapping)
        context = {}
        self.assertEqual(getter(context), "N/A")

    def test_split_operation_with_index(self):
        mapping = FieldMapping(
            operation="split",
            sources=["email"],
            separator="@",
            index=1,
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("domain", mapping)
        context = {"email": "user@example.com"}
        self.assertEqual(getter(context), "example.com")

    def test_split_operation_with_negative_index(self):
        mapping = FieldMapping(
            operation="split", sources=["path"], separator="/", index=-1, default=""
        )
        getter = RegistryBuilder._create_operation_getter("filename", mapping)
        context = {"path": "/home/user/file.txt"}
        self.assertEqual(getter(context), "file.txt")

    def test_split_operation_index_out_of_bounds(self):
        mapping = FieldMapping(
            operation="split", sources=["text"], separator=" ", index=10, default="N/A"
        )
        getter = RegistryBuilder._create_operation_getter("word", mapping)
        context = {"text": "hello world"}
        self.assertEqual(getter(context), "N/A")

    def test_conditional_operation_true(self):
        mapping = FieldMapping(
            operation="conditional",
            condition={"field": "currency", "equals": "usd"},
            if_true="~price_usd~",
            if_false="~price_default~",
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("price", mapping)
        context = {"currency": "usd", "price_usd": "100", "price_default": "50"}
        self.assertEqual(getter(context), "100")

    def test_conditional_operation_false(self):
        mapping = FieldMapping(
            operation="conditional",
            condition={"field": "currency", "equals": "usd"},
            if_true="~price_usd~",
            if_false="~price_default~",
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("price", mapping)
        context = {"currency": "eur", "price_usd": "100", "price_default": "50"}
        self.assertEqual(getter(context), "50")

    def test_conditional_operation_with_text(self):
        mapping = FieldMapping(
            operation="conditional",
            condition={"field": "is_admin", "equals": True},
            if_true="Admin: ~username~",
            if_false="User: ~username~",
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("user_label", mapping)
        context = {"is_admin": True, "username": "alice"}
        self.assertEqual(getter(context), "Admin: alice")

    def test_conditional_operation_missing_field(self):
        mapping = FieldMapping(
            operation="conditional",
            condition={"field": "status", "equals": "active"},
            if_true="~active_message~",
            if_false="~inactive_message~",
            default="N/A",
        )
        getter = RegistryBuilder._create_operation_getter("message", mapping)
        context = {}
        self.assertEqual(getter(context), "N/A")

    def test_conditional_operation_missing_referenced_field(self):
        mapping = FieldMapping(
            operation="conditional",
            condition={"field": "currency", "equals": "usd"},
            if_true="~missing_field~",
            if_false="default",
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("price", mapping)
        context = {"currency": "usd"}
        self.assertEqual(getter(context), "")

    def test_format_number_operation_comma_separator(self):
        mapping = FieldMapping(
            operation="format_number",
            sources=["value"],
            thousands_sep=",",
            decimals_param=0,
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("formatted_value", mapping)
        context = {"value": 100000}
        self.assertEqual(getter(context), "100,000")

    def test_format_number_operation_dot_separator(self):
        mapping = FieldMapping(
            operation="format_number",
            sources=["value"],
            thousands_sep=".",
            decimals_param=0,
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("formatted_value", mapping)
        context = {"value": 100000}
        self.assertEqual(getter(context), "100.000")

    def test_format_number_operation_space_separator(self):
        mapping = FieldMapping(
            operation="format_number",
            sources=["value"],
            thousands_sep=" ",
            decimals_param=0,
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("formatted_value", mapping)
        context = {"value": 1234567}
        self.assertEqual(getter(context), "1 234 567")

    def test_format_number_operation_with_decimals(self):
        mapping = FieldMapping(
            operation="format_number",
            sources=["value"],
            thousands_sep=",",
            decimals_param=2,
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("formatted_value", mapping)
        context = {"value": 1234.567}
        self.assertEqual(getter(context), "1,234.57")

    def test_format_number_operation_no_separator(self):
        mapping = FieldMapping(
            operation="format_number",
            sources=["value"],
            thousands_sep="",
            decimals_param=0,
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("formatted_value", mapping)
        context = {"value": 100000}
        self.assertEqual(getter(context), "100000")

    def test_format_number_operation_missing_value(self):
        mapping = FieldMapping(
            operation="format_number",
            sources=["value"],
            thousands_sep=",",
            decimals_param=0,
            default="N/A",
        )
        getter = RegistryBuilder._create_operation_getter("formatted_value", mapping)
        context = {}
        self.assertEqual(getter(context), "N/A")

    def test_format_number_operation_context_key(self):
        mapping = FieldMapping(
            operation="format_number",
            context_key="value",
            thousands_sep=".",
            decimals_param=2,
            default="",
        )
        getter = RegistryBuilder._create_operation_getter("formatted_value", mapping)
        context = {"value": 1234567.89}
        self.assertEqual(getter(context), "1.234.567.89")

    def test_format_number_operation_european_format(self):
        mapping = FieldMapping(
            operation="format_number",
            sources=["amount"],
            thousands_sep=".",
            decimal_sep=",",
            decimals_param=2,
            default="N/A",
        )
        getter = RegistryBuilder._create_operation_getter("formatted_value", mapping)
        context = {"amount": 1234567.89}
        self.assertEqual(getter(context), "1.234.567,89")

    def test_format_number_operation_swiss_format(self):
        mapping = FieldMapping(
            operation="format_number",
            sources=["price"],
            thousands_sep="'",
            decimal_sep=".",
            decimals_param=2,
            default="0.00",
        )
        getter = RegistryBuilder._create_operation_getter("formatted_value", mapping)
        context = {"price": 1234567.89}
        self.assertEqual(getter(context), "1'234'567.89")

    def test_format_number_operation_decimal_sep_only(self):
        mapping = FieldMapping(
            operation="format_number",
            sources=["value"],
            decimal_sep=",",
            decimals_param=2,
            default="0,00",
        )
        getter = RegistryBuilder._create_operation_getter("formatted_value", mapping)
        context = {"value": 1234.56}
        self.assertEqual(getter(context), "1234,56")


class TestPythonFunctionGetter(unittest.TestCase):
    def test_python_function_datetime(self):
        import time

        mapping = FieldMapping(
            python_module="datetime",
            python_function="datetime.datetime.now().timestamp()",
            transform="int",
        )
        getter = RegistryBuilder._create_python_function_getter("current_time", mapping)
        context = {}
        result = getter(context)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)
        self.assertLess(result - int(time.time()), 2)

    def test_python_function_caching(self):
        mapping = FieldMapping(
            python_module="random", python_function="random.random()", default=0.0
        )
        getter = RegistryBuilder._create_python_function_getter("random_value", mapping)
        context = {}
        first_call = getter(context)
        second_call = getter(context)
        self.assertEqual(first_call, second_call)

    def test_python_function_uuid(self):
        mapping = FieldMapping(
            python_module="uuid", python_function="str(uuid.uuid4())", default=""
        )
        getter = RegistryBuilder._create_python_function_getter("unique_id", mapping)
        context = {}
        result = getter(context)
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 36)

    def test_python_function_math(self):
        mapping = FieldMapping(
            python_module="math", python_function="math.pi", default=0.0
        )
        getter = RegistryBuilder._create_python_function_getter("pi_value", mapping)
        context = {}
        result = getter(context)
        self.assertAlmostEqual(result, 3.14159, places=5)

    def test_python_function_with_transform(self):
        mapping = FieldMapping(
            python_module="math",
            python_function="math.pi",
            transform="int",
            default=0,
        )
        getter = RegistryBuilder._create_python_function_getter("pi_int", mapping)
        context = {}
        result = getter(context)
        self.assertEqual(result, 3)

    def test_python_function_bad_module_returns_default(self):
        mapping = FieldMapping(
            python_module="nonexistent_module",
            python_function="nonexistent_module.func()",
            default="default",
        )
        getter = RegistryBuilder._create_python_function_getter("bad_module", mapping)
        context = {}
        result = getter(context)
        self.assertEqual(result, "default")

    def test_python_function_bad_function_returns_default(self):
        mapping = FieldMapping(
            python_module="math",
            python_function="math.nonexistent_function()",
            default=999,
        )
        getter = RegistryBuilder._create_python_function_getter("bad_func", mapping)
        context = {}
        result = getter(context)
        self.assertEqual(result, 999)

    def test_python_function_syntax_error_returns_default(self):
        mapping = FieldMapping(
            python_module="math",
            python_function="invalid syntax here",
            default="error",
        )
        getter = RegistryBuilder._create_python_function_getter("bad_syntax", mapping)
        context = {}
        result = getter(context)
        self.assertEqual(result, "error")

    def test_python_function_no_module(self):
        mapping = FieldMapping(python_function="2 + 2", default=0)
        getter = RegistryBuilder._create_python_function_getter("simple_math", mapping)
        context = {}
        result = getter(context)
        self.assertEqual(result, 4)

    def test_python_function_with_validator(self):
        mapping = FieldMapping(
            python_module="math",
            python_function="math.pi",
            type="float",
            min_value=3.0,
            max_value=4.0,
            default=0.0,
        )
        getter = RegistryBuilder._create_python_function_getter("validated_pi", mapping)
        context = {}
        result = getter(context)
        self.assertAlmostEqual(result, 3.14159, places=5)

    def test_python_function_validator_out_of_range(self):
        mapping = FieldMapping(
            python_module="math",
            python_function="math.pi",
            type="float",
            min_value=5.0,
            max_value=10.0,
            on_validation_error="use_default",
            default=7.5,
        )
        getter = RegistryBuilder._create_python_function_getter("invalid_pi", mapping)
        context = {}
        result = getter(context)
        self.assertEqual(result, 7.5)


if __name__ == "__main__":
    unittest.main()
