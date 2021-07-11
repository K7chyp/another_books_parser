from bs4 import BeautifulSoup
import scrapy


class ExampleSpider(scrapy.Spider):
    name = "spider"

    def start_requests(self):
        last_page = True
        page_num = 0
        while last_page:
            url = f"https://knijky.ru/authors/lev-tolstoy?page={page_num}"
            page_num += 1
            yield scrapy.Request(url=url, callback=self.parse)
            last_page = scrapy.Request(url=url, callback=self.parse).response.status == 200

    def parse(self, response):
        self.soup = BeautifulSoup(response.text, "lxml")
        for part_of_page in self.soup.find_all(
            "div", {"class": "views-field views-field-title"}
        ):
            current_element = part_of_page.find(
                "span", {"class": "field-content"}
            ).find("a")

            yield {"text": current_element.text, "href": current_element.get("href")}
