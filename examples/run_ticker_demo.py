#!/usr/bin/env python3
"""
Run the ticker demo to demonstrate method calls in field registries.

This script shows how to use the demo_ticker.py classes with the
demo_layouts_methods.toml configuration to display cryptocurrency data.
"""

import sys
from pathlib import Path

from viewtext import LayoutEngine
from viewtext.loader import LayoutLoader
from viewtext.registry_builder import RegistryBuilder

# Add the examples directory to Python path so demo_ticker can be imported
examples_dir = Path(__file__).parent
sys.path.insert(0, str(examples_dir))


def main():
    """Run the ticker demo."""
    print("=" * 60)
    print("Cryptocurrency Dashboard Demo")
    print("Demonstrating method calls in field registries")
    print("=" * 60)

    # Load the configuration that uses demo_ticker.create_demo_context
    config_path = str(Path(__file__).parent / "demo_layouts_methods.toml")
    loader = LayoutLoader(config_path)

    # Build registry from config (this will call demo_ticker.create_demo_context)
    registry = RegistryBuilder.build_from_config(loader=loader)

    # Create engine with both registry and layout loader
    engine = LayoutEngine(field_registry=registry, layout_loader=loader)

    # Get the crypto dashboard layout
    layout = loader.get_layout("crypto_dashboard")

    # The context is automatically created by the context_provider in the TOML
    # But we need to get it to display what's being used
    from demo_ticker import create_demo_context

    context = create_demo_context()

    print("Context data:")
    btc_price = context["btc"].get_current_price("fiat")
    print(f"  BTC Ticker: {context['btc'].symbol} - ${btc_price}")

    eth_price = context["eth"].get_current_price("fiat")
    print(f"  ETH Ticker: {context['eth'].symbol} - ${eth_price}")

    portfolio_balance = context["portfolio"].get_balance("usd")
    print(f"  Portfolio Balance: ${portfolio_balance}")
    print(f"  User: {context['user_name']}")
    print()

    # Build the layout
    result = engine.build_line_str(layout, context)

    print("Dashboard Output:")
    print("-" * 40)
    print(f"Ticker:        {result[0]}")
    print(f"BTC Price:     {result[1]}")
    print(f"BTC Change:    {result[2]}")
    print(f"BTC Volume:    {result[3]}")
    print(f"ETH Price:     {result[4]}")
    print(f"Portfolio:     {result[5]}")
    print(f"User:          {result[6]}")
    print(f"Portfolio BTC:  {result[7]}")
    print("-" * 40)
    print()

    print("Features demonstrated:")
    print("• Method calls with parameters: btc.get_current_price('fiat')")
    print("• Method calls without parameters: btc.get_price_change()")
    print(
        "• Chained method calls: portfolio.get_ticker('BTC').get_current_price('fiat')"
    )
    print("• Attribute access: btc.symbol, btc.name")
    print("• String transforms: upper() on btc.symbol")
    print("• Mixed data types: strings, floats, integers")
    print("• Context provider function in TOML")


if __name__ == "__main__":
    main()
