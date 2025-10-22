Examples
========

This section provides practical examples of using ViewText for various use cases.

Weather Dashboard
-----------------

A simple weather information display.

**Field Registry**

.. code-block:: python

    from viewtext import BaseFieldRegistry

    registry = BaseFieldRegistry()

    registry.register("city", lambda ctx: ctx["location"]["city"])
    registry.register("temp", lambda ctx: ctx["current"]["temp"])
    registry.register("feels_like", lambda ctx: ctx["current"]["feels_like"])
    registry.register("humidity", lambda ctx: ctx["current"]["humidity"])
    registry.register("wind_speed", lambda ctx: ctx["current"]["wind_speed"])
    registry.register("condition", lambda ctx: ctx["current"]["condition"])

**Layout Configuration** (``weather.toml``)

.. code-block:: toml

    [layouts.weather]
    name = "Weather Display"

    [[layouts.weather.lines]]
    field = "city"
    index = 0
    formatter = "text_uppercase"

    [[layouts.weather.lines]]
    field = "condition"
    index = 1
    formatter = "text"

    [[layouts.weather.lines]]
    field = "temp"
    index = 2
    formatter = "number"

    [layouts.weather.lines.formatter_params]
    suffix = "°F"
    decimals = 1

    [[layouts.weather.lines]]
    field = "feels_like"
    index = 3
    formatter = "text"

    [layouts.weather.lines.formatter_params]
    prefix = "Feels like: "
    suffix = "°F"

    [[layouts.weather.lines]]
    field = "humidity"
    index = 4
    formatter = "number"

    [layouts.weather.lines.formatter_params]
    prefix = "Humidity: "
    suffix = "%"
    decimals = 0

    [[layouts.weather.lines]]
    field = "wind_speed"
    index = 5
    formatter = "number"

    [layouts.weather.lines.formatter_params]
    prefix = "Wind: "
    suffix = " mph"
    decimals = 1

**Usage**

.. code-block:: python

    from viewtext import LayoutEngine, LayoutLoader

    loader = LayoutLoader("weather.toml")
    engine = LayoutEngine(field_registry=registry)

    context = {
        "location": {"city": "San Francisco"},
        "current": {
            "temp": 72.5,
            "feels_like": 70.2,
            "humidity": 65,
            "wind_speed": 8.3,
            "condition": "Partly Cloudy"
        }
    }

    layout = loader.get_layout("weather")
    lines = engine.build_line_str(layout, context)

    for line in lines:
        print(line)

**Output**

.. code-block:: text

    SAN FRANCISCO
    Partly Cloudy
    72.5°F
    Feels like: 70.2°F
    Humidity: 65%
    Wind: 8.3 mph

Cryptocurrency Ticker
---------------------

Display cryptocurrency prices and changes.

**Field Registry**

.. code-block:: python

    from viewtext import BaseFieldRegistry
    from datetime import datetime

    registry = BaseFieldRegistry()

    registry.register("symbol", lambda ctx: ctx["symbol"])
    registry.register("price", lambda ctx: ctx["price"])
    registry.register("change_24h", lambda ctx: ctx["change_24h"])
    registry.register("volume", lambda ctx: ctx["volume_24h"])
    registry.register("last_update", lambda ctx: ctx["timestamp"])

**Layout Configuration** (``crypto.toml``)

.. code-block:: toml

    [formatters.usd]
    type = "price"
    symbol = "$"
    decimals = 2
    thousands_sep = ","

    [formatters.large_number]
    type = "number"
    decimals = 0
    thousands_sep = ","

    [layouts.crypto_ticker]
    name = "Crypto Ticker"

    [[layouts.crypto_ticker.lines]]
    field = "symbol"
    index = 0
    formatter = "text_uppercase"

    [[layouts.crypto_ticker.lines]]
    field = "price"
    index = 1
    formatter = "usd"

    [[layouts.crypto_ticker.lines]]
    field = "change_24h"
    index = 2
    formatter = "text"

    [layouts.crypto_ticker.lines.formatter_params]
    prefix = "24h: "
    suffix = "%"

    [[layouts.crypto_ticker.lines]]
    field = "volume"
    index = 3
    formatter = "usd"

    [layouts.crypto_ticker.lines.formatter_params]
    prefix = "Vol: "

    [[layouts.crypto_ticker.lines]]
    field = "last_update"
    index = 4
    formatter = "datetime"

    [layouts.crypto_ticker.lines.formatter_params]
    format = "%H:%M:%S"

