# -*- coding: utf-8 -*-
# @Author: Hayashi 林
# @Date  : 2021/12/18 16:37
# 世界中に嵐を巻き起こしよう

# 导入目标公司列表 —— 中国 36家 上市银行
bank_list = ['工商银行', '农业银行', '中国银行', '建设银行', '交通银行', '邮储银行',
             '招商银行', '兴业银行', '中信银行', '平安银行', '光大银行', '民生银行',
             '浙商银行', '浦发银行', '华夏银行', '北京银行', '宁波银行', '杭州银行',
             '上海银行', '郑州银行', '西安银行', '青岛银行', '长沙银行', '江苏银行',
             '南京银行', '苏州银行', '苏农银行', '无锡银行', '江阴银行', '常熟银行',
             '紫金银行', '成都银行', '贵阳银行', '张家港行', '渝农商行', '青农商行']

# # 或者，以文件形式导入：
# import pandas as pd
# bank_list = pd.read_csv('company_list.csv', encoding='utf-8', header=None)
# bank_list = bank_list.iloc[:, 0].tolist()

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import ChromeOptions
import time

# 目标网页：巨潮资讯网
Url = 'http://www.cninfo.com.cn/new/index'


class Crawler(object):
    # 初始化浏览器配置
    def __init__(self, url, bank_name, start_date, end_date):
        option = ChromeOptions()
        # 反屏蔽
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option('useAutomationExtension', False)
        # 修改下载地址
        option.add_experimental_option("prefs",
                                       {"download.default_directory": "D:\\Temp临时文件\\Chrome\\{}1".format(bank_name)})
        self.browser = webdriver.Chrome(options=option)
        self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                                     {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})
        # 隐式等待，直到网页加载完毕，最长等待时间为20s
        self.browser.implicitly_wait(20)

        # 目标网页：url
        self.url = url
        # 目标银行名称
        self.bank_name = bank_name
        # 起止日期
        self.start_date, self.end_date = start_date, end_date

    # 提交查询命令
    def search(self):
        # 填写“银行名称”
        element = self.browser.find_element_by_xpath('//*[@id="searchTab"]/div[2]/div[2]/div/div[1]/div/div[1]/input')
        ActionChains(self.browser).double_click(element).perform()
        element.send_keys(self.bank_name)
        ActionChains(self.browser).move_by_offset(0, 0).click().perform()  # 点击空白处
        time.sleep(1)
        # 修改“开始日期”
        element = self.browser.find_element_by_xpath('//div[@class="ct-line"]/div[1]/input[@placeholder="开始日期"]')
        ActionChains(self.browser).double_click(element).perform()
        element.clear()
        element.send_keys(self.start_date)
        ActionChains(self.browser).move_by_offset(0, 0).click().perform()  # 点击空白处
        # 修改“结束日期”
        element = self.browser.find_element_by_xpath('//div[@class="ct-line"]/div[1]/input[@placeholder="结束日期"]')
        ActionChains(self.browser).double_click(element).perform()
        element.clear()
        element.send_keys(self.end_date)
        ActionChains(self.browser).move_by_offset(0, 0).click().perform()  # 点击空白处
        # 修改“分类”
        self.browser.find_element_by_xpath('//*[@id="searchTab"]/div[2]/div[2]/div/div[2]/span/button').click()
        self.browser.find_element_by_css_selector('span[title="年报"]').click()
        # self.browser.find_element_by_css_selector('span[title="三季报"]').click()
        # self.browser.find_element_by_css_selector('span[title="半年报"]').click()
        # self.browser.find_element_by_css_selector('span[title="一季报"]').click()
        self.browser.find_element_by_xpath('//div[@class="ft"]/button').click()
        # 提交“查询”
        self.browser.find_element_by_xpath('//*[@id="searchTab"]/div[2]/div[5]/button').click()

    # 下载每一页的pdf
    def download_pdf(self):
        # 提取当前页面所有待点击的子链接
        sublink_list = self.browser.find_elements_by_xpath('//span[@class="ahover"]')
        max_node_num = len([node for node in sublink_list])
        print('max_node_num: ', max_node_num)
        for node_num in range(1, max_node_num + 1):
            subpath = '//tbody/tr[{}]/td[3]/div/span/a'.format(node_num)  # 获取子链接
            sub_link = self.browser.find_element_by_xpath(subpath)  # 点击子链接
            self.browser.execute_script("arguments[0].click();", sub_link)
            self.browser.switch_to.window(self.browser.window_handles[-1])  # 切换到最新打开的窗口（文件下载页面）
            try:
                self.browser.find_element_by_xpath(
                    '//*[@id="noticeDetail"]/div/div[1]/div[3]/div[1]/button').click()  # 点击“下载”，文件保存到默认下载路径
            except:
                print('该文件为年报摘要，不可下载')
            time.sleep(0.5)
            self.browser.close()  # 关闭当前窗口
            self.browser.switch_to.window(self.browser.window_handles[0])  # 返回起始窗口
            print('当前页面已下载到第', node_num, '条')

    # 提交查询并下载
    def search_and_download(self):
        self.browser.get(self.url)
        # 先关闭浮窗
        # self.browser.find_element_by_css_selector('span[class="close-btn"]').click()
        # 输入检索条件
        self.search()
        page = 1
        while True:
            time.sleep(1)
            # 翻页循环
            print('开始下载第', page, '页')
            self.download_pdf()  # 下载当前页面所有pdf文件
            try:
                a = self.browser.find_element_by_xpath('//button[@class="btn-next" and @disabled="disabled"]')
                print('已下载到最后一页')
                time.sleep(3)
                break
            except:
                next_page_button = self.browser.find_element_by_xpath('//button[@class="btn-next"]')
                next_page_button.click()  # 翻页
                page += 1
                time.sleep(1)
        self.browser.close()
        time.sleep(3)


for bn in bank_list:
    print('开始下载：', bn)
    Juchaozixun = Crawler(Url, bn, '2000-01-01', '2021-12-31')  # 后两个参数分别对应查询起止日期，可自行修改
    Juchaozixun.search_and_download()
