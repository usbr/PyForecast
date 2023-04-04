;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; InnoSetup Compiler File 
; 
; This file is intended to be run by the InnoSetup Compiler program which is available
;      at http://www.jrsoftware.org/isinfo.php. This file relies on the batch file
;      installerPreBuild.bat which comes with the PyForecast source code and should be
;      located in the same directory as this file. Update the path below to point to
;      where you have the batch file on your local machine.
; 

#define MyAppName "PyForecast"
#define MyAppVersion "5.0.9"
#define MyAppPublisher "USBR"
#define MyAppURL "https://github.com/usbr/PyForecast"
#define MyAppExeName "PyForecast.exe"
#define bin "dist\main\"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{03AAA034-F1FD-45B1-913D-9C27573728A9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName=C:\{#MyAppName}
DisableProgramGroupPage=yes
; Assign a name to the installer file
OutputBaseFilename=PyForecast_Installer
; Define the icon to use for the installer and the application
SetupIconFile={#bin}Resources\Icons\AppIcon.ico
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
;SignTool=signtool $f
;signtool = "signtool.exe" sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a $p  
LicenseFile=.\license.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

; Copy all the files from the defined bin-directory into the installation folder
[Files]
Source: "{#bin}*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

; Create a shortcut to the application at the specified locations
[Icons]
Name: "{userprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

