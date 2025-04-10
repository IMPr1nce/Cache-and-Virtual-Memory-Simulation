import argparse
import math

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
    #assigning the variable names for the flags 
    cache_size = args.s
    block_size = args.b
    associativity = args.a
    replacement_policy = args.r
    physical_memory = args.p
    os_memory_usage = args.u
    instructions_per_slice = args.n
    trace_files = args.f

    if (replacement_policy == "rr" or replacement_policy == "RR"):
        replacement_policy = "Round Robin"
    else:
        replacement_policy = "Random"


    print("Cache Simulator - CS 3853 - Team #01")
    print()
    print("Trace File(s):")
    for i in trace_files:
        print("\t"+i)

# cache Input parameters 
    print()
    print("***** Cache Input Parameters *****")
    print()
    print(f"{'Cache Size:':<30} ",cache_size,"KB")
    print(f"{'Block Size:':<30} ",block_size,"bytes")
    print(f"{'Associativity:':<30} ",associativity)
    print(f"{'Replacement Policy:':<30} ",replacement_policy )
    print(f"{'Physical Memory:':<30} ", physical_memory,"MB")
    print(f"{'Percent Memory Used by System:':<30}  {os_memory_usage:.1f}%")
    print(f"{'Instructions / Time Slice:':<30} ",instructions_per_slice)
        
#Cache Calculated values 

    # all of the calculations 
    num_blocks = int(cache_size * 1024 / block_size)
    index_size = int(math.log2(cache_size*1024/(block_size*associativity)))
    tag_size = int(math.log2(physical_memory*(2**20))- math.log2(block_size) - index_size)
    num_rows = int(2**index_size)
    overhead_size = int((tag_size+1)*num_blocks/8)
    implementation_memory_size = int(overhead_size + (cache_size * (2**10)))
    cost = (implementation_memory_size/(2**10)) * 0.12

    print()
    print("***** Cache Calculated Values *****")
    print()
    print(f"{'Total # Blocks:':<30}  {num_blocks}")
    print(f"{'Tag Size:':<30}  {tag_size} bits")
    print(f"{'Index Size:':<30}  {index_size} bits")
    print(f"{'Total # Rows':<30}  {num_rows}")
    print(f"{'Overhead Size':<30}  {overhead_size} bytes")
    print(f"{'Implementation Memory Size:':<31} {implementation_memory_size/1024:.2f} KB ({implementation_memory_size} bytes)")
    print(f"{'Cost:':<30}  {cost:.2f} @ $0.12 per KB")

# physical memory calculations

    num_physical_pages = int((physical_memory * (2**20))/(4096))    # considering that the page size is 4K
    num_pages_for_system = int(num_physical_pages * os_memory_usage /100)
    page_table_size = int(math.log2(num_physical_pages) + 1)
    total_ram = int ((cache_size * (2**10)) * (len(trace_files)) * page_table_size / 8 )

    print()
    print("***** Physical Memory Calculated Values *****")
    print()
    print(f"{'Number of Physical Pages:':<30}  {num_physical_pages}")
    print(f"{'Number of Pages for system:':<30}  {num_pages_for_system}")
    print(f"{'Size of Page Table Entry:':<30}  {page_table_size} bits")
    print(f"{'Total RAM for Page Table(s):':<30}  {total_ram} bytes")