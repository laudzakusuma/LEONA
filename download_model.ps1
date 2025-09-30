# ============================================
# LEONA Simple Model Downloader
# No bugs, just works!
# ============================================

Clear-Host

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "    LEONA MODEL DOWNLOADER (SIMPLE)"        -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Create directory
$modelsDir = "data\models"
New-Item -ItemType Directory -Path $modelsDir -Force | Out-Null

# Show menu
Write-Host "Available Models:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. TinyLLaMA 1.1B (638 MB) - FASTEST" -ForegroundColor White
Write-Host "2. Qwen 1.8B (1.2 GB) - RECOMMENDED" -ForegroundColor Green  
Write-Host "3. Phi-2 2.7B (1.6 GB) - BALANCED" -ForegroundColor White
Write-Host "4. Mistral 7B (4.1 GB) - BEST QUALITY" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Select model (1-4)"

# Define models
$modelURL = ""
$modelFile = ""
$modelName = ""

switch ($choice) {
    "1" {
        $modelName = "TinyLLaMA 1.1B"
        $modelURL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        $modelFile = "tinyllama-1.1b-chat.gguf"
    }
    "2" {
        $modelName = "Qwen 1.8B"
        $modelURL = "https://modelscope.cn/models/qwen/Qwen1.5-1.8B-Chat-GGUF/resolve/main/qwen1_5-1_8b-chat-q4_k_m.gguf"
        $modelFile = "qwen-1.8b-chat.gguf"
    }
    "3" {
        $modelName = "Phi-2 2.7B"
        $modelURL = "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"
        $modelFile = "phi-2.gguf"
    }
    "4" {
        $modelName = "Mistral 7B"
        $modelURL = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        $modelFile = "mistral-7b-instruct.gguf"
    }
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
        pause
        exit
    }
}

$outputPath = Join-Path $modelsDir $modelFile

Write-Host ""
Write-Host "Downloading: $modelName" -ForegroundColor Green
Write-Host "Destination: $outputPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please wait... This may take 5-30 minutes" -ForegroundColor Yellow
Write-Host ""

# Download
try {
    $ProgressPreference = 'Continue'
    Invoke-WebRequest -Uri $modelURL -OutFile $outputPath
    
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "   DOWNLOAD COMPLETE!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Model saved to: $outputPath" -ForegroundColor Cyan
    
    $fileSize = (Get-Item $outputPath).Length / 1MB
    Write-Host "File size: $($fileSize.ToString('N1')) MB" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Run: python leona_main.py" -ForegroundColor White
    Write-Host "2. Open: http://localhost:8000" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "ERROR: Download failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Try:" -ForegroundColor Yellow
    Write-Host "1. Check your VPN is connected" -ForegroundColor White
    Write-Host "2. Run the script again" -ForegroundColor White
    Write-Host ""
}

pause