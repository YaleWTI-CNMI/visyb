from ..server import send_message


ID_COUNTER = 0
PLOTS = dict()

def new_id() -> int:
    global ID_COUNTER
    ID_COUNTER += 1
    return ID_COUNTER

async def add_plot(plot):
    plot.id = new_id()
    PLOTS[plot.id] = plot

    data = None
    try:
        data = to_client_dict(plot)
    except:
        print("[ERROR] Plot result is not serializable")
    await send_message("PLOT_ADDED", to_client_dict(plot))

def to_client_dict(obj):
    if hasattr(obj, 'to_client_dict') and callable(obj.to_client_dict):
        return to_client_dict(obj.to_client_dict())
    elif isinstance(obj, dict):
        return {
            to_client_dict(k): to_client_dict(v)
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