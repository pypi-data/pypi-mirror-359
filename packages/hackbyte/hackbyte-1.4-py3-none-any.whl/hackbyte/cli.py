import cmd, getpass, os
from .scanner import MemoryScanner
from .memeditor import MemoryEditor
from .dummyproc import DummyProcess
from .utils import list_processes, find_pid_by_name
from hackbyte.info import get_process_info
from .version import __version__

class HackByteShell(cmd.Cmd):
	
	logo = f"""
    __  __           __   ____        __	 
   / / / /___ ______/ /__/ __ )__  __/ /____ 
  / /_/ / __ `/ ___/ //_/ /_/ / / / / __/ _ \\
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
		try:
			list_processes()
		except Exception as e:
			print(f"[-] Failed to list processes: {e}")

	def do_attach(self, pid_or_name):
		"Attach to a process by PID or name: attach <pid|name>"
		try:
			if not pid_or_name:
				print("Usage: attach <pid|name>")
				return
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
		except Exception as e:
			print(f"[-] Failed to attach: {e}")

	def do_kill(self, pid_or_name):
		"Kill a process by PID or name: kill <pid|name>"
		try:
			if not pid_or_name:
				print("Usage: kill <pid|name>")
				return
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
		try:
			self.scanner.first_scan(type_, value)
		except Exception as e:
			print(f"[-] Scan failed: {e}")

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
		try:
			self.scanner.refine_scan(type_, value)
		except Exception as e:
			print(f"[-] Refine failed: {e}")

	def do_results(self, arg):
		"Show last scan results: results"
		if not self.scanner or not self.scanner.results:
			print("[-] No scan results yet.")
			return
		try:
			for i, (addr, val) in enumerate(self.scanner.results):
				print(f"[{i}] {hex(addr)} => {val}")
		except Exception as e:
			print(f"[-] Failed to show results: {e}")

	def do_edit(self, arg):
		"Edit memory value by index or *: edit <index|*> <new_value>"
		args = arg.strip().split()
		if len(args) < 2:
			print("Usage: edit <index|*> <new_value>")
			return
		if not self.scanner or not self.scanner.results:
			print("[-] No scan results found.")
			return
		index_or_all, new_val = args[0], args[1]
		try:
			if index_or_all == '*':
				for i, (addr, _) in enumerate(self.scanner.results):
					self.editor.edit_direct(addr, new_val)
					print(f"[+] Edited result {i} at {hex(addr)} → {new_val}")
			else:
				index = int(index_or_all)
				if index < 0 or index >= len(self.scanner.results):
					print(f"[-] Invalid index. Found {len(self.scanner.results)} result(s).")
					return
				addr, _ = self.scanner.results[index]
				self.editor.edit_direct(addr, new_val)
				print(f"[+] Edited address {hex(addr)} → {new_val}")
		except Exception as e:
			print(f"[-] Edit failed: {e}")

	def do_freeze(self, arg):
		"Freeze memory value by index or *: freeze <index|*>"
		args = arg.strip().split()
		if len(args) < 1:
			print("Usage: freeze <index|*>")
			return
		if not self.scanner or not self.scanner.results:
			print("[-] No scan results found.")
			return
		index_or_all = args[0]
		try:
			if index_or_all == '*':
				for i, (addr, val) in enumerate(self.scanner.results):
					self.editor.freeze_direct(addr, val)
					print(f"[+] Freezing result {i} at {hex(addr)}")
			else:
				index = int(index_or_all)
				if index < 0 or index >= len(self.scanner.results):
					print(f"[-] Invalid index. Found {len(self.scanner.results)} result(s).")
					return
				addr, val = self.scanner.results[index]
				self.editor.freeze_direct(addr, val)
				print(f"[+] Freezing address {hex(addr)}")
		except Exception as e:
			print(f"[-] Freeze failed: {e}")

	def do_script(self, path):
		"Execute a HackByte script file (supports HackByte & bash commands)."
		if not path:
			print("Usage: script <file_path>")
			return
		if not os.path.isfile(path):
			print(f"[-] Script file not found: {path}")
			return
		try:
			with open(path) as f:
				for line in f:
					line = line.strip()
					if not line or line.startswith("#"):
						continue
					if line.startswith("!"):
						os.system(line[1:])
					else:
						print(f"{self.prompt}{line}")
						self.onecmd(line)
		except Exception as e:
			print(f"[-] Failed to execute script: {e}")

	def do_save(self, arg):
		"Save scan results: save <filename>"
		if not self.scanner or not self.scanner.results:
			print("[-] No scan results to save.")
			return
		if not arg:
			print("Usage: save <filename>")
			return
		try:
			self.scanner.save_results(arg)
		except Exception as e:
			print(f"[-] Save failed: {e}")

	def do_load(self, arg):
		"Load scan results from file: load <filename>"
		if not arg:
			print("Usage: load <filename>")
			return
		try:
			self.scanner.load_results(arg)
		except Exception as e:
			print(f"[-] Load failed: {e}")

	def do_dummy(self, arg):
		"Use dummy mode for testing without root"
		try:
			self.proc = DummyProcess()
			self.scanner = MemoryScanner(self.proc)
			self.editor = MemoryEditor(self.proc)
			print("[+] Dummy process is active for simulation.")
		except Exception as e:
			print(f"[-] Failed to activate dummy mode: {e}")

	def do_clear(self, arg):
		"Clear terminal screen"
		try:
			print("c", end="")
		except Exception as e:
			print(f"[-] Failed to clear screen: {e}")

	def do_info(self, arg):
		"Show info about the currently attached process"
		if not self.proc:
			print("[-] No process is currently attached.")
			return
		try:
			info = get_process_info(self.proc)
			if 'error' in info:
				print(f"[-] {info['error']}")
			else:
				print(f"[+] PID		: {info['pid']}")
				print(f"[+] Name	: {info['name']}")
				print(f"[+] Status	: {info['status']}")
				print(f"[+] Uptime	: {info['uptime']:.1f} seconds")
				print(f"[+] UID/GID	: {info['uid']} / {info['gid']}")
				print(f"[+] Memory	: {info['memory']}")
				print(f"[+] Threads	: {info['threads']}")
				print(f"[+] Executable	: {info['exe']}")
		except Exception as e:
			print(f"[-] Failed to get process info: {e}")

	def do_fuzzy(self, arg):
		"Fuzzy memory search: fuzzy start <type> | fuzzy increased | fuzzy decreased"
		args = arg.strip().split()
		if not self.scanner:
			print("[-] Not attached to any process.")
			return
		if not args:
			print("Usage: fuzzy start <type> | fuzzy increased | fuzzy decreased")
			return
		try:
			if args[0] == "start" and len(args) == 2:
				self.scanner.fuzzy_start(args[1])
			elif args[0] in ["increased", "decreased"]:
				self.scanner.fuzzy_filter(args[0])
			else:
				print("Invalid fuzzy command.")
		except Exception as e:
			print(f"[-] Fuzzy search failed: {e}")

	def do_exit(self, arg):
		"Exit the program"
		print("[*] Exiting...")
		return True