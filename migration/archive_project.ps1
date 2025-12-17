$ErrorActionPreference = "Stop"

$projectRoot = Get-Location
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$archiveName = "tamozh_service_migration_$timestamp.zip"
$destinationPath = Join-Path $projectRoot $archiveName
$stagingDir = Join-Path $projectRoot "temp_staging_$timestamp"

Write-Host "Starting project archiving..."
Write-Host "Project Root: $projectRoot"
Write-Host "Archive Name: $archiveName"

# Define exclusions (Regex patterns for relative paths)
$exclusions = @(
    "\\node_modules\\",
    "\\__pycache__\\",
    "\\.git\\",
    "\\.vscode\\",
    "\\.idea\\",
    "\\backend\\venv\\",
    "\\postgres_data\\",
    "\\_old\\",
    "\\.log$",
    "\\.zip$",
    "\\temp_verify_archive\\",
    "\\.next\\",
    "\\dist\\",
    "\\.pytest_cache\\" # Exclude verification folder
)

# Create staging directory
New-Item -ItemType Directory -Force -Path $stagingDir | Out-Null

# Get all files recursively
$files = Get-ChildItem -Path $projectRoot -Recurse -File

Write-Host "Scanning and copying files..."

foreach ($file in $files) {
    $filePath = $file.FullName
    $relativePath = $filePath.Substring($projectRoot.Path.Length)
    
    # Check exclusions
    $exclude = $false
    foreach ($pattern in $exclusions) {
        if ($relativePath -match $pattern) {
            $exclude = $true
            break
        }
    }
    
    if (-not $exclude) {
        # Construct destination path in staging
        $destPath = Join-Path $stagingDir $relativePath
        $destDir = Split-Path $destPath -Parent
        
        # Create directory if needed
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Force -Path $destDir | Out-Null
        }
        
        # Copy file
        Copy-Item -LiteralPath $filePath -Destination $destPath
    }
}

Write-Host "Files copied to staging area."

# Create archive from staging directory
# We zip the CONTENT of the staging directory, so the archive root corresponds to project root
Write-Host "Creating archive..."
Compress-Archive -Path "$stagingDir\*" -DestinationPath $destinationPath -Force

# Cleanup
Write-Host "Cleaning up staging area..."
Remove-Item -Path $stagingDir -Recurse -Force

Write-Host "Archive created successfully: $destinationPath"
