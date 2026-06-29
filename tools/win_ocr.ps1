# Windows OCR API - test on one image
Add-Type -AssemblyName System.Runtime.WindowsRuntime

$imgPath = "C:\Users\AUSU\Desktop\图片2\IMG_8767.JPG"

# Load file
$fileTask = [Windows.Storage.StorageFile]::GetFileFromPathAsync($imgPath)
while (-not $fileTask.Completed) { Start-Sleep -Milliseconds 50 }
$file = $fileTask.GetResults()

# Get stream
$streamTask = $file.OpenReadAsync()
while (-not $streamTask.Completed) { Start-Sleep -Milliseconds 50 }
$stream = $streamTask.GetResults()

# Decode bitmap
$decoderTask = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)
while (-not $decoderTask.Completed) { Start-Sleep -Milliseconds 50 }
$decoder = $decoderTask.GetResults()

# Get software bitmap
$bmpTask = $decoder.GetSoftwareBitmapAsync()
while (-not $bmpTask.Completed) { Start-Sleep -Milliseconds 50 }
$bmp = $bmpTask.GetResults()

# Create OCR engine (Chinese)
$lang = New-Object Windows.Globalization.Language("zh-Hans")
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)

if (-not $engine) {
    Write-Output "Cannot create Chinese OCR engine!"
    # Try from user profile
    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
    if ($engine) {
        Write-Output "Using user profile language: $($engine.RecognizerLanguage.DisplayName)"
    }
}

if ($engine) {
    $ocrTask = $engine.RecognizeAsync($bmp)
    while (-not $ocrTask.Completed) { Start-Sleep -Milliseconds 50 }
    $result = $ocrTask.GetResults()

    Write-Output "`n=== Windows OCR Result ==="
    Write-Output "Lines: $($result.Lines.Count)"
    foreach ($line in $result.Lines) {
        $lineText = ""
        foreach ($word in $line.Words) {
            $lineText += $word.Text
        }
        Write-Output "  $lineText"
    }
} else {
    Write-Output "No OCR engine available"
}
