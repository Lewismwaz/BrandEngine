; ============================================================
; Brand Engine - Inno Setup Script
; Requires: Inno Setup 6.x  (https://jrsoftware.org/isinfo.php)
; Build:    iscc installer_script.iss
; ============================================================

#define MyAppName        "Brand Engine"
#define MyAppVersion     "1.0.0"
#define MyAppPublisher   "Yavotu Team"
#define MyAppURL         "https://github.com/yavotu/BrandEngine"
#define MyAppExeName     "BrandEngine.exe"
#define MyAppId          "{F8B3F1E8-5E3A-4B8C-9D1E-2F4A6B8C0D1E}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Installer
VersionInfoCopyright=Copyright (C) 2024 {#MyAppPublisher}

; Install location (auto-selects Program Files or Program Files (x86))
DefaultDirName={autopf}\BrandEngine
DefaultGroupName=BrandEngine
DisableProgramGroupPage=yes
AllowNoIcons=yes

; Output
OutputDir=installer
OutputBaseFilename=BrandEngine_Setup_{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

; Privileges & architecture (x64 only)
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Misc
LicenseFile=LICENSE
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
AppMutex=BrandEngine_SingleInstance_Mutex

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenu";   Description: "Create a Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Main executable (PyInstaller one-file build)
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Static assets (read-only at runtime)
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Version info / README (optional, useful for support)
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

; VC++ Redistributable (REQUIRED for PyInstaller-built Python apps).
; Download vc_redist.x64.exe from:
; https://aka.ms/vs/17/release/vc_redist.x64.exe
; and place it in the project root. Comment out if you bundle
; it another way or rely on the user having it.
Source: "vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}";           Filename: "{app}\{#MyAppExeName}"; Tasks: startmenu
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop
Name: "{autodesktop}\{#MyAppName}";     Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Install Visual C++ Redistributable (silent, no reboot)
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; \
    StatusMsg: "Installing Visual C++ Redistributable..."; \
    Flags: waituntilterminated runhidden; Check: VCRedistNeedsInstall

; Launch app after install
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove app folder contents (the exe, assets, etc.)
Type: filesandordirs; Name: "{app}\assets"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: files;          Name: "{app}\*.log"
; NOTE: user data (database, exports) lives in %LOCALAPPDATA% - see [Code]

[Registry]
; App Paths so users can launch "BrandEngine" from Run dialog
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; \
    ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName}"; \
    Flags: uninsdeletekey

[Code]
{ ------------------------------------------------------------------
  Detect whether the VC++ 2015-2022 x64 runtime is already installed.
  If it is, skip the redistributable installer.
  ------------------------------------------------------------------ }
function VCRedistNeedsInstall: Boolean;
var
  Installed: Cardinal;
begin
  Result := True;
  // VC++ 2015-2022 x64 runtime key
  if RegQueryDWordValue(HKLM,
      'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64',
      'Installed', Installed) then
  begin
    if Installed = 1 then
      Result := False;
  end;
end;

{ ------------------------------------------------------------------
  Create user-writable data directories in %LOCALAPPDATA% on first
  install. This mirrors what config.DATABASE_PATH / exports do.
  ------------------------------------------------------------------ }
procedure CurStepChanged(CurStep: TSetupStep);
var
  DataDir: String;
begin
  if CurStep = ssPostInstall then
  begin
    DataDir := ExpandConstant('{localappdata}\BrandEngine');
    ForceDirectories(DataDir);
    ForceDirectories(DataDir + '\exports');
    ForceDirectories(DataDir + '\database');
  end;
end;

{ ------------------------------------------------------------------
  On uninstall, ask whether to keep user data.
  ------------------------------------------------------------------ }
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{localappdata}\BrandEngine');
    if DirExists(DataDir) then
    begin
      if MsgBox('Do you want to delete your saved brand names and exports?' + #13#10 +
                '(' + DataDir + ')',
                mbConfirmation, MB_YESNO) = IDYES then
        DelTree(DataDir, True, True, True);
    end;
  end;
end;