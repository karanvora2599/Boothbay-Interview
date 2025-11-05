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

def parse_line(line: str):
    # Expect "Name,Left,Right"
    parts = [p.strip() for p in line.strip().split(",")]
    if len(parts) != 3:
        raise ValueError(f"Bad line (need 3 fields): {line}")
    return parts[0], parts[1], parts[2]

# Read input
scales = {}                
referenced = set()          
order_seen = []             
for raw in sys.stdin:
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    name, L, R = parse_line(line)
    scales[name] = (L, R)
    order_seen.append(name)
    if not is_mass(L):
        referenced.add(L)
    if not is_mass(R):
        referenced.add(R)

if not scales:
    sys.exit(0)

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