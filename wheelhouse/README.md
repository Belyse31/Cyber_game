Put offline dependency wheels in this folder.

On a machine with internet access:

```powershell
py -m pip download -r ..\\requirements.txt -d .
```

Then serve them locally:

```powershell
py ..\\server\\local_repo_server.py
```

The launcher will install from `http://localhost:8000/wheelhouse/`.

