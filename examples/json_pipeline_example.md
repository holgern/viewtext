# JSON Pipeline Examples

The `render` command supports reading context data from stdin as JSON using the `--json`
or `-j` flag. This enables powerful pipeline workflows where you can process data from
other programs and visualize it with ViewText.

## Basic JSON Input

Pipe JSON data directly to ViewText:

```bash
echo '{"student":"Alice","score1":85.5,"score2":92.0,"score3":88.5}' | \
  viewtext -c examples/computed_fields.toml render scores --json
```

Output:

```
Rendered Output: scores

────────────────────────────────────────────────────────────────────────────────
0: Alice
...
15: 85.5
...
25: 92.0
...
35: 88.5
...
45: 88.7
────────────────────────────────────────────────────────────────────────────────
```

## Pipeline with Python

Generate JSON from a Python script and pipe it to ViewText:

```bash
python3 -c "import json; print(json.dumps({'product': 'Widget', 'quantity': 3, 'price': 25.50}))" | \
  viewtext -c examples/computed_fields.toml render shopping --json
```

Output:

```
Rendered Output: shopping

────────────────────────────────────────────────────────────────────────────────
0: Widget
...
15: 3x
...
20: 25.5
...
30: 76.5
...
45: 20.4
────────────────────────────────────────────────────────────────────────────────
```

## Pipeline with API Data

Fetch data from an API and visualize it:

```bash
curl -s https://api.example.com/data | \
  viewtext -c examples/computed_fields.toml render scores --json
```

Or with `jq` for data transformation:

```bash
curl -s https://api.example.com/users | \
  jq '.users[0]' | \
  viewtext -c examples/computed_fields.toml render scores --json
```

## Pipeline with File Processing

Process JSON files:

```bash
cat data.json | viewtext -c examples/computed_fields.toml render scores --json
```

Or with `jq` filtering:

```bash
jq '.[] | select(.status == "active")' data.json | \
  viewtext -c examples/computed_fields.toml render scores --json
```

## Real-World Example: Weather Data

```bash
curl -s "https://api.weather.com/current?location=NYC" | \
  jq '{location: .city, temp_morning: .temps[0], temp_noon: .temps[1], temp_evening: .temps[2]}' | \
  viewtext -c examples/computed_fields.toml render weather --json
```

## Real-World Example: Database Query

```bash
psql -U user -d database -t -A -F"," -c "SELECT name, score1, score2, score3 FROM students WHERE id = 123" | \
  awk -F',' '{print "{\"student\":\""$1"\",\"score1\":"$2",\"score2\":"$3",\"score3\":"$4"}"}' | \
  viewtext -c examples/computed_fields.toml render scores --json
```

## Error Handling

### Invalid JSON

If the input is not valid JSON, you'll get a clear error message:

```bash
echo 'invalid json' | viewtext -c examples/computed_fields.toml render scores --json
```

Output:

```
Error parsing JSON: Expecting value: line 1 column 1 (char 0)
```

### Missing stdin

If you use the `--json` flag without piping data:

```bash
viewtext -c examples/computed_fields.toml render scores --json
```

Output:

```
Error: --json flag requires JSON data from stdin
```

## Use Cases

1. **API Integration**: Fetch live data from REST APIs and visualize it
2. **Database Queries**: Transform database query results into formatted layouts
3. **Log Processing**: Parse and display structured log data
4. **IoT/Sensors**: Process sensor data streams
5. **Monitoring**: Display system metrics from monitoring tools
6. **Testing**: Generate test data programmatically for layout validation
7. **CI/CD**: Display build/deployment information from automation pipelines

## Tips

1. **Use `jq` for transformation**: Pre-process JSON data to match your field structure
2. **Combine with `watch`**: Create live dashboards:
   `watch -n 5 'curl -s API_URL | viewtext -c config.toml render layout --json'`
3. **Handle errors**: Use `|| echo '{}'` to provide fallback empty JSON on errors
4. **Format complex data**: Use `jq` to flatten nested structures before piping to
   ViewText
5. **Testing**: Use `echo` with JSON for quick testing before connecting real data
   sources

## Comparison: JSON Input vs Context Provider

There are two ways to provide context data to ViewText:

### JSON Input (Pipeline)

- **When to use**: Dynamic data from external sources, API calls, one-off rendering
- **Advantages**: Flexible, no code needed, composable with other tools
- **Example**: `curl ... | viewtext render layout --json`

### Context Provider (Function)

- **When to use**: Reusable data sources, complex data generation, development
- **Advantages**: No external dependencies, version controlled, can include complex
  logic
- **Example**: Set `context_provider` in TOML, run `viewtext render layout`

Choose based on your use case: pipelines for dynamic/external data, context providers
for static/reusable configurations.
