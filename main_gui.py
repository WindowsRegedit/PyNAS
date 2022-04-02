import sys
from threading import Thread
from tkinter import *
from ttkbootstrap import Style
from main import main as m
from main import handler

def main():
    def callback():
        args = {
            "directory": directory.get(),
            "username": username.get(),
            "password": password.get(),
            "host": host.get(),
            "port": port.get()
        }
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
            t.insert('end', info)
            t.update()
            t.see(END)

        def restoreStd(self):
            sys.stdout = self.stdoutbak
            sys.stderr = self.stderrbak

        def flush(self):
            t.update()
            t.see(END)


    style = Style(theme='minty')
    r = Redirect()
    root_window = style.master
    root_window.title('NAS启动服务工具')
    root_window.iconbitmap('./static/images/favicon.ico')
    root_window.geometry('900x500')
    root_window.attributes('-alpha', 1)
    input_frame = Frame(root_window)
    Label(input_frame, text="网盘路径：", font=('Times', 15)).grid(column=1, row=1)
    directory = Entry(input_frame)
    directory.grid(column=2, row=1)
    Label(input_frame, text="用户名：", font=('Times', 15)).grid(column=1, row=2)
    username = Entry(input_frame)
    username.grid(column=2, row=2)
    Label(input_frame, text="登陆密码：", font=('Times', 15)).grid(column=1, row=3)
    password = Entry(input_frame)
    password.grid(column=2, row=3)
    Label(input_frame, text="服务IP：", font=('Times', 15)).grid(column=1, row=4)
    host = Entry(input_frame)
    host.grid(column=2, row=4)
    Label(input_frame, text="服务端口：", font=('Times', 15)).grid(column=1, row=5)
    port = Entry(input_frame)
    port.grid(column=2, row=5)
    Button(input_frame, text="确认", command=callback, width=8, height=1).grid(column=2, row=6)
    col_count, row_count = input_frame.grid_size()
    server_frame = Frame()
    t = Text(server_frame)
    t.pack()
    server_frame.pack(side='right')

    for row in range(1, row_count+1):
        input_frame.grid_rowconfigure(row, minsize=50)
    input_frame.pack(side='left')
    root_window.mainloop()
    root_window.destroy()
    r.restoreStd()
    handler(None, None)

if __name__ == "__main__":
    main()