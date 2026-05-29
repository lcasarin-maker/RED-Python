"""Bulk rename script for legacy CoderCerberus references and version updates."""
import pathlib
import re
root = pathlib.Path(r'd:\GoogleDrive\AI\Cerberus')
patterns = [
    (re.compile(r'(?i)CoderCerberus'), 'CoderCerberus'),
    (re.compile(r'(?i)\.CoderCerberus'), '.protocol/metadata'),
    (re.compile(r'(?i)\bv5\.7\b'), 'v0.02'),
    (re.compile(r'(?i)\bv5\.0\b'), 'v0.02'),
    (re.compile(r'(?i)\b5\.0\b'), 'v0.02'),
]

for path in root.rglob('*'):
    if path.is_file() and path.suffix.lower() in {'.md', '.txt', '.py', '.yml', '.json'}:
        content = path.read_text(encoding='utf-8')
        new_content = content
        for pat, repl in patterns:
            new_content = pat.sub(repl, new_content)
        if new_content != content:
            path.write_text(new_content, encoding='utf-8')
            print('Updated {}'.format(path))
