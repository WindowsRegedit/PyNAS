import os
import json
import uuid
import signal
import argparse

from flask import Flask, render_template, send_file, redirect, request, send_from_directory, url_for, abort, jsonify
from flask_wtf import FlaskForm as Form
from flask_login import LoginManager, current_user, login_required
from flask_login import UserMixin, login_user, logout_user
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.serving import run_simple

from utils.path import is_valid_subpath, is_valid_upload_path, get_parent_directory, process_files
from utils.output import error, info, warn, success
from config import version as VERSION

##Warning:You must use Werkzeug==2.0.3 or below
def handler(signal, frame):
    print()
    error('退出!')
    exit(0)

def read_write_directory(directory):
    if os.path.exists(directory):
        if os.access(directory, os.W_OK and os.R_OK):
            return directory
        else:
            error('输出无法写入或读取')
    else:
        error('选择的文件夹不存在')

def parse_arguments():
    parser = argparse.ArgumentParser(prog='nas')
    cwd = os.getcwd()
    parser.add_argument('-d', '--directory', metavar='DIRECTORY', type=read_write_directory, default=cwd,
                        help='根目录，默认当前路径')
    parser.add_argument('-p', '--port', type=int, default=9090,
                        help='服务端口，默认为9090')
    parser.add_argument('-usr', '--username', type=str, default='admin', help='登陆用户名，默认为admin')
    parser.add_argument('-pwd', '--password', type=str, default='admin', help='登陆密码，默认为admin')
    parser.add_argument('-v', '--version', action='version', version='Python NAS v'+VERSION, help="Python NAS 版本")
    parser.add_argument('-host', '--host', default="0.0.0.0", type=str, help="服务IP，默认为0.0.0.0")
    parser.add_argument('-c', '--config', type=str, default='', help='配置文件位置，默认没有，注意此文件会覆盖所有命令行配置')
    args = parser.parse_args()
    if args.config:
        if os.path.exists(args.config):
            with open(args.config, "r", encoding="utf-8") as f:
                args = json.load(f)
                return args
        else:
            raise RuntimeError("配置文件错误：不存在")
    else:
        args = {
            "directory": args.directory,
            "port": args.port,
            "username": args.username,
            "password": args.password,
            "host": args.host
        }
        return args

def main(args=parse_arguments()):
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    app.secret_key = 'pleasedontcryptmywebpageitreallyspentmealongtimeplease'
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    global base_directory
    base_directory = args.get("directory", "")

    # Deal with Favicon requests
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'images/favicon.ico', mimetype='image/vnd.microsoft.icon')

    ############################################
    # File Browsing and Download Functionality #
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
                        return send_file(requested_path, mimetype=mimetype, as_attachment=send_as_attachment, conditional=True)
                    else:
                        return send_file(requested_path, mimetype=mimetype, as_attachment=send_as_attachment)
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
                directory_files = process_files(os.scandir(requested_path), base_directory)
            except PermissionError:
                abort(403, 'Read Permission Denied: ' + requested_path)

            return render_template('home.html', files=directory_files, back=back,
                                   directory=requested_path, is_subdirectory=is_subdirectory, version=VERSION, username=args.get("username", ""))
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
                    filename = secure_filename(file.filename)
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

    create_user(args.get("username", ""), args.get("password", ""))

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
                if user.get('id') == user_id:
                    return User(user)
            return None


    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    class LoginForm(Form):
        username = StringField("用户名", validators=[DataRequired()])
        password = PasswordField("密码", validators=[DataRequired()])


    @app.route('/login/', methods=('GET', 'POST'))  # 登录
    def login():
        return render_template('login.html', next=request.args.get("next") or "/", emsg=request.args.get("emsg") or None)

    @app.route('/logout')  # 登出
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/ajax/login')
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
                return redirect(request.args.get('next') or '/')
            else:
                emsg = "密码有误"
        return redirect('/login?emsg='+emsg)
    # Inform user before server goes up
    success('在 {} 服务...'.format(args.get("directory", ""), args.get("port", 9090)))

    try:
        signal.signal(signal.SIGINT, handler)
    except ValueError:
        pass

    run_simple(args.get("host", "0.0.0.0"), int(args.get("port", 9090)), app, threaded=True)


if __name__ == '__main__':
    main()