; MyTimetableNext installer script
; 이 파일은 build/installer.iss 위치에 저장하세요.
; build_pc_release.bat 또는 Inno Setup Compiler에서 실행합니다.

#define MyAppName "명덕외고 시간표"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "MyTimetableNext"
#define MyAppExeName "MyTimetableNext.exe"

[Setup]
AppId={{8F9B1B20-97A4-4D5E-9F67-MyTimetableNext}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\MyTimetableNext
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=MyTimetableNextSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=..\assets\logo.ico

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "바탕 화면 아이콘 만들기"; GroupDescription: "추가 아이콘:"; Flags: unchecked

[Files]
; PyInstaller one-file EXE
Source: "..\dist\MyTimetableNext.exe"; DestDir: "{app}"; Flags: ignoreversion

; 읽기용 fallback 데이터와 로고/아이콘
Source: "..\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} 실행"; Flags: nowait postinstall skipifsilent
