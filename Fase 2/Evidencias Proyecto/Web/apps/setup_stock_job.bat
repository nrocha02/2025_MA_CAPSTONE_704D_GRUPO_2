@echo off
REM Script para programar el job diario de stock en Windows Task Scheduler
REM Ejecutar como administrador

setlocal

echo ================================================
echo CONFIGURANDO JOB DIARIO DE STOCK - CORDILLERA PETS
echo ================================================

REM --- Configuración de rutas (AJUSTA SI CAMBIAN)
set "PYTHON_PATH=C:\Users\Caro\Documents\2025_MA_CAPSTONE_704D_GRUPO_2\Fase 2\Evidencias Proyecto\Web\.venv\Scripts\python.exe"
set "PROJECT_PATH=C:\Users\Caro\Documents\2025_MA_CAPSTONE_704D_GRUPO_2\Fase 2\Evidencias Proyecto\Web"
set "ADMIN_EMAIL=cordillerapetschile@gmail.com"
set "RUNNER_PATH=%PROJECT_PATH%\apps\run_daily_stock_job.cmd"

echo Ruta Python : %PYTHON_PATH%
echo Ruta Proyecto: %PROJECT_PATH%
echo Email Admin  : %ADMIN_EMAIL%
echo.

REM --- Validaciones básicas
if not exist "%PYTHON_PATH%" (
    echo ✗ No se encontró PYTHON en: %PYTHON_PATH%
    echo   Corrige la ruta y vuelve a ejecutar.
    exit /b 1
)
if not exist "%PROJECT_PATH%" (
    echo ✗ No se encontró el proyecto en: %PROJECT_PATH%
    echo   Corrige la ruta y vuelve a ejecutar.
    exit /b 1
)

REM --- Crear runner .cmd que ejecutará la tarea (evita problemas de comillas y espacios)
echo Creando runner: %RUNNER_PATH%
> "%RUNNER_PATH%" (
    echo @echo off
    echo cd /d "%PROJECT_PATH%"
    echo "%PYTHON_PATH%" manage.py daily_stock_job --admin-email=%ADMIN_EMAIL%
)

if %errorlevel% neq 0 (
    echo ✗ No se pudo crear el runner en: %RUNNER_PATH%
    exit /b 1
)

REM --- Mostrar comando que se ejecutará (para que quede claro)
echo.
echo Comando del runner:
type "%RUNNER_PATH%"
echo.

REM --- Crear/actualizar la tarea programada
echo Creando tarea programada...
schtasks /create ^
  /tn "CordilleraPets_StockJob" ^
  /tr "\"%RUNNER_PATH%\"" ^
  /sc daily ^
  /st 10:00 ^
  /rl HIGHEST ^
  /f

if %ERRORLEVEL%==0 (
    echo.
    echo ✓ TAREA CREADA/ACTUALIZADA CORRECTAMENTE
    echo   - Nombre : CordilleraPets_StockJob
    echo   - Horario: Diario a las 10:00 AM
    echo   - Ejecuta: %RUNNER_PATH%
) else (
    echo.
    echo ✗ ERROR AL CREAR LA TAREA
    echo   Ejecuta este .bat como administrador.
    exit /b 1
)

REM --- Probar de inmediato (dry-run)
echo.
echo ¿Deseas probar el comando ahora? (s/n)
set /p RESPUESTA=

if /i "%RESPUESTA%"=="s" (
    echo.
    echo Ejecutando prueba (dry-run)...
    cd /d "%PROJECT_PATH%"
    "%PYTHON_PATH%" manage.py daily_stock_job --admin-email=%ADMIN_EMAIL% --dry-run
)

echo.
echo ================================================
echo CONFIGURACIÓN COMPLETADA
echo ================================================
pause
endlocal