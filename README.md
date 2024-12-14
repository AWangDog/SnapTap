# SnapTap

## 介绍
+ 基于Python在软件层面实现的SnapTap
+ 有一个用QT做的粗制滥造的窗口
+ 理论来讲应该不会被反作弊封禁

## 启动参数
+ background : 静默启动
+ run : 启动时启用

## 未来计划
1. ~~开机自启动与打开软件自动运行~~
2. ~~支持小键盘/caps等按键~~
3. ~~添加多开检测防止出现难以预料的问题~~
4. ~~重做ui~~
5. ~~显示窗口时自动放到前台~~
6. ~~ui缺失自动补全~~(用nuitka打包代替)
7. Github自动检查更新
8. 配置切换
9. 跨平台

## 打包命令
``` batch
pip install nuitka
```
``` batch
python -m nuitka --standalone --onefile --windows-console-mode=disable "--onefile-tempdir-spec={TEMP}\SnapTap_{PID}" --mingw64 --output-dir=out --enable-plugin=pyside6 --windows-icon-from-ico=ui\icon.ico --windows-product-version=1.13.0 --remove-output --windows-uac-admin --include-data-dir=ui=ui --product-name=SnapTap --file-description=SnapTap --output-filename=SnapTap main.py
```
+ 需要的库
``` batch
pip install PySide6
pip install pynput
pip install WinKeyBoard
pip install psutil
```
