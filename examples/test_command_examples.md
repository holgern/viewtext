# Test Command Examples

The `test` command allows you to test individual fields with custom context values and
formatters. This is useful for debugging your field configurations and experimenting
with different values.

## Basic Field Testing

Test a computed field by providing context values:

```bash
viewtext -c examples/computed_fields.toml test total_price price=19.99 quantity=3
```

Output:

```
Testing Field: total_price

Operation: multiply
Sources: price, quantity
Default: 0.0

Context:
  price = 19.99
  quantity = 3

Result: 59.97
```

## Testing with Formatters

Apply a formatter to see the final formatted output:

```bash
viewtext -c examples/computed_fields.toml test total_price price=19.99 quantity=3 --formatter price_fmt
```

Output:

```
Result: 59.97
Formatted: '$59.97'
```

## Testing Temperature Conversion

```bash
viewtext -c examples/computed_fields.toml test temp_f temp_c=25 --formatter temperature
```

Output:

```
Result: 77.0
Formatted: '77.0°F'
```

## Testing Conditional Fields

```bash
viewtext -c examples/computed_fields.toml test user_badge membership=premium
```

Output:

```
Result: '⭐ Premium'
```

```bash
viewtext -c examples/computed_fields.toml test user_badge membership=standard
```

Output:

```
Result: 'Standard'
```

## Testing String Operations

```bash
viewtext -c examples/computed_fields.toml test full_name first_name=John last_name=Doe
```

Output:

```
Result: 'John Doe'
```

## Testing Template Formatters

Template formatters combine multiple fields using a template string. They require the
`--layout` option to specify where the formatter parameters are defined:

```bash
viewtext -c examples/demo_template_formatter.toml test current_price \
  'current_price={"fiat": "€1.234", "usd": 1.15, "sat_usd": 115000}' \
  --formatter template --layout crypto_composite_price
```

Output:

```
Testing Field: current_price

Formatter Parameters:
  template: {current_price_fiat} - ${current_price_usd} - {current_price_sat_usd:.0f} /$
  fields: current_price.fiat, current_price.usd, current_price.sat_usd

Result: {'fiat': '€1.234', 'usd': 1.15, 'sat_usd': 115000}
Formatted: '€1.234 - $1.15 - 115000 /$'
```

## Tips

1. **Numeric values are automatically parsed**: `price=19.99` becomes `float(19.99)`,
   not a string
2. **Use quotes for complex values**: Dictionary values must be quoted in the shell
3. **Template formatters need --layout**: This tells the command where to find the
   template and fields parameters
4. **Test without context**: Omit context values to see the default value behavior

## Error Handling

If you try to use a template formatter without specifying a layout, you'll get a helpful
hint:

```bash
viewtext -c examples/demo_template_formatter.toml test current_price --formatter template
```

Output:

```
Hint: Template formatter requires 'template' and 'fields' parameters.
      Use --layout option to specify a layout that uses this formatter.
      Example: viewtext test current_price --formatter template --layout <layout_name>
```
