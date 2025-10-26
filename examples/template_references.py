"""
Demo: Template References with {{field_name}} Syntax

This example demonstrates how to use {{field_name}} template references in computed
fields. Template references allow you to embed field values directly in strings with
custom formatting.
"""

from pathlib import Path

from viewtext import LayoutEngine
from viewtext.loader import LayoutLoader
from viewtext.registry_builder import RegistryBuilder

config_path = str(Path(__file__).parent / "template_references.toml")
loader = LayoutLoader(config_path)
registry = RegistryBuilder.build_from_config(loader=loader)
engine = LayoutEngine(field_registry=registry, layout_loader=loader)


print("=" * 60)
print("User Profile Display")
print("=" * 60)
context = {
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "city": "New York",
    "country": "USA",
}
layout = loader.get_layout("user_profile")
result = engine.build_line_str(layout, context)
print(f"{result[0]}")
print(f"{result[1]}")
print(f"{result[2]}")
print()

context = {
    "first_name": "Alice",
    "last_name": "Smith",
    "age": 25,
    "city": "London",
    "country": "UK",
}
result = engine.build_line_str(layout, context)
print(f"{result[0]}")
print(f"{result[1]}")
print(f"{result[2]}")
print()


print("=" * 60)
print("Product Information")
print("=" * 60)
context = {
    "product_name": "Laptop",
    "brand": "TechCorp",
    "price": 999.99,
    "currency": "USD",
    "stock": 15,
}
layout = loader.get_layout("product_info")
result = engine.build_line_str(layout, context)
print(f"{result[0]}")
print(f"{result[1]}")
print(f"{result[2]}")
print()

context = {
    "product_name": "Smartphone",
    "brand": "MobileTech",
    "price": 699.99,
    "currency": "EUR",
    "stock": 0,
}
result = engine.build_line_str(layout, context)
print(f"{result[0]}")
print(f"{result[1]}")
print(f"{result[2]}")
print()


print("=" * 60)
print("Weather Report")
print("=" * 60)
context = {
    "location": "San Francisco",
    "temperature": 22,
    "condition": "Sunny",
    "humidity": 65,
    "wind_speed": 12,
}
layout = loader.get_layout("weather_report")
result = engine.build_line_str(layout, context)
print(f"{result[0]}")
print(f"{result[1]}")
print(f"{result[2]}")
print(f"{result[3]}")
print()

context = {
    "location": "Seattle",
    "temperature": 8,
    "condition": "Rainy",
    "humidity": 85,
    "wind_speed": 20,
}
result = engine.build_line_str(layout, context)
print(f"{result[0]}")
print(f"{result[1]}")
print(f"{result[2]}")
print(f"{result[3]}")
print()


print("=" * 60)
print("Order Status")
print("=" * 60)
context = {
    "order_id": "ORD-2024-001",
    "customer_name": "Bob Johnson",
    "status": "shipped",
    "tracking_number": "TRK123456789",
    "estimated_delivery": "2024-01-15",
}
layout = loader.get_layout("order_status")
result = engine.build_line_str(layout, context)
print(f"{result[0]}")
print(f"{result[1]}")
print(f"{result[2]}")
print(f"{result[3]}")
print()

context = {
    "order_id": "ORD-2024-002",
    "customer_name": "Carol White",
    "status": "processing",
    "tracking_number": "",
    "estimated_delivery": "2024-01-20",
}
result = engine.build_line_str(layout, context)
print(f"{result[0]}")
print(f"{result[1]}")
print(f"{result[2]}")
print(f"{result[3]}")
print()


print("=" * 60)
print("File System Display")
print("=" * 60)
context = {
    "file_name": "document.pdf",
    "file_size": 2048576,
    "file_type": "PDF",
    "modified_date": "2024-01-10",
    "permissions": "rw-r--r--",
}
layout = loader.get_layout("file_info")
result = engine.build_line_str(layout, context)
print(f"{result[0]}")
print(f"{result[1]}")
print(f"{result[2]}")
print(f"{result[3]}")
print()

context = {
    "file_name": "image.jpg",
    "file_size": 1024000,
    "file_type": "Image",
    "modified_date": "2024-01-12",
    "permissions": "rwxr-xr-x",
}
result = engine.build_line_str(layout, context)
print(f"{result[0]}")
print(f"{result[1]}")
print(f"{result[2]}")
print(f"{result[3]}")
print()


print("=" * 60)
print("Available Template Reference Features:")
print("=" * 60)
print("• {{field_name}} - Basic field substitution")
print("• {{field_name}} {{field_name}} - Multiple fields in one template")
print("• Prefix{{field_name}}Suffix - Field with custom prefix/suffix")
print("• Conditional templates with different formats")
print("• Default values for missing fields")
print("• Works with formatters for additional formatting")
print("• Combines with other computed operations")
print()
