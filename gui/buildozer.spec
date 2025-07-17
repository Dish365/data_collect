[app]
title = Research Data Collector
package.name = researchcollector
package.domain = org.research

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json,txt,md
source.include_patterns = kv/*,screens/*,services/*,widgets/*,*.py,*.kv,*.json

version = 1.0.0

# Main entry point
source.main = main

# Requirements - updated to match your requirements.txt
requirements = python3,kivy==2.3.1,kivymd==1.2.0,pillow,requests,pandas,numpy,matplotlib,peewee,plyer,humanize

# Android specific
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,CAMERA,ACCESS_NETWORK_STATE,WAKE_LOCK
android.api = 31
android.minapi = 21
android.ndk = 23b
android.accept_sdk_license = True
android.arch = arm64-v8a
android.allow_backup = True
android.orientation = portrait

# Android build options
android.gradle_dependencies = 'androidx.webkit:webkit:1.4.0'
android.add_compile_options = org
android.add_gradle_repositories = mavenCentral()
android.add_gradle_dependencies = 'androidx.webkit:webkit:1.4.0'

# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.7.0

[buildozer]
log_level = 2
warn_on_root = 1 