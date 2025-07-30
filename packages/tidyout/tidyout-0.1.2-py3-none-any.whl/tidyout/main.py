import ast
import json
import re
from rich import print_json
from typing import Any, Dict, Optional


def extract_key_value_blocks(raw_text: str) -> Dict[str, Any]:
    """Extract top-level key=value or key: value pairs even across lines."""
    pattern = pattern = re.compile(r'(\w+)\s*=\s*((?:.|\n)*?)(?=\s+\w+\s*=|\s*$)', re.MULTILINE)
    result = {}
    for key, val in pattern.findall(raw_text):
        val = val.strip()
        try:
            parsed = ast.literal_eval(val)
            if isinstance(parsed, str):
                parsed = parsed.encode().decode("unicode_escape")
            result[key] = parsed
        except Exception:
            result[key] = val
    return result


def parse_colon_separated_content(content: str) -> Dict[str, str]:
    """Parse 'key: value' lines into a dictionary."""
    result = {}
    for line in content.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            result[k.strip()] = v.strip()
    return result


def tidyout(
    raw_text: str,
    *,
    split_content: bool = False,
    rich: bool = True,
    return_dict: bool = False
) -> Optional[Dict[str, Any]]:
    """Parse and optionally pretty-print LLM output."""
    data = extract_key_value_blocks(raw_text)

    if split_content and isinstance(data.get("content"), str):
        data["content"] = parse_colon_separated_content(data["content"])

    if return_dict:
        return data

    try:
        if rich:
            from rich import print_json
            print_json(data)
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print(json.dumps(data, indent=2, ensure_ascii=False))

    return None
