import asyncio
import IPython
from traitlets.config import Config
from IPython.terminal.embed import InteractiveShellEmbed
import threading
import sys

from . import server
from .server import send_message
from .processor import add_plot

def server_thread_entry():
    asyncio.set_event_loop(server.server_loop)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.start())
    loop.run_forever() # this is missing
    loop.close()

def shell_thread_entry():
    c = Config()

    c.TerminalInteractiveShell.banner1 = "VISYB Interactive Shell"
    c.TerminalInteractiveShell.banner2 = "=" * 50 + "\n"
    c.TerminalInteractiveShell.confirm_exit = False

    shell = InteractiveShellEmbed(config=c)
    shell()

def execute_file(path):
    from .processor.builtin import plot_generator, ScatterPlot, modcont, modcat, modbool
    from .processor import add_plot

    exec_globals = {
        "plot_generator": plot_generator,
        "ScatterPlot": ScatterPlot,
        "modcont": modcont,
        "modcat": modcat,
        "modbool": modbool,
        "add_plot": add_plot,
        "__builtins__": __builtins__,
    }

    with open(path, "r") as f:
        exec(f.read(), exec_globals)


if __name__ == "__main__":
    server_thread = threading.Thread(target=server_thread_entry, daemon=True)
    shell_thread = threading.Thread(target=shell_thread_entry, daemon=True)

    server_thread.start()
    shell_thread.start()

    if sys.stdin.isatty():
        shell_thread.join()
    else:
        server_thread.join()


    print("VISYB terminated")