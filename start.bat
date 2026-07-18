@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    Narra · 叙界                            ║
echo ║              让每一个故事，都拥有自己的世界。                ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║  后端服务: http://127.0.0.1:8005                           ║
echo ║  前端服务: http://127.0.0.1:3000                           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 📋 检查端口占用...
netstat -ano | findstr ":8005" >nul
if %errorlevel%==0 (
    echo   ⚠ 端口 8005 被占用，尝试释放...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8005"') do (
        taskkill /f /pid %%a >nul 2>&1
    )
    echo   ✓ 已释放端口 8005
    timeout /t 2 /nobreak >nul
)

echo.
echo 📦 启动服务...
echo.

echo 🚀 启动后端服务...
start "Narra Backend" /D "%~dp0" cmd /c "python -m uvicorn interfaces.main:app --host 127.0.0.1 --port 8005 --reload"
echo   后端服务已启动...

echo.
echo 🚀 启动前端服务...
start "Narra Frontend" /D "%~dp0frontend" cmd /c "npm run dev"
echo   前端服务已启动...

echo.
echo 🎉 服务启动完成！
echo    后端 API: http://127.0.0.1:8005
echo    前端页面: http://127.0.0.1:3000
echo.
echo 按任意键退出...
pause >nul
