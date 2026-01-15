#!/usr/bin/env python3
from pathlib import Path
import urllib.request

UPSTREAM = "https://raw.githubusercontent.com/ImMALWARE/dns.malw.link/refs/heads/master/hosts"
MARKER = "# Блокировка"

EXCLUDE_FILE = "exclude.txt"
EXTRA_FILE = "extra_hosts.txt"
OUT_FILE = "hosts"


def load_set(path: str) -> set[str]:
    p = Path(path)
    if not p.exists():
        return set()
    return {
        line.strip().lower()
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def excluded(domain: str, ex: set[str]) -> bool:
    d = domain.lower()
    return d in ex or any(d.endswith("." + x) for x in ex)


def read_extra() -> str:
    p = Path(EXTRA_FILE)
    if not p.exists():
        return ""
    lines = []
    for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s + "\n")
    return "".join(lines)


def main():
    ex = load_set(EXCLUDE_FILE)

    text = urllib.request.urlopen(UPSTREAM, timeout=30).read().decode("utf-8", errors="ignore")

    out = []
    for raw in text.splitlines(True):  # keep \n
        line = raw.replace("\ufeff", "")

        if line.strip() == MARKER:
            break

        low = line.strip().lower()

        # убрать заголовки/комментарии про TikTok
        if line.lstrip().startswith("#") and "tiktok" in low:
            continue

        parts = low.split()
        if len(parts) >= 2 and not parts[0].startswith("#"):
            domain = parts[1]
            if excluded(domain, ex):
                continue

        out.append(line)

    extra = read_extra()
    if extra:
        if out and not out[-1].endswith("\n"):
            out.append("\n")
        out.append("\n# Extra (manual)\n")
        out.append(extra)

    Path(OUT_FILE).write_text("".join(out), encoding="utf-8", newline="")


if __name__ == "__main__":
    main()
