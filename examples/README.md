# LuminaAI Examples

This directory contains example code demonstrating how to use the LuminaAI platform.

## Examples

### planner_client.py

A Python client that demonstrates how to use the Planner gRPC API.

**Usage:**

```bash
# Make sure the Planner service is running
python -m agents.planner.main

# In another terminal, run the example
cd examples
python planner_client.py
```

**Features:**
- Connect to Planner service
- Generate plans from natural language prompts
- Parse and display DAGs
- Error handling and timeouts

## Running Examples

### Prerequisites

1. Install dependencies:
   ```bash
   pip install -r ../agents/planner/requirements.txt
   ```

2. Start the Planner service:
   ```bash
   python -m agents.planner.main
   ```

3. Run an example:
   ```bash
   python planner_client.py
   ```

## Support

For questions or issues, please open an issue on GitHub:
https://github.com/goody81/LuminaAI/issues
