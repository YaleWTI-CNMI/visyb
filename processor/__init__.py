from ..server import send_message
from .builtin import to_client_dict


ID_COUNTER = 0
PLOTS = dict()

def new_id() -> int:
    global ID_COUNTER
    ID_COUNTER += 1
    return ID_COUNTER

def add_plot(plot):
    plot.id = new_id()
    PLOTS[plot.id] = plot

    print(to_client_dict(plot))
    # await server.send_message("PLOT_ADDED", to_client_dict(plot))
