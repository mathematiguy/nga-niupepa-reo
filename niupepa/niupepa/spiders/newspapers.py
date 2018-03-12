# -*- coding: utf-8 -*-
import re
from urlparse import urljoin
import scrapy

class NewspapersSpider(scrapy.Spider):
    name = 'newspapers'
    # allowed_domains = ['http://www.nzdl.org/']
    nzdl_base_url = "http://www.nzdl.org/"
    start_urls = ['http://www.nzdl.org/gsdlmod?gg=text&e=p-00000-00---off-0niupepa--00-0----0-10-0---0---0direct-10---4-------0-1lpc--11-en-50---20-about---00-0-1-00-0-0-11-1-0utfZz-8-00-0-0-11-10-0utfZz-8-00&a=d&cl=CL1']

    def parse(self, response):

        name_tags = (response
            .xpath('/html/body/div/div[4]/div/table/tr/td[3]')
            .extract()
        )

        paper_names = [re.sub("<[^>]+>|\([^\)]+\)", "", name_tag).strip() \
                        for name_tag in name_tags]

        paper_links = (response
            .xpath('/html/body/div/div[4]/div/table/tr/td[@valign="top"]/a/@href')
            .extract()
        )

        assert len(paper_names) == len(paper_links)

        for name, link in zip(paper_names, paper_links):
            yield scrapy.Request(
                url = urljoin(self.nzdl_base_url, link),
                meta = dict(paper_name = name, paper_link = link),
                callback = self.parse_paper)

    def parse_paper(self, response):
        issue_names = (response
            .xpath("/html/body/div/div[4]/div/table[2]/tr/td[2]/table/tr/td[@valign=\"top\"][2]")
            .re(">\s*(.+)\s+<"))

        issue_names = [issue_name.strip() for issue_name in issue_names]

        issue_links = (response
            .xpath('/html/body/div/div[4]/div/table[2]/tr/td[2]/table/tr/td[@valign="top"]/a/@href')
            .extract()
        )

        assert len(issue_names) == len(issue_links)

        for name, link in zip(issue_names, issue_links):
            output_dict = dict(issue_name = name, issue_link = link)
            output_dict.update(response.meta)
            yield scrapy.Request(
                url = urljoin(self.nzdl_base_url, link),
                meta = output_dict,
                callback = self.parse_issue)

    def parse_issue(self, response):
        page_text = (response
            .xpath("/html/body/div/div[4]/div/center/table[1]/table/tr/td")
            .extract()
        )

        next_link = (response
            .xpath('///*/center/table/tr/td[@align="right"]/a/@href')
            .extract()
        )

        if len(next_link) > 0:
            # There is a next page link to follow
            yield scrapy.Request(
                url = urljoin(self.nzdl_base_url, next_link[0]),
                callback = self.parse_issue)
        else:
            output_dict = dict(text = page_text, url = response.url)
            output_dict.update(response.meta)
            yield output_dict

        



