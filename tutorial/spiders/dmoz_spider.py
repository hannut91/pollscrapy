import logging
from tutorial.items import Boxoffice, Artist,Tour,Venue, City
import re
from scrapy.http import Request, FormRequest
from scrapy.spiders.crawl import CrawlSpider
from scrapy.spiders import Rule
from scrapy.utils.spider import iterate_spider_output
from scrapy.linkextractors import LinkExtractor

class PollSpider(CrawlSpider):
    name = 'poll'
    allowed_domains = ['pollstarpro.com']
    start_urls=[
        "http://www.pollstarpro.com/search.aspx?ArticleID=35&id=home"
    ]
    rules = [
        Rule(LinkExtractor(allow=(r'http\:\/\/www\.pollstarpro\.com\/search\.aspx\?ArticleID=\d{1,}&id=research&ArtistID=\d{1,}&ScienceArtistID=\d{1,}'),allow_domains=['pollstarpro.com'], unique=True),
            follow=True, callback='artist_page_parse'
        ),
        #Rule(LinkExtractor(allow=(r'http\:\/\/www\.pollstarpro\.com\/search\.aspx\?ArticleID=\d{1,}&id=research&VenueID=\d{1,}&ScienceID=\d{1,}'),allow_domains=['pollstarpro.com'], unique=True),
        #     follow=True, callback='venue_page_parse'
        #),
        #Rule(LinkExtractor(allow=(r'http\:\/\/www\.pollstarpro\.com\/search\.aspx\?ArticleID=\d{1,}&ScienceID=\d{1,}&VenueID=\d{1,}&id=research'),allow_domains=['pollstarpro.com'], unique=True),
        #     follow=True, callback='venue_page_parse'
        #),
        #Rule(LinkExtractor(allow=(r'http\:\/\/www\.pollstarpro\.com\/search\.aspx\?ArticleID=\d{1,}&id=research&CityID=\d{1,}'),allow_domains=['pollstarpro.com'], unique=True),
        #     follow=True, callback='city_page_parse'
        #)
    ]
    def process_value(self, value):
        logging.info("@@@@@ process_value is called")
        m = re.search("javascript:__doPostBack('ctl10$ctl01$lbNext1','')",value)
        if m:
            logging.info("m is here")

    def start_requests(self):
        logging.info("@@@@@ start_requests is called @@@@@")
        self._postinit_reqs = super(PollSpider, self).start_requests()
        return iterate_spider_output(self.login())

    def login(self):
        logging.info("@@@@@ login is called @@@@@")
        return FormRequest(url="https://www.pollstarpro.com/controls/content/mainLoginHandler.aspx",
                    formdata={'ctl16$userNameText': 'nujabes8', 'ctl16$passwordText': 'sxsw2016'},callback=self.logged_in)

    def logged_in(self, response):
        logging.info("@@@@@ logged_in is called @@@@@")
        if "Hello, Jinwook" in response.body:
            logging.info("@@@@@ Login Success! @@@@@")
            return self.initialized()
        else:
            logging.info("@@@@@ Login Fail.. @@@@@")


    def initialized(self, response=None):
        logging.info("@@@@@ initialized is called @@@@@")
        for url in self.start_urls:
            yield Request(url=url)

    def parse_start_url(self, response):
        logging.info("@@@@@@@@parse_start_url is called @@@@@@")

        seltemp = response.xpath('//select[@name="ctl10$ctl01$cboCount1"]')
        selopt = seltemp.xpath('.//option[@selected="selected"]/text()').extract()[0]

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
        response.meta['depth']=1
        if response.xpath('//a[@id="ctl10_ctl01_lbNext1"]/@href'):
            logging.info(response.xpath('//input[@id="ctl10_ctl01_txtPage1"]/@value'))
            yield FormRequest.from_response(response,formname="form1",
                    formdata={'__EVENTTARGET': 'ctl10$ctl01$lbNext1', '__EVENTARGUMENT': ''})

    def artist_page_parse(self, response):
        logging.info("@@@@@ artist_page_parse is called @@@@@")
        tmstr = ""
        tmstr2 = ""
        tmstr3 = ""
        tmstr4 = ""

        if response.url == "http://www.pollstarpro.com/opencontent.aspx?ArticleID=14194&id=home":
            logging.info("@@@@@ Link follow failed @@@@@")

        if response.xpath('//span[@id="ctl10_ctl01_lblArtistTHCount"]') :
            str = response.xpath('//span[@id="ctl10_ctl01_lblArtistTHCount"]/text()').extract()[0]
            nxstr = str.split('of',1)
            tmstr = re.sub(r'\D',"",nxstr[0])
            tmstr2 = re.sub(r'\D',"",nxstr[1])
        if response.xpath('//span[@id="ctl10_ctl01_lblArtistRBCount"]/text()') :
            str2 = response.xpath('//span[@id="ctl10_ctl01_lblArtistRBCount"]/text()').extract()[0]
            nxstr2 = str2.split('of',1)
            tmstr3 = re.sub(r'\D',"",nxstr2[0])
            tmstr4 = re.sub(r'\D',"",nxstr2[1])
        if tmstr != tmstr2:
            logging.info("@@@@@ Artist First Show More @@@@@")
            yield FormRequest.from_response(response,formname="form1",
                    formdata={'__EVENTTARGET': 'ctl10$ctl01$lbShowAllArtistTH', '__EVENTARGUMENT': ''},
                    callback=self.artist_page_parse,dont_filter=True)
        elif tmstr3 != tmstr4 :
            logging.info("@@@@@ Artist Second Show More @@@@@")
            yield FormRequest.from_response(response,formname="form1",
                    formdata={'__EVENTTARGET': 'ctl10$ctl01$lbShowAllArtistRB', '__EVENTARGUMENT': ''},
                    callback=self.artist_page_parse,dont_filter=True)
        else:
            logging.info("@@@@@ artist_page_parse PASS @@@@@")
            logging.info(response.url)
            item = Artist()

            name = response.xpath('//div[@class="pageSubHeader"]/h3/span/text()').extract()
            item['name'] = name

            if response.xpath('//span[@id="ctl10_ctl01_lblGenre"]/text()'):
                item['genre'] = response.xpath('//span[@id="ctl10_ctl01_lblGenre"]/text()').extract()
            if response.xpath('//span[@id="ctl10_ctl01_lblHeadlineShows"]/text()'):
                temp = response.xpath('//span[@id="ctl10_ctl01_lblHeadlineShows"]/text()').extract()[0]
                item['headlineshows'] = re.sub(r'\D',"",temp)
            if response.xpath('//span[@id="ctl10_ctl01_lblCoBillShows"]/text()'):
                temp = response.xpath('//span[@id="ctl10_ctl01_lblCoBillShows"]/text()').extract()[0]
                item['cobillshows'] = re.sub(r'\D',"",temp)
            if response.xpath('//span[@id="ctl10_ctl01_lblQB1"]/text()'):
                temp = response.xpath('//span[@id="ctl10_ctl01_lblQB1"]/text()').extract()[0]
                item['totalheadlinerpts'] = re.sub(r'\D',"",temp)
            if response.xpath('//span[@id="ctl10_ctl01_lblQB2"]/text()'):
                temp = response.xpath('//span[@id="ctl10_ctl01_lblQB2"]/text()').extract()[0]
                item['avgticketsold'] = re.sub(r'\D',"",temp)
            if response.xpath('//span[@id="ctl10_ctl01_lblQB3"]/text()'):
                temp = response.xpath('//span[@id="ctl10_ctl01_lblQB3"]/text()').extract()[0]
                item['avggross'] = re.sub(r'\D',"",temp)

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

                    tour['venue'] = re.sub(r'\t|\r|\n',"",tdlist[2].xpath('./a/text()').extract()[0])
                    temp = tdlist[3].xpath('./a/text()').extract()[0].split(',',2)
                    if len(temp) == 2:
                        temp2 = re.sub(r'\s',"",temp[0])
                        temp3 = re.sub(r'\s',"",temp[1])
                        temp4 = temp2+", "+temp3
                        tour['city'] = temp4
                    elif len(temp) ==3:
                        temp2 = re.sub(r'\s',"",temp[0])
                        temp3 = re.sub(r'\s',"",temp[1])
                        temp4 = re.sub(r'\s',"",temp[2])
                        temp5 = temp2 + ", "+temp3+ ", "+temp4
                        tour['city'] = temp5
                    if tdlist[4].xpath('./img/@src'):
                        tour['boxoffice'] = 1
                    else:
                        tour['boxoffice'] = 0
                    tour['artist'] = name
                    yield tour
            yield item

    def venue_page_parse(self,response):
        logging.info("@@@@@ venue_page_parse is called @@@@@")
        tmstr = ""
        tmstr2 = ""
        tmstr3 = ""
        tmstr4 = ""

        if response.url == "http://www.pollstarpro.com/opencontent.aspx?ArticleID=14194&id=home":
            logging.info("@@@@@ Link follow failed @@@@@")
            self.login()
            return
        if response.xpath('//span[@id="ctl10_ctl01_lblVenueTHCount"]') :
            str = response.xpath('//span[@id="ctl10_ctl01_lblVenueTHCount"]/text()').extract()[0]
            nxstr = str.split('of',1)
            tmstr = re.sub(r'\D',"",nxstr[0])
            tmstr2 = re.sub(r'\D',"",nxstr[1])
        if response.xpath('//span[@id="ctl10_ctl01_lblVenueRBCount"]/text()') :
            str2 = response.xpath('//span[@id="ctl10_ctl01_lblVenueRBCount"]/text()').extract()[0]
            nxstr2 = str2.split('of',1)
            tmstr3 = re.sub(r'\D',"",nxstr2[0])
            tmstr4 = re.sub(r'\D',"",nxstr2[1])
        if tmstr != tmstr2:
            logging.info("@@@@@ Venue First Show More @@@@@")
            yield FormRequest.from_response(response,formname="form1",
                    formdata={'__EVENTTARGET': 'ctl10$ctl01$lbShowAllVenueTH', '__EVENTARGUMENT': ''},
                    callback=self.venue_page_parse,dont_filter=True)
        elif tmstr3 != tmstr4 :
            logging.info("@@@@@ Venue Second Show More @@@@@")
            yield FormRequest.from_response(response,formname="form1",
                    formdata={'__EVENTTARGET': 'ctl10$ctl01$lbShowAllVenueRB', '__EVENTARGUMENT': ''},
                    callback=self.venue_page_parse,dont_filter=True)
        else:
            logging.info("@@@@@ venue_page_parse PASS @@@@@")
            venue = Venue()

            name = response.xpath('//span[@id="ctl10_ctl01_lblVenueName"]/text()').extract()
            venue['name'] = name

            if response.xpath('//span[@id="ctl10_ctl01_lblBO1"]/text()'):
                temp =  response.xpath('//span[@id="ctl10_ctl01_lblBO1"]/text()').extract()[0]
                venue['avgsold'] = re.sub(r'\,',"",temp)
            if response.xpath('//span[@id="ctl10_ctl01_lblBO2"]/text()'):
                temp =  response.xpath('//span[@id="ctl10_ctl01_lblBO2"]/text()').extract()[0]
                venue['avggross'] = re.sub(r'\,|\$',"",temp)

            city =  response.xpath('//a[@id="ctl10_ctl01_hlCityID"]/text()').extract()
            venue['city'] = city

            tour = Tour()
            table = response.xpath('//table[@class="datatable"]')
            for ta in table:
                tr = ta.xpath('.//tr')[1:]
                for seltr in tr:
                    seltr.xpath('./td/text()').extract()
                    tdlist = seltr.xpath('.//td')
                    str = re.sub(r'\D',"",tdlist.xpath('./text()').extract()[0])
                    temp2 = []
                    if "50" < str[4:]:
                        temp2.append("19" + str[4:]+str[0:2]+str[2:4])
                    else:
                        temp2.append("20" + str[4:] + str[0:2] + str[2:4])
                    tour['date']=temp2

                    tour['artist'] = re.sub(r'\r|\n|\t',"",tdlist[1].xpath('./a/text()').extract()[0])
                    if tdlist[3].xpath('./img/@src'):
                        tour['boxoffice'] = 1
                    else:
                        tour['boxoffice'] = 0
                    tour['city'] = city
                    tour['venue'] = name
                    yield tour
            yield venue

    def city_page_parse(self, response):
        logging.info("@@@@@ city_page_parse is called @@@@@")
        tmstr = ""
        tmstr2 = ""
        tmstr3 = ""
        tmstr4 = ""

        if response.url == "http://www.pollstarpro.com/opencontent.aspx?ArticleID=14194&id=home":
            logging.info("@@@@@ Link follow failed @@@@@")
            self.login()
            return

        if response.xpath('//span[@id="ctl10_ctl01_cityTHCountLbl"]') :
            str = response.xpath('//span[@id="ctl10_ctl01_cityRBCountLbl"]/text()').extract()
            for selstr in str:
                if not selstr.isspace():
                    nxstr = selstr.split('of',1)
                    tmstr = re.sub(r'\D',"",nxstr[0])
                    tmstr2 = re.sub(r'\D',"",nxstr[1])
        if response.xpath('//span[@id="ctl10_ctl01_cityRBCountLbl"]/text()') :
            str2 = response.xpath('//span[@id="ctl10_ctl01_cityRBCountLbl"]/text()').extract()[0]
            nxstr2 = str2.split('of',1)
            tmstr3 = re.sub(r'\D',"",nxstr2[0])
            tmstr4 = re.sub(r'\D',"",nxstr2[1])
        if tmstr != tmstr2:
            logging.info("@@@@@ City First Show More @@@@@")
            yield FormRequest.from_response(response,formname="form1",
                    formdata={'__EVENTTARGET': 'ctl10$ctl01$showAllCityTHLinkBtn', '__EVENTARGUMENT': ''},
                    callback=self.city_page_parse,dont_filter=True)
        elif tmstr3 != tmstr4 :
            logging.info("@@@@@ City Second Show More @@@@@")
            yield FormRequest.from_response(response,formname="form1",
                    formdata={'__EVENTTARGET': 'ctl10$ctl01$showAllCityRBLinkBtn', '__EVENTARGUMENT': ''},
                    callback=self.city_page_parse,dont_filter=True)
        else:
            logging.info("@@@@@ city_page_parse PASS @@@@@")

            city = City()
            tour = Tour()
            name = response.xpath('//span[@id="ctl10_ctl01_cityNameLbl"]/text()').extract()
            city['name'] = name

            table = response.xpath('//table[@class="datatable"]')
            for seltable in table:
                tr = seltable.xpath('.//tr')[1:]
                for seltr in tr:
                    td = seltr.xpath('.//td')
                    str = re.sub(r'\D',"",td[0].xpath('./span/text()').extract()[0])
                    temp2 = []
                    if "50" < str[4:]:
                        temp2.append("19" + str[4:]+str[0:2]+str[2:4])
                    else:
                        temp2.append("20" + str[4:] + str[0:2] + str[2:4])
                    tour['date']=temp2
                    venue = td[1].xpath('./a/text()').extract()[0]
                    tour['venue'] = re.sub(r'\t|\n|\r',"",venue)
                    artist = td[2].xpath('./a/text()').extract()[0]
                    tour['artist'] = re.sub(r'\t|\n|\r',"",artist)
                    if td[3].xpath('./img/@src'):
                        tour['boxoffice'] = 1
                    else:
                        tour['boxoffice'] = 0
                    yield tour

            yield city



