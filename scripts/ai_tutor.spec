# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect all data files
datas = [
    ('../prompts', 'prompts'),  # Include prompts directory  
    ('../CLAUDE.md', '.'),      # Include project documentation
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'openai',
    'anthropic',
    'rich.console',
    'rich.prompt',
    'rich.table',
    'rich.panel',
    'rich.text',
    'prompt_toolkit',
    'prompt_toolkit.keys',
    'prompt_toolkit.application',
    'prompt_toolkit.shortcuts',
    'dotenv',
    'json',
    'pathlib',
    'threading',
    'queue',
    'fnmatch',
    'importlib',
    'inspect',
]

a = Analysis(
    ['../main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'cv2',
        'torch',
        'tensorflow',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ai-tutor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)