**Usage**

.. code-block:: python

    from viewtext import LayoutEngine, LayoutLoader
    import time

    loader = LayoutLoader("crypto.toml")
    engine = LayoutEngine(field_registry=registry)

    context = {
        "symbol": "btc",
        "price": 45234.56,
        "change_24h": 2.34,
        "volume_24h": 28500000000,
        "timestamp": time.time()
    }

    layout = loader.get_layout("crypto_ticker")
    lines = engine.build_line_str(layout, context)

    for line in lines:
        print(line)

**Output**

.. code-block:: text

    BTC
    $45,234.56
    24h: 2.34%
    Vol: $28,500,000,000.00
    14:23:45

System Monitor
--------------

Display system resource usage.

**Field Registry**

.. code-block:: python

    import psutil
    from viewtext import BaseFieldRegistry

    registry = BaseFieldRegistry()

    registry.register("cpu_percent", lambda ctx: psutil.cpu_percent())
    registry.register("memory_percent", lambda ctx: psutil.virtual_memory().percent)
    registry.register("disk_percent", lambda ctx: psutil.disk_usage('/').percent)
    registry.register("uptime", lambda ctx: time.time() - psutil.boot_time())

**Layout Configuration** (``system.toml``)

.. code-block:: toml

    [layouts.system_monitor]
    name = "System Monitor"

    [[layouts.system_monitor.lines]]
    field = "cpu_percent"
    index = 0
    formatter = "number"

    [layouts.system_monitor.lines.formatter_params]
    prefix = "CPU: "
    suffix = "%"
    decimals = 1

    [[layouts.system_monitor.lines]]
    field = "memory_percent"
    index = 1
    formatter = "number"

    [layouts.system_monitor.lines.formatter_params]
    prefix = "RAM: "
    suffix = "%"
    decimals = 1

    [[layouts.system_monitor.lines]]
    field = "disk_percent"
    index = 2
    formatter = "number"

    [layouts.system_monitor.lines.formatter_params]
    prefix = "Disk: "
    suffix = "%"
    decimals = 1

    [[layouts.system_monitor.lines]]
    field = "uptime"
    index = 3
    formatter = "relative_time"

    [layouts.system_monitor.lines.formatter_params]
    format = "long"

**Usage**

.. code-block:: python

    from viewtext import LayoutEngine, LayoutLoader

    loader = LayoutLoader("system.toml")
    engine = LayoutEngine(field_registry=registry)

    layout = loader.get_layout("system_monitor")

    # Update every second
    import time
    while True:
        lines = engine.build_line_str(layout, {})

        # Clear screen and print
        print("\033[2J\033[H")
        for line in lines:
            print(line)

        time.sleep(1)

**Output**

.. code-block:: text

    CPU: 23.5%
    RAM: 67.2%
    Disk: 45.8%
    Uptime: 5 hours ago

E-Commerce Product Display
---------------------------

Display product information for e-commerce.

**Field Registry**

.. code-block:: python

    from viewtext import BaseFieldRegistry

    registry = BaseFieldRegistry()

    registry.register("name", lambda ctx: ctx["product"]["name"])
    registry.register("sku", lambda ctx: ctx["product"]["sku"])
    registry.register("price", lambda ctx: ctx["product"]["price"])
    registry.register("stock", lambda ctx: ctx["product"]["stock"])
    registry.register("category", lambda ctx: ctx["product"]["category"])

**Layout Configuration** (``product.toml``)

.. code-block:: toml

    [formatters.currency]
    type = "price"
    symbol = "$"
    decimals = 2

    [layouts.product_card]
    name = "Product Card"

    [[layouts.product_card.lines]]
    field = "name"
    index = 0
    formatter = "text"

    [[layouts.product_card.lines]]
    field = "sku"
    index = 1
    formatter = "text"

    [layouts.product_card.lines.formatter_params]
    prefix = "SKU: "

    [[layouts.product_card.lines]]
    field = "price"
    index = 2
    formatter = "currency"

    [[layouts.product_card.lines]]
    field = "stock"
    index = 3
    formatter = "number"

    [layouts.product_card.lines.formatter_params]
    prefix = "In Stock: "
    decimals = 0

    [[layouts.product_card.lines]]
    field = "category"
    index = 4
    formatter = "text"

    [layouts.product_card.lines.formatter_params]
    prefix = "Category: "

