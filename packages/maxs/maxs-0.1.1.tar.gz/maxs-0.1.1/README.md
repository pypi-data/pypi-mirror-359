# maxs

minimalist ai agent using local ollama models

## install

```bash
pipx install maxs
maxs
```

## prerequisites

- ollama installed and running
- model pulled: `ollama pull qwen3:1.7b`

## usage

```bash
# basic
maxs

# custom model
MODEL_ID=llama3.2:3b maxs

# custom host
OLLAMA_HOST=http://192.168.1.100:11434 maxs
```

## custom tools

create python files in `./tools/`:

```python
# ./tools/tip.py
from strands import tool

@tool
def calculate_tip(amount: float, percentage: float = 15.0) -> dict:
    tip = amount * (percentage / 100)
    return {
        "status": "success",
        "content": [{"text": f"tip: ${tip:.2f}, total: ${amount + tip:.2f}"}]
    }
```

tools are immediately available.

## configuration

| variable | default | description |
|----------|---------|-------------|
| MODEL_ID | qwen3:1.7b | ollama model |
| OLLAMA_HOST | http://localhost:11434 | ollama server |

## build binary

```bash
pip install maxs[binary]
pyinstaller --onefile --name maxs -m maxs.main
```

binary in `./dist/maxs`

## license

mit