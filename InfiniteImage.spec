from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules
project_dir = Path(SPEC).parent
a = Analysis([str(project_dir/"main.py")], pathex=[str(project_dir)], binaries=[], datas=[(str(project_dir/"app_icon.ico"),"."),(str(project_dir/"infinite_image_logo.png"),".")], hiddenimports=collect_submodules("PIL"), hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz,a.scripts,a.binaries,a.datas,[],name="InfiniteImage",debug=False,bootloader_ignore_signals=False,strip=False,upx=True,console=False,disable_windowed_traceback=False,icon=str(project_dir/"app_icon.ico"))
