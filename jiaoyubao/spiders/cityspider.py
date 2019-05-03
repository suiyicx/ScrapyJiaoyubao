from scrapy.spider import CrawlSpider
import redis
from urllib.parse import urljoin


class JiaoyubaoCitySpider(CrawlSpider):
    name = 'jiaoyubao_city'
    allowed_domains = ['jiaoyubao.cn']
    #爬取城市 成都、南宁、绵阳
    start_urls = ['http://cd.jiaoyubao.cn', 'http://nn.jiaoyubao.cn', 'http://mianyang.jiaoyubao.cn']
    #扩展：手动输入城市
    #def __init__(self, city=None, *args, **kwargs): #scrapy crawl cityspider -a city=cd 字母简写
        #super(JiaoyubaoCitySpider,self).__init__(*args,**kwargs)
        #self.__city = city
        #self.start_urls = ['http://%s.jiaoyubao.cn'%city]

    def parse(self, response):
        jiaoyubao = response.url#'http://%s.jiaoyubao.cn' % self.__city
        menus = 'jiaoyubao:start_urls'
        pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=1)
        r = redis.Redis(connection_pool=pool)
        pipe = r.pipeline(transaction=True)
        urls = response.xpath('//div[4]/div[1]/div/dl')
        for d in range(4):
            url1 = urls[d].xpath('dd/a/@href').extract()
            url1 = set(url1)
            url3 = []
            for url2 in url1:
                url3.append(urljoin(jiaoyubao, url2))
            for url in url3:
                pipe.lpush(menus, url)
            pipe.execute()
