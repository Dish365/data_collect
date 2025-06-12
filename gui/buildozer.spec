[app]
title = Research Data Collector
package.name = researchcollector
package.domain = org.research

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json

version = 1.0.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,requests,sqlalchemy,pandas,numpy,matplotlib,scikit-learn,nltk

# Android specific
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,CAMERA
android.api = 31
android.minapi = 21
android.ndk = 23b
android.accept_sdk_license = True
android.arch = arm64-v8a

# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.7.0

[buildozer]
log_level = 2
warn_on_root = 1 