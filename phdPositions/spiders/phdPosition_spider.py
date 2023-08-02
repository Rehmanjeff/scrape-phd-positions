from pathlib import Path
import re
import scrapy

class PhdSpider(scrapy.Spider):
    name = "phd"

    def start_requests(self):
        urls = [
            "https://scholarshipdb.net/scholarships?listed=Last-30-days&page=3&q=iot+phd"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        data_response = {}

        for phd in response.css(".position-details"):
           
            heading = phd.xpath('string(//h1)').extract_first()
            heading = "".join([re.sub("  +"," ",x.strip(" ")) for x in "".join(heading).split("\n")])

            university_filter_url = phd.css("h2 a:first-child::attr(href)").get()
            university = phd.css("h2 a:first-child::text").get()
            country = phd.css("h2 a:last-child::text").get()

            summary = phd.css(".summary div:first-child")
            summary_text = summary.css("span:first-child::text").get()
            last_update = summary.css("span:nth-child(2)::text").get() if "Updated: " == summary_text else None

            deadline = None
            my_summary = {}
            for detail in phd.css(".summary div"):
                text = detail.css("span:first-child::text").get()
                if text:
                    text = text.replace(" ","")
                    text = text.replace(":","")
                else:
                    print("ELSE START")
                    print(detail)
                    print("ELSE END")

                if text == "Deadline":
                    value = detail.css('div::text')[1].get()
                    if value:
                        value = "".join([re.sub("  +"," ",x.strip(" ")) for x in "".join(value).split("\n")])
                else:
                    value = detail.css("span:nth-child(2)::text").get() 

                my_summary.update({
                    text: value
                })

            url = response.css("a.btn.btn-primary::attr(href)").get()

            if heading is not None:
                
                yield {
                    "apply_url": url,
                    "position" : heading,
                    "university": university,
                    "university_filter": university_filter_url,
                    "country": country,
                    "summary": my_summary
                }



        for phd in response.css("h4 a"):
            if phd.css("a::text").get() is not None and phd.css("a::attr(href)").get() is not None:
                deep_link = phd.css("a::attr(href)").get()
                deep_link =  "https://scholarshipdb.net"+deep_link
                data_response = {
                    "text": phd.css("a::text").get(),
                    "url": deep_link
                }
                
                yield scrapy.Request(url=deep_link, callback=self.parse)

        # Scrape througth pages
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

        # Write to file
        # page = response.url.split("/")[-2]
        # filename = f"phd-{page}.html"
        # Path(filename).write_bytes(next_page)
        # self.log(f"Saved file {filename}")