# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Analysis configuration
a = Analysis(
    ['main.py'],
    pathex=['f:/All Projects/Python/Projects/Cursor-Tools'],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'rich.console',
        'rich.panel',
        'rich.table',
        'rich.text',
        'rich.prompt',
        'rich.align',
        'rich.progress',
        'colorama',
        'requests',
        'winreg',
        'ctypes',
        'sqlite3',
        'configparser',
        'uuid',
        'hashlib',
        'tempfile',
        'glob',
        'json',
        're',
        'datetime',
        'pathlib',
        'typing',
        'subprocess',
        'shutil',
        'time'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ configuration
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Cursor-Tools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon=None,
    version=None,
)












