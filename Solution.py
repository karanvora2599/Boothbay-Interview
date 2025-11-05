#!/usr/bin/env python3
import sys
import re
from collections import defaultdict

# Parse helpers
is_int = re.compile(r"^[+-]?\d+$").match
def is_mass(tok: str) -> bool:
    return is_int(tok.strip())

def parse_mass(tok: str) -> int:
    return int(tok.strip())

def is_scale_name(tok: str) -> bool:
    tok = tok.strip()
    return len(tok) > 0 and tok[0].isalpha()

def parse_line(line: str):
    # Expect "Name,Left,Right"
    parts = [p.strip() for p in line.strip().split(",")]
    if len(parts) != 3:
        raise ValueError(f"Bad line (need 3 fields): {line}")
    # Validate scale name starts with a letter
    if not is_scale_name(parts[0]):
        raise ValueError(f"Invalid scale name {parts[0]!r}: must start with [A-Za-z]")
    # Validate tokens are either integer masses or scale names
    for tok in (parts[1], parts[2]):
        if not (is_mass(tok) or is_scale_name(tok)):
            raise ValueError(
                f"Invalid token {tok!r}: must be integer mass or start with [A-Za-z] for a scale name"
            )
    return parts[0], parts[1], parts[2]

_source = None
if len(sys.argv) > 1 and sys.argv[1] != "-":
    _source = open(sys.argv[1], "r", encoding="utf-8")
else:
    _source = sys.stdin

# Read input
scales = {}                 
referenced = set()          
order_seen = []       
for raw in _source:
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    name, L, R = parse_line(line)
    if name in scales:
        raise ValueError(f"Duplicate scale name {name!r}")
    scales[name] = (L, R)
    order_seen.append(name)
    if (not is_mass(L)) and is_scale_name(L):
        referenced.add(L)
    if (not is_mass(R)) and is_scale_name(R):
        referenced.add(R)

# Close file handle if we opened one
if _source is not sys.stdin:
    _source.close()

if not scales:
    sys.exit(0)

# Verify that all referenced child scales exist
_unknown = [c for c in referenced if c not in scales]
if _unknown:
    raise ValueError(f"Unknown referenced scale(s): {', '.join(sorted(_unknown))}")

# Find root (a scale never referenced by others)
roots = [n for n in scales.keys() if n not in referenced]
if len(roots) != 1:
    roots = sorted(roots)
root = roots[0]

additions = {}
memo_weight = {}

def total_weight_of_token(tok: str) -> int:
    if is_mass(tok):
        return parse_mass(tok)
    return weight_of_scale(tok)

def weight_of_scale(name: str) -> int:
    if name in memo_weight:
        return memo_weight[name]

    Ltok, Rtok = scales[name]
    Lw = total_weight_of_token(Ltok)
    Rw = total_weight_of_token(Rtok)

    if Lw < Rw:
        addL, addR = (Rw - Lw), 0
    elif Rw < Lw:
        addL, addR = 0, (Lw - Rw)
    else:
        addL, addR = 0, 0

    additions[name] = (addL, addR)

    # Total weight passed upward includes the 1kg scale body
    total = 1 + (Lw + addL) + (Rw + addR)
    memo_weight[name] = total
    return total

# Kick off recursion from the root to ensure every reachable scale is processed
weight_of_scale(root)

# Some scales might be isolated in unusual inputs; ensure all get computed
for name in scales:
    if name not in memo_weight:
        weight_of_scale(name)

# Output in alphanumeric (lexicographic) order of scale names
for name in sorted(scales.keys()):
    Ladd, Radd = additions.get(name, (0, 0))
    print(f"{name},{Ladd},{Radd}")