# =============================================
#     MoneyPrinterTurbo Launcher - PowerShell
#     ?? ??? CUDA + ????? ?????
# =============================================

# ????? ??? UTF-8 ???????
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "     MoneyPrinterTurbo Launcher" -ForegroundColor Green
Write-Host "     (PowerShell Edition - CUDA Ready)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# ?????? ??????
$CurrentDir = $PSScriptRoot
if (-not $CurrentDir) { $CurrentDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $CurrentDir) { $CurrentDir = Get-Location }

Write-Host "?? ?????? ??????: " -NoNewline
Write-Host $CurrentDir -ForegroundColor Yellow

# ==================== ????? ???????? ====================
$FFmpegPath     = Join-Path $CurrentDir "lib\ffmpeg\ffmpeg-7.0-essentials_build\ffmpeg.exe"
$ImageMagickPath = Join-Path $CurrentDir "lib\imagemagick\ImageMagick-7.1.1-29-portable-Q16-x64\magick.exe"
$PythonPath     = Join-Path $CurrentDir "lib\python\python.exe"
$MainScript     = Join-Path $CurrentDir "MoneyPrinterTurbo\main.py"

Write-Host "`n?? ?????? ?? ????????:" -ForegroundColor Cyan

# ==================== ??? ??????? ====================
$ErrorCount = 0

function Test-File {
    param([string]$Path, [string]$Name)
    if (Test-Path $Path) {
        Write-Host "? $Name ?????" -ForegroundColor Green
        return $true
    } else {
        Write-Host "? $Name ??? ?????: " -NoNewline -ForegroundColor Red
        Write-Host $Path
        return $false
    }
}

$AllGood = $true

if (-not (Test-File $FFmpegPath "FFmpeg")) { $AllGood = $false; $ErrorCount++ }
if (-not (Test-File $ImageMagickPath "ImageMagick")) { $AllGood = $false; $ErrorCount++ }
if (-not (Test-File $PythonPath "Python")) { $AllGood = $false; $ErrorCount++ }
if (-not (Test-File $MainScript "main.py")) { $AllGood = $false; $ErrorCount++ }

if (-not $AllGood) {
    Write-Host "`n??  ???? $ErrorCount ????? ?? ???????." -ForegroundColor Red
    Write-Host "???? ?????? ?? ???? ???? ???????? ?? ?????? ??????." -ForegroundColor Yellow
    pause
    exit 1
}

# ==================== ??? ??? CUDA ====================
Write-Host "`n?? ??? ??? CUDA ?? FFmpeg..." -ForegroundColor Cyan

$FFmpegVersion = & $FFmpegPath -version 2>&1
if ($FFmpegVersion -match "cuda|nvenc|cuvid") {
    Write-Host "? FFmpeg ???? ?? ??? CUDA (NVENC)" -ForegroundColor Green
} else {
    Write-Host "??  FFmpeg ???? ???? CUDA (??????? CPU ???)" -ForegroundColor Yellow
    Write-Host "   ?????: ??? ???? FFmpeg-full ?? CUDA" -ForegroundColor Gray
}

Write-Host "`n?? ???? ????? MoneyPrinterTurbo..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# ==================== ????? ???????? ====================
try {
    & $PythonPath $MainScript
    
    Write-Host "`n=============================================" -ForegroundColor Cyan
    Write-Host "? ????? ??????? ?????" -ForegroundColor Green
} 
catch {
    Write-Host "`n? ??? ??? ????? ???????:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host "`n???? ?? ????? ???????..." -ForegroundColor Gray
pause