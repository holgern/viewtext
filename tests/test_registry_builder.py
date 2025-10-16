import unittest

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


class TestRegistryBuilder(unittest.TestCase):
    def test_getter_with_simple_key(self):
        getter = RegistryBuilder._create_getter("name", default="Unknown")
        context = {"name": "Alice"}
        self.assertEqual(getter(context), "Alice")

    def test_getter_with_missing_key_returns_default(self):
        getter = RegistryBuilder._create_getter("name", default="Unknown")
        context = {}
        self.assertEqual(getter(context), "Unknown")

    def test_getter_with_attribute_access(self):
        class Obj:
            name = "Alice"

        getter = RegistryBuilder._create_getter("obj.name", default="Unknown")
        context = {"obj": Obj()}
        self.assertEqual(getter(context), "Alice")

    def test_getter_with_method_call_no_args(self):
        class Obj:
            def get_name(self):
                return "Alice"

        getter = RegistryBuilder._create_getter("obj.get_name()", default="Unknown")
        context = {"obj": Obj()}
        self.assertEqual(getter(context), "Alice")

    def test_getter_with_method_call_with_args(self):
        class Obj:
            def get_value(self, key):
                return {"name": "Alice", "age": 30}.get(key)

        getter = RegistryBuilder._create_getter("obj.get_value('name')", default="???")
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
            "portfolio.get_ticker('BTC').get_price()", default=0.0
        )
        context = {"portfolio": Portfolio()}
        self.assertEqual(getter(context), 50000.0)

    def test_getter_with_transform_upper(self):
        getter = RegistryBuilder._create_getter(
            "name", default="unknown", transform="upper"
        )
        context = {"name": "alice"}
        self.assertEqual(getter(context), "ALICE")

    def test_getter_with_transform_lower(self):
        getter = RegistryBuilder._create_getter(
            "name", default="UNKNOWN", transform="lower"
        )
        context = {"name": "ALICE"}
        self.assertEqual(getter(context), "alice")

    def test_getter_with_attribute_error_returns_default(self):
        class Obj:
            pass

        getter = RegistryBuilder._create_getter("obj.missing", default="default")
        context = {"obj": Obj()}
        self.assertEqual(getter(context), "default")

    def test_getter_with_type_error_returns_default(self):
        class Obj:
            def get_value(self, key):
                return {"name": "Alice"}.get(key)

        getter = RegistryBuilder._create_getter("obj.get_value()", default="default")
        context = {"obj": Obj()}
        self.assertEqual(getter(context), "default")

    def test_getter_with_missing_object_returns_default(self):
        getter = RegistryBuilder._create_getter("obj.name", default="default")
        context = {}
        self.assertEqual(getter(context), "default")


if __name__ == "__main__":
    unittest.main()
