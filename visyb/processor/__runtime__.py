from .. import server

ID_COUNTER = 0
PLOTS = dict()


def new_id() -> int:
    global ID_COUNTER
    ID_COUNTER += 1
    return ID_COUNTER

async def add_plot(plot):
    plot.id = new_id()
    PLOTS[plot.id] = plot

    await server.send_message("PLOT_ADDED", to_client_dict(plot))

async def on_received_message(conn, message):
    print(message)
    if message["type"] == "UPDATE_MODS":
        id = message["data"]["id"]

        for mod_name, mod_value in message["data"]["mods"].items():
            PLOTS[id].update_mod(mod_name, mod_value)

        await server.send_message("PLOT_UPDATED", to_client_dict(PLOTS[id]))



def to_client_dict(obj):
    if hasattr(obj, 'to_client_dict') and callable(obj.to_client_dict):
        return to_client_dict(obj.to_client_dict())
    elif isinstance(obj, dict):
        return {
            # to_client_dict(k): to_client_dict(v)
            str(k): to_client_dict(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, (list, tuple, set)):
        return type(obj)(to_client_dict(item) for item in obj)
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        if hasattr(obj, '__dict__'):
            return to_client_dict(vars(obj))
        else:
            return str(obj)

# ===============

server.on_received_message.connect(on_received_message)
