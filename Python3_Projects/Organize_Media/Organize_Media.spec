# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Organize_Media.py'],
             pathex=['C:\\Users\\MediaPC\\Documents\\Gitrepos\\Work\\venv\\Lib\\site-packages', 'C:\\Users\\MediaPC\\Documents\\Gitrepos\\Work\\Python3_Projects\\Organize_Media'],
             binaries=[],
             datas=[],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Organize_Media',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
