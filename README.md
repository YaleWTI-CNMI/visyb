# VISYB — Python shell for VISY

VISY runs your analysis in Python and displays its plots in the Godot client. You load code into an IPython shell, construct a plot, and explicitly send it with `await add_plot(...)`. Selections and sliders in Godot call back into Python.

**[Illustrated macOS desktop tutorial](docs/visy-desktop-tutorial.md)** — Homebrew setup, VISYB shell commands, and expected views for ATLAS and Kuramoto.

## One-time macOS setup

Use this repository's `master` branch together with the Godot project's `main` branch. Keep the repositories beside each other:

```text
VISY/
  visyb/
  project-visy/
```

Install [Miniforge](https://github.com/conda-forge/miniforge#download) for your Mac's architecture, or use your existing Conda. Open a new terminal, then run from the **visyb repository**:

```bash
conda env create -f environment.yml
conda activate visyb
python -m visyb.prepare_examples ~/Downloads/visy-desktop-examples.zip
```

The last command imports the separately shared `visy-desktop-examples.zip` archive. The original `visyb.7z` archive is also supported by substituting its path. It copies only ATLAS, Kuramoto, and their required data into `examples/sensitive/`. Those files and generated protein models stay Git-ignored. It prepares ATLAS for headless PyMOL on macOS and generates molecular frames only when selected. Repeating preparation keeps existing local files, including edits. It may take around a minute.

Install the standard [Godot 4.6 macOS editor](https://godotengine.org/download/archive/4.6-stable/) and import `../project-visy/project.godot`. No .NET edition, export templates, headset, or VR runtime is needed.

## Each session: start Python, then Godot

In Terminal, from **visyb/**:

```bash
conda activate visyb
python -m visyb
```

Leave this terminal open. You should see `VISYB Interactive Shell` and an `In [1]:` prompt. The server listens locally at `ws://localhost:8765`.

In Godot, press **Play Project (F5 or the top-right Play button)**. The project opens the desktop scene, `intro_scene_debug.tscn`. Its status should say **Connected · send a plot from the VISYB shell**. An empty workspace is expected until you send a plot.

**Enter the following commands at the VISYB `In [...]` prompt, not at your normal terminal prompt.** `add_plot` and `clear_plots` are already imported.

### ATLAS: select a point to see its protein structure

```python
%run examples/sensitive/atlas_vr.py examples/sensitive
atlas = atlas_plot()
await add_plot(atlas)
```

You should see 1,000 colored points. Click a point in Godot: Python loads that trajectory frame, generates its cartoon representation, and sends a protein model beside the plot with a `frame_<index>` caption. Click another point to compare structures. The first selection takes longer; generated models are cached in `examples/sensitive/frames/`.

You can also request a particular frame directly from the shell:

```python
await add_plot(model3d_for_index(94))
```

### Kuramoto: adjust frame and tail length

Clear the previous workspace, load the simulation, and explicitly send its plot:

```python
await clear_plots()
%run examples/sensitive/kuramoto_vr.py examples/sensitive/kuramoto_traces_N3_null_omega.pkl
kuramoto = kuramoto_builder_test()
await add_plot(kuramoto)
```

The inspector starts at **frame 62** and **tail_window 10**. Move either slider: Godot sends the change to Python, which rebuilds and returns the trajectories. The interior group is red; the exterior group is blue. In the null-omega dataset, the exterior group is almost stationary, so its tracks are very small. Click a white point to add the example's linked scatter plot.

To compare the skew-omega simulation, which shows both groups more clearly:

```python
await clear_plots()
%run examples/sensitive/kuramoto_vr.py examples/sensitive/kuramoto_traces_N3_skew_omega.pkl
await add_plot(kuramoto_builder_test())
```

You can choose starting parameters in Python too:

```python
await clear_plots()
await add_plot(kuramoto_builder_test(frame=90, tail_window=20))
```

Load one variant at a time and clear before rerunning its script: `%run` replaces that script's variables and functions in the shell.

## Desktop controls and shutdown

- Choose **UI size** (100%, 125%, or 150%) in the top bar. The default is 125%, and your choice is remembered.
- Click a point to select it; drag to orbit.
- Shift + drag pans; scroll or pinch zooms. **Reset camera** restores the view.
- `await clear_plots()` removes plots and inspector controls.
- Close Godot and type `exit` in the VISYB shell to stop. Closing only Godot keeps Python's plots; reopening Godot restores them.

## Troubleshooting

- **No module named …:** run `conda activate visyb`; `python -c "import sys; print(sys.executable)"` should point into that environment. PyMOL comes from Conda, so a bare `pip install` is insufficient for ATLAS.
- **Missing example/data:** run the preparation command from `visyb/`, then use the exact `%run` commands above. Archive data is deliberately absent from Git. Only load pickle datasets from the trusted, privately shared archive.
- **Port 8765 already in use:** exit the other VISYB shell. Do not run two servers simultaneously.
- **Waiting for Python:** start `python -m visyb`; confirm the Godot URL is `ws://localhost:8765`. It retries automatically.
- **XR initialization error:** open `intro_scene_debug.tscn` or use Play Project on this branch. `intro_scene.tscn` is the headset scene.
- **Nothing after `%run`:** this only loads functions and data. You must also run `await add_plot(...)`.

## Verification

Run `python -m pytest tests`. See [VALIDATION.md](VALIDATION.md) for the tested runtime versions, actual desktop checks, and limitations. This work builds on Python's `milestone-2` and Godot's `demo` branches.
