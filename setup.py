import sys
from cx_Freeze import setup, Executable
# sys.setrecursionlimit(5000)
# # 基本的脚本配置
# base = None
# if sys.platform == "win32":
#     base = "Win32GUI"  # 如果你正在创建一个 GUI 应用程序

# # 可执行文件的配置
# executables = [
#     Executable('main.py', base=base, icon='icon.ico')
# ]

# # 包的配置
# build_options = {
#     'packages': ['uiautomation', 'comtypes'],
#     'excludes': [],
#     'include_files': [
#         ('JS', 'JS'),
#         ('data', 'data'),
#         'key.json',
#         'location.txt'
#     ]
# }

# MSI 安装包的配置
# msi_options = {
#     'add_to_path': True,
#     'data': {
#         'Shortcut': [
#             ('DesktopShortcut', 'DesktopFolder', 'ordersApp', 'TARGETDIR', '[TARGETDIR]main.exe', None, 'icon.ico', None, None, None, None, 'TARGETDIR')
#         ]
#     },
#     'target_name': 'ordersApp',
#     'initial_target_dir': r'C:\\ordersApp'
# }

# setup(
#     name="ordersApp",
#     version="0.0.1",
#     description="抢单软件",
#     options={
#         "build_exe": build_options,
#         "bdist_msi": msi_options
#     },
#     executables=executables
# )

# directory_table = [
#     ("ProgramMenuFolder", "TARGETDIR", "."),
#     ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|GetOrders"),
# ]

# msi_data = {
#     "Directory": directory_table,
#     "ProgId": [
#         ("Prog.Id", None, None, "This is a description", "IconId", None),
#     ],
#     "Icon": [
#         ("IconId", "icon.ico"),
#     ],
# }

# bdist_msi_options = {
#     "add_to_path": True,
#     "data": msi_data,
#     # "environment_variables": [
#     #     ("E_MYAPP_VAR", "=-*MYAPP_VAR", "1", "TARGETDIR")
#     # ],
#     "upgrade_code": "{6b0386b3-a0bf-420c-8572-490a644530e0}",
# }

# build_exe_options = {"excludes": ["tkinter"], "include_msvcr": True}

# executables = [
#     Executable(
#         "main.py",
#         copyright="Copyright (C) 2024 cx_Freeze",
#         base="gui",
#         icon="icon.ico",
#         shortcut_name="My Program Name",
#         shortcut_dir="MyProgramMenu",
#     )
# ]

# setup(
#     name="hello",
#     version="0.1",
#     description="Sample cx_Freeze script to test MSI arbitrary data stream",
#     executables=executables,
#     options={
#         "build_exe": build_exe_options,
#         "bdist_msi": bdist_msi_options,
#     },
# )


# from cx_Freeze import setup, Executable
# sys.setrecursionlimit(10000)
# directory_table = [
#     ("ProgramMenuFolder", "TARGETDIR", "."),
#     ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|GetOrders"),
# ]

# msi_data = {
#     "Directory": directory_table,
#     "ProgId": [
#         ("Prog.Id", None, None, "A Tool", "IconId", None),
#     ],
#     "Icon": [
#         ("IconId", "icon.ico"),
#     ],
# }

# bdist_msi_options = {
#     "add_to_path": True,
#     "data": msi_data,
#     # "environment_variables": [
#     #     ("E_MYAPP_VAR", "=-*MYAPP_VAR", "1", "TARGETDIR")
#     # ],
#     "upgrade_code": "{6b0386b3-a0bf-420c-8572-490a644530e0}",
# }

# build_exe_options = {"excludes": ["tkinter"], "include_msvcr": True}

# executables = [
#     Executable(
#         "main.py",
#         copyright="Copyright (C) 2024 cx_Freeze",
#         base="gui",
#         icon="icon.ico",
#         shortcut_name="getOrders",
#         shortcut_dir="DesktopFolder",
#     )
# ]

# setup(
#     name="getOrders",
#     version="0.0.1",
#     description="A Tool",
#     executables=executables,
#     options={
#         "build_exe": build_exe_options,
#         "bdist_msi": bdist_msi_options,
#     },
# )

from cx_Freeze import setup, Executable
sys.setrecursionlimit(20000)
# 修改此处的选项以符合您的需求
# build_exe_options = { "excludes": ["tkinter"],
#     "include_msvcr": True,
#     "packages": ["uiautomation", "comtypes"],
#     "include_files": [
#         ("JS", "JS"),
#         ("data", "data"),
#         ("key.json", "key.json"),
#         ("location.txt", "location.txt")
#     ],
#     "include_packages": ["tkinter"],}
build_exe_options = {
    "includes": ["uiautomation", "comtypes","tkinter"],  # 包含的包
    # "excludes": ["tkinter"],  # 排除的包
    "include_files": [
        ("JS", "JS"),  # 包含数据目录
        ("data", "data"),  # 包含数据目录
        ("key.json", "key.json"),  # 包含数据文件
        ("location.txt", "location.txt") 
    ],
    # "include_msvcr": True,  # 包括 MSVC 运行时
}
bdist_msi_options = {
    "add_to_path": True,
    "data": {
        "Directory": [
            ("ProgramMenuFolder", "TARGETDIR", "."),
            ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|GetOrders"),
        ],
        "ProgId": [
            ("Prog.Id", None, None, "A Tool", "IconId", None),
        ],
        "Icon": [
            ("IconId", "icon.ico"),
        ],
    },
    "upgrade_code": "{1919f1c5-61cc-47ca-b2c0-83b0320405c9}",
}

executables = [
    Executable(
        "main.py",
        base="Win32GUI",
        icon="icon.ico",
        shortcut_name="getOrders",
        shortcut_dir="DesktopFolder",
    )
]

setup(
    name="getOrders",
    version="0.0.2",
    description="A Tool",
    executables=executables,
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
)