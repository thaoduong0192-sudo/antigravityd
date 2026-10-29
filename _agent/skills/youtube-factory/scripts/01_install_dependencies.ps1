Write-Host "Checking prerequisites..."

# Check Python
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    Write-Host "Python is installed." -ForegroundColor Green
} else {
    Write-Host "Python is not installed. Please install Python 3.10+ from https://www.python.org/downloads/ and ensure it is added to PATH." -ForegroundColor Red
    exit 1
}

# Check UV
if (Get-Command "uv" -ErrorAction SilentlyContinue) {
    Write-Host "UV is installed." -ForegroundColor Green
} else {
    Write-Host "UV is not installed. Installing UV..." -ForegroundColor Yellow
    pip install uv
}

# Check Chrome
$chromePath = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
$chromePath86 = "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"

if ((Test-Path $chromePath) -or (Test-Path $chromePath86)) {
    Write-Host "Google Chrome is installed." -ForegroundColor Green
} else {
    Write-Host "Google Chrome not found at standard paths. Please install Chrome." -ForegroundColor Red
    exit 1
}

# Run install python packages
Write-Host "Installing Python packages..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
& "$scriptDir\02_install_python_packages.ps1"

# Install Playwright chromium
Write-Host "Installing Playwright Chromium..." -ForegroundColor Yellow
uv run playwright install chromium

Write-Host "Dependencies installed successfully!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run 03_login_notebooklm.bat" -ForegroundColor Cyan
Write-Host "2. Run 04_login_youtube.bat" -ForegroundColor Cyan
Write-Host "3. Update .env with credentials" -ForegroundColor Cyan
