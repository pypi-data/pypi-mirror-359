param(
  [string]$Dir         = $(Join-Path $PSScriptRoot 'pywershell'),
  [string]$SessionName = 'powershell-session'
)

function Ensure-SQLite3 {
  Write-Host '[INFO] checking sqlite3.exe'
  $exe = "$env:USERPROFILE\sqlite3.exe"
  if (-not (Test-Path $exe)) {
    Write-Host '[INFO] downloading sqlite3'
    $page = Invoke-WebRequest 'https://www.sqlite.org/download.html'
    $url  = ($page.ParsedHtml.getElementsByTagName('a') |
             Where-Object href -match 'sqlite-tools-win-x64.*?\.zip' |
             Select-Object -First 1).href
    if ($url -notmatch '^https?://') { $url = "https://www.sqlite.org/$url" }
    $zip = "$env:TEMP\sqlite.zip"; $out = "$env:USERPROFILE\sqlite"
    Invoke-WebRequest $url -OutFile $zip
    Expand-Archive $zip -DestinationPath $out -Force
    Move-Item (Get-ChildItem $out -Recurse -Filter sqlite3.exe |
               Select-Object -First 1).FullName $exe -Force
  }
  Write-Host "[INFO] sqlite3 at $exe"
  return $exe
}

function Escape-SQL([string]$s) { $s -replace "'","''" }

function Sanitize-Output([string]$t) {
  $clean = $t -replace "`0",""
  $clean = $clean -replace '\r?\n','\n'
  $clean = $clean -replace '\s+',' '
  return $clean.Trim()
}

function Exec-SQL([string]$sql, [string]$db, [string]$sqlite) {
  $psi = [System.Diagnostics.ProcessStartInfo]::new($sqlite, "`"$db`"")
  $psi.RedirectStandardInput = $true
  $psi.UseShellExecute       = $false
  $psi.CreateNoWindow        = $true
  $proc = [System.Diagnostics.Process]::new()
  $proc.StartInfo = $psi
  $proc.Start() | Out-Null
  $proc.StandardInput.WriteLine($sql)
  $proc.StandardInput.Close()
  $proc.WaitForExit()
}

function Try-ExecSQL {
  param (
    [string]$sql,
    [string]$db,
    [string]$sqlite,
    [int]$retries = 5,
    [int]$delayMs = 100
  )
  for ($i = 0; $i -lt $retries; $i++) {
    try {
      Exec-SQL $sql $db $sqlite
      return
    } catch {
      if ($_ -match 'database is locked') {
        Start-Sleep -Milliseconds $delayMs
      } else {
        throw
      }
    }
  }
  throw "Failed to execute SQL after $retries retries: $sql"
}

class Pywershell {
  [string]$Dir; [string]$SessionName; [string]$SessionDir
  [string]$Alive; [string]$DB; [string]$Sqlite; [string]$LogFile

  Pywershell([string]$dir,[string]$session) {
    $ts = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
    $this.Dir         = $dir
    $this.SessionName = $session
    $this.SessionDir  = Join-Path $dir "$ts-$session"
    $this.Alive       = Join-Path $this.SessionDir 'alive.file'
    $this.DB          = Join-Path $this.SessionDir 'output.db'
    $this.Sqlite      = Ensure-SQLite3
    $this.LogFile     = Join-Path $this.SessionDir 'session.log'

    New-Item -ItemType Directory -Path $this.SessionDir -Force | Out-Null
    New-Item -ItemType File      -Path $this.Alive      -Force | Out-Null

    $this.WriteLog("[INIT] session started $session")

    $schema = @"
CREATE TABLE IF NOT EXISTS commands(
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  input      TEXT    NOT NULL,
  ts         TEXT    DEFAULT CURRENT_TIMESTAMP,
  ran        BOOLEAN DEFAULT 0,
  new_window BOOLEAN DEFAULT 0
);
CREATE TABLE IF NOT EXISTS logs(
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  input    TEXT,
  output   TEXT,
  ts       TEXT    DEFAULT CURRENT_TIMESTAMP,
  streamed BOOLEAN DEFAULT 0
);
"@
    Try-ExecSQL $schema $this.DB $this.Sqlite
    Try-ExecSQL "ALTER TABLE commands ADD COLUMN new_window BOOLEAN DEFAULT 0;" $this.DB $this.Sqlite
    $this.WriteLog('[INIT] sqlite db created')
  }

  [void]WriteLog([string]$m) {
    $line = "[$(Get-Date -Format o)] $m"
    Add-Content -Path $this.LogFile -Value $line -Encoding Unicode
    Write-Host  $line
  }

  [void]LogCmd([string]$in,[string]$out) {
    $ts = Get-Date -Format o
    $i  = Escape-SQL $in
    $o  = Escape-SQL (Sanitize-Output $out)
    Try-ExecSQL "INSERT INTO logs(input,output,ts,streamed) VALUES('$i','$o','$ts',0);" $this.DB $this.Sqlite
    $this.WriteLog("[LOG] $in")
  }

  [void]Start() {
    $this.WriteLog('[START] command loop')
    while (Test-Path $this.Alive) {
      $row = & $this.Sqlite $this.DB "SELECT id||'|'||input||'|'||new_window FROM commands WHERE ran=0 ORDER BY id LIMIT 1"
      if ($row) {
        $parts = $row -split '\|'
        $id   = $parts[0]
        $cmd  = $parts[1]
        $neww = $parts[2] -eq '1'
        $this.WriteLog("[RUN] ID $id :: $cmd")

        try {
          if ($neww) {
            $guid = [guid]::NewGuid().ToString()
            $logPath = "$env:TEMP\$guid.log"
            $escaped = $cmd.Replace('"','""')
            $wrapped = "Start-Transcript -Path `"$logPath`"; $escaped; Stop-Transcript"
            $proc = Start-Process powershell -ArgumentList "-Command", $wrapped -WindowStyle Normal -PassThru
            $proc.WaitForExit()
            $out = Get-Content $logPath -Raw -Encoding UTF8
          } else {
            $out = Invoke-Expression $cmd 2>&1 | Out-String
          }
        } catch {
          $out = $_.Exception.Message
        }

        $this.LogCmd($cmd,$out)
        Try-ExecSQL "UPDATE commands SET ran=1 WHERE id=$id;" $this.DB $this.Sqlite
        $this.WriteLog("[DONE] ID $id")
      } else {
        Start-Sleep -Milliseconds 200
      }
    }
    $this.WriteLog('[STOP] session ending')
  }
}

$py = [Pywershell]::new($Dir,$SessionName)
$py.Start()