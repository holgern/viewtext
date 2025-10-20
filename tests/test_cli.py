import json
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from viewtext.cli import app

runner = CliRunner()


def test_render_json_output():
    config_content = """
[fields.demo1]
context_key = "demo1"

[fields.demo2]
context_key = "demo2"

[layouts.demo]
name = "Demo Display"

[[layouts.demo.lines]]
field = "demo1"
index = 0
formatter = "text"

[[layouts.demo.lines]]
field = "demo2"
index = 1
formatter = "text"
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "layouts.toml"
        config_path.write_text(config_content)

        json_input = '{"demo1": "Line 1", "demo2": "Line 2"}'

        result = runner.invoke(
            app,
            ["--config", str(config_path), "render", "demo", "--json"],
            input=json_input,
        )

        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert output == ["Line 1", "Line 2"]


def test_render_json_output_with_formatters():
    config_content = """
[fields.text_value]
context_key = "text_value"

[fields.number_value]
context_key = "number_value"

[fields.price_value]
context_key = "price_value"

[layouts.advanced]
name = "Advanced Features Demo"

[[layouts.advanced.lines]]
field = "text_value"
index = 0
formatter = "text"

[[layouts.advanced.lines]]
field = "number_value"
index = 1
formatter = "number"

[[layouts.advanced.lines]]
field = "price_value"
index = 2
formatter = "price"
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "layouts.toml"
        config_path.write_text(config_content)

        json_input = (
            '{"text_value": "hello", "number_value": 1234.56, "price_value": 99.99}'
        )

        result = runner.invoke(
            app,
            ["--config", str(config_path), "render", "advanced", "--json"],
            input=json_input,
        )

        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert len(output) == 3
        assert output[0] == "hello"
        assert output[1] == "1235"
        assert output[2] == "99.99"


def test_render_without_json_output():
    config_content = """
[fields.demo1]
context_key = "demo1"

[layouts.demo]
name = "Demo Display"

[[layouts.demo.lines]]
field = "demo1"
index = 0
formatter = "text"
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "layouts.toml"
        config_path.write_text(config_content)

        json_input = '{"demo1": "Test Line"}'

        result = runner.invoke(
            app, ["--config", str(config_path), "render", "demo"], input=json_input
        )

        assert result.exit_code == 0
        assert "Test Line" in result.stdout
        assert "[" not in result.stdout or "Rendered Output" in result.stdout


def test_generate_fields_simple():
    json_input = '{"name": "John", "age": 30}'

    result = runner.invoke(app, ["generate-fields"], input=json_input)

    assert result.exit_code == 0
    assert "[fields.name]" in result.stdout
    assert 'context_key = "name"' in result.stdout
    assert 'type = "str"' in result.stdout
    assert "[fields.age]" in result.stdout
    assert 'context_key = "age"' in result.stdout
    assert 'type = "int"' in result.stdout


def test_generate_fields_nested():
    json_input = '{"user": {"name": "Alice", "age": 25}, "active": true}'

    result = runner.invoke(app, ["generate-fields"], input=json_input)

    assert result.exit_code == 0
    assert "[fields.user_name]" in result.stdout
    assert 'context_key = "user.name"' in result.stdout
    assert 'type = "str"' in result.stdout
    assert "[fields.user_age]" in result.stdout
    assert 'context_key = "user.age"' in result.stdout
    assert 'type = "int"' in result.stdout
    assert "[fields.active]" in result.stdout
    assert 'type = "bool"' in result.stdout


def test_generate_fields_with_prefix():
    json_input = '{"temp": 25.5, "city": "Berlin"}'

    result = runner.invoke(
        app, ["generate-fields", "--prefix", "api_"], input=json_input
    )

    assert result.exit_code == 0
    assert "[fields.api_temp]" in result.stdout
    assert 'context_key = "temp"' in result.stdout
    assert 'type = "float"' in result.stdout
    assert "[fields.api_city]" in result.stdout
    assert 'context_key = "city"' in result.stdout


def test_generate_fields_to_file():
    json_input = '{"test": "value"}'

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "fields.toml"

        result = runner.invoke(
            app, ["generate-fields", "--output", str(output_path)], input=json_input
        )

        assert result.exit_code == 0
        assert output_path.exists()

        content = output_path.read_text()
        assert "[fields.test]" in content
        assert 'context_key = "test"' in content
        assert 'type = "str"' in content


def test_generate_fields_no_stdin():
    result = runner.invoke(app, ["generate-fields"])

    assert result.exit_code == 1
    assert "stdin data" in result.stdout.lower() or "empty" in result.stdout.lower()


def test_generate_fields_empty_stdin():
    result = runner.invoke(app, ["generate-fields"], input="")

    assert result.exit_code == 1
    assert "Empty stdin data" in result.stdout


def test_generate_fields_invalid_json():
    result = runner.invoke(app, ["generate-fields"], input="not valid json")

    assert result.exit_code == 1
    assert "Invalid JSON" in result.stdout


def test_generate_fields_non_dict_json():
    result = runner.invoke(app, ["generate-fields"], input='["array", "not", "dict"]')

    assert result.exit_code == 1
    assert "must be an object/dictionary" in result.stdout


def test_generate_fields_types():
    json_input = """{
        "str_val": "hello",
        "int_val": 42,
        "float_val": 3.14,
        "bool_val": true,
        "null_val": null,
        "list_val": [1, 2, 3]
    }"""

    result = runner.invoke(app, ["generate-fields"], input=json_input)

    assert result.exit_code == 0
    assert 'type = "str"' in result.stdout
    assert 'type = "int"' in result.stdout
    assert 'type = "float"' in result.stdout
    assert 'type = "bool"' in result.stdout
    assert 'type = "any"' in result.stdout
    assert 'type = "list"' in result.stdout
