#!/usr/bin/env python3
import urllib.request
import re
from pathlib import Path

UPSTREAM = "https://raw.githubusercontent.com/ImMALWARE/dns.malw.link/refs/heads/master/hosts"
MARKER = "# Блокировка"

EXCLUDE_FILE = Path("exclude.txt")

# Линии формата: "IP domain"
LINE_RE = re.compile(r"^\s*([0-9a-fA-F:.]+)\s+([a-zA-Z0-9.-]+)\s*(?:#.*)?$")

def load_exclude() -> set[str]:
    if not EXCLUDE_FILE.exists():
        return set()
    out = set()
    for line in EXCLUDE_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip().lower()
        if not line or line.startswith("#"):
            continue
        out.add(line)
    return out

def is_excluded(domain: str, exclude: set[str]) -> bool:
    domain = domain.lower()
    return (domain in exclude) or any(domain.endswith("." + x) for x in exclude)

def main():
    exclude = load_exclude()

    with urllib.request.urlopen(UPSTREAM, timeout=30) as r:
        text = r.read().decode("utf-8", errors="ignore")

    out_lines = []
    marker_found = False

    for raw_line in text.splitlines(True):  # True = keep \n
        if raw_line.strip() == MARKER:
            marker_found = True
            break

        m = LINE_RE.match(raw_line)
        if not m:
            # сохраняем комментарии/пустые строки до маркера как есть
            out_lines.append(raw_line)
            continue

        ip, domain = m.group(1), m.group(2).lower()

        # выкидываем исключённые домены (и их поддомены)
        if is_excluded(domain, exclude):
            continue

        out_lines.append(f"{ip} {domain}\n")

    if not marker_found:
        raise SystemExit("ERROR: marker '# Блокировка' not found")

    Path("hosts").write_text("".join(out_lines), encoding="utf-8", newline="")

if __name__ == "__main__":
    main()
