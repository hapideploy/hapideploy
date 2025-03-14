import re


def extract_curly_braces(text):
    pattern = r"\{\{([^}]*)\}\}"
    matches = re.findall(pattern, text)
    return matches
