import time
import urllib

from fake_useragent import UserAgent

import requests
from requests_html import HTMLSession

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import re
from lxml import etree

import numpy as np
import pandas as pd

from requests_toolbelt import threaded
from requests_toolbelt import user_agent

DEFAULT_URL = "https://movie.douban.com/tag/#/?sort=U&range=0,10&tags=电影"
DEFAULT_PAGE = 2000

class DoubanSpiderMan(object):
    """docstring for Crawler

    :param start_url: The URL from which the HTML originated
    :param locators: The xpath of elements
    :param df: The final output of parser
    :param timeout: The timeout of crawler
    :param result: The temperally output of parser

    """

    def __init__(self):

        self.locators = {'original_title': '//*[@id="content"]/h1/span[@property="v:itemreviewed"]/text()',
                         'release_year': '//*[@id="content"]/h1/span[@class="year"]/text()',
                         'poster_url': '//*[@id="mainpic"]/a/img/@src',
                         'director': '//*[@id="info"]/span[1]/span[2]/a[@rel="v:directedBy"]/text()',
                         'writer': '//*[@id="info"]/span[2]/span[@class="attrs"]/a[@*]/text()',
                         'actor': '//*[@id="info"]/span[@class="actor"]//*[@rel="v:starring"]/text()',
                         'genre': '//*[@id="info"]/span[@property="v:genre"]/text()',
                         'region': '//*[@id="info"]/text()',
                         'language': '//*[@id="info"]/text()',
                         'release_date': '//*[@id="info"]/span[@property="v:initialReleaseDate"]/text()',
                         'runtime': '//*[@id="info"]/span[@property="v:runtime"]/text()',
                         'alternative_title': '//*[@id="info"]/text()',
                         'imdb_id': '//*[@id="info"]/a[@rel="nofollow"]/text()',
                         'vote_average': '//*[@id="interest_sectl"]/div/div[2]/strong/text()',
                         'vote_count': '//*[@id="interest_sectl"]/div/div[2]/div/div[2]/a/span/text()',
                         'vote_start5_percent': '//*[@id="interest_sectl"]/div/div[3]/div[1]/span[2]/text()',
                         'vote_start4_percent': '//*[@id="interest_sectl"]/div/div[3]/div[2]/span[2]/text()',
                         'vote_start3_percent': '//*[@id="interest_sectl"]/div/div[3]/div[3]/span[2]/text()',
                         'vote_start2_percent': '//*[@id="interest_sectl"]/div/div[3]/div[4]/span[2]/text()',
                         'vote_start1_percent': '//*[@id="interest_sectl"]/div/div[3]/div[5]/span[2]/text()',
                         'tag': '//*[@id="content"]/div[@class="grid-16-8 clearfix"]/div[2]/div[@class="tags"]/div/a[@*]/text()',
                         'watched_count': '//*[@id="subject-others-interests"]/div/a[1]/text()',
                         'towatch_count': '//*[@id="subject-others-interests"]/div/a[2]/text()',
                         'overview': '//*[@id="link-report"]//*[@property="v:summary"]/text()',
                         'recommend_name': '//*[@id="recommendations"]/div/dl[@*]/dd/a/text()',
                         'recommend_url': '//*[@id="recommendations"]/div/dl[@*]/dd/a/@href',
                         'short_review': '//*[@id="hot-comments"]/div[@*]/div/p/span/text()',
                         'short_review_count': '//*[@id="comments-section"]/div[1]/h2/span/a/text()',
                         'full_review_title': '//*[@class="reviews mod movie-content"]/div[2]/div[@*]/div/div[@class="main-bd"]/h2/a/text()',
                         'full_review_short': '//*/div[@class="short-content"]/text()',
                         'full_review_count': '//*[@id="content"]//*[@class="reviews mod movie-content"]/header//*/a[@href="reviews"]/text()',
                         'full_review_link': '//*[@class="reviews mod movie-content"]/div[2]/div[@*]/div/div[@class="main-bd"]/h2/a/@href',
                         'discussion_count': '//*[@id="content"]//*/div[@class="section-discussion"]/p/a/text()',
                         'ask_count': '//*[@id="askmatrix"]//*/span[@class="pl"]/a/text()',
        }
        self.timeout = 20
        self.columns = ['id'] + [val for val in self.locators]
        # Add proies by ShawdowSocks (Scraying Out of Great Wall)
        self.proxies = {'http': 'http://127.0.0.1:1087',
                        'https': 'http://127.0.0.1:1087'}
        # Add proies by Trojan
        #self.proxies = {'http': 'http://127.0.0.1:1081',
        #                'https': 'http://127.0.0.1:1081'}

    def get_headers(self):
        """
        Settings for headers
        """
        ua = UserAgent()
        user_agent = ua.random
        headers = {'user-agent': user_agent}

        return headers

    def set_chrome_options(self, proxies=False):
        """
        Chrome webdriver sets

        :chrome_options: add arguments
        """
        chrome_options = Options()
        # Add proies
        if proxies:
            options.add_argument('--proxy-server={}'.format(self.proxies['http']))

        chrome_options.add_argument('--user-agent={}'.format(
                                    self.get_headers()['user-agent'])
        )
        chrome_options.add_argument('--disable-gpu')
        #chrome_options.add_argument('--headless')
        #chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument('--window-size=800,900')
        chrome_options.add_experimental_option('excludeSwitches',
                                               ['enable-automation'])

        return chrome_options

    def wait_for_element_located(self, driver, locator, timeout=20):

        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, locator))
            )
        except:
            print('No Such Element There!\n{}'.format('-'*20))
            print('locator is {}'.format(locator))
            return
        else:
            return element

    def selenium_parser_urls(self, url):
        """
        Use selenium to parser
        """
        driver = webdriver.Chrome(options=self.set_chrome_options(proxies=False))
        driver.implicitly_wait(10)
        start_url = url
        print('link is %s' %start_url)
        print('='*20)
        if proxies:
            driver.get(start_url, proxies=proxies)
        else:
            driver.get(start_url)

        time.sleep(np.random.randint(10, 15)+np.random.random())
        time.sleep(60)

        for count in range(DEFAULT_PAGE // 20 - 1):
            load_more_locator = 'a.more'
            try:
                print(f'count {count}: start click\n', '='*20)
                continue_element = self.wait_for_element_located(driver,
                                load_more_locator)
                continue_element.click()
                print(f'count {count}: after click', '='*20)
            except:
                print('No more elements to show!')
                break
            finally:
                print('sleeping')
                time.sleep(np.random.randint(5, 10)+np.random.random())

        html = driver.page_source
        root = etree.HTML(html)
        movie_chains_xpath = '//*[@id="app"]/div/div[1]/div[3]/a[@*]/@href'
        movie_chains = root.xpath(movie_chains_xpath)

        driver.close()

        print(f"length of movie_chains: {len(movie_chains)}", '\n\t', '-'*20)

        return movie_chains

    def selenium_parser_page(self, url):
        """
        Use selenium to parser
        """
        chrome_options = self.set_chrome_options(proxies=False)
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        time.sleep(np.random.randint(1, 5))
        try:
            html = driver.page_source
        except:
            print('exceptions!\n', 'scrapying by requests instead!')
            try:
                return self.requests_html_parser_page(url)
            except:
                return self.requests_parser_page(url)
        else:
            root = etree.HTML(html)

        s_results = {'id': re.findall(r'.*?subject/(\d+)', url)[0]}

        for locator in self.locators:
            s_results[locator] = root.xpath(self.locators[locator])
        driver.close()

        return s_results

    def requests_parser_page(self, url):
        """
        Use requests to parser
        """
        r = requests.get(url, headers=self.get_headers())

        time.sleep(np.random.randint(1, 5)+np.random.random())

        root = etree.HTML(r.text)

        r_results = {'id': re.findall(r'.*?subject/(\d+)', url)[0]}

        for locator in self.locators:
            r_results[locator] = root.xpath(self.locators[locator])

        return r_results

    def requests_html_parser_page(self, url):
        """
        Use requests-html to parser
        """
        if url is None:
            return None
        else:
            session = HTMLSession()
            r = session.get(url)
            r.html.render(wait=5)

        rh_results = {'id': re.findall(r'.*?subject/(\d+)', url)[0]}

        for locator in self.locators:
            rh_results[locator] = r.html.xpath(self.locators[locator])

        return rh_results

    def crawl_page(self, url, page_state=True, interactive=False):
        """
        Parsing html

        :param url: scrapying target
        :param page_state: True for static page
        :param interactive: True for interactive access
        """
        page_lists = []

        if url is None:
            return None
        elif page_state:
            print('page crawl is requests_parser_page\n\t', '-'*20)
            page_results = self.requests_parser_page(url)
        elif not interactive:
            print('page crawl is requests_html_parser_page\n\t', '-'*20)
            page_results = self.requests_html_parser_page(url)
        else:
            print('page crawl is selenium_parser_page\n\t', '-'*20)
            page_results = self.selenium_parser_page(url)

        return page_results

    def initialize_session(self, session):
        session.headers['User-Agent'] = self.get_headers()['user-agent']

    def async_crawl_pages(self, urls):
        """
        async parsing htmls
        """
        urls_to_get = []

        for url in urls:
            urls_to_get.append({'url': url,
                                'method': 'GET',
                                'headers': self.get_headers(),
                                'timeout': self.timeout})

        responses, errors = threaded.map(urls_to_get,
                                        num_processes=3)

        page_lists = []

        for response in responses:

            print(f'response is {response}')
            print('GET {0}. Returned {1}.'.format(response.request_kwargs['url'],
                                                  response.status_code))

            root = etree.HTML(response.text)

            print(f'type(root) is {type(root)}')

            r_results = {'id': re.findall(r'.*?subject/(\d+)',
                                          response.request_kwargs['url'])[0]}

            for locator in self.locators:
                r_results[locator] = root.xpath(self.locators[locator])

            page_lists.append(r_results)

        df_pages = pd.DataFrame(page_lists, columns=self.columns)
        df_pages.info()

        return df_pages

    def crawl_pages(self, urls):
        """
        Parsing htmls
        """

        page_lists = []
        for idx, url in enumerate(urls):
            print(f'{idx} url: \n\t{url}\n\t', '-'*20)
            page_lists.append(self.crawl_page(url))

        df_pages = pd.DataFrame(page_lists, columns=self.columns)
        df_pages.info()

        return df_pages

    def crawl(self, url=DEFAULT_URL, async_crawl=False):
        """
        Crawling
        """
        movie_chains = self.selenium_parser_urls(url)
        if not async_crawl:
            return self.crawl_pages(movie_chains)
        else:
            return self.async_crawl_pages(movie_chains)

if __name__ == "__main__":
    douban_crawler = DoubanSpiderMan()
    df = douban_crawler.crawl(async_crawl=True)
    df.to_csv('douban_crawler.csv', index=False)
