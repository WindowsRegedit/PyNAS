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

第一种：

::

    pip install PyNAS

第二种：

::

    git clone https://gitee.com/shwufan/nas.git
    python setup.py install

第三种：

::

    git clone https://github.com/WindowsRegedit/PyNAS.git
    python setup.py install

使用说明
^^^^^^^^

比如: 1. nas -c conf.json

2. nas --config configure.json

3. nas --username admin --password admin

4. nas --host 0.0.0.0 --port 80 --username admin --password admin

5. nas-gui

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

PyNAS 2022.4.12 正式版更新说明
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. 优化了requirements.txt

2. 解决了nas-gui无法调用的问题

3. 将nas-gui设置为默认使用python -m PyNAS调用包时打开的程序

4. 解决了SSL使用时导致连接拒绝的问题

5. 添加了一些没有添加的包

6. 现在可以添加多个用户了
