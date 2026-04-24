[Setup]
AppName=차세대 시간표 데스크톱
AppVersion=1.0.0
DefaultDirName={autopf}\My-Timetable-Next
DefaultGroupName=차세대 시간표 데스크톱
OutputDir=..\dist\installer
OutputBaseFilename=MyTimetableNextSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\assets\logo.ico

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "바탕 화면 아이콘 만들기"; GroupDescription: "추가 아이콘:"; Flags: unchecked

[Files]
Source: "..\MyTimetableNext.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\차세대 시간표 데스크톱"; Filename: "{app}\MyTimetableNext.exe"
Name: "{autodesktop}\차세대 시간표 데스크톱"; Filename: "{app}\MyTimetableNext.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MyTimetableNext.exe"; Description: "차세대 시간표 데스크톱 실행"; Flags: nowait postinstall skipifsilent