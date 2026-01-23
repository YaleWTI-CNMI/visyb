import argparse
import asyncio
import signal
import IPython
from traitlets.config import Config
from IPython.terminal.embed import InteractiveShellEmbed
import threading
import sys
import runpy
import os

from . import server
from .server import send_message
from .processor.__runtime__ import add_plot

def server_thread_entry():
    asyncio.set_event_loop(server.server_loop)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.start())

def shell_thread_entry():
    c = Config()

    c.TerminalInteractiveShell.banner1 = "VISYB Interactive Shell"
    c.TerminalInteractiveShell.banner2 = "\n"
    c.TerminalInteractiveShell.confirm_exit = False

    shell = InteractiveShellEmbed(config=c)
    shell()

def execute_file(filepath):
    import sys, os, builtins

    filepath = os.path.abspath(filepath)
    script_dir = os.path.dirname(filepath)
    visyb_root = os.path.abspath(".")

    # Store current directory
    original_cwd = os.getcwd()

    # Change to script directory
    os.chdir(script_dir)

    code = open(filepath, encoding="utf-8").read()
    compiled = compile(code, filepath, 'exec')

    exec_globals = {"__file__": filepath, "__name__": "__main__"}

    sys_path_backup = sys.path[:]
    sys.path.insert(0, visyb_root)
    try:
        exec(compiled, exec_globals)
    finally:
        sys.path = sys_path_backup
        # Restore original directory
        os.chdir(original_cwd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VISYB Server")
    parser.add_argument("--no-shell", action="store_true", help="Disable interactive shell (for deployments)")
    args = parser.parse_args()

    server_thread = threading.Thread(target=server_thread_entry, daemon=True)
    server_thread.start()

    if args.no_shell:
        # Headless mode - just run the server
        print("[INFO] Running in headless mode (no interactive shell)")
        print("[INFO] Press Ctrl+C to stop")
        try:
            while server_thread.is_alive():
                server_thread.join(timeout=0.5)
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down...")
    else:
        # Interactive mode - start shell
        shell_thread = threading.Thread(target=shell_thread_entry, daemon=True)
        shell_thread.start()

        if sys.stdin.isatty():
            shell_thread.join()
        else:
            server_thread.join()

    print("VISYB terminated")