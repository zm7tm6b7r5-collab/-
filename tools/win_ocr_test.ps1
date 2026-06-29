# Windows 10/11 自带 OCR API 测试
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Foundation.Metadata.ApiInformation, Windows.Foundation, ContentType=WindowsRuntime]

# Load OCR
$ocrEngine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if (-not $ocrEngine) {
    Write-Output "Falling back to Chinese Simplified..."
    $lang = New-Object Windows.Globalization.Language("zh-Hans")
    $ocrEngine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
}

Write-Output "OCR Engine available languages:"
$ocrEngine.RecognizerLanguage.DisplayName

# Test image
$imgPath = "C:\Users\AUSU\Desktop\图片2\IMG_8774.JPG"
$file = Get-Item $imgPath

# Load image using Windows Storage
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
$task = [Windows.Storage.StorageFile]::GetFileFromPathAsync($imgPath)
$task.Wait()
$storageFile = $task.GetResults()

# Get stream
$streamTask = $storageFile.OpenReadAsync()
$streamTask.Wait()
$stream = $streamTask.GetResults()

# Create bitmap
$bitmapTask = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)
$bitmapTask.Wait()
$bitmap = $bitmapTask.GetResults()

# Get software bitmap
$getSoftTask = $bitmap.GetSoftwareBitmapAsync()
$getSoftTask.Wait()
$softBmp = $getSoftTask.GetResults()

# OCR
$ocrTask = $ocrEngine.RecognizeAsync($softBmp)
$ocrTask.Wait()
$result = $ocrTask.GetResults()

Write-Output "`n=== OCR Result ==="
Write-Output "Lines: $($result.Lines.Count)"
foreach ($line in $result.Lines) {
    $lineText = ""
    foreach ($word in $line.Words) {
        $lineText += $word.Text + " "
    }
    Write-Output "  $lineText"
}
