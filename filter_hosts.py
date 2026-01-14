#!/usr/bin/env python3
import urllib.request

UPSTREAM = "https://raw.githubusercontent.com/ImMALWARE/dns.malw.link/refs/heads/master/hosts"
MARKER = "# Блокировка"

def main():
    with urllib.request.urlopen(UPSTREAM, timeout=30) as r:
        text = r.read().decode("utf-8", errors="ignore")

    lines = text.splitlines(True)  # сохраняем \n
    out = []
    marker_found = False

    for line in lines:
        if line.strip() == MARKER:
            marker_found = True
            break
        out.append(line)

    # если маркер внезапно пропал — лучше НЕ публиковать полный файл молча
    if not marker_found:
        raise SystemExit("ERROR: marker '# Блокировка' not found")

    with open("hosts", "w", encoding="utf-8", newline="") as f:
        f.writelines(out)

if __name__ == "__main__":
    main()
