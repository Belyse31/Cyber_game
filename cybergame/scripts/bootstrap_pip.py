"""
Bootstrap pip from the bundled pip wheel.
Called by start.bat as:
    python.exe bootstrap_pip.py <path_to_pip.whl> <path_to_wheelhouse>
"""
import sys
import runpy

pip_whl = sys.argv[1]   # e.g. C:\CyberGame\wheelhouse\pip-25.0.1-py3-none-any.whl
wheelhouse = sys.argv[2]  # e.g. C:\CyberGame\wheelhouse

sys.path.insert(0, pip_whl)
sys.argv = [
    "pip", "install",
    "--no-index",
    "--find-links", wheelhouse,
    "pip", "setuptools", "wheel",
    "-q",
]
runpy.run_module("pip", run_name="__main__")
