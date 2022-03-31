# PyNAS

#### 介绍
Python NAS 在updog的基础上编写而成.

#### 软件架构
使用 Flask, Flask-Login, Flask-WTF 制作登陆界面.


#### 安装教程

1.  pip install PyNAS
2.  git clone https://gitee.com/shwufan/nas.git
    python setup.py install

#### 使用说明

比如:
nas -c conf.json
nas --config configure.json

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 教程

nas 配置编写指南：

username: 登陆用户名

password: 登陆密码

host: 网盘服务ip

（0.0.0.0允许所有人访问, 127.0.0.1只有自己能访问，默认0.0.0.0）

port: 网盘服务端口（默认9090）

