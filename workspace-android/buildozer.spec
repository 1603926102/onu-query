[app]

title = 未注册光猫查询
package.name = onuquery
package.domain = org.onuquery

source.dir = .
version = 1.0.0

source.include_exts = py,png,jpg,kv

requirements = python3,kivy,requests,pillow

android.archs = arm64-v8a
android.api = 27
android.minapi = 21

android.permissions = INTERNET,ACCESS_NETWORK_STATE

orientation = portrait
android.allow_backup = True
android.accept_sdk_license = True

fullscreen = 0
