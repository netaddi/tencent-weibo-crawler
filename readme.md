# 腾讯微博备份图片下载器

## 效果

下载备份里的所有图片到当前目录里的`img`文件夹下，并替换html文件里的链接为本地图片地址。

## 使用对象

从腾讯微博获得的html备份文件。

## 使用方法

在 python3 下运行

```bash
python3 main.py 备份html文件路径
```

需要安装依赖lxml

```bash
python3 -m pip install lxml
```
