# -*- mode: python -*-
block_cipher = None

datas = [('UI','UI')]

a = Analysis(['Rudy.py'],
             pathex=['D:\\Norton & Abert\\Project Rudy\\Rudy'],
             binaries=None,
             datas=datas,
             hiddenimports=['packaging', 'packaging.version', 'packaging.specifiers', 'packaging.requirements'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

 
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Rudy',
          debug=False,
          strip=False,
          upx=True,
          window =True ,
          console = True,
          icon = './UI/Icons/RUDYicon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Rudy')
