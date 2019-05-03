#encoding:utf-8
from scrapy.selector import Selector
from scrapy.http import Request
import re
import redis
from ScrapyJiaoyubao.jiaoyubao.items import JiaoyubaoItem
from urllib.parse import urljoin
from urllib.request import urlretrieve
from scrapy_redis.spiders import RedisCrawlSpider
import os
from w3lib.html import remove_tags
import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
import string


class JiaoyubaoSchoolSpider(RedisCrawlSpider):
    name = 'jiaoyubao_school'
    allowed_domains = ["jiaoyubao.cn"]
    #start_urls = ["https://movie.douban.com/top250"]
    redis_key = 'jiaoyubao:start_urls' #开始url在redis的键名
    #city = re.match(r'jiaoyubao_(.+):.*', redis_key).group(1) #get city
    path1 = 'D:/Upload/product/'
    path2 = '/Upload/product/'

    def parse(self, response):
        jiaoyubao_url = re.match(r'(http://\w+\.jiaoyubao\.cn)/.*', response.url).group(1)
        item = JiaoyubaoItem()
        s = Selector(response)
        srcurls = s.xpath('//div[@class="ComLine"]')
        for srcurl in srcurls:
            #name1 = srcurl.xpath('div/div[2]/div[1]/a/text()').extract_first()
            src1 = srcurl.xpath('div/div[1]/div[1]/div/div/a/img/@src').extract_first()
            filepath2 = ''
            if src1:
                src2 = src1
                #localtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                year = time.strftime('%Y', time.localtime(time.time()))
                month = time.strftime('%Y.%m', time.localtime(time.time()))
                day = time.strftime('%Y.%m.%d', time.localtime(time.time()))
                t = int(time.time())
                num = random.randint(1000, 9999)
                filename = str(t) + str(num) + '.png'
                filepath2 = self.path2 + year + '/' + month + '/' + day + '/' + filename
                fileYear = self.path1 + year
                fileMonth = fileYear + '/' + month
                fileDay = fileMonth + '/' + day
                filepath1 = fileDay + '/' + filename
                if not os.path.exists(fileYear):
                    os.mkdir(fileYear)
                    os.mkdir(fileMonth)
                    os.mkdir(fileDay)
                else:
                    if not os.path.exists(fileMonth):
                        os.mkdir(fileMonth)
                        os.mkdir(fileDay)
                    else:
                        if not os.path.exists(fileDay):
                            os.mkdir(fileDay)
                try:
                    urlretrieve(src2, filepath1)
                except:
                    urlretrieve(urllib.parse.quote(src1,safe=string.printable), filepath1)#处理url中有中文
            item['course_pic'] = filepath2
            sch_url = srcurl.xpath('div/div[2]/div[1]/a/@href').extract_first()
            if sch_url:
                res = Request(sch_url, callback=self.parse_school)
                res.meta['item'] = item
                yield res
        nextLink = s.xpath('//div[@class="page"]/div//table/tr//td[last()-2]/a/@href').extract_first()
        if nextLink:
            next = urljoin(jiaoyubao_url, nextLink)
            yield Request(next, callback=self.parse)

    def parse_school(self, response):
        jiaoyubao_url = re.match(r'(http://\w+\.jiaoyubao\.cn)/.*', response.url).group(1)
        item = response.meta['item']
        s = Selector(response)
        course_urls = s.xpath('//div[@class="ZcTabSerP"]/div/a/@href').extract()
        pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=1)
        r = redis.Redis(connection_pool=pool)
        pipe = r.pipeline(transaction=True)
        for course in course_urls:
            courses_url = urljoin(jiaoyubao_url, course)
            pipe.lpush("jyb_course_urls", courses_url)
        pipe.execute()  # 保存学校页面的课程链接到reids
        name = s.xpath('//div[1]/div[1]/div/div[1]/div[4]/text()').extract_first()
        features = s.xpath('//div[@class="item2"]').extract_first()
        feature = ''
        if features:
            feature = remove_tags(features)
        msg = s.xpath('//div[@class="content_description"]')
        intros2 = s.xpath('//div[@class="ZcTabC"]').extract()
        intros1 = s.xpath('//div[@class="ComTab"]/div[@class="ComTab_Item"][2]/div[@class="ComTab_Item_body"]').extract()
        intro = ''
        if msg:
            #src = msg.xpath('img/@href').extract_first()
            intros = msg.xpath('p').extract()
            for text in intros:
                if text != ' ':
                    intro += remove_tags(text.strip())
        elif intros1:
            for text in intros1:
                if text != ' ':
                    intro += remove_tags(text.strip())
        elif intros2:
            for text in intros2:
                if text != ' ':
                    intro += remove_tags(text.strip())
        else:
            intros3 = s.xpath('//a[@name="机构简介"]/../div').extract()
            for text3 in intros3:
                if text3 != ' ':
                    intro += remove_tags(text3.strip())
        srcs = s.xpath('//div[@class="j j_Slide loading"]/div/ol/li/img/@src').extract()
        if not srcs:
            srcs = s.xpath('//div[@class="j j_Slide loading"]/ol/li/img/@src').extract()
            if not srcs:
                srcs = s.xpath('//li[@class="J_ECPM"]/img/@src').extract()
        pic = []
        if srcs:
            i = 0
            for src in srcs:
                src3 = src
                year = time.strftime('%Y', time.localtime(time.time()))
                month = time.strftime('%Y.%m', time.localtime(time.time()))
                day = time.strftime('%Y.%m.%d', time.localtime(time.time()))
                t = int(time.time())
                num = random.randint(1000, 9999)
                filename = str(t) + str(num) + '.png'
                filepath2 = self.path2 + year + '/' + month + '/' + day + '/' + filename
                fileYear = self.path1 + year
                fileMonth = fileYear + '/' + month
                fileDay = fileMonth + '/' + day
                filepath1 = fileDay + '/' + filename
                if not os.path.exists(fileYear):
                    os.mkdir(fileYear)
                    os.mkdir(fileMonth)
                    os.mkdir(fileDay)
                else:
                    if not os.path.exists(fileMonth):
                        os.mkdir(fileMonth)
                        os.mkdir(fileDay)
                    else:
                        if not os.path.exists(fileDay):
                            os.mkdir(fileDay)
                try:
                    urlretrieve(src3, filepath1)
                except :
                    urlretrieve(urllib.parse.quote(src,safe=string.printable), filepath1)
                pic.append(filepath2)
                i += 1
                if i == 5:
                    break
        js = s.xpath('//div[@class="wangdian"]/span/@onclick').extract_first()
        if not js:
            js = s.xpath('//div[@class="ZcPoint"]/div[@class="pa"]/div[@class="pa02"]/@onclick').extract_first()
            if not js:
                js = s.xpath('//div[@class="tl3_dd2"]/div[@class="tl3_dr2"]/span/@onclick').extract_first()
        datas = ''
        maps = []
        address = []
        tel = ''
        city = ''
        if js:
            datas = js[27:-1].split(',')
        if datas:
            try:
                arg = int(datas[3])
            except:
                arg = int(datas[3][1:-1])
            cityid = int(datas[9][4:-1])
            #经过网页跟踪发现定位数据需要传入参数并从http://api.jiaoyubao.cn/map/Ajax.aspx动态加载而来
            data = {"os": 1, "arg": arg, "city": cityid, "page": 1, "pagesize": 10, "key": ''}
            map_url = "http://api.jiaoyubao.cn/map/Ajax.aspx"
            if data:
                r = requests.post(map_url, data=data)
                s = BeautifulSoup(r.text, "html.parser")
                point1 = s.find_all('point')
                city = s.points['cityname']
                p = s.find('point')
                if not name:
                    name = p.get('cp_name')
                tel1 = p.get('u400')
                tel2 = p.get('tel400')
                if tel2:
                    tel = tel1 + '转' + tel2
                else:
                    tel = tel1
                for point in point1:
                    map = []
                    addr = ''
                    campus = point.get('name')
                    campus_address = point.get('address')
                    lng = point.get('lng')
                    lat = point.get('lat')
                    addr = point.get('name') + '/' + point.get('address')
                    value = lng, lat
                    map.append(campus)
                    map.append(campus_address)
                    map.append(value)
                    maps.append(map)
                    address.append(addr)
        else:
            citys = s.xpath('//div[@class="Item_ComTop1"]/div[1]/div[1]/a[2]/text()').extract_first()
            if citys:
                city = citys[:(len(citys)-3)]
            tels = s.xpath('//div[@class="ZcTel"]/div[1]')
            tel1 = tels.xpath('span[2]/text()').extract_first()
            tel2 = tels.xpath('text()').extract_first()
            if tel2:
                tel = tel1 + '转' + tel2
            else:
                tel = tel1
        item['city'] = city
        item['tel'] = tel
        item['address'] = address
        item['average_price'] = None
        item['location'] = maps
        item['teacher_num'] = None
        item['pic'] = pic
        item['intro'] = ''.join(intro.split())
        item['feature'] = feature
        item['tags'] = None
        item['name'] = name
        yield item