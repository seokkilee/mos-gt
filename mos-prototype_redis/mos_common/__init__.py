import toml
import pathlib
import os


with open(
    os.path.join(pathlib.Path(__file__).parent.resolve(), '../mos.toml'), 'r'
) as f:
    MOS_CONFIG = toml.load(f)
