# visyb

## Requirements

- [Conda](https://docs.conda.io/en/latest/miniconda.html) (recommended) or Python 3.12 with pip
- Python **3.12**

## Installation


```bash
conda env create -f environment.yml
conda activate visyb
pip install ipython numpy pandas traitlets websockets
pip install -e .
```

## Running

Start the interactive shell and WebSocket server:

```bash
python -m visyb
```

You will be dropped into the `VISYB Interactive Shell` (IPython). The WebSocket server runs in the background on `localhost:8765`.