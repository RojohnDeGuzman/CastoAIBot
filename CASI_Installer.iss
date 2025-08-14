; Casto AI Bot Installer Script
[Setup]
AppName=CASI
AppVersion=1.2.2
AppPublisher=CastoTravel Philippines Inc.
AppPublisherURL=https://castotravel.ph
DefaultDirName={pf}\CASI
DefaultGroupName=CASI
UninstallDisplayIcon={app}\chatbot_ui.exe
OutputBaseFilename=CASI_Installer_v1.2.2
Compression=lzma
SolidCompression=yes
SetupIconFile=CASInew-nbg.ico
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
WizardImageFile=CASInew-nbg.bmp
WizardSmallImageFile=CASInew-nbg.bmp
DisableProgramGroupPage=no
DisableDirPage=no
AllowNoIcons=yes
OutputDir=installer_output

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "dist\chatbot_ui.exe"; DestDir: "{app}"; Flags: ignoreversion; Check: not IsRunning

; Assets directory
Source: "dist\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuration files
Source: "config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "backend.py"; DestDir: "{app}"; Flags: ignoreversion

; Icons and images
Source: "CASInew-nbg.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "CASInew-nbg.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "attachment.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "logout.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "default_user.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "feedback.png"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "DEPLOYMENT_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "BUILD_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "NETWORK_TROUBLESHOOTING.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "SINGLE_INSTANCE_TROUBLESHOOTING.md"; DestDir: "{app}"; Flags: ignoreversion

; Troubleshooting scripts
Source: "fix_single_instance.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "network_troubleshooting.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "test_backend_connectivity.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "test_single_instance.py"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\CASI"; Filename: "{app}\chatbot_ui.exe"; IconFilename: "{app}\CASInew-nbg.ico"
Name: "{group}\CASI Documentation"; Filename: "{app}\DEPLOYMENT_GUIDE.md"
Name: "{group}\Network Troubleshooting"; Filename: "{app}\NETWORK_TROUBLESHOOTING.md"
Name: "{group}\Single Instance Troubleshooting"; Filename: "{app}\SINGLE_INSTANCE_TROUBLESHOOTING.md"
Name: "{group}\Uninstall CASI"; Filename: "{uninstallexe}"
Name: "{commondesktop}\CASI"; Filename: "{app}\chatbot_ui.exe"; Tasks: desktopicon; IconFilename: "{app}\CASInew-nbg.ico"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\CASI"; Filename: "{app}\chatbot_ui.exe"; Tasks: quicklaunchicon; IconFilename: "{app}\CASInew-nbg.ico"

[Registry]
; Create registry entries for easy uninstall
Root: HKLM; Subkey: "SOFTWARE\CASI"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\CASI"; ValueType: string; ValueName: "Version"; ValueData: "1.2.2"; Flags: uninsdeletekey

[Run]
Filename: "{app}\chatbot_ui.exe"; Description: "Launch CASI"; Flags: nowait postinstall skipifsilent
Filename: "{app}\DEPLOYMENT_GUIDE.md"; Description: "View Deployment Guide"; Flags: nowait postinstall skipifsilent shellexec

[UninstallDelete]
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.tmp"

[Code]
var
  IsRunning: Boolean;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  Output: String;
begin
  Result := True;
  IsRunning := False;
  
  // Check if CASI is already running
  if Exec('tasklist.exe', '/FI "IMAGENAME eq chatbot_ui.exe" /FO CSV /NH', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
    begin
      IsRunning := True;
      if MsgBox('CASI is currently running.' + #13#10 + #13#10 + 
                 'It is recommended to close CASI before installing the update.' + #13#10 + #13#10 + 
                 'Do you want to continue with the installation?', 
                 mbConfirmation, MB_YESNO) = IDNO then
      begin
        Result := False;
      end;
    end;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = wpReady then
  begin
    if IsRunning then
    begin
      if MsgBox('CASI is still running. The installation may not work correctly.' + #13#10 + #13#10 + 
                 'Do you want to continue anyway?', 
                 mbConfirmation, MB_YESNO) = IDNO then
      begin
        Result := False;
      end;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    // Create configuration directory if it doesn't exist
    if not DirExists(ExpandConstant('{userappdata}\CASI')) then
    begin
      CreateDir(ExpandConstant('{userappdata}\CASI'));
    end;
  end;
end;

function IsRunning: Boolean;
begin
  Result := IsRunning;
end;

[CustomMessages]
english.CreateDesktopIcon=Create a &desktop icon
english.CreateQuickLaunchIcon=Create a &Quick Launch icon
english.AdditionalIcons=Additional icons:
