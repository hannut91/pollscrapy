import scrapy
import logging
from tutorial.items import Boxoffice, Artist,Tour
import re
from scrapy.http import Request, FormRequest
from scrapy.spider import BaseSpider


class PollSpider(scrapy.Spider):

    name = 'poll'
    allowed_domains = ['http://www.pollstarpro.com/']

    def start_requests(self):
        logging.info("@@@@@@@@request is called @@@@@")
        yield FormRequest(url="https://www.pollstarpro.com/controls/content/mainLoginHandler.aspx",
                    formdata={'ctl16$userNameText': 'demo', 'ctl16$passwordText': 'sxsw2016'},
                    callback=self.post_after)

    def post_after(self,response):
        logging.info("@@@@@ post_after is called @@@@@")
        yield Request(url="http://www.pollstarpro.com/search.aspx?ArticleID=35&id=home"
                      ,callback=self.parse,dont_filter=True)

    def parse(self, response):
        logging.info("@@@@@@@@parse is called @@@@@@")
        table=response.xpath('//table[@class="datatable"]')
        tr=table.xpath('.//tr')[1:]
        for sel in tr:
            item=Boxoffice()
            row_items=sel.xpath('.//td')
            str=(row_items[0].xpath('text()').extract()
                +row_items[0].xpath('./div/text()').extract())
            sum=''
            temp=[]

            for arr in str:
                if not arr.isspace():
                    if not re.search('[a-zA-Z]',arr):
                        if not re.sub(r'\D',"",arr)in temp:
                            temp.append(re.sub(r'\D',"",arr))
            temp2=[]
            for tem in temp:
                temp2.append("20"+tem[4:]+tem[0:2]+tem[2:4])
            item['date']=temp2

            temp3=[]
            str=row_items[1].xpath('./a/text()').extract()
            for arr in  str:
                temp3.append(re.sub(r'\"',"",arr))
            item['artist']=temp3
            urlt = row_items[1].xpath('./a/@href').extract()[0]

            yield Request(url=urlt, callback=self.artist_page_parse, dont_filter=True)

            str=row_items[1].xpath('./div/a/text()').extract()
            for arr in str:
                if not arr.isspace():
                    temp=re.sub(r'\t|\n|\r',"",arr)
            item['venue']=temp
            str=row_items[1].xpath('./div/text()').extract()
            for arr in str:
                if not arr.isspace():
                    if "," in arr:
                        temp=re.sub(r'\t|\n|\r',"",arr)
                        item['city']=temp
                    elif "/" in arr:
                        temp=re.sub(r'\t|\n|\r',"",arr).split(',',1)
                        item['promoter']=temp
                    else:
                        temp=re.sub(r'\t|\n|\(|\)|\r',"",arr)
                        item['promoter']=temp
            item['support']=row_items[2].xpath('.//a/text()').extract()
            str=row_items[3].xpath('./b/text()').extract()
            for arr in str:
                temp=re.sub(r'\,',"",arr)
                item['sold']=temp
            str=row_items[4].xpath('./b/text()').extract()
            for arr in str:
                temp=re.sub(r'\$|\,',"",arr)
                item['money']=temp
            yield item

    def artist_page_parse(self, response):
        logging.info("@@@@@ artist_page_parse is called @@@@@")

        if "Show More" in response.xpath('//a[@id="ctl10_ctl01_lbShowAllArtistTH"]/text()').extract():
            logging.info("@@@@@ First Show More @@@@@")
            yield FormRequest.from_response(response,formname="form1",
                    formdata={'__EVENTTARGET': 'ctl10$ctl01$lbShowAllArtistTH', '__EVENTARGUMENT': ''},
                    callback=self.artist_page_parse,dont_filter=True)
        elif "Show More" in response.xpath('//a[@id="ctl10_ctl01_lbShowAllArtistRB"]/text()').extract():
            logging.info("@@@@@ Second Show More @@@@@")
            yield FormRequest.from_response(response,formname="form1",
                    formdata={'__EVENTTARGET': 'ctl10$ctl01$lbShowAllArtistRB', '__EVENTARGUMENT': ''},
                    callback=self.artist_page_parse,dont_filter=True)

        else:
            logging.info("@@@@@ PASS @@@@@")

            item = Artist()

            name = response.xpath('//div[@class="pageSubHeader"]/h3/span/text()').extract()
            logging.info(name)
            item['name'] = name

            div = response.xpath('//div[@id="pod-artistQuickBytes"]')
            table = div.xpath('.//table')
            tr = table[0].xpath('.//tr')
            td = tr[0].xpath('.//td')
            item['genre'] = td[1].xpath('./div/span/text()').extract()
            td = tr[1].xpath('.//td')
            item['headlineshows'] = td[1].xpath('./div/span/text()').extract()
            td = tr[2].xpath('.//td')
            item['cobillshows'] = td[1].xpath('./div/span/text()').extract()
            tr = table[2].xpath('.//tr')
            td = tr[0].xpath('.//td')
            item['totalheadlinerpts'] = td[1].xpath('./div/span/text()').extract()
            td = tr[1].xpath('.//td')
            item['avgticketsold'] = td[1].xpath('./div/span/text()').extract()
            tr = table[3].xpath('.//tr')
            td = tr[0].xpath('.//td')
            item['avggross'] = td[1].xpath('./div/span/text()').extract()

            tour = Tour()

            table = response.xpath('//table[@class="datatable"]')
            for ta in table:
                tr = ta.xpath('.//tr')[1:]
                for seltr in tr:
                    tdlist = seltr.xpath('.//td')

                    str = re.sub(r'\D',"",tdlist[0].xpath('./span/text()').extract()[0])
                    temp2 = []
                    if "50" < str[4:]:
                        temp2.append("19" + str[4:]+str[0:2]+str[2:4])
                    else:
                        temp2.append("20" + str[4:] + str[0:2] + str[2:4])
                    tour['date']=temp2

                    tour['venue'] = re.sub(r'\r|\n|\t',"",tdlist[2].xpath('./a/text()').extract()[0])
                    tour['city'] = re.sub(r'\r|\n|\t',"",tdlist[3].xpath('./a/text()').extract()[0])
                    tdlist[4].xpath('./img/@src')
                    logging.info(tdlist[4].xpath('./img/@src'))
                    if tdlist[4].xpath('./img/@src'):
                        tour['boxoffice'] = 1
                    else:
                        tour['boxoffice'] = 0
                    tour['artist'] = name
                    yield tour
            yield item


