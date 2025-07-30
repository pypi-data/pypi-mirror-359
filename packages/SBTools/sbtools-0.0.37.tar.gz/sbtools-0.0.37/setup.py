#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Marj
# Mail: 598175639@qq.com
# Created Time:  2019-09-05 16:36:34
#############################################

from setuptools import setup, find_packages
import requests
from bs4 import BeautifulSoup

def get_latest_version(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # 获取最新版本号
        latest_version = data.get("info", {}).get("version", None)
        return latest_version
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for package '{package_name}': {e}")
        return None

package_name = "SBTools"
sb_ver_list = get_latest_version(package_name).split(".")
# sb_ver_list=soup.find_all(name='h1',attrs={"class":"package-header__name"})[0].text.strip().replace("SBTools","").split(".")
sb_ver_list[-1]=int(sb_ver_list[-1])+1
sb_version=""
for i in sb_ver_list:
    if sb_version=="":
        sb_version=str(i)
    else:
        sb_version=sb_version+"."+str(i)
print(sb_version)

setup(
    name = "SBTools",
    version = sb_version, 
    keywords = ["pip", "SBTools","sbtools"],
    description = "Tool Box",
    long_description = "Tool Box",
    license = "MIT Licence",

    url = "",
    author = "Marj",
    author_email = "598175639@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["requests","pymysql","websockets","python-socks"]
)