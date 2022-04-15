###介绍
PyNAS是一个以Python的Updog的库为基础，制作而来的库
###安装
1. pip安装（推荐）
``pip install PyNAS``
2. 源码安装（推荐）
Github:
```
git clone https://github.com/WindowsRegedit/PyNAS.git
cd PyNAS
python setup.py install
```
Gitee:
```
git clone https://gitee.com/shwufan/nas.git
cd nas
python setup.py install
```
3. 安装包安装
```
从https://github.com/WindowsRegedit/PyNAS/releases或https://gitee.com/shwufan/nas/releases下载安装包
然后自行安装......
```
4. easy_install安装（不推荐）（即将弃用）
``easy_install PyNAS``

###用法
GUI窗口启动：
```
1. nas-gui
2. python -m PyNAS
```
命令行启动
```
usage: nas [-h] [-d DIRECTORY] [-p PORT] [-usr USERNAME [USERNAME ...]] [-pwd PASSWORD [PASSWORD ...]] [-v]
           [-host HOST] [-c CONFIG] [-f] [-fp FTP_PORT] [-se SECRET] [-s] [-st SSL_TYPE] [-ce CERT] [-k KEY]

nas服务器启动工具

选择性参数:
  -h, --help            显示帮助信息
  -d DIRECTORY, --directory DIRECTORY
                        根目录，默认当前路径
  -p PORT, --port PORT  服务端口，默认为80
  -usr USERNAME [USERNAME ...], --username USERNAME [USERNAME ...]
                        用户名列表，默认为admin
  -pwd PASSWORD [PASSWORD ...], --password PASSWORD [PASSWORD ...]
                        密码列表（注意要和用户名列表相同长度），默认为admin
  -v, --version         Python NAS 版本
  -host HOST, --host HOST
                        服务IP，默认为0.0.0.0
  -c CONFIG, --config CONFIG
                        配置文件位置，默认没有，注意此文件会覆盖所有命令行配置
  -f, --ftp             是否开启FTP服务（默认关闭）
  -fp FTP_PORT, --ftp_port FTP_PORT
                        FTP服务开启端口（当-f被指定时）（默认2121）
  -se SECRET, --secret SECRET
                        运行网盘时的加密字符串（默认有的）
  -s, --ssl             是否开启SSL（默认关闭）
  -st SSL_TYPE, --ssl_type SSL_TYPE
                        在开启SSL的情况下使用哪种方式（自动/手动）自动的话参数里加auto，手动的话参数里加custom（默认自动）
  -ce CERT, --cert CERT
                        在选择手动并开启SSL的情况下使用的证书（比如cert.pem）
  -k KEY, --key KEY     在选择手动并开启SSL的情况下使用的密钥（比如key.pem）
配置文件同理（注意是json格式，并且要用全拼）。
例如：
一个叫做conf.json的文件：
{"key": "1234567", "ssl_type": "auto"}
```

###PyNAS 2022.4.15版本更新内容
1. 使用装饰器优化GUI

###PyNAS 2022.4.15版本已知问题
1. 在某些设备上路径的第一个字符有可能会丢失（求pr）