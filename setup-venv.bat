@echo off
echo 🐍 Setting up Python Virtual Environment for Certification Coupon Hunter

REM Check Python version
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install development dependencies
echo Installing development dependencies...
pip install -r requirements-dev.txt

REM Install CDK dependencies
echo Installing CDK dependencies...
cd cdk
pip install -r requirements.txt
cd ..

REM Install Lambda dependencies locally for development
echo Installing Lambda dependencies for local development...
pip install boto3 requests beautifulsoup4 lxml

echo ✅ Virtual environment setup complete!
echo.
echo 📝 To activate the environment in the future:
echo    venv\Scripts\activate.bat
echo.
echo 📝 To deactivate:
echo    deactivate
echo.
echo 🧪 Ready to test:
echo    python debug_local.py

pause