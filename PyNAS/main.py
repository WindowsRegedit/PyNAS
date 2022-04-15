import argparse
import json
import os
import threading
import uuid

from flask import Flask, render_template, send_file, redirect, request, send_from_directory, url_for, abort
from flask_login import LoginManager, login_required
from flask_login import UserMixin, login_user, logout_user
from flask_wtf import FlaskForm as Form
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.serving import run_simple
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

from PyNAS.config import version as VERSION
from PyNAS.utils.output import error, success
from PyNAS.utils.path import is_valid_subpath, is_valid_upload_path, get_parent_directory, process_files


# Warning:You must use Werkzeug==2.0.3 or below


def read_write_directory(directory):
    if os.path.exists(directory):
        if os.access(directory, os.W_OK and os.R_OK):
            return directory
        else:
            error("输出文件夹无法写入或读取")
    else:
        error("选择的文件夹不存在")


def read_file(file):
    if os.path.exists(file):
        if os.access(file, os.R_OK):
            return file
        else:
            error("选择的文件无法读取")
    else:
        error("选择的文件不存在")


def parse_arguments():
    parser = argparse.ArgumentParser(prog="nas", description="nas服务器启动工具")
    cwd = os.getcwd()
    parser.add_argument("-d", "--directory", metavar="DIRECTORY", type=read_write_directory, default=cwd,
                        help="根目录，默认当前路径")
    parser.add_argument("-p", "--port", type=int, default=80,
                        help="服务端口，默认为80")
    parser.add_argument(
        "-usr",
        "--username",
        type=str,
        nargs='+',
        help="用户名列表，默认为admin",
        default=["admin"])
    parser.add_argument("-pwd", "--password", type=str, nargs='+', help="密码列表（注意要和用户名列表相同长度），默认为admin",
                        default=["admin"])
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="Python NAS v" +
                VERSION,
        help="Python NAS 版本")
    parser.add_argument(
        "-host",
        "--host",
        default="0.0.0.0",
        type=str,
        help="服务IP，默认为0.0.0.0")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="",
        help="配置文件位置，默认没有，注意此文件会覆盖所有命令行配置")
    parser.add_argument(
        "-f",
        "--ftp",
        action="store_true",
        default=False,
        help="是否开启FTP服务（默认关闭）")
    parser.add_argument(
        "-fp",
        "--ftp_port",
        type=int,
        default=2121,
        help="FTP服务开启端口（当-f被指定时）（默认2121）")
    parser.add_argument(
        "-se",
        "--secret",
        type=str,
        default="pleasedontcryptmywebpageitreallyspentmealongtimeplease",
        help="运行网盘时的加密字符串（默认有的）"
    )
    parser.add_argument(
        "-s",
        "--ssl",
        action="store_true",
        default=False,
        help="是否开启SSL（默认关闭）")
    parser.add_argument(
        "-st",
        "--ssl_type",
        type=str,
        default="auto",
        help="在开启SSL的情况下使用哪种方式（自动/手动）自动的话参数里加auto，手动的话参数里加custom（默认自动）")
    parser.add_argument(
        "-ce",
        "--cert",
        type=read_file,
        default=None,
        help="在选择手动并开启SSL的情况下使用的证书（比如cert.pem）")
    parser.add_argument(
        "-k",
        "--key",
        type=read_file,
        default=None,
        help="在选择手动并开启SSL的情况下使用的密钥（比如key.pem）")
    args = parser.parse_args()
    if args.config:
        if os.path.exists(args.config):
            with open(args.config, "r", encoding="utf-8") as f:
                args = json.load(f)
        else:
            error("配置文件错误：不存在")
            os._exit(0)
    else:
        args = {
            "directory": args.directory,
            "port": args.port,
            "username": args.username,
            "password": args.password,
            "host": args.host,
            "ftp": args.ftp,
            "ftp_port": args.ftp_port,
            "secret": args.secret,
            "ssl": args.ssl,
            "ssl_type": args.ssl_type,
            "cert": args.cert,
            "key": args.key
        }
    if len(args.get("username")) != len(args.get("password")):
        error("错误：用户名列表和密码列表长度不相同")
        os._exit(0)
    return args


