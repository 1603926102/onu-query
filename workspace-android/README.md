# 未注册光猫查询工具 - 安卓版

> 基于 Kivy 框架重写，适配手机触屏操作，可打包为 Android APK

## 📱 一键打包 APK（推荐）

### 步骤

1. **把整个文件夹上传到 GitHub**
   - 在 GitHub 新建一个空白仓库（如 `onu-query`）
   - 上传本文件夹所有文件

2. **启用 GitHub Actions**
   - 访问仓库 → `Settings` → `Actions` → `General`
   - 确认 `Read and write permissions` 已勾选
   - 保存

3. **触发构建**
   - 访问仓库 → `Actions` → 点击左侧 `🤖 Build Android APK` → `Run workflow`
   - 等待约 **10~15 分钟**，完成后在 `Artifacts` 下载 `onu-query-apk`

4. **安装到手机**
   - 把 APK 传到手机，安装（首次需开启"允许安装未知来源应用"）

---

## 💻 本地构建（Linux / WSL）

```bash
# 安装编译工具链（Ubuntu）
sudo apt update
sudo apt install -y python3-pip git cmake zip unzip openjdk-17-jdk
# Android SDK（Buildozer 自动下载，或手动指定 ANDROID_HOME）

# 克隆代码
pip install buildozer kivy requests pillow
buildozer init
# 把 main.py 和 icon.png 放入项目
buildozer -v android debug
```

---

## 🎮 功能说明

| 功能 | 说明 |
|------|------|
| OLT 设备名称 | 支持模糊搜索，如"体育馆" |
| SN 码 | 留空查全部 / 输入后取后4位精确匹配 |
| 命中高亮 | 命中的 ONU 行显示绿色背景 |
| 并行查询 | 多 OLT 时自动并发加速 |
| 触屏适配 | 大按钮、大字号，安卓原生体验 |

---

## 📂 文件说明

```
workspace-android/
├── main.py          # Kivy 主程序（移动端 UI）
├── buildozer.spec   # 打包配置
├── icon.png         # 应用图标（512x512）
├── requirements.txt # Python 依赖
├── README.md        # 本文件
└── .github/
    └── workflows/
        └── build.yml  # GitHub Actions 自动构建脚本
```
