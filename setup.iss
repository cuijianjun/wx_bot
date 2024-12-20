[Setup]
AppName=抢单
AppVersion=0.0.2
DefaultDirName=C:\MyApplication
DefaultGroupName=MyApplication
OutputDir=.
OutputBaseFilename=抢单002
PrivilegesRequired=admin
AllowRootDirectory=yes
AllowUNCPath=no
DisableDirPage=no
Uninstallable=yes

[Dirs]
Name: "{app}\main.dist"

[Files]
Source: "D:\wx_bot_exe_v2\main.dist\*"; DestDir: "{app}\main.dist"; Flags: ignoreversion recursesubdirs createallsubdirs overwritereadonly restartreplace
Source: "D:\wx_bot_exe_v2\icon.ico"; DestDir: "{app}"

[Icons]
Name: "{group}\抢单"; Filename: "{app}\main.dist\main.exe"; IconFilename: "{app}\icon.ico"
Name: "{commondesktop}\抢单"; Filename: "{app}\main.dist\main.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[InstallDelete]
Type: filesandordirs; Name: "{app}\main.dist\*"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    // 删除旧版本文件夹
    DelTree(ExpandConstant('{app}\main.dist'), True, True, True);
  end;
end;