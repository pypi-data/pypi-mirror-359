import json
from .valuetypes import parse_value
from .utils import read_memory_regions, scan_memory, read_memory_value

class MemoryScanner:
    def __init__(self, pid):
        self.pid = pid
        self.results = []

    def first_scan(self, type_, value):
        val_bytes = parse_value(type_, value)
        regions = read_memory_regions(self.pid)
        self.results = scan_memory(self.pid, regions, val_bytes)
        print(f"[+] Found {len(self.results)} results.")

    def refine_scan(self, type_, value):
        new_val = parse_value(type_, value)
        refined = []
        for addr, _ in self.results:
            try:
                mem_val = read_memory_value(self.pid, addr, len(new_val))
                if mem_val == new_val:
                    refined.append((addr, mem_val))
            except OSError as e:
                continue
        self.results = refined
        print(f"[+] Results after refining: {len(self.results)}")

    def save_results(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.results, f)
        print(f"[+] Saved to {filename}")

    def load_results(self, filename):
        with open(filename, 'r') as f:
            self.results = json.load(f)
        print(f"[+] Loaded from {filename}")

