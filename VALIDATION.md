# Desktop onboarding verification

Verified on 2026-10-01 on macOS, Apple M2 Max (arm64).

## Environment

- Godot **4.6.stable.official.89cea1439**, standard macOS universal build, Compatibility renderer (OpenGL on Metal).
- Python **3.12**, from conda-forge.
- PyMOL **3.1.0**, MDTraj **1.10.3**, NumPy **1.26.4**, netCDF4 **1.7.4**, Matplotlib **3.11.2**.
- IPython **9.17.1**, traitlets **5.16.1**, websockets **15.0.1**, tqdm **4.70.1**.

`conda env create --prefix /private/tmp/visy-clean-env --file environment.yml` completed successfully in a second, clean environment, including the editable package installation. A subsequent dependency audit identified incompatible upstream pip metadata in the newest PyMOL/MDTraj combination. The final environment bounds NumPy below 2 and MDTraj below 1.11, and includes netCDF4. Both test environments were updated from that final file; `pip check` reports no broken requirements. That environment started the real VISYB shell and sent a parameterized Kuramoto plot to the desktop client. The main local test environment is at `visyb/.venv` (activate that path to reuse it; new colleagues can use the named environment in the README).

## Upstream integration

Fetched and merged `project-visy` `origin/demo` at **3969dfa** and `origin/main` at **ed7a718**. Retained upstream XR scenes, bindings, interaction changes, materials, themes, and color handling, with renderer-specific color conversion for the Compatibility desktop renderer. Desktop startup, visible modifier values, and larger UI remain in place. Removed the scatter scene's `Hey` placeholder.

## Real examples and UI

The preparation command read `~/Downloads/visyb.7z`, importing only the two scripts and their five required datasets. Sensitive scripts, input data, generated PDB/OBJ files, and the local environment are Git-ignored. No data was uploaded or committed.

The actual commands from the README were entered into `python -m visyb`, followed by `await add_plot(...)`:

- **ATLAS:** 1,000 colored points rendered. Mouse selections generated **frame 94** and **frame 237**, each with a nonempty roughly 860 KB OBJ payload. Both structures appeared beside the cloud with distinct captions and colors. Only selected frames were generated. After the final dependency update and upstream merge, a new **frame 321** was generated successfully, and both Kuramoto datasets were loaded again.
- **Kuramoto, null omega:** loaded a `(201, 4096, 3)` simulation and rendered its trajectory plot. Clicking the inspector sliders changed Python's values to **frame 97** and **tail_window 35**, followed by visible geometry updates.
- **Kuramoto, skew omega:** loaded the second `(201, 4096, 3)` simulation and displayed red and blue trajectory groups. Clicking a white point created the linked scatter plot.
- **Explicit Python parameters:** `await add_plot(kuramoto_builder_test(frame=90, tail_window=20))` worked from the clean environment.
- **Reconnect:** the client restored existing Python plots after restart. Both Python-first and client-first startup were exercised.
- **Clear:** `await clear_plots()` removed both plots and inspector rows between examples.
- **Readable UI:** added larger default scaling and a persistent 100% / 125% / 150% selector; the enlarged interface and live values were visually inspected at 150%.
- **Shutdown / occupied port:** `exit` shut down the server cleanly; starting another server on port 8765 failed promptly with an explanatory message.

## Automated checks

`python -m pytest tests`: **6 passed**, also repeated in the clean environment. Covers private archive allowlisting, preservation of local edits, missing members without partial installation, independent plot parameters, replay, modifier updates, callback-created plots, large chunked messages, clearing, and malformed client input.

Godot `tests/desktop_smoke.gd`: **PASS**, including after upstream integration. Verifies the real desktop scene, chunk reassembly, viewport placement, initialized sliders, duplicate replay suppression, mouse selection, camera orbit/zoom, independent point buffers, and clearing controls. Uses synthetic fixtures, not private data.

## Remaining limitations

- Intel Macs and VR/headset operation were not tested.
- Initial Godot import reports missing texture references in the pre-existing VR controller FBX files. These assets are not used by the desktop scene. Godot 4.6 also refreshes tracked import metadata.
- The bundled project's XR support emits two `remove_tracker` diagnostics on Godot shutdown, even in desktop mode. Desktop rendering and process exit succeeded; those diagnostics remain.
- A sandbox-only macOS certificate diagnostic appeared during headless checking. The normal desktop runs connected successfully to the local Python server.
- In the null-omega data, the exterior group is almost stationary; tiny blue trajectories are expected. The skew-omega variant makes both groups easier to see.
- Dependencies are bounded in `environment.yml`; the versions above record this successful solve, rather than promising identical future Conda resolutions.
