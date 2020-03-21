# 【爬虫】问题集-豆瓣电影

[TOC]

> 本文章用于豆瓣电影爬取信息过程中出现的问题


## 问题1 pip install numpy命令行输入的时候报错 OSError: [WinError 87] 参数错误

1. 场景
    * 用conda创建一个虚拟的环境：`conda create -n scrapy python=3`

2. 问题
    * 运行爬虫代码时，出现 `OSError: [WinError 87] The parameter is incorrect`

3. 描述
    * python=3默认安装3.8，有些python库并不支持python3.8

4. 解决方案
    * conda create -n scrapy python=3.7

## 问题2 WebDriverException: Message: unknown error: bad inspector message

1. 场景
    * 用python，selenium构建爬虫获取网页信息，并用xpath进行页面内容解析
    * url: https://movie.douban.com/subject/3878007/

2. 问题
    * webdriver能加载网站，但不能正确返回页面内容

> WebDriverException: Message: unknown error: bad inspector message
<ipython-input-20-f8b39f61b4ff> in <module>
      3 driver = webdriver.Chrome(options=chrome_options)
      4 driver.get(url)
----> 5 html = driver.page_source
> UnicodeEncodeError: 'utf-8' codec can't encode character '\ud83d' in position 76660: surrogates not allowed
> html = HTML(url=self.url, html=content.encode(DEFAULT_ENCODING), default_encoding=DEFAULT_ENCODING)

3. 描述
    * 爬虫在爬取页面中含有emoji字符串时不能正确返回html
    * driver.page_source编码使用的是utf-8,其最大的一个字符是3个字节，而emoji存储需要4个字节

4. 解决方案
    * 不返回page_source，直接通过find_element_by_xpath来获取内容
    * 使用requests获取页面内容

## 问题3 如何获取字符串相同名称的变量值

1. 场景
    * 爬虫获取相应信息后，将变量值添加到DataFrame

2. 问题
    * 获取字符串相同名称的变量值

3. 描述
    * 爬取内容时，将需要获取的信息以字符串的形式存储在可迭代的数据结构中，需要用时通过循环访问可迭代数据结构即可

4. 解决方案
    * 用python内置的eval()函数，例如eval('egg')返回egg变量的值

## 问题4 chrome添加参数

from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

chrome_options = Options()
ua = UserAgent()
user_agent = {"user-agent": ua.random}

chrome_options.add_argument(f'--user-agent={user_agent}') # 添加请求头中的用户代理
chrome_options.add_argument('--disable-gpu') # 禁用GPU
chrome_options.add_argument('--headless') # 无图形界面
chrome_options.add_argument('--blink-settings=imagesEnabled=false') # 禁止图片加载
chrome_options.add_argument('--window-size=800,900') # 设定屏幕分辨率
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation']) # 设定浏览器调控模式