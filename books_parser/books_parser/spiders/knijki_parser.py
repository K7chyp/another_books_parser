from bs4 import BeautifulSoup
import scrapy
import csv


class ParseBooksByAuthorName(scrapy.Spider):
    name = "author_crawler"

    def start_requests(self):
        for author in ("lev-tolstoy", "fedor-dostoevskiy", "mihail-bulgakov"):
            self.last_page = True
            self.author_ = author
            page_num = 0
            while self.last_page:
                yield scrapy.Request(
                    url=f"https://knijky.ru/authors/{author}?page={page_num}",
                    callback=self.parse,
                )
                page_num += 1
                if not self.last_page:
                    break

    def parse(self, response):
        self.soup = BeautifulSoup(response.text, "lxml")
        if response.status == 404:
            self.last_page = False
        for element_with_title in self.soup.find_all(
            "div", {"class": "views-field views-field-title"}
        ):
            current_element_contains_title = element_with_title.find(
                "span", {"class": "field-content"}
            ).find("a")

            yield {
                "title": current_element_contains_title.text,
                "href": current_element_contains_title.get("href"),
                "author": self.author_,
            }


class PageTextParser(scrapy.Spider):
    name = "text_crawler"

    def start_requests(self):
        main_page_name = "https://knijky.ru"
        with open("data.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.current_title = row["title"]
                self.author = row["author"]
                self.last_page = True
                page_num = 0
                while self.last_page:
                    self.current_url = (
                        main_page_name + row["href"] + "?page={}".format(page_num)
                        if page_num != 0
                        else main_page_name + row["href"]
                    )
                    page_num += 1
                    if not self.last_page:
                        break
                    yield scrapy.Request(
                        url=self.current_url,
                        callback=self.parse,
                    )

    def parse(self, response):
        if response.status == 404:
            self.last_page = False
        self.soup = BeautifulSoup(response.text, "lxml")
        yield {
            "text": "".join(
                current_text.text for current_text in self.soup.find_all("table")
            )
            .replace("\xa0", "")
            .replace("\n", "")
            .replace("\r", ""),
            "href": self.current_url,
            "title": self.current_title,
            "author": self.author,
        }
