"""
gemma_tool_call.py – minimal “function calling” demo with Gemma 3 4B in MLX
"""

import json, re
from mlx_lm import load, generate
from tools.create_file import create_file

# ----------------------------------------------------------------------
# 1. Load the Gemma-3 model that’s in MLX format (4-bit = fits in ~6 GB RAM)
# ----------------------------------------------------------------------
MODEL_ID = "mlx-community/gemma-3-text-4b-it-4bit"
model, tokenizer = load(MODEL_ID)

def get_current_weather(location, unit="celsius"):
    """
    Dummy function to simulate a weather API call.
    In practice, you would replace this with an actual API call.
    """
    return {
        "location": location,
        "temperature": 20 if unit == "celsius" else 68,
        "unit": unit
    }

# ----------------------------------------------------------------------
# 2. Declare one or more tools in JSON (OpenAI / Gemini style schema)
# ----------------------------------------------------------------------
tools = [
    {
        "name": "get_current_weather",
        "description": "Return the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "unit":     {"type": "string",
                             "enum": ["celsius", "fahrenheit"],
                             "description": "Temperature unit"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "create_file",
        "description": "Create a file with the specified name, path, and content.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Name of file to create (with extension)"},
                "filepath": {"type": "string", "description": "Path where file should be created (default: current directory)"},
                "content": {"type": "string", "description": "Content to write to the file"}
            },
            "required": ["filename"]
        }
    }
]

# ----------------------------------------------------------------------
# 3. Build a prompt the way Google’s Gemma docs recommend
#    – “setup” line(s)  ➜  function definitions  ➜  user request
#    The tokenizer’s chat_template turns this list into the right markup.
# ----------------------------------------------------------------------
setup_block = (
    "You have access to functions. If you decide to invoke any function, "
    "reply *only* with a JSON object of the form "
    '{"name": <func>, "parameters": {...}} – no other text.\n'
    "The functions you can call are:\n\n"
    f"{json.dumps(tools, indent=2)}\n\n"
    "Reply in natural language with the result of the function call.\n"
    "You can also answer questions directly, if you prefer.\n\n"
)

messages = [
    {"role": "system", "content": setup_block},
    {"role": "user",   "content": "Create a Python file called hello.py in the tools dir with a simple print statement that says 'Hello, world!'"}
]

prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True)

# ----------------------------------------------------------------------
# 4. Run the model
# ----------------------------------------------------------------------
response = generate(model, tokenizer,
                    prompt=prompt,
                    max_tokens=1024)

print("Raw model output:\n", response, "\n")

# ----------------------------------------------------------------------
# 5. Detect and parse the tool call
# ----------------------------------------------------------------------
match = re.search(r"\{.*\}", response, re.DOTALL)
if match:
    call = json.loads(match.group(0))
    print("Parsed tool call:\n", call)     # {'name': 'get_current_weather', ...}
    # Here you would actually dispatch:
    if call["name"] == "get_current_weather":
        result = get_current_weather(**call["parameters"])
    elif call["name"] == "create_file":
        result = create_file(**call["parameters"])
    else:
        result = {"error": f"Unknown function: {call['name']}"}

    print("Tool call result:\n", result)
else:
    print("No tool call – model chose to answer directly.")