**Usage**

.. code-block:: python

    from viewtext import LayoutEngine, LayoutLoader

    loader = LayoutLoader("product.toml")
    engine = LayoutEngine(field_registry=registry)

    context = {
        "product": {
            "name": "Wireless Headphones",
            "sku": "WH-2024-001",
            "price": 149.99,
            "stock": 47,
            "category": "Electronics"
        }
    }

    layout = loader.get_layout("product_card")
    lines = engine.build_line_str(layout, context)

    for line in lines:
        print(line)

**Output**

.. code-block:: text

    Wireless Headphones
    SKU: WH-2024-001
    $149.99
    In Stock: 47
    Category: Electronics

Array Indexing and Nested Data
-------------------------------

Access array elements and nested data structures using dot notation and numeric indices.

**Field Mappings** (``fields.toml``)

.. code-block:: toml

    [fields.first_block_fee]
    context_key = "mempool_blocks.0.medianFee"
    default = 0

    [fields.second_block_fee]
    context_key = "mempool_blocks.1.medianFee"
    default = 0

    [fields.fastest_fee]
    context_key = "recommended_fees.fastestFee"
    default = 0

**Layout Configuration** (``mempool.toml``)

.. code-block:: toml

    [layouts.mempool_fees]
    name = "Mempool Fees"

    [[layouts.mempool_fees.lines]]
    field = "fastest_fee"
    index = 0
    formatter = "number"

    [layouts.mempool_fees.lines.formatter_params]
    prefix = "Fastest: "
    suffix = " sat/vB"
    decimals = 0

    [[layouts.mempool_fees.lines]]
    field = "first_block_fee"
    index = 1
    formatter = "number"

    [layouts.mempool_fees.lines.formatter_params]
    prefix = "Block 1: "
    suffix = " sat/vB"
    decimals = 0

    [[layouts.mempool_fees.lines]]
    field = "second_block_fee"
    index = 2
    formatter = "number"

    [layouts.mempool_fees.lines.formatter_params]
    prefix = "Block 2: "
    suffix = " sat/vB"
    decimals = 0

**Usage**

.. code-block:: python

    from viewtext import LayoutEngine, LayoutLoader, RegistryBuilder

    loader = LayoutLoader("mempool.toml", fields_path="fields.toml")
    layout = loader.get_layout("mempool_fees")

    registry = RegistryBuilder.build_from_config(loader=loader)
    engine = LayoutEngine(field_registry=registry)

    context = {
        "recommended_fees": {
            "fastestFee": 15,
            "halfHourFee": 12,
            "hourFee": 10
        },
        "mempool_blocks": [
            {"medianFee": 14, "totalFees": 0.5},
            {"medianFee": 12, "totalFees": 0.4},
            {"medianFee": 10, "totalFees": 0.3}
        ]
    }

    lines = engine.build_line_str(layout, context)

    for line in lines:
        print(line)

**Output**

.. code-block:: text

    Fastest: 15 sat/vB
    Block 1: 14 sat/vB
    Block 2: 12 sat/vB

**Array Indexing Syntax**

- ``tags.0`` - Access first element of array
- ``matrix.0.1`` - Access nested array element
- ``users.0.name`` - Access property of array element
- ``items.5.price.usd`` - Deep nesting with arrays and objects

See ``examples/mempool_layouts.toml`` for a complete example.

Dictionary Layout Example
-------------------------

Dictionary layouts produce key-value pairs instead of indexed lines. This is ideal for
JSON APIs, configuration generation, or structured data export.

**Field Mappings** (``fields.toml``)

.. code-block:: toml

    [fields.temperature]
    context_key = "temp"
    default = 0

    [fields.price_value]
    context_key = "price"
    default = 0

    [fields.text_value]
    context_key = "message"
    default = ""

    [fields.timestamp]
    context_key = "time"
    default = 0

