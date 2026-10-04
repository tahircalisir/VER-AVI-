@echo off
title Yerel Veri Avcisi ve AI Asistani
cd /d "%~dp0"

echo ========================================================
echo   Yerel Veri Avcisi ve AI Asistani Baslatiliyor...
echo ========================================================
echo.

REM Python kontrolu
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bilgisayarinizda bulunamadi!
    echo Lutfen Python'in kurulu oldugundan emin olun.
    pause
    exit /b
)

echo [1/2] Gerekli Python kutuphaneleri kuruluyor...
echo (Bu islem ilk acilista internet hizina bagli olarak 1-2 dakika surebilir)
python -m pip install -r requirements.txt

echo.
echo [2/2] Arayuz baslatiliyor (Tarayicinizda acilacak)...
echo.
python -m streamlit run app.py

pause
