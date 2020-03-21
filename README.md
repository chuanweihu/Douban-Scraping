# 【爬虫】总结-豆瓣电影

[TOC]

> 经过几天的爬虫，终于得到豆瓣返回的状态码`403（'forbidden'）`

## 思考1: 数据匹配

对于豆瓣这种运行了十几年的网站，网站的页面结构也随之变化，在解析时不容易统一位置。这让我学到了许多关于lxml解析的方法（注：bs4支持lxml）。

### lxml解析

在内容定位过程中，主要有两大问题，一个是**页面结构的调整**，另一个是**匹配多个值**。问题可以通过lxml中的通配符`*`的语法解决，找不到元素时通过css查找匹配解决。

1. 通过`*`匹配任何元素节点
    * **表达式**：`//*`选取文件中的所有元素(注：`//`为当前节点后的任意节点选取)；`/bookstore/*`选取book元素的所有子元素节点
    * **例如**：剧情简介用的xpath为`'//*[@id="link-report"]//*[@property="v:summary"]/text()'`
    * **解释**: `//*[@id="link-report"]`表示从根节点到任意节点属性`id`值为`"link-report"`的节点，`//*[@property="v:summary"]`表示从当前节点到之后属性`property`值为`"v:summary"`的任意节点

2. 通过`@*`匹配任何属性节点
    * **表达式**：`//title[@*]`选取所有title元素（至少有一种属性）
    * **例如**：编剧用的xpath为`'//*[@id="info"]/span[2]/span[@class="attrs"]/a[@*]/text()'`
    * **解释**: `/a[@*]`表示从a节点任意属性的节点

### 异常处理

虽然通过了通配符`*`的处理，但有时也有匹配不到的情况，主要原因是**匹配的语法并不通用**，**页面没有该内容**以及**页面获取超时**。

1. 该问题可以直接通过python的异常处理`try-except`语句解决，出现异常时返回空值。
2. 使用selenium时，可以通过`selenium.webdriver.support`模块中`expected_conditions`进行条件设定以减少**页面获取超时**问题而得不到页面内容

