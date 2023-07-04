from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import urllib.request
import threading

app = Flask(__name__)

# 设置共享文件夹路径
shared_folder = "/tmp"

# 用于存储下载任务的字典，键为下载链接，值为目标文件夹路径
download_tasks = {}

@app.route("/")
def index():
    # 获取共享文件夹中的文件和文件夹列表
    files = []
    folders = []
    for item in os.listdir(shared_folder):
        item_path = os.path.join(shared_folder, item)
        if os.path.isfile(item_path):
            files.append(item)
        elif os.path.isdir(item_path):
            folders.append(item)
    
    return render_template("index.html", files=files, folders=folders)

@app.route("/folder/<path:folder>")
def show_folder(folder):
    # 构建文件夹的绝对路径
    folder_path = os.path.join(shared_folder, folder)
    
    # 检查文件夹是否存在
    if not os.path.isdir(folder_path):
        return "文件夹不存在"
    
    # 获取文件夹下的子文件夹和文件
    subfolders = []
    files = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            subfolders.append(item)
        else:
            files.append(item)
    
    # 返回上一级目录的路径
    parent_folder = ""
    if folder != "":
        parent_folder = os.path.dirname(folder)
    
    return render_template("folder.html", current_folder=folder, parent_folder=parent_folder, subfolders=subfolders, files=files)

@app.route("/upload", methods=["POST"])
def upload():
    # 获取上传的文件和目标文件夹
    file = request.files["file"]
    target_folder = request.form["folder"]
    
    # 拼接目标文件夹路径
    target_folder_path = os.path.join(shared_folder, target_folder)
    
    # 检查目标文件夹是否存在，若不存在则创建
    if not os.path.exists(target_folder_path):
        os.makedirs(target_folder_path)
    
    # 保存上传的文件到目标文件夹
    file.save(os.path.join(target_folder_path, file.filename))
    
    return redirect(url_for("index"))

def download_file(url, target_folder):
    try:
        # 从下载链接中提取文件名
        filename = url.split("/")[-1]
        
        # 拼接目标文件路径
        target_file_path = os.path.join(shared_folder, target_folder, filename)
        
        # 下载文件并保存到目标文件夹
        urllib.request.urlretrieve(url, target_file_path)
    except Exception as e:
        print("下载失败:", e)

@app.route("/download", methods=["POST"])
def start_download():
    form_data = request.values
    # 获取下载链接和目标文件夹
    url = form_data.get("url")
    target_folder = form_data.get("folder")
    
    # 启动下载线程
    download_thread = threading.Thread(target=download_file, args=(url, target_folder))
    download_thread.start()
    
    # 将下载任务添加到任务字典中
    download_tasks[url] = target_folder
    
    return jsonify({"message": "下载已启动"})
    

@app.route("/tasks")
def get_tasks():
    return jsonify(download_tasks)

@app.route("/download/<path:filename>")
def download(filename):
    # 构建文件的相对路径
    relative_path = os.path.join(request.args.get('folder', ''), filename)
    
    # 直接返回文件供下载
    return send_from_directory(directory=shared_folder, path=relative_path, as_attachment=True)

if __name__ == "__main__":
    app.run(port=8888)

