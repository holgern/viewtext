# Ticker Demo - Method Calls in Field Registries

This demo demonstrates how to use method calls and attribute access in viewtext field
registries. It shows how to call methods on objects, access attributes, and chain method
calls.

## Files

- **`demo_ticker.py`** - Mock cryptocurrency ticker and portfolio classes
- **`demo_layouts_methods.toml`** - Configuration using method calls and context
  provider
- **`run_ticker_demo.py`** - Python script to run the demo

## How to Use

### Method 1: Run the Python Demo Script

```bash
python examples/run_ticker_demo.py
```

This is the recommended approach as it handles the Python path automatically.

### Method 2: Use the ViewText CLI

```bash
# First, add examples directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/examples"

# Then run the CLI command
viewtext --config examples/demo_layouts_methods.toml render crypto_dashboard
```

### Method 3: Use Python Interactively

```python
import sys
from pathlib import Path

# Add examples to path
sys.path.insert(0, str(Path('examples')))

from viewtext import LayoutEngine, LayoutLoader, RegistryBuilder
from demo_ticker import create_demo_context

# Load and run
loader = LayoutLoader('examples/demo_layouts_methods.toml')
registry = RegistryBuilder.build_from_config(loader=loader)
engine = LayoutEngine(field_registry=registry, layout_loader=loader)

context = create_demo_context()
layout = loader.get_layout('crypto_dashboard')
result = engine.build_line_str(layout, context)

for i, line in enumerate(result):
    print(f"[{i}]: {line}")
```

## Features Demonstrated

### Method Calls with Parameters

```toml
[inputs.btc_fiat_price]
context_key = "btc.get_current_price('fiat')"
```

### Method Calls without Parameters

```toml
[inputs.btc_price_change]
context_key = "btc.get_price_change()"
```

### Chained Method Calls

```toml
[inputs.portfolio_btc_ticker_price]
context_key = "portfolio.get_ticker('BTC').get_current_price('fiat')"
```

### Attribute Access

```toml
[inputs.btc_symbol]
context_key = "btc.symbol"
```

### String Transforms

```toml
[inputs.btc_symbol_upper]
context_key = "btc.symbol"
transform = "upper"
```

### Context Provider Function

```toml
context_provider = "demo_ticker.create_demo_context"
```

## Expected Output

```
============================================================
Cryptocurrency Dashboard Demo
Demonstrating method calls in field registries
============================================================
Context data:
  BTC Ticker: BTC - $67890.5
  ETH Ticker: ETH - $3456.78
  Portfolio Balance: $10000.0
  User: Alice

Dashboard Output:
----------------------------------------
Ticker:        [BTC] BTC Token
BTC Price:     67890.50
BTC Change:    5
BTC Volume:    1234567
ETH Price:     3456.78
Portfolio:     10000.00
User:          Alice
Portfolio BTC:  50000.00
----------------------------------------
```

## Key Concepts

1. **Context Provider**: The TOML file specifies
   `context_provider = "demo_ticker.create_demo_context"` which automatically creates
   the context object.

2. **Method Call Syntax**: Use `object.method()` syntax in `context_key` to call
   methods.

3. **Method Parameters**: Pass parameters to methods using standard Python syntax:
   `method('param')`.

4. **Chained Calls**: Chain multiple method calls: `obj.method1().method2()`.

5. **Attribute Access**: Access object attributes directly: `object.attribute`.

6. **Transforms**: Apply string transforms like `upper`, `lower`, etc.

This demo shows how viewtext can work with complex Python objects, not just simple
dictionaries.
