@echo off
cd /d "%~dp0"
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" "%~dp0start.py" %*
) else (
    where py >nul 2>nul
    if not errorlevel 1 (
        py "%~dp0start.py" %*
    ) else (
        where python >nul 2>nul
        if not errorlevel 1 (
            python "%~dp0start.py" %*
        ) else (
            echo [ERROR / 错误] Python was not found. Install Python 3.10+ and run again. / 未找到 Python，请安装 Python 3.10+ 后重试。
            pause
            exit /b 1
        )
    )
)
