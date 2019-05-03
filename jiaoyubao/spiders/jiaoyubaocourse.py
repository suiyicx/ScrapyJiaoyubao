#encoding:utf-8
from .ScrapyJiaoyubao.jiaoyubao.items import JiaoyubaoCourseItem
from scrapy.selector import Selector
from scrapy.http import Request
import re
from urllib.parse import urljoin
from scrapy_redis.spiders import RedisCrawlSpider
from w3lib.html import remove_tags


class CourseSpider(RedisCrawlSpider):

    name = 'jiaoyubao_course'
    #allowed_domains = ['jiaoyubao.com']
    #redis_key = 'jyb_course_urls'#'jyb_course_urls'
    #name = 'jiaoyubao_school'
    allowed_domains = ["jiaoyubao.cn"]
    # start_urls = ["https://movie.douban.com/top250"]
    redis_key = 'jiaoyubao:start_urls'  # 开始url在redis的键名

    def parse(self, response):
        jiaoyubao_url = re.match(r'(http://\w+\.jiaoyubao\.cn)/.*', response.url).group(1)
        s = Selector(response)
        srcurls = s.xpath('//div[@class="ComLine"]')
        for srcurl in srcurls:
            sch_url = srcurl.xpath('div/div[2]/div[1]/a/@href').extract_first()
            if sch_url:
                yield Request(sch_url, callback=self.parse_school)
        nextLink = s.xpath('//div[@class="page"]/div//table/tr//td[last()-2]/a/@href').extract_first()
        if nextLink:
            next = urljoin(jiaoyubao_url, nextLink)
            yield Request(next, callback=self.parse)

    def parse_school(self, response):
        jiaoyubao_url = re.match(r'(http://\w+\.jiaoyubao\.cn)/.*', response.url).group(1)
        s = Selector(response)
        name = s.xpath('//div[1]/div[1]/div/div[1]/div[4]/text()').extract_first()
        course_urls = s.xpath('//div[@class="ZcTabSerP"]/div/a/@href').extract()
        for course in course_urls:
            curl = urljoin(jiaoyubao_url, course)
            req = Request(curl, callback=self.parse_course)
            req.meta['item'] = name
            yield req

    def parse_course(self, response):
        s = Selector(response)
        item = JiaoyubaoCourseItem()
        name = response.meta['item']
        if not name:
            name = s.xpath('//div[@class="ComTop2_name"]/text()').extract_first()
            if not name:
                name = s.xpath('//div[@class="Com_name"]/span/text()').extract_first()
                if not name:
                    nam = s.xpath('//div[@class="Com_SerList_Item"]/div[1]/div/text()').extract_first()
                    if nam:
                        name = nam[0:-4]
        course_name = s.xpath('//div[@class="title_txt"]/div[@class="title_txt_mid"]/text()').extract_first()
        if not course_name:
            course_name = s.xpath('//div[@class="Item_title"]/div/div[@class="txt"]/text()').extract_first()
        client = ''
        price = ''
        class_type = ''
        date = ''
        campus = ''
        student_num = '请咨询'
        type = []
        details = s.xpath('//div[@class="jianjie"]').extract_first()
        if course_name:
            infos = s.xpath('//ul[@class="Product_Show"]/li')
            if infos:
                if len(infos) > 6:
                    client = infos[0].xpath('div[2]/text()').extract_first()
                    price = infos[1].xpath('div[2]/text()').extract_first()
                    class_type1 = infos[2].xpath('div[2]/text()').extract()
                    class_type2 = infos[3].xpath('div[2]/text()').extract()
                    class_type = class_type1 + class_type2
                    date1 = infos[5].xpath('div[2]/text()').extract()
                    hour = infos[4].xpath('div[2]/text()').extract()
                    date = date1 + hour
                    campus = infos[6].xpath('div[2]/div/span/text()').extract_first()
                else:
                    client = infos[0].xpath('div[2]/text()').extract_first()
                    price = infos[0].xpath('div[2]/text()').extract_first()
                    class_type1 = infos[1].xpath('div[2]/text()').extract()
                    class_type2 = infos[2].xpath('div[2]/text()').extract()
                    class_type = class_type1 + class_type2
                    date1 = infos[4].xpath('div[2]/text()').extract()
                    hour = infos[3].xpath('div[2]/text()').extract()
                    date = date1 + hour
                    campus = infos[5].xpath('div[2]/div/span/text()').extract_first()
            if not details:
                details = s.xpath(
                '//div[@id="ajaxContent1"]/div[@class="ComTab_Item"][2]/div[@class="ComTab_Item_body"]').extract_first()
        else:
            course = s.xpath('//div[@class="ZcTabCPro"]')
            if course:
                if len(course) > 6:
                    price = course[0].xpath('div[2]/span/text()').extract_first()
                    client = course[1].xpath('div[2]/text()').extract_first()
                    class_type1 = course[2].xpath('div[2]/text()').extract()
                    class_type2 = course[3].xpath('div[2]/text()').extract()
                    class_type = class_type1 + class_type2
                    date1 = course[5].xpath('div[2]/text()').extract()
                    hour = course[4].xpath('div[2]/text()').extract()
                    date = date1 + hour
                    campus = course[6].xpath('div[2]/text()').extract_first()
                else:
                    price = course[0].xpath('div[2]/span/text()').extract_first()
                    #client = course[1].xpath('div[2]/text()').extract_first()
                    class_type1 = course[1].xpath('div[2]/text()').extract()
                    class_type2 = course[2].xpath('div[2]/text()').extract()
                    class_type = class_type1 + class_type2
                    date1 = course[4].xpath('div[2]/text()').extract()
                    hour = course[3].xpath('div[2]/text()').extract()
                    date = date1 + hour
                    campus = course[5].xpath('div[2]/text()').extract_first()
            if not details:
                details = s.xpath('//div[@class="ZcTabC"]').extract_first()
        detail = ''
        if details:
            text = remove_tags(details)
            if text:
                detail = ''.join(text.split())
        types = s.xpath('//div[@class="Item_ComTop1"]/div[1]/div')
        if types:
            tcity = types[0].xpath('a[2]/text()').extract_first()
            i = len(tcity) - 3
            type1 = types[1].xpath('a[1]/text()').extract_first()
            if type1:
                type.append(type1[i:])
                type2 = types[1].xpath('a[2]/text()').extract_first()
                if type2:
                    type.append(type2[i:])
                course_name1 = types[2].xpath('text()').extract_first()
                if course_name1:
                    if not course_name:
                        course_name = course_name1.split()[-1]
            else:
                type1 = types[1].xpath('text()').extract_first()
                if type1:
                    type = type.append(type1[i:])
                    course_name1 = types[2].xpath('text()').extract_first()
                    if course_name1:
                        if not course_name:
                            course_name = course_name1.split()[-1]
        else:
            types = s.xpath('//div[@class="top1_in"]/div[1]/div')
            if types:
                tcity = types[0].xpath('a[2]/text()').extract_first()
                i = len(tcity) - 3
                type1 = types[1].xpath('a[1]/text()').extract_first()
                if type1:
                    type.append(type1[i:])
                    type2 = types[1].xpath('a[2]/text()').extract_first()
                    if type2:
                        type.append(type2[i:])
                course_name1 = types[2].xpath('text()').extract_first()
                if course_name1:
                    if not course_name:
                        course_name = course_name1.split()[-1]
        item['name'] = name
        item['course'] = course_name
        item['status'] = student_num
        item['type'] = type
        item['class_type'] = class_type
        item['student_num'] = student_num
        item['date'] = date
        item['campus'] = campus
        item['price'] = price
        item['detail'] = detail
        item['client'] = client
        yield item







