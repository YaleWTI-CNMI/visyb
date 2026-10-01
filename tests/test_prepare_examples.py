import io
from pathlib import Path
import tarfile

import pytest

from visyb.prepare_examples import FILES, prepare

ATLAS = '''import os
import pymol
pymol.finish_launching(["pymol", "-qc"])
if not os.path.exists(frame_path(name_override="atlas_0", extension=".pdb")):
    expensive_export()
# Load the numpy file with the PHATE coordinates
x = 1
'''


def archive_at(path, missing=None):
    with tarfile.open(path, 'w') as archive:
        for name in (*FILES, '../../../unexpected', '.git/config'):
            if name == missing:
                continue
            content = (ATLAS if name == 'atlas_vr.py' else 'x = 1\n').encode()
            info = tarfile.TarInfo('visyb/examples/sensitive/' + name)
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))


def test_allowlist_private_preparation_and_repeat_import(tmp_path):
    archive = tmp_path / 'examples.tar'
    archive_at(archive)
    destination = tmp_path / 'private'
    prepare(archive, destination)
    assert {p.name for p in destination.iterdir()} == set(FILES)
    source = (destination / 'atlas_vr.py').read_text()
    assert 'expensive_export()' not in source
    assert 'pymol2.PyMOL()' in source
    assert not (tmp_path / 'unexpected').exists()
    (destination / 'atlas_vr.py').write_text('# local edit')
    prepare(archive, destination)
    assert (destination / 'atlas_vr.py').read_text() == '# local edit'


def test_missing_archive_member_does_not_install_partial_example(tmp_path):
    import subprocess
    archive = tmp_path / 'missing.tar'
    archive_at(archive, missing='1ptq_A_R1.xtc')
    with pytest.raises(subprocess.CalledProcessError):
        prepare(archive, tmp_path / 'private')
    assert not (tmp_path / 'private').exists()
