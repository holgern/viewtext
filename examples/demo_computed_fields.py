"""
Demo: Computed Fields

This example demonstrates how to use computed fields in viewtext layouts.
Computed fields allow you to perform calculations on source data without
writing Python code - everything is defined in TOML configuration.
"""

from pathlib import Path

from viewtext import LayoutEngine
from viewtext.loader import LayoutLoader
from viewtext.registry_builder import RegistryBuilder

config_path = str(Path(__file__).parent / "computed_fields.toml")
loader = LayoutLoader(config_path)
registry = RegistryBuilder.build_from_config(loader=loader)
engine = LayoutEngine(registry)


print("=" * 60)
print("Temperature Conversion")
print("=" * 60)
context = {"temp_c": 25}
layout = loader.get_layout("temperature")
result = engine.build_line_str(layout, context)
print(f"Celsius: {result[0]:>10}  Fahrenheit: {result[10]:>10}")
print()

context = {"temp_c": 0}
result = engine.build_line_str(layout, context)
print(f"Celsius: {result[0]:>10}  Fahrenheit: {result[10]:>10}")
print()

context = {"temp_c": 100}
result = engine.build_line_str(layout, context)
print(f"Celsius: {result[0]:>10}  Fahrenheit: {result[10]:>10}")
print()


print("=" * 60)
print("Shopping Cart with Price Calculations")
print("=" * 60)
context = {
    "product": "Widget",
    "quantity": 3,
    "price": 19.99,
}
layout = loader.get_layout("shopping")
result = engine.build_line_str(layout, context)
print(
    f"Product: {result[0]:12}  Qty: {result[15]:3}  "
    f"Price: {result[20]:8}  Total: {result[30]:8}  {result[45]}"
)
print()

context = {
    "product": "Gadget",
    "quantity": 5,
    "price": 49.99,
}
result = engine.build_line_str(layout, context)
print(
    f"Product: {result[0]:12}  Qty: {result[15]:3}  "
    f"Price: {result[20]:8}  Total: {result[30]:8}  {result[45]}"
)
print()


print("=" * 60)
print("Student Scores with Average")
print("=" * 60)
context = {
    "student": "Alice",
    "score1": 85.5,
    "score2": 92.0,
    "score3": 88.5,
}
layout = loader.get_layout("scores")
result = engine.build_line_str(layout, context)
print(
    f"Student: {result[0]:10}  Scores: {result[15]:5} {result[25]:5} "
    f"{result[35]:5}  {result[45]}"
)
print()

context = {
    "student": "Bob",
    "score1": 78.0,
    "score2": 82.5,
    "score3": 80.0,
}
result = engine.build_line_str(layout, context)
print(
    f"Student: {result[0]:10}  Scores: {result[15]:5} {result[25]:5} "
    f"{result[35]:5}  {result[45]}"
)
print()


print("=" * 60)
print("Weather with Min/Max Temperatures")
print("=" * 60)
context = {
    "location": "New York",
    "temp_morning": 15,
    "temp_noon": 25,
    "temp_evening": 20,
}
layout = loader.get_layout("weather")
result = engine.build_line_str(layout, context)
print(f"Location: {result[0]:15}  {result[15]:12}  {result[30]}")
print()

context = {
    "location": "Boston",
    "temp_morning": -5,
    "temp_noon": 2,
    "temp_evening": -3,
}
result = engine.build_line_str(layout, context)
print(f"Location: {result[0]:15}  {result[15]:12}  {result[30]}")
print()


print("=" * 60)
print("Speed Unit Conversion")
print("=" * 60)
context = {"speed_kmh": 100}
layout = loader.get_layout("speed")
result = engine.build_line_str(layout, context)
print(f"Speed: {result[0]:12}  =  {result[20]}")
print()

context = {"speed_kmh": 60}
result = engine.build_line_str(layout, context)
print(f"Speed: {result[0]:12}  =  {result[20]}")
print()


print("=" * 60)
print("Available Operations:")
print("=" * 60)
print("• celsius_to_fahrenheit - Convert °C to °F")
print("• fahrenheit_to_celsius - Convert °F to °C")
print("• multiply - Multiply two or more values")
print("• divide - Divide two values (safe with divide-by-zero handling)")
print("• add - Sum multiple values")
print("• subtract - Subtract two values")
print("• average - Calculate average of multiple values")
print("• min - Find minimum of multiple values")
print("• max - Find maximum of multiple values")
print("• abs - Absolute value")
print("• round - Round to nearest integer")
print("• linear_transform - Apply formula: (value * multiply / divide) + add")
print()
