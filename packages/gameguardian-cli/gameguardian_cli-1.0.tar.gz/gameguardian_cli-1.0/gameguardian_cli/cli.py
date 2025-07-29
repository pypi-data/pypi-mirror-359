import cmd, getpass, os
from .scanner import MemoryScanner
from .memeditor import MemoryEditor
from .dummyproc import DummyProcess
from .utils import list_processes, find_pid_by_name
from .version import __version__
class GameGuardianShell(cmd.Cmd):
    
    logo = f"""  ________  ________ 
 /  _____/ /  _____/ 
/   \\  ___/   \\  ___ \tMaintained by Dx4Grey
\\    \\_\\  \\    \\_\\  \\\tGG Cli Version v{__version__}
 \\______  /\\______  /\tLinux/Android memory mod tool.
        \\/        \\/ """
    intro = f"{logo}\nWelcome to GameGuardian CLI! Type help or ? for help."
    prompt = f"{getpass.getuser()}@gg-cli> "

    def __init__(self):
        super().__init__()
        self.proc = None
        self.scanner = None
        self.editor = None

    def do_list(self, arg):
        "List of active processes: list"
        list_processes()

    def do_attach(self, pid_or_name):
        "Attach to a process by PID or name: attach <pid|name>"
        try:
            if pid_or_name.isdigit():
                pid = int(pid_or_name)
            else:
                pid = find_pid_by_name(pid_or_name)
                if pid is None:
                    print("[-] Process not found.")
                    return
            self.proc = pid
            self.scanner = MemoryScanner(pid)
            self.editor = MemoryEditor(pid)
            print(f"[+] Attached to PID {pid}")
        except:
            print("[-] Failed to attach. Invalid PID or name?")

    def do_kill(self, pid_or_name):
        "Kill a process by PID or name: kill <pid|name>"
        try:
            pid = int(pid_or_name) if pid_or_name.isdigit() else find_pid_by_name(pid_or_name)
            if pid is None:
                print("[-] Process not found.")
                return
            os.kill(pid, 9)
            print(f"[+] Killed process {pid}")
        except Exception as e:
            print(f"[-] Failed to kill process: {e}")

    def do_scan(self, arg):
        "Scan value: scan <type> <value>"
        if not self.scanner:
            print("[-] Not attached to any process yet.")
            return
        args = arg.split()
        if len(args) < 2:
            print("Usage: scan <type> <value>")
            return
        type_, value = args[0], ' '.join(args[1:])
        self.scanner.first_scan(type_, value)

    def do_refine(self, arg):
        "Refine scan results: refine <type> <value>"
        if not self.scanner or not self.scanner.results:
            print("[-] No results to refine.")
            return
        args = arg.split()
        if len(args) < 2:
            print("Usage: refine <type> <value>")
            return
        type_, value = args[0], ' '.join(args[1:])
        self.scanner.refine_scan(type_, value)

    def do_results(self, arg):
        "Show last scan results: results"
        if not self.scanner:
            print("[-] No scan results yet.")
            return
        for i, (addr, val) in enumerate(self.scanner.results):
            print(f"[{i}] {hex(addr)} => {val}")

    def do_edit(self, arg):
        "Edit scan result values: edit <index|*> <value>"
        if not self.editor or not self.scanner:
            print("[-] Not yet attached to the process.")
            return
        args = arg.split()
        if len(args) != 2:
            print("Usage: edit <index|*> <value>")
            return
        target, value = args
        if target == '*':
            for address, _ in self.scanner.results:
                self.editor.edit_direct(address, value)
            print(f"[+] All results are set to {value}")
        else:
            try:
                index = int(target)
                address, _ = self.scanner.results[index]
                self.editor.edit_direct(address, value)
            except ValueError:
                print("[-] Invalid index.")

    def do_freeze(self, arg):
        "Freeze values to keep them constant: freeze <index> <value>"
        if not self.editor or not self.scanner:
            print("[-] Not attached to the process yet.")
            return
        args = arg.split()
        if len(args) != 2:
            print("Usage: freeze <index> <value>")
            return
        try:
            index = int(args[0])
            address, _ = self.scanner.results[index]
            self.editor.freeze_direct(address, args[1])
        except ValueError:
            print("[-] Invalid index.")

    def do_save(self, arg):
        "Save scan results: save <filename>"
        self.scanner.save_results(arg)

    def do_load(self, arg):
        "Load scan results from file: load <filename>"
        self.scanner.load_results(arg)

    def do_dummy(self, arg):
        "Use dummy mode for testing without root"
        self.proc = DummyProcess()
        self.scanner = MemoryScanner(self.proc)
        self.editor = MemoryEditor(self.proc)
        print("[+] Dummy process is active for simulation.")
        
    def do_clear(self, arg):
        "Clean all terminal outputs"
        print("\033c", end="")

    def do_exit(self, arg):
        "Exit the program"
        return True