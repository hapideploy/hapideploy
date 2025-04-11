import re
import shlex


def env_stringify(env: dict) -> str:
    items = []
    for name, value in env.items():
        items.append(f"%s=%s" % (name, shlex.quote(str(value))))
    return " ".join(items)


def extract_curly_brackets(text: str) -> list[str]:
    pattern = r"\{\{([^}]*)\}\}"
    matches = re.findall(pattern, text)
    return matches
