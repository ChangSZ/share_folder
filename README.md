# share_folder

## 功能：
- 文件夹在线共享及文件下载
- 文件上传至共享路径下的指定目录
- 通过互联网文件下载链接异步上传文件至指定目录

<br />

## 使用方法：
1. 设置共享文件夹路径
```python
    shared_folder = "/tmp"
```

1. 设置对外端口
```python
    app.run(port=8888)
```

1. 启动服务
```bash
    python3 share_folder.py
```