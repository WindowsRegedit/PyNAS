import os
import requests
from os import system as exec_command

def md_to_rst(from_file, to_file):
    response = requests.post(
        url='http://c.docverter.com/convert',
        data={'to': 'rst', 'from': 'markdown'},
        files={'input_files[]': open(from_file, 'rb')}
    )

    if response.ok:
        with open(to_file, "wb") as f:
            f.write(response.content)

directory = os.getcwd()
commit = input("输入commit消息：")

code = f'''cd {directory} & \
rd /S /Q dist & \
rd /S /Q build & \
rd /S /Q PyNAS.egg-info & \
git add . & \
git commit -am "{commit}" & \
git push -u origin master & \
python setup.py bdist_msi & \
python setup.py bdist_egg & \
python setup.py bdist_wheel & \
python setup.py sdist & \
twine upload dist/*
'''
md_to_rst(os.path.join(directory, "README.md"), os.path.join(directory, "README.rst"))
exec_command(code)
