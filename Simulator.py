import math
import random
import re
import argparse

#class models the cache block - validity , tag , usage tracking
class CacheBlock:
    def __init__(self):
        self.valid = False # validity
        self.tag = None #tag
        self.used = False  # Track if this block was ever used
 #simulate cache based on the parameters
def simulate_cache(trace_files=None, trace_lines=None, cache_size_kb=0, block_size=0, associativity=0, replacement_policy="RR"):

    total_cache_size_bytes = cache_size_kb * 1024 #cache size
    num_blocks = total_cache_size_bytes // block_size #total blocks
    num_sets = num_blocks // associativity
    cache = [[CacheBlock() for _ in range(associativity)] for _ in range(num_sets)]
    rr_pointer = [0] * num_sets

#function to acess a cache block for a given address
    def access(address):
        nonlocal compulsory_misses, conflict_misses, cache_hits, cache_misses
        set_index = (address // block_size) % num_sets
        tag = (address // block_size) // num_sets
# check for cache hit
        for block in cache[set_index]:
            if block.valid and block.tag == tag:
                cache_hits += 1
                block.used = True
                return "hit"

        cache_misses += 1

        # check for compulsory miss  - block not valid
        for i, block in enumerate(cache[set_index]):
            if not block.valid:
                block.valid = True
                block.tag = tag
                block.used = True
                compulsory_misses += 1
                return "compulsory"

        conflict_misses += 1

        # conlict miss using RR - Rand replacement policy
        if replacement_policy.upper() == "RR":
            victim = rr_pointer[set_index]
            cache[set_index][victim].tag = tag
            cache[set_index][victim].used = True
            rr_pointer[set_index] = (rr_pointer[set_index] + 1) % associativity
        else:  # Random replacement
            victim = random.randint(0, associativity - 1)
            cache[set_index][victim].tag = tag
            cache[set_index][victim].used = True
        
        return "conflict"

# initalize cointer for cache stats
    cache_hits = cache_misses = compulsory_misses = conflict_misses = 0
    total_accesses = 0
    total_cycles = 0
    instruction_count = 0
    instruction_bytes = 0
    data_bytes = 0
    total_addresses = 0
    # collect all trace lines from provided trace files/liens
    all_trace_lines = []
    
    # Handle both function signatures
    if trace_files:
        # Process multiple trace files
        for trace_file in trace_files:
            try:
                with open(trace_file, "r") as f:
                    all_trace_lines.extend([line.strip() for line in f if line.strip()])
            except FileNotFoundError:
                print(f"Error: Could not open trace file '{trace_file}'")
    elif trace_lines:
        # Already have loaded trace lines
        all_trace_lines = trace_lines
    # Procee the trace lines
    for i in range(0, len(all_trace_lines), 2):
        instr_line = all_trace_lines[i]
        data_line = all_trace_lines[i + 1] if i + 1 < len(all_trace_lines) else ""
# Proceess instruction fetch
        instr_match = re.search(r"EIP \((\d+)\): ([0-9a-fA-F]{8})", instr_line)
        if instr_match:
            instr_len = int(instr_match.group(1))
            instr_addr = int(instr_match.group(2), 16)
            instruction_count += 1
            instruction_bytes += instr_len
            total_addresses += 1
            
            # Process instruction fetch
            for offset in range(instr_len):
                total_accesses += 1
                result = access(instr_addr + offset)
                # CPI calculation for instruction fetch
                if result == "hit":
                    total_cycles += 1
                else:
                    # Cache miss: (4 cycles * number of memory reads to populate cache block)
                    # number of reads == CEILING(block_size / 4)
                    total_cycles += 4 * math.ceil(block_size / 4)
            
            # Add 2 cycles for instruction execution
            total_cycles += 2

        # Process data accesses
        for label in ["dstM", "srcM"]:
            match = re.search(fr"{label}: ([0-9a-fA-F]{{8}}) (\S+)", data_line)
            if match and not match.group(2).startswith("-"):
                addr = int(match.group(1), 16)
                data_bytes += 4  # All data accesses are 4 bytes
                total_addresses += 1
                # loop thouh 4 byte dtaa and acess each in cache
                for offset in range(4):
                    total_accesses += 1
                    result = access(addr + offset)
                    # CPI calculation for data access
                    if result == "hit":
                        total_cycles += 1
                    else:
                        total_cycles += 4 * math.ceil(block_size / 4)
                
                # Add 1 cycle for effective address calculation
                total_cycles += 1

    # Count unused blocks
    unused_blocks = 0
    for set_row in cache:
        for block in set_row:
            if not block.used:
                unused_blocks += 1
# calculate  hit rate,  miss rate, and cpi
    hit_rate = (cache_hits / total_accesses) * 100 if total_accesses else 0
    miss_rate = 100 - hit_rate
    cpi = total_cycles / instruction_count if instruction_count else 0
    
    # Calculate unused cache space
    index_size = int(math.log2(num_sets))
    tag_size = 32 - index_size - int(math.log2(block_size))
    overhead_per_block = (tag_size + 1) / 8  # +1 for valid bit, converted to bytes
    total_overhead = num_blocks * overhead_per_block
    
    implementation_memory_size = total_overhead + (cache_size_kb * 1024)
    implementation_memory_kb = implementation_memory_size / 1024
    
    unused_cache_bytes = unused_blocks * (block_size + overhead_per_block)
    unused_cache_kb = unused_cache_bytes / 1024
    cost = implementation_memory_kb * 0.12
    unused_cost = unused_cache_kb * 0.12
    
    unused_percentage = (unused_cache_kb / implementation_memory_kb) * 100 if implementation_memory_kb else 0

    print("\n***** CACHE SIMULATION RESULTS *****\n")
    print(f"{'Total Cache Accesses:':<30} {total_accesses} ({stats['total_virtual_pages']} addresses)")
    print(f"{'--- Instruction Bytes:':<30} {instruction_bytes}")
    print(f"{'--- SrcDst Bytes:':<30} {data_bytes}")
    print(f"{'Cache Hits:':<30} {cache_hits}")
    print(f"{'Cache Misses:':<30} {cache_misses}")
    print(f"{'--- Compulsory Misses:':<30} {compulsory_misses}")
    print(f"{'--- Conflict Misses:':<30} {conflict_misses}")
    print("\n***** ***** CACHE HIT & MISS RATE: ***** *****\n")
    print(f"{'Hit Rate:':<30} {hit_rate:.8f}%")
    print(f"{'Miss Rate:':<30} {miss_rate:.4f}%")
    print(f"{'CPI:':<30} {cpi:.4f} Cycles/Instruction ({instruction_count})")
    print(f"{'Unused Cache Space:':<30} {unused_cache_kb:.2f} KB / {implementation_memory_kb:.2f} KB = {unused_percentage:.2f}% Waste: ${unused_cost:.2f}/chip")
    print(f"{'Unused Cache Blocks:':<30} {unused_blocks} / {num_blocks}")

# define constant for virtual mem simulation
PAGE_SIZE = 4096  # 4 KB
NUM_VIRTUAL_PAGES = 2 ** 19  # 4GB / 4KB = 524,288
PTE_SIZE_BYTES = 2  # 16 bits (1 valid + 15 for physical page number)
# PageTebleEntry claas models on entry in page table
class PageTableEntry:
    def __init__(self):
        self.valid = False
        self.physical_page = -1
#functionto initialize page tables
def init_page_tables(num_files):
    return [[PageTableEntry() for _ in range(NUM_VIRTUAL_PAGES)] for _ in range(num_files)]
#function to initzlaie physical mem
def init_physical_memory(total_phys_pages, os_percentage):
    used_by_os = int(total_phys_pages * os_percentage / 100)
    free_pages = set(range(used_by_os, total_phys_pages))
    return used_by_os, free_pages

def get_physical_page(v_addr, page_table, free_pages):
    vpn = v_addr >> 12
    entry = page_table[vpn]
    if entry.valid:
        return 'hit', entry.physical_page
    elif free_pages:
        ppn = free_pages.pop()
        entry.valid = True
        entry.physical_page = ppn
        return 'new_map', ppn
    else:
        return 'page_fault', None

def parse_trace_file(filename):
    addresses = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    for i in range(0, len(lines), 2):
        if i + 1 >= len(lines):
            break
        if "EIP" in lines[i]:
            try:
                length = int(lines[i].split("(")[1].split(")")[0])
                addr_str = lines[i].split(":")[1].split()[0]
                addr = int(addr_str, 16)
                for j in range(length):
                    addresses.append(addr + j)
            except:
                continue
        if "dstM:" in lines[i+1] and "srcM:" in lines[i+1]:
            parts = lines[i+1].split()
            try:
                dst_addr = parts[1]
                dst_data = parts[2]
                src_addr = parts[3]
                src_data = parts[4]
                if dst_addr != "00000000" and dst_data != "--------":
                    for j in range(4):
                        addresses.append(int(dst_addr, 16) + j)
                if src_addr != "00000000" and src_data != "--------":
                    for j in range(4):
                        addresses.append(int(src_addr, 16) + j)
            except:
                continue
    return addresses

def simulate_virtual_memory(trace_files, os_percent, total_phys_mem_mb):
    total_phys_pages = total_phys_mem_mb * 1024 * 1024 // PAGE_SIZE
    used_by_os, free_pages = init_physical_memory(total_phys_pages, os_percent)
    page_tables = init_page_tables(len(trace_files))

    stats = {
        "total_virtual_pages": 0,
        "total_byte_addresses": 0,  # <-- Add this line
        "hits": 0,
        "new_maps": 0,
        "page_faults": 0,
        "per_process": [],
        "unique_virtual_pages": set()
    }

    for i, file in enumerate(trace_files):
        addresses = parse_trace_file(file)
        used_entries = set()
        mapped_pages = set()

        for addr in addresses:
            vpn = addr >> 12
            mapped_pages.add(vpn)
            stats["unique_virtual_pages"].add((i, vpn))
            stats["total_byte_addresses"] += 1  # <-- Count each byte-level address
            result, _ = get_physical_page(addr, page_tables[i], free_pages)
            used_entries.add(vpn)
            if result == 'hit':
                stats["hits"] += 1
            elif result == 'new_map':
                stats["new_maps"] += 1
            elif result == 'page_fault':
                stats["page_faults"] += 1

        stats["per_process"].append((len(mapped_pages), (NUM_VIRTUAL_PAGES - len(used_entries)) * PTE_SIZE_BYTES))

    stats["total_virtual_pages"] = stats["hits"] + stats["new_maps"]
    stats["pages_used_by_system"] = used_by_os
    stats["pages_available"] = total_phys_pages - used_by_os
    return stats


def print_vm_results(stats, files):
    print()
    print("***** VIRTUAL MEMORY SIMULATION RESULTS *****\n")
    print(f"Physical Pages Used By SYSTEM:  {stats['pages_used_by_system']}")
    print(f"Pages Available to User:        {stats['pages_available']}\n")
    print(f"Total Unique Virtual Pages Mapped: {stats['total_virtual_pages']}")
    print("        ------------------------------")
    print(f"        Page Table Hits:       {stats['hits']}")
    print(f"        Pages from Free:       {stats['new_maps']}")
    print(f"        Total Page Faults:     {stats['page_faults']}\n")
    
    print("Page Table Usage Per Process:")
    print("------------------------------")
    for i, (used, wasted) in enumerate(stats["per_process"]):
        percent = (used / NUM_VIRTUAL_PAGES) * 100
        print(f"[{i}] {files[i]}:")
        print(f"        Used Page Table Entries: {used}  ({percent:.2f}%)")
        print(f"        Page Table Wasted: {wasted} bytes\n")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Cache Simulator Argument Parser")
    
    parser.add_argument("-s", type=int, choices=[2**x for x in range(3, 15)], required=True,help="Cache size in KB (8 to 16384 KB)")
    
    parser.add_argument("-b", type=int, choices=[8, 16, 32, 64], required=True,help="Block size (8 to 64 bytes)")
    
    parser.add_argument("-a", type=int, choices=[1, 2, 4, 8, 16], required=True,help="Associativity (1, 2, 4, 8, 16)")
    
    parser.add_argument("-r", type=str, choices=["rr", "rnd","RR", "RND"], required=True,help="Replacement policy (rr or rnd)")
    
    parser.add_argument("-p", type=int, choices=[128, 256, 512, 1024, 2048, 4096], required=True,help="Physical memory size in MB (128MB to 4GB)")
    
    parser.add_argument("-u", type=int, choices=range(0, 101), required=True,help="Percentage of physical memory used by OS (0% to 100%)")
    
    parser.add_argument("-n", type=int, default=-1,help="Instructions per time slice (1 to 0xFFFFFFFF, enter -1 for max)")
    
    parser.add_argument("-f", type=str, nargs='+', required=True,help="Trace file names (1 to 3 files allowed)")
    
    args = parser.parse_args()
    
    if len(args.f) > 3:
        parser.error("You can specify a maximum of 3 trace files.")
    return args


if __name__ == "__main__":
    args = parse_arguments()
    cache_size = args.s
    block_size = args.b
    associativity = args.a
    replacement_policy = args.r.upper()
    physical_memory = args.p
    os_memory_usage = args.u
    instructions_per_slice = args.n
    trace_files = args.f

    if replacement_policy.upper() == "RR":
        replacement_policy_display = "Round Robin"
    else:
        replacement_policy_display = "Random"

    print("Cache Simulator - CS 3853 - Team #01")
    print("\nTrace File(s):")
    for i in trace_files:
        print("\t" + i)

    print("\n***** Cache Input Parameters *****\n")
    print(f"{'Cache Size:':<30} {cache_size} KB")
    print(f"{'Block Size:':<30} {block_size} bytes")
    print(f"{'Associativity:':<30} {associativity}")
    print(f"{'Replacement Policy:':<30} {replacement_policy_display}")
    print(f"{'Physical Memory:':<30} {physical_memory} MB")
    print(f"{'Percent Memory Used by System:':<30} {os_memory_usage:.1f}%")
    print(f"{'Instructions / Time Slice:':<30} {instructions_per_slice}")

    # Fixed cache parameter calculations to match milestone1.py
    num_blocks = int(cache_size * 1024 / block_size)
    index_size = int(math.log2(cache_size*1024/(block_size*associativity)))
    tag_size = int(math.log2(physical_memory*(2**20))- math.log2(block_size) - index_size)
    num_rows = int(2**index_size)
    overhead_size = int((tag_size+1)*num_blocks/8)
    implementation_memory_size = int(overhead_size + (cache_size * (2**10)))
    cost = (implementation_memory_size/(2**10)) * 0.12

    print("\n***** Cache Calculated Values *****\n")
    print(f"{'Total # Blocks:':<30}  {num_blocks}")
    print(f"{'Tag Size:':<30}  {tag_size} bits")
    print(f"{'Index Size:':<30}  {index_size} bits")
    print(f"{'Total # Rows:':<30}  {num_rows}")
    print(f"{'Overhead Size:':<30}  {overhead_size} bytes")
    print(f"{'Implementation Memory Size:':<30}  {implementation_memory_size/1024:.2f} KB ({implementation_memory_size} bytes)")
    print(f"{'Cost:':<30}  ${cost:.2f} @ $0.12 per KB")

    # Calculate physical memory parameters
    num_physical_pages = int((physical_memory * (2**20))/(4096))    # considering that the page size is 4K
    num_pages_for_system = int(num_physical_pages * os_memory_usage /100)
    page_table_size = int(math.log2(num_physical_pages) + 1)
    total_ram = int ((cache_size * (2**10)) * (len(trace_files)) * page_table_size / 8 )

    print("\n***** Physical Memory Calculated Values *****\n")
    print(f"{'Number of Physical Pages:':<30}  {num_physical_pages}")
    print(f"{'Number of Pages for system:':<30}  {num_pages_for_system}")
    print(f"{'Size of Page Table Entry:':<30}  {page_table_size} bits")
    print(f"{'Total RAM for Page Table(s):':<30}  {total_ram} bytes")

    stats = simulate_virtual_memory(trace_files, os_memory_usage, physical_memory)
    print_vm_results(stats, trace_files)
        # Simulate cache for all trace files at once
    simulate_cache(
        trace_files=trace_files,
        cache_size_kb=cache_size,
        block_size=block_size,
        associativity=associativity,
        replacement_policy=replacement_policy
    )
