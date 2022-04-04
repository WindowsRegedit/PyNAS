PyNAS
=====

介绍
^^^^

Python NAS 在updog的基础上编写而成.

软件架构
^^^^^^^^

使用 Flask, Flask-Login, Flask-WTF 制作登陆界面.

安装教程
^^^^^^^^

1. pip install PyNAS
2. git clone https://gitee.com/shwufan/nas.git python setup.py install

使用说明
^^^^^^^^

比如: 1. nas -c conf.json 2. nas --config configure.json 3. nas
--username admin --password admin 4. nas --host 0.0.0.0 --port 80
--username admin --password admin

参与贡献
^^^^^^^^

1. Fork 本仓库
2. 新建 Feat\_xxx 分支
3. 提交代码
4. 新建 Pull Request

教程
^^^^

nas 配置编写指南：

username: 登陆用户名

password: 登陆密码

host: 网盘服务ip

（0.0.0.0允许所有人访问, 127.0.0.1只有自己能访问，默认0.0.0.0）

port: 网盘服务端口（默认9090）

更新说明
^^^^^^^^

1. 由于添加了GUI，所以版本临时改动至Alpha版
2. GUI仍然不稳定，不建议使用（如果要使用，请输入nas-gui）
3. 经过作者的测试，在Python3.9上比Python3.10稳定，所以暂时不会支持Python3.10以上版本
4. 修复了GUI中文乱码的问题
5. 使用 "\*"代替了输入的密码
6. 添加了验证输入合法性的函数
