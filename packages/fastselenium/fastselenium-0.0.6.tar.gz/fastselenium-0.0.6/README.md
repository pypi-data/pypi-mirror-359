# fastselenium

#### 介绍
封装了一些selenium的用法，使其更加简单

#### 软件架构
软件架构说明


#### 安装教程

1.  pip安装
```shell script
pip install fastselenium
```
2.  pip安装（使用阿里镜像加速）
```shell script
pip install fastselenium -i https://mirrors.aliyun.com/pypi/simple
```

#### 使用说明

1.  demo
```python
import fastselenium
from selenium import webdriver
driver = webdriver.Chrome()
driver.get('www.gitee.com')
test_res = fastselenium.save_cookie(
            driver=driver
        )
```
