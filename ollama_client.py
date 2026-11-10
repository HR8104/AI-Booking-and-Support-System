import json
import inspect
import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any, Callable, Optional

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
REQUEST_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "180"))
MAX_TOOL_ROUNDS = 5
# Ollama's default context (2-4k tokens) is too small for the system prompt + tools + menu,
# which makes the model "forget" earlier parts of the conversation.
MODEL_OPTIONS = {
    "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "8192")),
    "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.2")),
}


def _function_schema(fn: Callable) -> Dict[str, Any]:
    """
    Convert a Python callable to an OpenAI/Ollama-style function schema.
    """
    sig = inspect.signature(fn)
    props = {}
    required = []

    for name, param in sig.parameters.items():
        param_type = "string"
        if param.annotation == int:
            param_type = "integer"
        elif param.annotation == float:
            param_type = "number"
        elif param.annotation == bool:
            param_type = "boolean"

        props[name] = {"type": param_type}
        if param.default is param.empty:
            required.append(name)

    schema = {
        "type": "function",
        "function": {
            "name": fn.__name__,
            "description": (fn.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": props,
                "required": required,
            },
        },
    }
    return schema


def chat_completion(
    system_prompt: Optional[str] = None,
    user_message: Optional[str] = None,
    tools: Optional[List[Callable]] = None,
    messages: Optional[List[Dict[str, Any]]] = None,
    tool_log: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Sends a chat request to Ollama, automatically handling tool calls.
    Returns the final textual response produced by the model.
    """
    if tools is None:
        tools = []

    if messages is None:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if user_message:
            messages.append({"role": "user", "content": user_message})

    # Prepare tool definitions for Ollama (function calling)
    tool_defs = [_function_schema(fn) for fn in tools] if tools else None

    for _ in range(MAX_TOOL_ROUNDS + 1):
        payload: Dict[str, Any] = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False,
            "options": MODEL_OPTIONS,
        }
        if tool_defs:
            payload["tools"] = tool_defs

        resp = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        message = data.get("message", {})
        content = message.get("content", "").strip()
        tool_calls = message.get("tool_calls", [])

        # If there are tool calls, invoke them locally and feed the results back
        if tool_calls:
            # Append the assistant message that requested tool calls
            messages.append(message)

            for call in tool_calls:
                fn_name = call.get("function", {}).get("name")
                args_data = call.get("function", {}).get("arguments", {})

                if isinstance(args_data, dict):
                    args = args_data
                elif isinstance(args_data, str):
                    try:
                        args = json.loads(args_data)
                    except (json.JSONDecodeError, TypeError):
                        args = {"value": args_data}
                else:
                    args = {}

                # Find the matching Python function
                fn = next((f for f in tools if f.__name__ == fn_name), None)
                if not fn:
                    result = f"Error: function '{fn_name}' not found."
                else:
                    try:
                        # Convert arguments if necessary to match signatures
                        sig = inspect.signature(fn)
                        filtered_args = {}
                        for k, v in args.items():
                            if k in sig.parameters:
                                param = sig.parameters[k]
                                if param.annotation == int and isinstance(v, (str, float)):
                                    try:
                                        v = int(float(v))
                                    except ValueError:
                                        pass
                                filtered_args[k] = v
                        result = fn(**filtered_args)
                    except Exception as exc:
                        result = f"Error while executing '{fn_name}': {exc}"

                if tool_log is not None:
                    tool_log.append({"name": fn_name, "args": args, "result": str(result)})

                # Append tool response
                messages.append(
                    {
                        "role": "tool",
                        "tool_name": fn_name,
                        "content": str(result),
                    }
                )

            # Loop again so model can see tool responses and continue
            continue

        # No tool calls -> we have the final answer
        return content

    return ("Mi dispiace, I couldn't complete that request. "
            "Please try again or call the restaurant directly.")
