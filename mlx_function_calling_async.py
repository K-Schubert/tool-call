"""
Enhanced Gemma‑3 function‑calling demo
=====================================
Adds the following features to the original `gemma_tool_call.py` example:
  • Decorator‑based auto‑registration of LLM tools.
  • Parameter validation with **pydantic**.
  • Support for both **async** and sync tool functions.
  • **Sandboxed** file creation so paths can’t escape the `tools/` directory.
"""

from __future__ import annotations

import asyncio, inspect, json, re, textwrap
from pathlib import Path
from typing import Callable, Dict, Any

from pydantic import BaseModel, ValidationError, validator

# ----------------------------------------------------------------------
# 0. Load the Gemma‑3 model (unchanged)
# ----------------------------------------------------------------------
from mlx_lm import load, generate  # pip install mlx‑lm – GPU/Apple‑silicon only

MODEL_ID = "mlx-community/gemma-3-text-4b-it-4bit"
model, tokenizer = load(MODEL_ID)

# ----------------------------------------------------------------------
# 1. Tool registry + decorator
# ----------------------------------------------------------------------
_DispatchEntry = Dict[str, Any]
DISPATCHER: Dict[str, _DispatchEntry] = {}


def tool(name: str, params_model: type[BaseModel]):
    """Decorator that auto‑registers `fn` in **DISPATCHER** under *name*."""

    def _register(fn: Callable):
        DISPATCHER[name] = {"func": fn, "model": params_model}
        return fn

    return _register


# ----------------------------------------------------------------------
# 2. Parameter schemas (pydantic) ------------------------------------------------
# ----------------------------------------------------------------------

class WeatherParams(BaseModel):
    location: str
    unit: str | None = "celsius"


class CreateFileParams(BaseModel):
    filename: str  # **no** path separators allowed
    filepath: str = "."  # relative to sandbox root
    content: str

    @validator("filename")
    def _no_separators(cls, v: str):  # pylint: disable=no-self-argument
        if "/" in v or "\\" in v:
            raise ValueError("filename may not contain path separators")
        return v


# ----------------------------------------------------------------------
# 3. Tool implementations -------------------------------------------------------
# ----------------------------------------------------------------------

@tool("get_current_weather", WeatherParams)
async def get_current_weather(location: str, unit: str = "celsius") -> dict[str, Any]:
    """Dummy async weather function (replace with real API call)."""
    await asyncio.sleep(0)  # simulate I/O
    return {
        "location": location,
        "temperature": 20 if unit == "celsius" else 68,
        "unit": unit,
    }


SANDBOX_ROOT = Path("sandbox").resolve()
SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)


def _sandbox_path(filename: str, filepath: str) -> Path:
    """Return an **absolute** path that’s guaranteed to live inside *SANDBOX_ROOT*."""
    candidate = (SANDBOX_ROOT / filepath / filename).resolve()
    if SANDBOX_ROOT not in candidate.parents and candidate != SANDBOX_ROOT:
        raise ValueError("Path escapes sandbox root")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return candidate


@tool("create_file", CreateFileParams)
async def create_file(
    *, filename: str, filepath: str = ".", content: str = ""
) -> dict[str, Any]:
    """Safely create a file inside the sandbox directory."""
    target = _sandbox_path(filename, filepath)
    await asyncio.to_thread(target.write_text, content)
    return {"created": str(target)}


# ----------------------------------------------------------------------
# 4. Build the JSON tool spec handed to the LLM ---------------------------------
# ----------------------------------------------------------------------

def _model_schema(model_cls: type[BaseModel]) -> dict[str, Any]:
    """Return *OpenAI‑style* schema for the pydantic model, v1 or v2."""
    if hasattr(model_cls, "model_json_schema"):
        return model_cls.model_json_schema()
    return model_cls.schema()  # type: ignore[attr-defined]


def build_tools_schema() -> list[dict[str, Any]]:
    """Build the list the LLM sees, directly from the registry."""
    result = []
    for _name, entry in DISPATCHER.items():
        fn = entry["func"]
        result.append(
            {
                "name": _name,
                "description": inspect.getdoc(fn) or "",
                "parameters": _model_schema(entry["model"]),
            }
        )
    return result


tools_json_block = json.dumps(build_tools_schema(), indent=2)

# ----------------------------------------------------------------------
# 5. Prompt helper ---------------------------------------------------------------
# ----------------------------------------------------------------------

def build_prompt(user_message: str) -> str:
    setup = textwrap.dedent(
        f"""
        You have access to functions. If you decide to invoke any function, reply *only* with a JSON object of the form
        {{"name": <func>, "parameters": {{...}}}} — no other text.
        The functions you can call are:

        {tools_json_block}

        Reply in natural language with the result of the function call. You can also answer questions directly, if you prefer.
        """
    ).strip()

    messages = [
        {"role": "system", "content": setup},
        {"role": "user", "content": user_message},
    ]
    return tokenizer.apply_chat_template(messages, add_generation_prompt=True)


# ----------------------------------------------------------------------
# 6. LLM interaction + **async** dispatch ----------------------------------------
# ----------------------------------------------------------------------

async def dispatch_tool_call(call: dict[str, Any]):
    name = call.get("name")
    entry = DISPATCHER.get(name)
    if entry is None:
        raise RuntimeError(f"Unknown function: {name!r}")

    # 1️⃣ Validate parameters via pydantic
    try:
        params_obj = entry["model"](**call.get("parameters", {}))
    except ValidationError as exc:
        raise RuntimeError(f"Parameter validation failed: {exc}") from exc

    # 2️⃣ Call (await if coroutine)
    fn = entry["func"]
    args = params_obj.dict()  # pydantic v1; use .model_dump() for v2
    if inspect.iscoroutinefunction(fn):
        return await fn(**args)
    return fn(**args)  # sync fallback


async def handle_request(user_message: str):
    prompt = build_prompt(user_message)
    raw = generate(model, tokenizer, prompt=prompt, max_tokens=1024)
    print("Raw model output:\n", raw, "\n")

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        print("No tool call — model answered directly.")
        return

    call = json.loads(match.group(0))
    try:
        result = await dispatch_tool_call(call)
    except Exception as exc:  # noqa:  BLE001, broad except (demo)
        print(exc)
        return

    print("Tool call result:\n", result)


# ----------------------------------------------------------------------
# 7. Quick CLI test --------------------------------------------------------------
# ----------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(
        handle_request(
            "Create a Python file called test.py in the sandbox dir "
            "with a simple print statement that says 'Hello, world!!!!!'"
        )
    )
