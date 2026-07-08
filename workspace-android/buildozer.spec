[app]

title = 未注册光猫查询
package.name = onuquery
package.domain = org.onuquery

# 源代码目录（当前目录）
source.dir = .

# 版本号
version = 1.0.0

source.include_exts = py,png,jpg,kv

mainmodule = main

android.archs = arm64-v8a armeabi-v7a
android.api = 27
android.minapi = 21

android.permissions = INTERNET ACCESS_NETWORK_STATE

orientation = portrait

android.allow_backup = True

fullscreen = 0
