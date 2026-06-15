# -*- mode: python ; coding: utf-8 -*-
"""
CleanBot v2.0 — PyInstaller 打包配置

在 Windows 上运行:
    pyinstaller cleanbot.spec --clean --noconfirm
    或直接双击 build.bat
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ── 隐式导入（确保所有模块被打包） ──
hidden_imports = [
    # PyQt6
    'PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtCore', 'PyQt6.QtGui',
    'PyQt6.sip',
    # 核心
    'core', 'core.utils',
    'core.scanner', 'core.scanner.file_scanner',
    'core.analyzer', 'core.analyzer.smart_analyzer',
    'core.cleaner', 'core.cleaner.file_cleaner',
    'core.diagnosis', 'core.diagnosis.system_diagnosis',
    'core.monitor', 'core.monitor.disk_monitor',
    'core.migrator', 'core.migrator.file_migrator', 'core.migrator.app_migrator',
    'core.deep_cleaner', 'core.deep_cleaner.deep_cleaner',
    'core.interactive', 'core.interactive.interactive_cleaner',
    'core.ai', 'core.ai.recommendation', 'core.ai.dialog_system',
    'core.updater',
    # UI
    'ui', 'ui.dashboard', 'ui.main_window',
    'ui.threads', 'ui.styles', 'ui.update_dialog',
    'ui.robot', 'ui.robot.robot_widget', 'ui.robot.character',
    'ui.robot.animation', 'ui.robot.expression', 'ui.robot.character_selector',
    # 第三方
    'psutil', 'Pillow', 'send2trash',
    # 标准库（有些在 Windows 打包时可能被遗漏）
    'json', 'urllib', 'webbrowser',
    'dataclasses', 'enum', 'pathlib',
]

# ── 数据文件 ──
datas = [
    ('config/file_types.json', 'config'),
    ('config/update_config.json', 'config'),
    ('resources/icons/cleanbot.ico', 'resources/icons'),
    # Robot character resources
    ('ui/robot/characters/conan/config.json', 'ui/robot/characters/conan'),
]

# ── 排除不需要的模块（减小体积） ──
excluded_modules = [
    'tkinter', 'unittest', 'test', 'pydoc', 'distutils',
    'matplotlib', 'numpy', 'scipy', 'pandas',
    'IPython', 'jupyter', 'notebook',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CleanBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/cleanbot.ico',
)

# 文件夹模式 — 所有 DLL 和资源放在 exe 旁边，无需解压到临时目录
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='CleanBot',
)
