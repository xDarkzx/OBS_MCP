@echo off
setlocal enabledelayedexpansion

echo.
echo  ============================================
echo   OBS-MCP - One-Click Installer
echo   AI-powered stream and recording control for OBS Studio
echo  ============================================
echo.

:: ---- Check Python ----
echo [1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  Python is not installed or not in PATH.
    echo.
    set /p INSTALL_PY="  Would you like to install Python via winget? (y/n): "
    if /i "!INSTALL_PY!"=="y" (
        echo.
        echo  Installing Python 3.12 via winget...
        winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        if !errorlevel! neq 0 (
            echo.
            echo  ERROR: winget install failed.
            echo  Download manually from: https://www.python.org/downloads/
            echo.
            pause
            exit /b 1
        )
        echo.
        echo  Python installed! You need to CLOSE and REOPEN this terminal,
        echo  then run install.bat again so Python is in your PATH.
        echo.
        pause
        exit /b 0
    ) else (
        echo.
        echo  OBS-MCP requires Python 3.10+ to run.
        echo  Install it and come back!
        echo.
        echo  Download from: https://www.python.org/downloads/
        echo  IMPORTANT: Check "Add Python to PATH" during installation!
        echo.
        pause
        exit /b 1
    )
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo   Found Python %PYVER%

:: Verify Python >= 3.10
for /f %%m in ('python -c "import sys; print(sys.version_info.minor)"') do set PY_MINOR=%%m
for /f %%M in ('python -c "import sys; print(sys.version_info.major)"') do set PY_MAJOR=%%M
if !PY_MAJOR! lss 3 (
    echo.
    echo  ERROR: Python 3.10+ is required, but you have Python %PYVER%
    echo  Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
if !PY_MAJOR! equ 3 if !PY_MINOR! lss 10 (
    echo.
    echo  ERROR: Python 3.10+ is required, but you have Python %PYVER%
    echo  Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: ---- Install obs-mcp ----
:: Warn if running inside a virtual environment
if defined VIRTUAL_ENV (
    echo.
    echo  WARNING: You are inside a virtual environment.
    echo  obs-mcp should be installed globally so Claude Desktop can find it.
    echo  Deactivate your venv first, or run: pip install obs-mcp outside of it.
    echo.
    pause
    exit /b 1
)

:: Check if pip is available
echo.
echo [2/5] Installing obs-mcp...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   pip not found, installing pip...
    python -m ensurepip --upgrade >nul 2>&1
    if !errorlevel! neq 0 (
        echo.
        echo  ERROR: pip is not installed and ensurepip failed.
        echo  Try reinstalling Python with pip enabled.
        echo.
        pause
        exit /b 1
    )
)

:: Install from local directory (not on PyPI yet)
pushd "%~dp0"
python -m pip install -e .
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: pip install failed. Try running as administrator,
    echo  or run manually: python -m pip install -e .
    echo.
    pause
    exit /b 1
)
popd
echo   obs-mcp installed successfully!

:: Verify the 'obs-mcp' command actually resolves on PATH - Claude Desktop
:: runs whatever 'obs-mcp' resolves to in a fresh shell, which may not be
:: what this script just installed if another Python install shadows it.
where obs-mcp >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo   NOTE: 'obs-mcp' isn't resolving on PATH yet in this session.
    echo   Close and reopen your terminal before asking Claude to use it -
    echo   Claude Desktop launches commands using your normal PATH, so if
    echo   it doesn't resolve here, it won't resolve there either.
)

:: ---- Configure Claude Desktop ----
echo.
echo [3/5] Configuring Claude Desktop...

set "CONFIG_DIR=%APPDATA%\Claude"
set "CONFIG_FILE=%CONFIG_DIR%\claude_desktop_config.json"

set /p CONFIGURE_CLAUDE="  Configure Claude Desktop for OBS-MCP? (y/n): "
if /i not "!CONFIGURE_CLAUDE!"=="y" (
    echo   Skipped. See docs/INSTALLATION.md for manual setup.
    goto :skip_config
)

if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

