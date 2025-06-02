# Cache and Virtual Memory Simulator

This project simulates a **cache memory** and **virtual memory system** based on instruction and data access trace files. The simulator models cache behavior (hits, misses, replacement policies) and virtual memory management (page mapping, page faults) to analyze performance metrics such as **CPI**, **hit/miss rates**, and **memory usage**.

---

## 📁 Features

### ✅ Cache Simulation:
- Configurable cache size, block size, and associativity
- Supports **Round-Robin (RR)** and **Random Replacement** policies
- Tracks:
  - Cache hits & misses
  - Compulsory and conflict misses
  - Cycles Per Instruction (CPI)
  - Cache utilization and cost analysis

### ✅ Virtual Memory Simulation:
- Simulates a basic page table with:
  - Physical page allocation
  - Page hits, new mappings, and page faults
- Supports multiple processes (via multiple trace files)
- Tracks:
  - Virtual-to-physical page mapping
  - Free/used physical pages
  - Per-process page table memory usage

---

## 📦 Requirements

- Python 3.x
- Works on macOS, Linux, and Windows

No external libraries are required beyond Python's standard library.

---

## 🚀 Usage

### 1. Run Cache Simulation:

```bash
python3 simulator.py --cache --cache-size 32 --block-size 16 --associativity 2 --policy RR --traces trace1.txt trace2.txt
