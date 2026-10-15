# Build script for Windows
# Run this in PowerShell as Administrator

Write-Host "🚀 Building Brand Engine Installer" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Step 1: Install/Update required packages
Write-Host "`n📦 Installing required packages..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Step 2: Build the executable
Write-Host "`n🔨 Building executable..." -ForegroundColor Yellow
python build_exe.py

# Step 3: Download required dependencies (if not already downloaded)
Write-Host "`n📥 Checking for required dependencies..." -ForegroundColor Yellow

# Visual C++ Redistributable
$vcRedistUrl = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
$vcRedistFile = "vc_redist.x64.exe"
if (-not (Test-Path $vcRedistFile)) {
    Write-Host "Downloading Visual C++ Redistributable..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $vcRedistUrl -OutFile $vcRedistFile
}

# .NET Framework (optional - only if needed)
# $dotNetUrl = "https://download.microsoft.com/download/6/E/4/6E48E8AB-DC00-419E-9704-06DD46E5F81D/ndp48-x86-x64-allos-enu.exe"
# $dotNetFile = "ndp48-x86-x64-allos-enu.exe"
# if (-not (Test-Path $dotNetFile)) {
#     Write-Host "Downloading .NET Framework..." -ForegroundColor Yellow
#     Invoke-WebRequest -Uri $dotNetUrl -OutFile $dotNetFile
# }

# Step 4: Build installer using Inno Setup
Write-Host "`n📦 Building installer..." -ForegroundColor Yellow

# Check if Inno Setup is installed
$innoPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (Test-Path $innoPath) {
    & $innoPath installer_script.iss
    Write-Host "`n✅ Installer created successfully!" -ForegroundColor Green
    Write-Host "📁 Location: installer/BrandEngine_Setup.exe" -ForegroundColor Green
} else {
    Write-Host "`n❌ Inno Setup not found!" -ForegroundColor Red
    Write-Host "Please install Inno Setup from: https://jrsoftware.org/isdl.php" -ForegroundColor Red
    Write-Host "Or download the portable version." -ForegroundColor Red
}

Write-Host "`n🎉 Build complete!" -ForegroundColor Cyan