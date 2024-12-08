# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

added_files = [
    ('ui/*.ui', 'ui'),
    ('resources/*', 'resources'),
    ('modules/*', 'modules'),
    ('lib/*', 'lib'),
    ('core/*', 'core'),
]

hidden_imports = [
    'modules.main.main_view',
    'modules.main.main_controller',
    'core.app_module',
    'modules.process',
    'modules.history',
    'modules.pe',
    'modules.network',
    'modules.main',
    'lib.isegye_viewer_core',
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
