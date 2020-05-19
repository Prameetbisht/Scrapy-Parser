import scrapy
from scrapy import Request
import pandas as pd


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://books.toscrape.com/index.html',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        book_links = response.xpath('//*[@class="image_container"]/a/@href').extract()
        for book_link in book_links:
            # into_book = book_link.xpath('.//a/@href').extract_first()
            into_book_url = response.urljoin(book_link)
            # print("Book link :", into_book_url)
            yield Request(into_book_url, callback=self.parsebook)

        next_page = response.xpath('.//*[@class="next"]/a/@href').extract_first()
        next_page_url = response.urljoin(next_page)
        yield Request(next_page_url, callback=self.parse)

    def parsebook(self, response):
        book_name = response.xpath('//*[@class="col-sm-6 product_main"]/h1/text()').extract_first()
        book_category = response.xpath('//*[@class="breadcrumb"]/li[3]/a/text()').extract_first()
        book_availability = response.xpath('//*[@class="table table-striped"]/tr[6]/td/text()').extract_first()
        book_price_tax = response.xpath('//*[@class="table table-striped"]/tr[4]/td/text()').extract_first()
        book_rating = \
            response.xpath('.//*[@class="col-sm-6 product_main"]/p[contains(@class,"star-rating")]/@class').extract()[
                0].split()[1]
        book_img_url = response.urljoin(response.xpath('//*[@class="item active"]/img/@src').extract_first())
        book_desc = response.xpath('.//p/text()').extract()[10]

        x = {"Description": book_desc, "Name": book_name, "Category": book_category,
             "Availability": book_availability, "Price": book_price_tax, "Rating": book_rating,
             "Image URL": book_img_url}
        yield x
