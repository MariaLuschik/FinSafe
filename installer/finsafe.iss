; ===========================================================================
; Скрипт Inno Setup для установщика FinSafe.
; Как собрать: открыть этот файл в Inno Setup Compiler и нажать Build -> Compile (Ctrl+F9)
; или запустить build_all.bat из корня репозитория.
;
; Перед компиляцией должен существовать файл dist\FinSafe.exe
; (его создаёт build_exe.bat с помощью PyInstaller).
; ===========================================================================

; --- Константы, чтобы менять название и версию в одном месте ---
#define MyAppName      "FinSafe"
#define MyAppVersion   "1.0.0"
#define MyAppPublisher "ООО «FinSafe»"
#define MyAppExeName   "FinSafe.exe"

[Setup]
; Уникальный идентификатор программы. Благодаря ему новая версия установится
; поверх старой, а не рядом с ней. Для своих проектов генерируйте новый GUID
; (в Inno Setup: меню Tools -> Generate GUID). Двойная скобка { в начале обязательна.
AppId={{8F4B1C52-6A7E-4D3B-9C21-5E0A7D4F9B13}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

; Папка установки. {autopf} это Program Files, а при установке без прав
; администратора (PrivilegesRequired=lowest) это папка Programs в профиле пользователя.
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; Установка не требует прав администратора, поэтому работает и на учебных компьютерах.
PrivilegesRequired=lowest

; Куда положить готовый установщик и как назвать файл: FinSafe_Setup_1.0.0.exe
OutputDir=Output
OutputBaseFilename=FinSafe_Setup_{#MyAppVersion}

; Сжатие файлов и современный вид мастера установки.
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

; Значок программы в списке «Установка и удаление программ».
UninstallDisplayIcon={app}\{#MyAppExeName}

; Текст, который показывается на первой странице мастера.
InfoBeforeFile=readme_ru.txt

[Languages]
; Русский язык мастера установки. Файл Russian.isl входит в состав Inno Setup.
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
; Флажок «Создать значок на рабочем столе». Параметр unchecked означает,
; что по умолчанию флажок снят.
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Что копируется на компьютер пользователя.
; Source указан относительно папки со скриптом, поэтому ..\ ведёт в корень репозитория.
Source: "..\dist\FinSafe.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md";       DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Ярлыки в меню «Пуск» и на рабочем столе.
Name: "{group}\{#MyAppName}";               Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName} (демо-данные)"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--demo"
Name: "{group}\Удалить {#MyAppName}";       Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}";         Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Последняя страница мастера: предложение сразу запустить программу.
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить {#MyAppName}"; Flags: nowait postinstall skipifsilent
