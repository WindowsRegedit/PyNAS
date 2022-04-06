# coding=utf-8
import re
import os
import sys
import json
import tkinter.scrolledtext as st
from threading import Thread
from tkinter import *
from tkinter.messagebox import showwarning as warn
from tkinter.messagebox import showinfo as info
import ttkbootstrap
from ttkbootstrap import Style
from main import main as m


def main():
    def help():
        with open("help.json", encoding="utf-8") as f:
            helps = json.load(f)["helps"]
        for help in helps:
            info("帮助", help)

    def LICENSE():
        with open("LICENSE", encoding="utf-8") as f:
            license = f.read()
        info("关于", license)

    def check_dir():
        if not os.path.exists(directory.get()):
            warn("错误", "路径不存在或不正确")
            directory.delete(0, END)
            return False
        return True

    def check_usr():
        if not username.get():
            warn("错误", "用户名不能为空")
            return False
        return True

    def check_pwd():
        if not password.get():
            warn("错误", "密码不能为空")
            return False
        return True

    def check_host():
        match = re.match(
            "^((2(5[0-5]|[0-4]\\d))|[0-1]?\\d{1,2})(\\.((2(5[0-5]|[0-4]\\d))|[0-1]?\\d{1,2})){3}$",
            host.get())
        if not match:
            warn("错误", "服务IP格式不正确")
            host.delete(0, END)
            return False
        return True

    def check_port():
        if not port.get().isdigit():
            warn("错误", "端口必须是一个数字")
            port.delete(0, END)
            return False
        if not (int(port.get()) <= 65536 or int(port.get()) >= 1):
            warn("错误", "端口必须是一个数字并且在1-65536之间")
            return False
        return True

    def check_ftp_port():
        if not ftp_port.get().isdigit() and use_ftp == 1:
            warn("错误", "ftp端口必须是一个数字")
            port.delete(0, END)
            return False
        if use_ftp == 1:
            if int(ftp_port.get()) >= 65536 or int(
                    ftp_port.get()) <= 1:
                warn("错误", "ftp端口必须是一个数字并且在1-65536之间")
                return False
        if use_ftp == 1:
            if int(ftp_port.get()) == int(port.get()):
                warn("错误", "ftp端口与网盘端口相等")
                return False
        return True

    def check_key():
        if not key.get():
            warn("错误", "密钥为空")
            return False
        return True

    def callback():
        args = {
            "directory": directory.get(),
            "username": username.get(),
            "password": password.get(),
            "host": host.get(),
            "port": port.get(),
            "ftp": bool(use_ftp.get()),
            "ftp_port": ftp_port.get(),
            "key": key.get(),
        }
        if not check_dir():
            return
        if not check_usr():
            return
        if not check_pwd():
            return
        if not check_host():
            return
        if not check_port():
            return
        if not check_ftp_port():
            return
        if not check_key():
            return
        s = Thread(target=m, args=(args,))
        s.start()

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
            if "200" in info:
                t.insert("end", info, "success")
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
    root_window.iconbitmap("./static/images/favicon.ico")
    root_window.geometry("900x700")
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
    Label(input_frame, text="用户名：", font=("Times", 15)).grid(column=1, row=2)
    username = Entry(
        input_frame)
    username.grid(column=2, row=2)
    Label(input_frame, text="登陆密码：", font=("Times", 15)).grid(column=1, row=3)
    password = Entry(input_frame, show="*")
    password.grid(column=2, row=3)
    Label(input_frame, text="服务IP：", font=("Times", 15)).grid(column=1, row=4)
    host = Entry(input_frame)
    host.grid(column=2, row=4)
    Label(input_frame, text="服务端口：", font=("Times", 15)).grid(column=1, row=5)
    port = Entry(input_frame)
    port.grid(column=2, row=5)
    Label(input_frame, text="服务密钥：", font=("Times", 15)).grid(column=1, row=6)
    key = Entry(input_frame, show="*")
    key.grid(column=2, row=6)
    use_ftp = IntVar()
    ttkbootstrap.Radiobutton(
        input_frame,
        text="使用FTP",
        variable=use_ftp,
        value=1).grid(
        column=1,
        row=7)
    ttkbootstrap.Radiobutton(
        input_frame,
        text="不使用FTP",
        variable=use_ftp,
        value=0).grid(
        column=2,
        row=7)
    Label(input_frame, text="FTP端口：", font=("Times", 15)).grid(column=1, row=8)
    ftp_port = Entry(input_frame)
    ftp_port.grid(column=2, row=8)
    Button(input_frame, text="确认", command=callback,
           width=8, height=1).grid(column=2, row=9)
    col_count, row_count = input_frame.grid_size()
    server_frame = Frame()
    t = st.ScrolledText(server_frame, width=75, height=50)
    t.tag_config("success", foreground="green")
    t.tag_config("info", foreground="blue")
    t.tag_config("error", foreground="red")
    t.pack()
    server_frame.pack(side="right")

    for row in range(1, row_count + 1):
        input_frame.grid_rowconfigure(row, minsize=50)
    input_frame.pack(side="left")
    root_window.mainloop()
    r.restoreStd()
    os._exit(0)


if __name__ == "__main__":
    main()