# yield Request(url="http://www.pollstarpro.com/search.aspx?ArticleID=35&id=home",callback=self.yoon_test)
#    name = 'poll'
#    allowed_domains = ['http://www.pollstarpro.com/']
#    start_urls = [
#        "http://www.pollstarpro.com/",
#    ]
#    def parse(self, response):
#        logging.info("@@@@@ parse is called @@@@@")
#        return scrapy.FormRequest.from_response(
#            response,
#            formdata={'ctl16$userNameText': 'demodd', 'ctl16$passwordText': 'sxsw2016'},
#            callback=self.after_login
#        )
#    def after_login(self, response):
#        logging.info("@@@@@ after_login is called @@@@@")
#        if "authentication failed" in response.body:
#            self.logger.error("Login failed")
#            return





        # you are logged in here

#    name = "dmoz"
#    allowed_domains = ["http://www.billboard.com"]
#    start_urls = [
#        "http://www.billboard.com/biz/current-boxscore/",
#    ]
#    def parse(self, response):
#        table = response.xpath('//table[@class="boxscore_table"]')
#        tr = table.xpath('.//tr')[1:]
#        for sel in tr:
#            item = DmozItem()
#            row_items = sel.xpath('.//td')
#            item['rank'] = row_items[0].xpath('text()').extract()
#            item['artist'] = row_items[1].xpath('text()').extract()
#            item['venue'] = row_items[2].xpath('text()').extract()
#            item['city'] = row_items[3].xpath('text()').extract()
#            item['eventdates'] = row_items[4].xpath('text()').extract()
#            item['grosssales'] = row_items[5].xpath('text()').extract()
#            item['attend'] = row_items[6].xpath('text()').extract()
#            item['shows'] = row_items[7].xpath('text()').extract()
#            item['prices'] = row_items[8].xpath('text()').extract()
#            item['promoters'] = row_items[9].xpath('text()').extract()
#            yield item


#    def parse(self, response):
#        for href in response.css("ul.directory.dir-col > li > a::attr('href')"):
#            url = response.urljoin(href.extract())
#            yield scrapy.Request(url, callback=self.parse_dir_contents)

#    def parse_dir_contents(self, response):
#        for sel in response.xpath('//ul/li'):
#            item = DmozItem()
#            item['title'] = sel.xpath('a/text()').extract()
#            item['link'] = sel.xpath('a/@href').extract()
#            item['desc'] = sel.xpath('text()').extract()
#            yield item

 
            