> **注意**
> 1. python内置的`eval()`函数获取相应的变量值，例如`eval('egg')`返回egg变量的值
> 2. 利用字符串中的`strip()`, `split()`, `join()`, `replace`方法进行数据的提取
> 3. 利用字符串中的`format()`进行print输出 (ref: [PEP 3101 -- Advanced String Formatting](https://www.python.org/dev/peps/pep-3101/))
> 4. 利用列表（字典）推导式处理(**List Comprehensions**)迭代数据和数据列标题`[expr for val in collection if condition]` (ref: [PEP 202 -- List Comprehensions](https://www.python.org/dev/peps/pep-0202/))
> 5. 利用三元表达式（**if-then-else ("ternary") expression**）处理简单的条件: `value = true-expr if condition else false-expr` (fef: [PEP 308 -- Conditional Expressions](https://www.python.org/dev/peps/pep-0308/))
> 6. 利用re正则表达式查找，替换，获取内容(**匹配中文**：`[\u4e00-\u9fff]`{注意该范围未包含扩展范围})

## 思考2: 反爬虫机制

爬取过程中，最顺利的是用selenium进行爬取信息，该软件和真实的浏览器操作类似，但页面获取的时间与网速有很大关系。笔者在中午爬取时，吃完中饭爬取了不到200个页面。

用过一段时间的爬虫后就会知道客户端向服务端发送请求后，得到正确响应的状态码是`200`，然而在爬取过程中会出现各种问题，笔者在爬取过程中出现了`418`和最经典的`403`

### 状态码(Response [418]: 418 I'm a teapot)

首先，我们先了解一下418的含义

> The HTTP 418 I'm a teapot client error response code indicates that the server **refuses to brew coffee** because **it is, permanently, a teapot**. A combined coffee/tea pot that is **temporarily out of coffee** should instead return 503. This error is a reference to Hyper Text Coffee Pot Control Protocol defined in April Fools' jokes in 1998 and 2014. (ref: [418 I'm a teapot](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/418)
418 I'm a teapot (RFC 2324, RFC 7168)
> This code was defined in 1998 as one of the **traditional IETF April Fools' jokes**, in RFC 2324, Hyper Text Coffee Pot Control Protocol, and is **not expected to be implemented by actual HTTP servers**. The RFC specifies this code should be returned by **teapots requested to brew coffee**.This HTTP status is used as an Easter egg in some websites, including Google.com. (ref: [List_of_HTTP_status_codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes)

从上面的内容可以看出，网站协议`RFC2324`表明客户端请求（茶壶）时并不是使用http服务器访问，就像被要求用茶壶倒一杯咖啡（返回），这样的请求当然被服务器端拒绝。换句话说，豆瓣服务器知道了你这次请求并不是来自浏览器的请求，所以拒绝访问。

那么如何解决这问题呢？
我们可以从模拟http服务器访问入手，网上还有专门的python模块`fake_useragent`

```python
from fake_useragent import UserAgent
import requests

ua = UserAgent()
user_agent = ua.random
headers = {'user-agent': user_agent}
url = "http://what.you.want.com"
r = requests.get(url, headers=headers)
r.text
```

### 状态码(Response [403]: 403 Forbidden)

首先，我们先了解一下403的含义

> The HTTP 403 Forbidden client error status response code indicates that the server **understood the request but refuses to authorize it**. This status is similar to 401, but in this case, **re-authenticating will make no difference**. The access is **permanently forbidden and tied to the application logic**, such as insufficient rights to a resource. (ref: [403 Forbidden](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403))
> The request **contained valid data and was understood by the server**, but the server is **refusing action**. This may be due to the **user not having the necessary permissions for a resource** or **needing an account of some sort**, or **attempting a prohibited action** (e.g. creating a duplicate record where only one is allowed). This code is also typically used if the request provided authentication via the WWW-Authenticate header field, but the server did not accept that authentication. The request should not be repeated. (ref: [List_of_HTTP_status_codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes)

从上面的内容可以知道，服务器端理解此次请求，但是拒绝访问，重要的是永久拒绝访问。换句话说，豆瓣服务器端知道了请求的内容超过了他们给予的普通权限，从此上了他们的黑名单，一般通过ip绑定黑名单。

那么如何解决这问题呢？我们可以从ip代理入手

1. ShadowSocks

如果你有过使用或者搭建shadowsocks服务器的经验，那么修改IP轻而易举。笔者Shadowsocks默认的socks请求端口为1087（可以通过shadowscocks客户端的`Copy HTTP Proxy Shell Export line`查看）

那么连接ss代理，在爬取时将代理ip写入请求即可。例如下面的代码将返回代理服务器的ip地址。

```python
import requests

proxies = {
  'http': 'http://127.0.0.1:1087',
  'https': 'http://127.0.0.1:1081',
}

url = 'http://checkip.amazonaws.com'
r = requests.get(url, proxies=proxies)
print(r.text)
```

ShadowSocks一般是当梯子使用，用于爬取外网内容比较快，内网相对来说就比较慢了。不过如果能够提供动态ip地址的话，爬取外网的效果应该很好。

2. ADSL

用动态IP（ADSL）拨号服务器试验的效果不是很好，因为需要在服务器端重新部署所有需要的软件，而且用程序控制adsl拨号时容易连接不上，不过每次都能更换IP地址。

3. Tor

最后是Tor代理服务器，和ShadowSocks使用很相似，使用9150端口为默认的socks端口。Tor浏览器在爬取过程中需要一直运行，抓取的效率也会随着抓取的数量而降低。但是Tor是免费的，更换ip快且稳定。

3.1 **使用Tor**

```python
import socket
import socks
import requests

socks.set_default_proxy(socks.Socks5, "127.0.0.1", 9150)
socket.socket = socks.socksocket

url = 'http://checkip.amazonaws.com'
r = requests.get(url)
print(r.text)
```

3.2 **更换Tor的ip**

```python
import socket
import socks
import requests

from stem import Signal
from stem.control import Controller

controller = Controller.from_port(port=9150)
controller.authenticate()
socks.set_default_proxy(socks.Socks5, "127.0.0.1", 9150)
socket.socket = socks.socksocket

url = 'http://checkip.amazonaws.com'
r = requests.get(url)
print(r.text)

controller.signal(Signal.NEWNY)

url = 'http://checkip.amazonaws.com'
r = requests.get(url)
print(r.text)
```

4. 验证码

暂时只能用手动解决（在selenium这样交互式的工具下才可以）

> **注意**
> 1. 利用`sleep(np.random.randint(3, 5)+np.random.random())`来随机调控间隔时间，模拟人操控浏览器
> 2. 利用[requests-html](https://github.com/psf/requests-html)库能够实现动态网站的js加载，requests作者建立的，但2019年7月后就不再更新

## 思考3: 爬虫效率

前面提到笔者在午饭期间爬取网站时，直到吃完饭300个没有爬取完成，可见速度有多慢。见到这种情况，笔者凭着自己并行的经验，查看了requests相应的异步并发（并行）库。

这里插一句，对于我的理解，并发（concurrency）就是客户端在等待服务器端响应的过程中又发出另一个请求访问。

先说一下进程和线程的关系，单个CPU只能执行单个进程，一个进程里面可以包含多个线程。由于python有GIL（Global Interpreter Lock，全局解释锁）存在，意思是说进程中的某个线程需要执行时必须要拿到GIL，而且一个线程中只有一个GIL，所以python中的一个进程只能同时执行一个线程。

### requests_toolbelt

requests自家(核心成员)的async多线程并发，但是2019年4月后就不再更新，并行库的名称为[requests_toolbelt](https://github.com/requests/toolbelt)

利用thread和queue控制线程，使用起来非常简单方便，但是API接口不提供proxies代理接口和休息间隔时间参数。速度很快，大概几分钟就爬取400多个网站，这就是我被403的罪魁祸首。

**代码如下**

```python
from fake_useragent import UserAgent

from requests_toolbelt import threaded
from requests_toolbelt import user_agent

urls = ["what.you.want.to.do.com", "what.you.have.done.com"]
urls_to_get = []

ua = UserAgent()
headers = {'user-agent': ua.random}
timeout = 5

for url in urls:
    urls_to_get.append({'url': url,
                      'method': 'GET',
                      'headers': headers,
                      'timeout': timeout})

responses, errors = threaded.map(urls_to_get,
                              num_processes=3)

for response in responses:
    print(f'response is {response}')
    print('GET {0}. Returned {1}.'.format(response.request_kwargs['url'],
                                       response.status_code))
    print(f'response.text[:20] is {response.text[:20]}')
```

### aiohttp

aiohttp是现在比较火的异步并发库，只是功能尚不完善，而且使用的体验并不友好，API接口支持的参数很多，这点做得不错，下面的例子我试验了一下代理ip的功能，内网速度有点慢，但是外网不错。

```python
import aiohttp
import asyncio

async def fetch(session, url):
    proxy = {
             "http": "http://127.0.0.1:1081",
             "https": "http://127.0.0.1:1081"
    }
    async with session.get(url, proxy=proxy['http']) as response:
        return await response.text()

async def get(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'https://en.wikipedia.org/wiki/Cat')
        print(f"html[:100] is {html[:100]}")
        pything = await get(session, 'http://python.org')
        print(f"pything[:100] is {pything[:100]}")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

> **注意**
> 1. 笔者这里只是探索了异步并发的加速，并未使用异步并行，本质上还是单线运行，具体参数可以参考相应的文档库
> 2. 可以通过调用`multiprocessing`库来获取cpu核心数量`from multiprocessing import cpu_count`
> 3. python网络爬虫还有一种叫协程(Coroutine)的轻量级线程，单个CPU可以支持上万个协程，通过`gevent`库实现