if exist "%CONFIG_FILE%" (
    findstr /c:"\"obs\"" "%CONFIG_FILE%" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   Claude Desktop config already has an obs entry - skipping.
        goto :skip_config
    )
    copy "%CONFIG_FILE%" "%CONFIG_FILE%.bak" >nul 2>&1
    echo   Backed up existing config to: %CONFIG_FILE%.bak
    echo.
    echo   Found existing Claude Desktop config at:
    echo   %CONFIG_FILE%
    echo.
    echo   You need to MANUALLY add this inside your "mcpServers" block:
    echo.
    echo     "obs": {
    echo       "command": "obs-mcp",
    echo       "env": {
    echo         "OBS_HOST": "localhost",
    echo         "OBS_PORT": "4455",
    echo         "OBS_PASSWORD": ""
    echo       }
    echo     }
    echo.
    echo   Opening the config file for you...
    notepad "%CONFIG_FILE%"
    goto :skip_config
)

(
echo {
echo   "mcpServers": {
echo     "obs": {
echo       "command": "obs-mcp",
echo       "env": {
echo         "OBS_HOST": "localhost",
echo         "OBS_PORT": "4455",
echo         "OBS_PASSWORD": ""
echo       }
echo     }
echo   }
echo }
) > "%CONFIG_FILE%"
echo   Created Claude Desktop config at:
echo   %CONFIG_FILE%

:skip_config

:: ---- Configure LM Studio ----
:: LM Studio's mcp.json uses the exact same {"mcpServers": {...}} shape as
:: Claude Desktop's config, just a different file location.
echo.
echo [4/5] Configuring LM Studio...

set "LMSTUDIO_CONFIG_DIR=%USERPROFILE%\.lmstudio"
set "LMSTUDIO_CONFIG_FILE=%LMSTUDIO_CONFIG_DIR%\mcp.json"

set /p CONFIGURE_LMSTUDIO="  Configure LM Studio for OBS-MCP? (y/n): "
if /i not "!CONFIGURE_LMSTUDIO!"=="y" (
    echo   Skipped. See docs/INSTALLATION.md for manual setup.
    goto :skip_lmstudio_config
)

if not exist "%LMSTUDIO_CONFIG_DIR%" mkdir "%LMSTUDIO_CONFIG_DIR%"

if exist "%LMSTUDIO_CONFIG_FILE%" (
    findstr /c:"\"obs\"" "%LMSTUDIO_CONFIG_FILE%" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   LM Studio config already has an obs entry - skipping.
        goto :skip_lmstudio_config
    )
    copy "%LMSTUDIO_CONFIG_FILE%" "%LMSTUDIO_CONFIG_FILE%.bak" >nul 2>&1
    echo   Backed up existing config to: %LMSTUDIO_CONFIG_FILE%.bak
    echo.
    echo   Found existing LM Studio config at:
    echo   %LMSTUDIO_CONFIG_FILE%
    echo.
    echo   You need to MANUALLY add this inside your "mcpServers" block:
    echo.
    echo     "obs": {
    echo       "command": "obs-mcp",
    echo       "env": {
    echo         "OBS_HOST": "localhost",
    echo         "OBS_PORT": "4455",
    echo         "OBS_PASSWORD": ""
    echo       }
    echo     }
    echo.
    echo   Opening the config file for you...
    notepad "%LMSTUDIO_CONFIG_FILE%"
    goto :skip_lmstudio_config
)

(
echo {
echo   "mcpServers": {
echo     "obs": {
echo       "command": "obs-mcp",
echo       "env": {
echo         "OBS_HOST": "localhost",
echo         "OBS_PORT": "4455",
echo         "OBS_PASSWORD": ""
echo       }
echo     }
echo   }
echo }
) > "%LMSTUDIO_CONFIG_FILE%"
echo   Created LM Studio config at:
echo   %LMSTUDIO_CONFIG_FILE%

:skip_lmstudio_config

:: ---- Done ----
echo.
echo [5/5] Done!
echo.
echo  ============================================
echo   SETUP COMPLETE!
echo  ============================================
echo.
echo  Next steps:
echo.
echo   1. Open OBS Studio
echo   2. Enable the WebSocket server:
echo      Tools ^> WebSocket Server Settings ^> Enable WebSocket server
echo      (default port 4455 - if you set a password there, put it in
echo      OBS_PASSWORD in your AI client's config)
echo   3. Restart Claude Desktop / LM Studio (whichever you configured, if open)
echo   4. Ask your AI: "What OBS scenes do I have?"
echo.
echo  OBS Studio must be open with the WebSocket server enabled for MCP to work.
echo.
echo  Docs: https://github.com/xDarkzx/OBS_MCP
echo  If this is useful to you, a star on GitHub helps other people find it!
echo  ============================================
echo.
pause
