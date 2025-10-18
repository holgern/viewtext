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
