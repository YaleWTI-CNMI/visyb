"""The VISY interactive shell and its local WebSocket server."""
import asyncio
import threading

from IPython.terminal.embed import InteractiveShellEmbed
from traitlets.config import Config

from . import server
from .processor.__runtime__ import add_plot, clear_plots


def main():
    thread = threading.Thread(target=server.server_loop.run_forever, name="visyb-server")
    thread.start()
    listener = None
    try:
        listener = asyncio.run_coroutine_threadsafe(server.start(), server.server_loop).result(10)
        config = Config()
        config.TerminalInteractiveShell.confirm_exit = False
        config.TerminalInteractiveShell.banner1 = (
            "VISYB Interactive Shell — ws://localhost:8765\n"
            "Open the Godot desktop client, then load an example with %run.\n"
            "Send a plot: await add_plot(your_plot())\n"
            "Clear the workspace: await clear_plots()\n"
            "See README.md for the ATLAS and Kuramoto commands.\n"
        )
        shell = InteractiveShellEmbed(config=config, user_ns={
            "add_plot": add_plot, "clear_plots": clear_plots,
        })
        shell()
    except OSError as error:
        raise SystemExit(f"Cannot start VISYB on localhost:8765: {error}. Close any other VISYB shell.") from error
    finally:
        if listener is not None:
            async def close():
                listener.close()
                await listener.wait_closed()
            asyncio.run_coroutine_threadsafe(close(), server.server_loop).result(10)
        server.server_loop.call_soon_threadsafe(server.server_loop.stop)
        thread.join(timeout=10)
        server.server_loop.close()
    print("VISYB terminated")


if __name__ == "__main__":
    main()
