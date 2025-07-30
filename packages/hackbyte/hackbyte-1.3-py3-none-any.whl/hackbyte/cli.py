import cmd, getpass, os
from .scanner import MemoryScanner
from .memeditor import MemoryEditor
from .dummyproc import DummyProcess
from .utils import list_processes, find_pid_by_name
from .version import __version__

class HackByteShell(cmd.Cmd):
	
	logo = f"""
    __  __           __   ____        __     
   / / / /___ ______/ /__/ __ )__  __/ /____ 
  / /_/ / __ `/ ___/ //_/ __  / / / / __/ _ \\
 / __  / /_/ / /__/ ,< / /_/ / /_/ / /_/  __/
/_/ /_/\\__,_/\\___/_/|_/_____/\\__, /\\__/\\___/ 
      Maintained By Dx4Grey /____/ v{__version__}\n"""
	intro = f"{logo}\nWelcome Hacker!! Type \"help\" or \"?\" for help."
	prompt = f"{getpass.getuser()}@hackbyte> "

	def __init__(self):
		super().__init__()
		self.proc = None
		self.scanner = None
		self.editor = None

	def do_ls(self, arg):
		"List of active processes: ls"
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
		"""Edit scanned memory value by index or * (edit all). Usage: edit <index|*> <new_value>"""
		args = arg.strip().split()
		if len(args) < 2:
			print("Usage: edit <index|*> <new_value>")
			return
		if not self.scanner.results:
			print("[-] No scan results found. Please scan first.")
			return
	
		index_or_all, new_val = args[0], args[1]
		if index_or_all == '*':
			for i, (addr, _) in enumerate(self.scanner.results):
				self.mem_editor.write_value(self.pid, addr, new_val, self.scanner.last_type)
				print(f"[+] Edited result {i} at {hex(addr)} → {new_val}")
		else:
			try:
				index = int(index_or_all)
				if index >= len(self.scanner.results) or index < 0:
					print(f"[-] Invalid index. Found {len(self.scanner.results)} result(s).")
					return
				address, _ = self.scanner.results[index]
				self.mem_editor.write_value(self.pid, address, new_val, self.scanner.last_type)
				print(f"[+] Edited address {hex(address)} → {new_val}")
			except ValueError:
				print("[-] Invalid index.")

	def do_freeze(self, arg):
		"""Freeze memory value by index or * (freeze all). Usage: freeze <index|*>"""
		args = arg.strip().split()
		if len(args) < 1:
			print("Usage: freeze <index|*>")
			return
		if not self.scanner.results:
			print("[-] No scan results found. Please scan first.")
			return
	
		index_or_all = args[0]
		if index_or_all == '*':
			for i, (addr, _) in enumerate(self.scanner.results):
				self.mem_editor.freeze_value(self.pid, addr, self.scanner.last_type)
				print(f"[+] Freezing result {i} at {hex(addr)}")
		else:
			try:
				index = int(index_or_all)
				if index >= len(self.scanner.results) or index < 0:
					print(f"[-] Invalid index. Found {len(self.scanner.results)} result(s).")
					return
				address, _ = self.scanner.results[index]
				self.mem_editor.freeze_value(self.pid, address, self.scanner.last_type)
				print(f"[+] Freezing address {hex(address)}")
			except ValueError:
				print("[-] Invalid index.")
			
	def do_script(self, path):
		"""Execute a HackByte script file (supports HackByte & bash commands)."""
		if not os.path.isfile(path):
			print(f"[-] Script file not found: {path}")
			return
		with open(path) as f:
			for line in f:
				line = line.strip()
				if not line or line.startswith("#"):
					continue
				if line.startswith("!"):  # Bash command
					os.system(line[1:])
				else:  # HackByte command
					print(f"{self.prompt}{line}")
					self.onecmd(line)
				
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