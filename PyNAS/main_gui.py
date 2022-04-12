# coding=utf-8
import re
import os
import sys
import json
import platform
import tkinter.scrolledtext as st
from tkinter import ttk
from threading import Thread
from tkinter import filedialog
from tkinter.simpledialog import askstring
from tkinter import *
from tkinter.messagebox import showerror as error
from tkinter.messagebox import showinfo as info
from tkinter.messagebox import showwarning as warn
import ttkbootstrap
from ttkbootstrap import Style
from PyNAS.main import main as m


def main():
    cwd = os.path.dirname(__file__)
    def help():
        with open(os.path.join(cwd, "help.json"), encoding="utf-8") as f:
            helps = json.load(f)["helps"]
        for help in helps:
            info("帮助", help)
    def LICENSE():
        with open(os.path.join(cwd, "LICENSE"), encoding="utf-8") as f:
            license = f.read()
        info("关于", license)

    def check_dir():
        if not os.path.exists(directory.get()):
            error("错误", "路径不存在或不正确")
            directory.delete(0, END)
            return False
        return True

    def check_host():
        match = re.match(
            "^((2(5[0-5]|[0-4]\\d))|[0-1]?\\d{1,2})(\\.((2(5[0-5]|[0-4]\\d))|[0-1]?\\d{1,2})){3}$",
            host.get())
        if not match:
            error("错误", "服务IP格式不正确")
            host.delete(0, END)
            return False
        return True

    def check_port():
        if not port.get().isdigit():
            error("错误", "端口必须是一个数字")
            port.delete(0, END)
            return False
        if not (int(port.get()) <= 65536 or int(port.get()) >= 1):
            error("错误", "端口必须是一个数字并且在1-65536之间")
            return False
        if use_ssl.get() == 1 and int(port.get()) != 443:
            warn("警告", "当使用SSL时只能使用443端口")
            port.delete(0, END)
            port.insert(0, "443")
        return True

    def check_ftp_port():
        if not ftp_port.get().isdigit() and use_ftp == 1:
            error("错误", "ftp端口必须是一个数字")
            port.delete(0, END)
            return False

        if use_ftp == 1:
            if int(ftp_port.get()) >= 65536 or int(
                    ftp_port.get()) <= 1:
                error("错误", "ftp端口必须是一个数字并且在1-65536之间")
                return False

        if use_ftp == 1:
            if int(ftp_port.get()) == int(port.get()):
                error("错误", "ftp端口与网盘端口相等")
                return False
        return True

    def check_key():
        if not key.get():
            error("错误", "密钥为空")
            return False
        return True

    def check_ssl():
        if use_ssl == 1 and type_ssl.get() == "手动选择证书文件" and not (
                cert_file.get() or key_file.get()):
            error("错误", "你指定了手动选择证书文件但是没有把证书文件选择完整")
            return False
        return True

    def check_user():
        if not tree.get_children():
            error("错误", "未添加任何用户")
            return False
        return True

    def add_user():
        username = askstring(title="输入用户名", prompt="请输入用户名：")
        password = askstring(title="输入密码", prompt="请输入密码", show="*")
        if not (username and password):
            warn("警告", "用户名或密码未输入。请重新输入。")
            add_user()
            return
        user.append({"user": username, "password": password})

        tree.insert('', END, values=[username, "*"*len(password)])

    def callback():
        username = []
        password = []
        for i in user:
            username.append(i["user"])
            password.append(i["password"])
        args = {
            "directory": directory.get(),
            "username": username,
            "password": password,
            "host": host.get(),
            "port": port.get(),
            "ftp": bool(use_ftp.get()),
            "ftp_port": ftp_port.get(),
            "secret": key.get(),
            "ssl": bool(use_ssl.get()),
            "ssl_type": "custom" if type_ssl.get() == "手动选择证书文件" else "auto",
            "key": key_file.get(),
            "cert": cert_file.get()
        }
        if not check_dir():
            return
        if not check_host():
            return
        if not check_port():
            return
        if not check_ftp_port():
            return
        if not check_key():
            return
        if not check_ssl():
            return
        if not check_user():
            return
        s = Thread(target=m, args=(args,))
        s.start()

    def view_cert_file():
        file = filedialog.askopenfilename(
            title="选择证书文件...", defaultextension=".crt", filetypes=[
                ("crt证书文件", ".crt"), ("所有文件", ".")])
        cert_file.set(file)

    def view_key_file():
        file = filedialog.askopenfilename(
            title="选择密钥文件...", defaultextension=".key", filetypes=[
                ("crt证书文件", ".key"), ("所有文件", ".")])
        key_file.set(file)

    class Redirect():
        def __init__(self):
            # 将其备份
            self.stdoutbak = sys.stdout
            self.stderrbak = sys.stderr
            sys.stdout = self
            sys.stderr = self

        def write(self, info):
            info = info.replace("", "")
            info = info.replace("[0m", "")
            info = info.replace("[32m", "")
            info = info.replace("[36m", "")
            if "200" in info or "206" in info:
                t.insert("end", info, "success")
            elif ("302" in info) or ("304" in info) or ("308" in info):
                t.insert("end", info, "redirect")
            elif "500" in info:
                t.insert("end", info, "error")
            else:
                t.insert("end", info, "info")
            t.update()
            t.see(END)

        def restoreStd(self):
            sys.stdout = self.stdoutbak
            sys.stderr = self.stderrbak

        def flush(self):
            t.update()
            t.see(END)

    style = Style(theme="litera")
    r = Redirect()
    root_window = style.master
    root_window.title("NAS启动服务工具")
    root_window.iconbitmap(os.path.join(cwd, "static/images/favicon.ico"))
    if platform.uname()[0] == "Windows":
        root_window.state("zoomed")
    else:
        screen = os.popen("xrandr | grep current")
        cur = screen.read().split(',')[1].split(' ')
        root_window.geometry(cur[2] + cur[3] + cur[4])
    w = root_window.winfo_screenwidth()
    h = root_window.winfo_screenheight()
    root_window.attributes("-alpha", 0.9)
    menubar = Menu(root_window)
    menubar.add_command(label="帮助", command=help)
    menubar.add_command(label="关于", command=LICENSE)
    root_window.config(menu=menubar)
    input_frame = Frame(root_window)
    Label(input_frame, text="网盘路径：", font=("Times", 15)).grid(column=1, row=1)
    directory = Entry(
        input_frame)
    directory.grid(column=2, row=1)
    Label(input_frame, text="服务IP：", font=("Times", 15)).grid(column=1, row=2)
    host = Entry(input_frame)
    host.grid(column=2, row=2)
    Label(input_frame, text="服务端口：", font=("Times", 15)).grid(column=1, row=3)
    port = Entry(input_frame)
    port.grid(column=2, row=3)
    Label(input_frame, text="服务密钥：", font=("Times", 15)).grid(column=1, row=4)
    key = Entry(input_frame, show="*")
    key.grid(column=2, row=4)
    use_ftp = IntVar()
    ttkbootstrap.Radiobutton(
        input_frame,
        text="使用FTP",
        variable=use_ftp,
        value=1).grid(
        column=1,
        row=5)
    ttkbootstrap.Radiobutton(
        input_frame,
        text="不使用FTP",
        variable=use_ftp,
        value=0).grid(
        column=2,
        row=5)
    Label(input_frame, text="FTP端口：", font=("Times", 15)).grid(column=1, row=6)
    ftp_port = Entry(input_frame)
    ftp_port.grid(column=2, row=6)
    use_ssl = IntVar()
    ttkbootstrap.Radiobutton(
        input_frame,
        text="使用SSL",
        variable=use_ssl,
        value=1).grid(
        column=1,
        row=7)
    ttkbootstrap.Radiobutton(
        input_frame,
        text="不使用SSL",
        variable=use_ssl,
        value=0).grid(
        column=2,
        row=7)
    Label(
        input_frame,
        text="SSL类型：",
        font=(
            "Times",
            15)).grid(
        column=1,
        row=8)
    type_ssl = ttkbootstrap.Combobox(input_frame)
    type_ssl["value"] = ("手动选择证书文件", "自动生成证书文件")
    type_ssl.current(1)
    type_ssl.grid(column=2, row=8)
    cert_file = StringVar()
    key_file = StringVar()
    Label(input_frame, text="证书文件：", font=("Times", 15)).grid(column=1, row=9)
    Button(
        input_frame,
        text="浏览",
        command=view_cert_file,
        width=8,
        height=1).grid(
        column=2,
        row=9)
    Label(
        input_frame,
        textvariable=cert_file,
        font=(
            "Times",
            15)).grid(
        column=3,
        row=9)
    Label(input_frame, text="密钥文件：", font=("Times", 15)).grid(column=1, row=10)
    Button(
        input_frame,
        text="浏览",
        command=view_key_file,
        width=8,
        height=1).grid(
        column=2,
        row=10)
    Label(
        input_frame,
        textvariable=key_file,
        font=(
            "Times",
            15)).grid(
        column=3,
        row=10)
    Button(input_frame, text="确认", command=callback,
           width=8, height=1).grid(column=2, row=11)
    col_count, row_count = input_frame.grid_size()
    server_frame = Frame()
    t = st.ScrolledText(server_frame, width=int(w//20), height=h)
    t.tag_config("success", foreground="green")
    t.tag_config("info", foreground="blue")
    t.tag_config("error", foreground="red")
    t.tag_config("redirect", foreground="orange")
    t.pack(side="right")

    user_frame = Frame()

    user = []
    columns = ("用户名", "用户密码")
    tree = ttkbootstrap.Treeview(user_frame, show="headings", columns=columns, selectmode=BROWSE, height=h-700)
    tree.column("用户名", anchor="center")
    tree.column("用户密码", anchor="center")
    tree.heading("用户名", text="用户名")
    tree.heading("用户密码", text="用户密码")
    tree.pack()
    ttkbootstrap.Button(user_frame, text="添加用户", width=8, command=add_user).pack()
    server_frame.pack(side="right")
    user_frame.pack(side="right")

    for row in range(1, row_count + 1):
        input_frame.grid_rowconfigure(row, minsize=50)
    input_frame.pack(side="left")
    root_window.mainloop()
    r.restoreStd()
    os._exit(0)


if __name__ == "__main__":
    main()
