# ShipBoss MCP Server

An MCP server that provides shipping and logistics capabilities through AI conversations. Connect to FedEx, UPS, and DHL to get rates, create labels, track packages, and manage freight shipments.

## What You Can Do

- **Get shipping rates** across multiple carriers
- **Create shipping labels** with tracking numbers  
- **Track packages** in real-time
- **Schedule carrier pickups**
- **Handle freight shipments** (LTL)
- **Smart address parsing** for global addresses

## Installation

### Step 1: Create Virtual Environment
```bash
python -m venv shipboss_env
```

### Step 2: Activate Virtual Environment
```bash
# Windows:
shipboss_env\Scripts\activate

# macOS/Linux:
source shipboss_env/bin/activate
```

### Step 3: Install Package
```bash
pip install shipboss-mcp-server
```

### Step 4: Find Python Path
```bash
# Windows:
where python
# Output example: C:\Users\yourname\shipboss_env\Scripts\python.exe

# macOS/Linux:
which python
# Output example: /Users/yourname/shipboss_env/bin/python
```

## Configuration

Add to your MCP client configuration:

**Windows:**
```json
{
  "mcpServers": {
    "shipboss": {
      "command": "C:\\Users\\yourname\\shipboss_env\\Scripts\\python.exe",
      "args": ["-m", "shipboss_mcp_server"],
      "env": {
        "SHIPBOSS_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

**macOS/Linux:**
```json
{
  "mcpServers": {
    "shipboss": {
      "command": "/Users/yourname/shipboss_env/bin/python",
      "args": ["-m", "shipboss_mcp_server"],
      "env": {
        "SHIPBOSS_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

Replace the `command` path with your actual Python path from Step 4.

## License

MIT License 