**Layout Configuration** (``weather_api.toml``)

.. code-block:: toml

    [layouts.weather_dict]
    name = "Weather API Response"

    [[layouts.weather_dict.items]]
    key = "temp"
    field = "temperature"
    formatter = "number"

    [layouts.weather_dict.items.formatter_params]
    decimals = 1
    suffix = "°"

    [[layouts.weather_dict.items]]
    key = "price"
    field = "price_value"
    formatter = "price"

    [layouts.weather_dict.items.formatter_params]
    symbol = "$"
    decimals = 2

    [[layouts.weather_dict.items]]
    key = "message"
    field = "text_value"
    formatter = "text"

    [[layouts.weather_dict.items]]
    key = "time"
    field = "timestamp"
    formatter = "datetime"

    [layouts.weather_dict.items.formatter_params]
    format = "%Y-%m-%d %H:%M:%S"

**Usage**

.. code-block:: python

    from viewtext import LayoutEngine, LayoutLoader, RegistryBuilder

    loader = LayoutLoader("weather_api.toml", fields_path="fields.toml")
    layout = loader.get_layout("weather_dict")

    registry = RegistryBuilder.build_from_config(loader=loader)
    engine = LayoutEngine(field_registry=registry)

    context = {
        "temp": 72.5,
        "price": 19.99,
        "message": "Partly cloudy",
        "time": 1234567890
    }

    result = engine.build_dict_str(layout, context)

    # Use as dictionary
    print(result["temp"])
    print(result["message"])

    # Or export as JSON
    import json
    print(json.dumps(result, indent=2))

**Output (Dictionary)**

.. code-block:: python

    {
        "temp": "72.5°",
        "price": "$19.99",
        "message": "Partly cloudy",
        "time": "2009-02-14 00:31:30"
    }

**CLI Usage**

.. code-block:: bash

    # Render as key:value pairs
    echo '{"temp": 72.5, "price": 19.99}' | viewtext render weather_dict

    # Output as JSON
    echo '{"temp": 72.5, "price": 19.99}' | viewtext render weather_dict --json

**Output (CLI text format)**

.. code-block:: text

    temp: 72.5°
    price: $19.99
    message: Partly cloudy
    time: 2009-02-14 00:31:30

**Output (CLI JSON format)**

.. code-block:: json

    {
      "temp": "72.5°",
      "price": "$19.99",
      "message": "Partly cloudy",
      "time": "2009-02-14 00:31:30"
    }

See ``dict_example.toml`` for a complete example with multiple dictionary layouts.

Custom Formatter Example
-------------------------

Create a custom formatter for special formatting needs.

**Custom Formatter**

.. code-block:: python

    from viewtext import get_formatter_registry

    def format_status(value, **kwargs):
        status_map = {
            "online": "🟢 Online",
            "offline": "🔴 Offline",
            "away": "🟡 Away",
            "busy": "🔴 Busy"
        }
        return status_map.get(value, f"❓ {value}")

    def format_progress_bar(value, **kwargs):
        width = kwargs.get("width", 20)
        filled = int((value / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"{bar} {value:.0f}%"

    # Register custom formatters
    registry = get_formatter_registry()
    registry.register("status", format_status)
    registry.register("progress", format_progress_bar)

**Usage**

.. code-block:: python

    from viewtext import BaseFieldRegistry, LayoutEngine

    field_registry = BaseFieldRegistry()
    field_registry.register("user_status", lambda ctx: ctx["status"])
    field_registry.register("download_progress", lambda ctx: ctx["progress"])

    layout = {
        "name": "Custom Display",
        "lines": [
            {
                "field": "user_status",
                "index": 0,
                "formatter": "status"
            },
            {
                "field": "download_progress",
                "index": 1,
                "formatter": "progress",
                "formatter_params": {"width": 30}
            }
        ]
    }

    engine = LayoutEngine(field_registry=field_registry)

    context = {
        "status": "online",
        "progress": 67
    }

    lines = engine.build_line_str(layout, context)

    for line in lines:
        print(line)

**Output**

.. code-block:: text

    🟢 Online
    ████████████████████░░░░░░░░░░ 67%
