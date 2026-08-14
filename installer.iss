#define MyAppName "Infinite Image"
#define MyAppVersion "1.3.0"
#define MyAppExeName "InfiniteImage.exe"
[Setup]
AppId={{F9C3BFE4-4A37-4C19-BB1A-5F0B7C5D82F4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\Infinite Image
DefaultGroupName=Infinite Image
OutputDir=installer_output
OutputBaseFilename=InfiniteImage_Setup_v1.3.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=app_icon.ico
[Files]
Source: "dist\InfiniteImage.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\Infinite Image"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Infinite Image"; Filename: "{app}\{#MyAppExeName}"
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Infinite Image"; Flags: nowait postinstall skipifsilent
