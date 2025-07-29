import os

def list_processes():
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f"/proc/{pid}/cmdline", 'rb') as f:
                    cmdline = f.read().decode().split('\0')[0]
                    print(f"{pid}\t{cmdline}")
            except:
                continue

def read_memory_regions(pid):
    maps = f"/proc/{pid}/maps"
    regions = []
    try:
        with open(maps, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.split()
                if len(parts) < 5 or 'r' not in parts[1]:
                    continue
                addr = parts[0]
                start, end = [int(x, 16) for x in addr.split('-')]
                regions.append((start, end))
    except Exception as e:
        print(f"[-] Failed to read maps: {e}")
    return regions

def scan_memory(pid, regions, value):
    matches = []
    with open(f"/proc/{pid}/mem", 'rb', 0) as mem:
        for start, end in regions:
            try:
                mem.seek(start)
                chunk = mem.read(end - start)
                offset = chunk.find(value)
                while offset != -1:
                    matches.append((start + offset, value))
                    offset = chunk.find(value, offset + 1)
            except:
                continue
    return matches

def write_memory(pid, address, value):
    with open(f"/proc/{pid}/mem", 'rb+', 0) as mem:
        mem.seek(address)
        mem.write(value)

def read_memory_value(pid, address, size):
    with open(f"/proc/{pid}/mem", 'rb', 0) as mem:
        mem.seek(address)
        return mem.read(size)

