#!/usr/bin/env python3
import urllib.request
import re
from pathlib import Path

UPSTREAM = "https://raw.githubusercontent.com/ImMALWARE/dns.malw.link/refs/heads/master/hosts"
MARKER = "# Блокировка"

# Домены, которые нужно полностью убрать (и их поддомены)
EXCLUDE_FILE = Path("exclude.txt")

# Линии формата: "IP domain" (IPv4/IPv6) + опциональный комментарий
LINE_RE = re.compile(r"^\s*([0-9a-fA-F:.]+)\s+([a-zA-Z0-9.-]+)\s*(?:#.*)?$")


def load_exclude() -> set[str]:
    if not EXCLUDE_FILE.exists():
        return set()
    out: set[str] = set()
    for line in EXCLUDE_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip().lower()
        if not line or line.startswith("#"):
            continue
        out.add(line)
    return out


def is_excluded(domain: str, exclude: set[str]) -> bool:
    d = domain.lower()
    return (d in exclude) or any(d.endswith("." + x) for x in exclude)


def main():
    exclude = load_exclude()

    with urllib.request.urlopen(UPSTREAM, timeout=30) as r:
        text = r.read().decode("utf-8", errors="ignore")

    out_lines: list[str] = []
    marker_found = False

    for raw_line in text.splitlines(True):  # True = keep \n
        # Обрезаем всё после маркера блокировки
        if raw_line.strip() == MARKER:
            marker_found = True
            break

        low = raw_line.strip().lower()

        # Убираем комментарии/заголовки про TikTok (например "# TikTok")
        if raw_line.lstrip().startswith("#") and "tiktok" in low:
            continue

        m = LINE_RE.match(raw_line)
        if not m:
            # Оставляем прочие комментарии/пустые строки/непонятные строки до маркера
            out_lines.append(raw_line)
            continue

        ip, domain = m.group(1), m.group(2).lower()

        # Убираем домены из exclude.txt (и их поддомены)
        if is_excluded(domain, exclude):
            continue

        out_lines.append(f"{ip} {domain}\n")

    if not marker_found:
        raise SystemExit("ERROR: marker '# Блокировка' not found")

    Path("hosts").write_text("".join(out_lines), encoding="utf-8", newline="")


if __name__ == "__main__":
    main()
