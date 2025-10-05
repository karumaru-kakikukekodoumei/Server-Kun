# AI-KUN Environment Setup Script for Windows

# --- Configuration ---
$python_major_version = 3
$python_minor_version = 8

# --- Helper Functions ---

# Function to print a message with a specific color
function Write-Host-Colored {
    param(
        [string]$Message,
        [string]$Color
    )
    Write-Host $Message -ForegroundColor $Color
}

# --- Main Script ---

Write-Host-Colored "Starting AI-KUN environment setup..." "Cyan"
Write-Host "This script will guide you through the setup process."
Write-Host "--------------------------------------------------"
""

# 1. Check for Python
Write-Host-Colored "[Step 1/5] Checking for Python..." "Yellow"
$python_executable = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $python_executable) {
    Write-Host-Colored "Error: Python is not installed or not found in your PATH." "Red"
    Write-Host-Colored "Please install Python $($python_major_version).$($python_minor_version) or higher from https://www.python.org/ and ensure it's added to your PATH." "Red"
    exit 1
}

$version_string = (python --version)
$version_parts = $version_string.Split(" ")[1].Split(".")
$major = [int]$version_parts[0]
$minor = [int]$version_parts[1]

if (($major -lt $python_major_version) -or ($major -eq $python_major_version -and $minor -lt $python_minor_version)) {
    Write-Host-Colored "Error: Your Python version is $major.$minor. AI-KUN requires Python $($python_major_version).$($python_minor_version) or higher." "Red"
    Write-Host-Colored "Please upgrade your Python installation." "Red"
    exit 1
}

Write-Host-Colored "✓ Python $($major).$($minor) found." "Green"
""

# 2. Check for Juman++ (Recommended)
Write-Host-Colored "[Step 2/5] Checking for Juman++ (Recommended)..." "Yellow"
$juman_executable = Get-Command jumanpp -ErrorAction SilentlyContinue
if ($null -eq $juman_executable) {
    Write-Host-Colored "⚠ Warning: Juman++ is not found in your PATH." "Yellow"
    Write-Host-Colored "Juman++ is recommended for better Japanese morphological analysis, which improves AI accuracy." "Yellow"
    Write-Host-Colored "The bot will work without it, but with potentially lower accuracy." "Yellow"
    Write-Host-Colored "Installation guide: https://github.com/ku-nlp/jumanpp" "Yellow"
} else {
    Write-Host-Colored "✓ Juman++ found." "Green"
}
""

# 3. Create Virtual Environment
Write-Host-Colored "[Step 3/5] Creating Python virtual environment..." "Yellow"
if (Test-Path -Path ".venv") {
    Write-Host-Colored "Virtual environment '.venv' already exists. Skipping creation." "Green"
} else {
    python -m venv .venv
    if ($?) {
        Write-Host-Colored "✓ Virtual environment created successfully." "Green"
    } else {
        Write-Host-Colored "Error: Failed to create virtual environment." "Red"
        exit 1
    }
}
""

# 4. Install Dependencies
Write-Host-Colored "[Step 4/5] Installing Python dependencies from requirements.txt..." "Yellow"
Write-Host "This may take a few minutes..."
$pip_executable = Join-Path ".venv" "Scripts" "pip.exe"
& $pip_executable install -r requirements.txt
if ($?) {
    Write-Host-Colored "✓ Dependencies installed successfully." "Green"
} else {
    Write-Host-Colored "Error: Failed to install dependencies. Please check the output above for errors." "Red"
    Write-Host-Colored "You can try running the following command manually:" "Red"
    Write-Host-Colored ".\.venv\Scripts\pip.exe install -r requirements.txt" "Red"
    exit 1
}
""

# 5. Create .env file
Write-Host-Colored "[Step 5/5] Setting up .env file..." "Yellow"
if (Test-Path -Path ".env") {
    Write-Host-Colored "✓ .env file already exists. Skipping creation." "Green"
} else {
    $token = Read-Host -Prompt "Please enter your Discord Bot Token"
    if ([string]::IsNullOrWhiteSpace($token)) {
        Write-Host-Colored "Error: Token cannot be empty." "Red"
        Write-Host-Colored "Please run the script again and provide a valid token." "Red"
        exit 1
    }
    $env_content = "DISCORD_BOT_TOKEN=`"$token`""
    Set-Content -Path ".env" -Value $env_content
    if ($?) {
        Write-Host-Colored "✓ .env file created successfully." "Green"
    } else {
        Write-Host-Colored "Error: Failed to create .env file." "Red"
        exit 1
    }
}
""

Write-Host-Colored "--------------------------------------------------" "Cyan"
Write-Host-Colored "🎉 AI-KUN setup is complete! 🎉" "Green"
Write-Host-Colored "--------------------------------------------------" "Cyan"
""
Write-Host-Colored "Next Steps:", "White"
Write-Host "1. Activate the virtual environment by running this command in your terminal:"
Write-Host-Colored "   .\.venv\Scripts\Activate.ps1" "Magenta"
""
Write-Host "2. Follow the usage instructions in README.md to start using AI-KUN."
Write-Host "   Recommended commands:"
Write-Host-Colored "   # To gather conversation data from your server" "Gray"
Write-Host-Colored "   python src/main.py research" "Magenta"
""
Write-Host-Colored "   # To train the AI model (fine-tuning)" "Gray"
Write-Host-Colored "   python src/main.py learning" "Magenta"
""
Write-Host-Colored "   # To run the bot" "Gray"
Write-Host-Colored "   python src/main.py run" "Magenta"
""
Write-Host "For more details, please refer to README.md."
""