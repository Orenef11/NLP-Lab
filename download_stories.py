from lxml.html import fromstring
import pycurl
from io import BytesIO
import os
from urllib import parse
import time

def open_file_to_read(path):
    file_data = ""
    try:
        with open(path, 'r', encoding='utf8') as f:
            file_data = f.read()
    except FileNotFoundError as e:
        exit("Error: File not found error({0}): {1}\nThe path file is {2}".format(e.errno, e.strerror, path))
    except PermissionError as e:
        exit("Error: Permission denied({0}): {1}\nThe path file is {2}".format(e.errno, e.strerror, path))
    except:
        exit("Error: Unable to create the file!\nThe path file is {0}".format(path))

    return file_data



def urlget(url):
    print('Get function start')
    header = BytesIO()
    response = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36")
    curl.setopt(pycurl.HEADERFUNCTION, header.write)
    curl.setopt(pycurl.WRITEFUNCTION, response.write)
    curl.setopt(pycurl.COOKIEJAR, 'cookie.txt')
    curl.setopt(pycurl.COOKIEFILE, 'cookie.txt')
    curl.perform()
    curl.close()
    print('Get function end')
    return header, response

def parse_description(node):
    links = []
    def recurse(node):
        if node.tag == 'a':
            for key, value in node.items():
                if key == 'href':
                    links.append(value)
        for element in node:
            recurse(element)
    recurse(node)
    return links


def parse_links_list_file(file):
    links = []
    def recurse(node):
        if node.tag == 'div':
            for key, value in node.items():
                if key == 'class' and value == 'describe':
                    links.extend(parse_description(node))
        for element in node:
            recurse(element)
        
    file_data = open_file_to_read(file)
    root = fromstring(file_data)
    recurse(root)
    return links


def main():
    # get links
    links_list_file = 'stories_list.html'
    links_list = parse_links_list_file(links_list_file)
	
    for link in links_list:
        link_name = parse.unquote(link.rsplit('/', 2)[1])
        print('Link: ', link)
        print('Name: ', link.rsplit('/', 2)[1])
        header, response = urlget(link)
        for line in header.getvalue().splitlines():
            print(line.decode())
        str_response = response.getvalue()
        with open(os.path.join(os.getcwd(), 'html_pages', link_name, '.html'), 'wb') as file:
            file.write(str_response)
        time.sleep(7)



if __name__ == '__main__':
    main()