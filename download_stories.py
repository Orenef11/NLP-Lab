from lxml.html import fromstring
import pycurl
from io import BytesIO
import os
from urllib import parse
from time import sleep
from html_parser import open_file_to_read
import logging
from logger import setting_up_logger


STORIES_FILE = r"stories_list.html"
HOST = r"http://www.shortstoryproject.com/he/"


def get_stories_links(root, links_list):
    root = root.findall(".//a")
    if root.__len__() != 0:
        for element in root:
            if "title" in element.attrib.keys():
                links_list.append(element.attrib["title"])


def urlget(url):
    logging.info('Get function start')
    header = BytesIO()
    response = BytesIO()
    curl = pycurl.Curl()
    print(curl)
    print(url)
    curl.setopt(pycurl.URL, url.encode(encoding='utf-8'))
    curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                                  " Chrome/56.0.2924.87 Safari/537.36")
    curl.setopt(pycurl.HEADERFUNCTION, header.write)
    curl.setopt(pycurl.WRITEFUNCTION, response.write)
    curl.setopt(pycurl.COOKIEJAR, 'cookie.txt')
    curl.setopt(pycurl.COOKIEFILE, 'cookie.txt')
    curl.perform()
    curl.close()
    logging.info('Get function end')
    return header, response


def main():
    setting_up_logger('debug', 'info')
    logging.getLogger(__name__)

    file_data = open_file_to_read(STORIES_FILE)
    open_file_to_read(STORIES_FILE)
    root = fromstring(file_data)
    links_list = []

    get_stories_links(root, links_list)
    if links_list.__len__() == 0:
        logging.info("Links not exist error: please check if Please check that you have successfully retrieved the "
                     "links from the 'stories_list.html file")
        exit()

    for link_name in links_list:
        link = HOST + link_name
        path = os.path.join(os.getcwd(), 'html_pages', link_name + '.html')
        if not os.path.exists(path):
            logging.info('Link: {0}'.format(link))
            logging.info('Name: '.format(link.rsplit('/', 2)[1]))
            header, response = urlget(link)
            for line in header.getvalue().splitlines():
                logging.info(line.decode())
            str_response = response.getvalue()

            with open(path, 'wb') as file:
                file.write(str_response)
        sleep(7)


if __name__ == '__main__':
    main()