def main(args=parse_arguments()):
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    app.secret_key = args.get("secret")
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    global base_directory, ssl_context
    base_directory = args.get("directory")

    # Deal with Favicon requests
    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(os.path.join(app.root_path, "static"),
                                   "images/favicon.ico", mimetype="image/vnd.microsoft.icon")

    ############################################
    @app.route('/', defaults={'path': None})
    @app.route('/<path:path>')
    @login_required
    def home(path):
        # If there is a path parameter and it is valid
        if path and is_valid_subpath(path, base_directory):
            # Take off the trailing '/'
            path = os.path.normpath(path)
            requested_path = os.path.join(base_directory, path)

            # If directory
            if os.path.isdir(requested_path):
                back = get_parent_directory(requested_path, base_directory)
                is_subdirectory = True

            # If file
            elif os.path.isfile(requested_path):

                # Check if the view flag is set
                if request.args.get('view') is None:
                    send_as_attachment = True
                else:
                    send_as_attachment = False

                # Check if file extension
                (filename, extension) = os.path.splitext(requested_path)
                if extension == '':
                    mimetype = 'text/plain'
                else:
                    mimetype = None

                try:
                    if extension in ('.mp4', '.avi', '.mkv'):
                        return send_file(requested_path, mimetype=mimetype,
                                         as_attachment=send_as_attachment, conditional=True)
                    else:
                        return send_file(
                            requested_path, mimetype=mimetype, as_attachment=send_as_attachment)
                except PermissionError:
                    abort(403, 'Read Permission Denied: ' + requested_path)

        else:
            # Root home configuration
            is_subdirectory = False
            requested_path = base_directory
            back = ''

        if os.path.exists(requested_path):
            # Read the files
            try:
                directory_files = process_files(
                    os.scandir(requested_path), base_directory)
            except PermissionError:
                abort(403, 'Read Permission Denied: ' + requested_path)

            return render_template('home.html', files=directory_files, back=back,
                                   directory=requested_path, is_subdirectory=is_subdirectory, version=VERSION)
        else:
            return redirect('/')

    #############################
    # File Upload Functionality #
    #############################
    @app.route('/upload', methods=['POST'])
    @login_required
    def upload():
        if request.method == 'POST':

            # No file part - needs to check before accessing the files['file']
            if 'file' not in request.files:
                return redirect(request.referrer)

            path = request.form['path']
            # Prevent file upload to paths outside of base directory
            if not is_valid_upload_path(path, base_directory):
                return redirect(request.referrer)

            for file in request.files.getlist('file'):

                # No filename attached
                if file.filename == '':
                    return redirect(request.referrer)

                # Assuming all is good, process and save out the file
                # TODO:
                # - Add support for overwriting
                if file:
                    filename = file.filename
                    full_path = os.path.join(path, filename)
                    try:
                        file.save(full_path)
                    except PermissionError:
                        abort(403, 'Write Permission Denied: ' + full_path)

            return redirect(request.referrer)

    # Password functionality is without username
    users = []

    def create_user(user_name, password):
        user = {
            "name": user_name,
            "password": generate_password_hash(password),
            "id": uuid.uuid4()
        }
        users.append(user)

    def get_user(user_name):
        for user in users:
            if user.get("name") == user_name:
                return user
        return None

    for i in range(len(args.get("username"))):
        create_user(args.get("username")[i], args.get("password")[i])

    class User(UserMixin):
        def __init__(self, user):
            self.username = user.get("name")
            self.password_hash = user.get("password")
            self.id = user.get("id")

        def verify_password(self, password):
            if self.password_hash is None:
                return False
            return check_password_hash(self.password_hash, password)

        def get_id(self):
            return self.id

        @staticmethod
        def get(user_id):
            if not user_id:
                return None
            for user in users:
                if user.get("id") == user_id:
                    return User(user)
            return None

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    class LoginForm(Form):
        username = StringField("用户名", validators=[DataRequired()])
        password = PasswordField("密码", validators=[DataRequired()])

    @app.route("/login/", methods=("GET", "POST"))  # 登录
    def login():
        return render_template("login.html", next=request.args.get(
            "next") or "/", emsg=request.args.get("emsg") or None, use_ssl=args.get("ssl"))

    @app.route("/logout")  # 登出
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/ajax/login")
    def ajax_login():
        form = LoginForm()
        emsg = None
        user_name = request.args.get("name")
        password = request.args.get("pwd")
        user_info = get_user(user_name)  # 从用户数据中查找用户记录
        if user_info is None:
            emsg = "用户名有误"
        else:
            user = User(user_info)  # 创建用户实体
            if user.verify_password(password):  # 校验密码
                login_user(user)  # 创建用户 Session
                return redirect(request.args.get("next") or "/")
            else:
                emsg = "密码有误"
        return redirect(f"/login?emsg=" + emsg)

    if args.get("ftp"):
        authorizer = DummyAuthorizer()
        for i in range(len(args.get("username"))):
            authorizer.add_user(
                args.get("username")[i],
                args.get("password")[i],
                args.get("directory"),
                perm="elradfmwMT")
        authorizer.add_anonymous(os.getcwd())
        handler = FTPHandler
        handler.authorizer = authorizer
        handler.banner = "欢迎来到个人FTP"
        address = (args.get("host"), args.get("ftp_port"))
        server = FTPServer(address, handler)
        server.max_cons = 256
        server.max_cons_per_ip = 5
        threading.Thread(target=server.serve_forever).start()

    # Inform user before server goes up
    success(
        "在 {} 服务...".format(
            args.get(
                "directory"), args.get(
                "port")))
    ssl_text = None
    if args.get("ssl"):
        if args.get("ssl_type") == "auto":
            ssl_text = "adhoc"
        else:
            ssl_text = (args.get("cert"), args.get("key"))
    run_simple(
        args.get(
            "host"), int(
            args.get(
                "port")), app, threaded=True, ssl_context=ssl_text)


if __name__ == "__main__":
    main()
