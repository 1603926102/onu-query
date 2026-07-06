@echo off
chcp 65001 >nul
echo ======================================================
echo   未注册光猫查询工具 - Buildozer APK 编译脚本
echo   (在 Linux 上运行，Windows 请用 WSL)
echo ======================================================
echo.
echo 当前环境似乎没有编译工具链（WSL/Docker/Java 均未找到）
echo.
echo 建议方案：
echo.
echo   方案 A【推荐 - 10分钟搞定】
echo   把 workspace-android 整个文件夹上传到 GitHub，
echo   在 GitHub Actions 里点一次构建，自动产出 APK：
echo   1. 访问 https://github.com/new 创建仓库
echo   2. 上传 workspace-android 文件夹所有内容
echo   3. Settings → Actions → 勾选 Read/write permissions
echo   4. Actions → "Build Android APK" → Run workflow
echo   5. 等 10 分钟，在 Artifacts 下载 .apk
echo.
echo   方案 B【手机端编译】
echo   在安卓手机上安装 Termux（应用商店搜索"Termux"），
echo   在 Termux 里运行：
echo     pkg update && pkg install python git
echo     pip install buildozer kivy requests pillow
echo     git clone <你的仓库地址>
echo     cd onu-query && buildozer android debug
echo.
echo   方案 C【本地 WSL】（需要管理员权限）
echo     wsl --install
echo   重启电脑后，再运行本脚本的 WSL 构建流程
echo.
echo 按任意键退出...
pause >nul
