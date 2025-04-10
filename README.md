# Cache Simulator

A Python command-line tool to simulate cache behavior with configurable parameters. Built for **CS 3853 – Team #01**.

---

# Usage

```bash
python3 cache_simulator.py -s 1024 -b 16 -a 2 -r rr -p 1024 -u 20 -n 100 -f trace1.txt trace2.txt
```

### Required Flags

| Flag | Description |
|------|-------------|
| `-s` | Cache size in KB (8–16384) |
| `-b` | Block size in bytes (8–64) |
| `-a` | Associativity (1, 2, 4, 8, 16) |
| `-r` | Replacement policy (`rr`, `rnd`) |
| `-p` | Physical memory in MB (128–4096) |
| `-u` | OS memory usage (%) |
| `-n` | Instructions per slice (or `-1` for max) |
| `-f` | 1–3 trace file names |

---

# Output

Displays input config and calculated metrics:

- Cache blocks, tag/index size
- Overhead and memory cost
- Page table size and RAM usage

---

# Author

** Prince Patel ** – CS 3853, UTSA
