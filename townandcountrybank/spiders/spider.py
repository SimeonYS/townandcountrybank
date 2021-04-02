import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import TtownandcountrybankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class TtownandcountrybankSpider(scrapy.Spider):
	name = 'townandcountrybank'
	start_urls = ['https://www.townandcountrybank.com/about-us/news/']

	def parse(self, response):
		articles = response.xpath('//div[@class="accordion-content mceEditable"]//li')
		for article in articles:
			post_links = article.xpath('.//a/@href').get()
			if not 'pdf' in post_links:
				date = article.xpath('.//a/following-sibling::text()').get()
				date = re.findall(r'\w+\s\d+\,\s\d+', date)
				yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//article[@class="main"]//text()[not (ancestor::h1 or ancestor::ul[@class="breadcrumb"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=TtownandcountrybankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
