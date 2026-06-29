<#
.SYNOPSIS
    安装考研英语外刊精选系统 Windows 计划任务
.DESCRIPTION
    创建每天北京时间 18:00 执行的计划任务
    注意：需要以管理员身份运行 PowerShell
#>

$ErrorActionPreference = "Stop"

$TaskName = "KaoyanDaily"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = (Get-Command python).Source
$ScriptPath = Join-Path $ScriptDir "kaoyan_daily.py"
$LogPath = Join-Path $ScriptDir "kaoyan_daily.log"

Write-Host "=== 考研英语外刊精选系统 — 计划任务安装 ===" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
if (-not $PythonExe) {
    Write-Host "错误：未找到 Python，请先安装 Python 3" -ForegroundColor Red
    exit 1
}
Write-Host "Python: $PythonExe" -ForegroundColor Green

# 检查脚本
if (-not (Test-Path $ScriptPath)) {
    Write-Host "错误：未找到 kaoyan_daily.py" -ForegroundColor Red
    exit 1
}
Write-Host "脚本: $ScriptPath" -ForegroundColor Green

# 检查依赖
Write-Host ""
Write-Host "正在检查 Python 依赖..." -ForegroundColor Yellow
$reqPath = Join-Path $ScriptDir "requirements.txt"
if (Test-Path $reqPath) {
    & $PythonExe -m pip install -r $reqPath --quiet 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "依赖安装完成" -ForegroundColor Green
    } else {
        Write-Host "警告：依赖安装可能不完整，请手动执行: pip install -r requirements.txt" -ForegroundColor Yellow
    }
}

# 删除旧任务
Write-Host ""
Write-Host "正在清理旧任务..." -ForegroundColor Yellow
try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "旧任务已清除" -ForegroundColor Green
} catch {
    # 忽略
}

# 创建任务动作
$Action = New-ScheduledTaskAction -Execute $PythonExe `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory $ScriptDir

# 创建触发器：每天 07:00（北京时间 = UTC+8，即前一天的 23:00 UTC）
# Windows 计划任务使用本地时间
$Trigger = New-ScheduledTaskTrigger -Daily -At 18:00

# 任务配置
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

# 创建任务
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

try {
    Register-ScheduledTask -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description "考研英语外刊精选系统 — 每日自动分析并推送考研英语精选外刊" `
        -Force

    Write-Host ""
    Write-Host "计划任务安装成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "任务详情：" -ForegroundColor Cyan
    Write-Host "  - 任务名称: $TaskName"
    Write-Host "  - 执行时间: 每天 18:00"
    Write-Host "  - 日志文件: $LogPath"
    Write-Host "  - 报告输出: $ScriptDir\kaoyan_report_YYYYMMDD.md"
    Write-Host ""
    Write-Host "手动测试：在计划任务中找到 'KaoyanDaily'，右键 → 运行" -ForegroundColor Yellow
    Write-Host "或直接执行：python kaoyan_daily.py --dry-run" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "提示：首次运行前请确保已在 kaoyan_config.json 中配置：" -ForegroundColor Magenta
    Write-Host "  1. deepseek_api_key（DeepSeek API 密钥）" -ForegroundColor Magenta
    Write-Host "  2. feishu_webhook_url（飞书机器人 Webhook 地址）" -ForegroundColor Magenta

} catch {
    Write-Host "计划任务创建失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请尝试以管理员身份运行此脚本" -ForegroundColor Yellow
    exit 1
}
