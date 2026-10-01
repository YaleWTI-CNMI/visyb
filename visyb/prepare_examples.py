"""Import the privately shared examples without importing their Git repository."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

FILES = (
    "atlas_vr.py", "kuramoto_vr.py", "1ptq_A.pdb", "1ptq_A_R1.xtc",
    "z_phate_3d_10k.npy", "kuramoto_traces_N3_null_omega.pkl",
    "kuramoto_traces_N3_skew_omega.pkl",
)


def prepare_atlas(source):
    """Apply narrowly scoped macOS/startup fixes to the private archive copy."""
    start = source.index('if not os.path.exists(frame_path(name_override="atlas_0", extension=".pdb")):')
    end = source.index('# Load the numpy file with the PHATE coordinates', start)
    source = source[:start] + source[end:]
    source = source.replace('pymol.finish_launching(["pymol", "-qc"])',
                            'import pymol2\n_pymol = pymol2.PyMOL()\n_pymol.start()\ncmd = _pymol.cmd')
    source = source.replace('    cmd.load(pdb_path, pdb_name)', '''    os.makedirs(os.path.dirname(pdb_path), exist_ok=True)
    if not os.path.exists(pdb_path):
        index = int(pdb_name.rsplit("_", 1)[1])
        md.load_frame(atlas_xtc, index, top=atlas_pdb).save_pdb(pdb_path)
    cmd.load(pdb_path, pdb_name)''')
    source = source.replace('    print(color_list)', '')
    # The desktop and VR plots use the same normalized point coordinates.
    source = source.replace('size=0.45', 'size=0.025')
    source = source.replace('color={"r": r, "g": g, "b": b}',
                            'color={"r": float(r), "g": float(g), "b": float(b)}')
    return '# Prepared for VISY desktop: lazy frames and headless PyMOL.\n' + source


def prepare(archive, destination):
    archive = Path(archive).expanduser().resolve(strict=True)
    destination = Path(destination).resolve()
    tar = shutil.which('bsdtar') or shutil.which('tar')
    if not tar:
        raise RuntimeError('BSD tar is required; macOS includes /usr/bin/tar.')
    # Stream each allowlisted member to a file we name ourselves. Archive paths,
    # symlinks, .git, and unrelated sensitive examples are never extracted.
    with tempfile.TemporaryDirectory(prefix='visyb-examples-') as temp:
        staged = Path(temp)
        for name in FILES:
            print(f'Preparing {name} …', flush=True)
            with (staged / name).open('wb') as output:
                subprocess.run([tar, '-xOf', str(archive), f'visyb/examples/sensitive/{name}'],
                               stdout=output, stderr=subprocess.PIPE, check=True)
            if not (staged / name).stat().st_size:
                raise ValueError(f'Archive member is empty or is not a regular file: {name}')
        atlas = staged / 'atlas_vr.py'
        atlas.write_text(prepare_atlas(atlas.read_text()))
        for name in ('atlas_vr.py', 'kuramoto_vr.py'):
            compile((staged / name).read_text(), name, 'exec')
        destination.mkdir(parents=True, exist_ok=True)
        # A repeat import is a no-op; it must not overwrite local script edits.
        for name in FILES:
            target = destination / name
            if not target.exists():
                shutil.copyfile(staged / name, target)
            else:
                print(f'Keeping existing {target.name}')
    print(f'Ready: {destination}\nStart python -m visyb, then follow README.md.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--destination', type=Path, default=Path('examples/sensitive'))
    args = parser.parse_args()
    try:
        prepare(args.archive, args.destination)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Cannot prepare examples: {error}\nCheck the archive and required members.\n')


if __name__ == '__main__':
    main()
