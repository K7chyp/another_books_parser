from bs4 import BeautifulSoup
import scrapy


class BooksParser(scrapy.Spider):
    name = "spider"

    def start_requests(self):
        for author in ("lev-tolstoy", "fedor-dostoevskiy", "mihail-bulgakov"):
            self.last_page = True
            page_num = 0
            while self.last_page:
                page_num += 1
                yield scrapy.Request(
                    url=f"https://knijky.ru/authors/{author}?page={page_num}",
                    callback=self.parse,
                )

    def parse(self, response):
        self.soup = BeautifulSoup(response.text, "lxml")
        for part_of_page in self.soup.find_all(
            "div", {"class": "views-field views-field-title"}
        ):
            current_element = part_of_page.find(
                "span", {"class": "field-content"}
            ).find("a")
            yield {
                "text": current_element.text,
                "href": current_element.get("href"),
            }
        if response.status == 404:
            self.last_page = False
