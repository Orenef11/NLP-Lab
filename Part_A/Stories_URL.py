from os import path, getcwd, makedirs, listdir
from time import sleep
from urllib.parse import urljoin, quote, unquote
from io import StringIO
from requests import get
import logging
from HTML_Parser import Singleton
from lxml import etree
from lxml.html import fromstring
from io import BytesIO
import pycurl
from traceback import print_exc


class StoriesURL(Singleton):
    def __init__(self, stories_page_folder_path, website_page_folder_path, replace_bad_chars_list=None):
        if not path.isdir(stories_page_folder_path):
            logging.info("\nThe '{}' folder created successfully".format(stories_page_folder_path))
            makedirs(stories_page_folder_path)
        if not path.isdir(website_page_folder_path):
            logging.info("\nThe '{}' folder created successfully".format(website_page_folder_path))
            makedirs(website_page_folder_path)

        if replace_bad_chars_list is None:
            replace_bad_chars_list = ['/', '\\', '?', '"', '|', '\t', '(', ')', '*']
        self.__host_parameters_dict = {
            "am_oved_hebrew":
                {
                    "host": "http://www.am-oved.co.il/page_23292",
                    "filename": path.join(stories_page_folder_path, "am_oved_hebrew.html")
                },

            "am_oved":
                {
                    "host": "http://www.am-oved.co.il/page_23290",
                    "filename": path.join(stories_page_folder_path, "am_oved.html")
                },

            "kibutz_poalim":
                {
                    "host": "http://www.kibutz-poalim.co.il/פרקים_ראשונים?bscrp=",
                    "filename": path.join(stories_page_folder_path, "kibutz_poalim.html")
                },

            "dortome":
                {
                    "host": "http://www.dortome.com/site/detail/detail/detailDetail.asp?detail_id=3243030&iPageNum=",
                    "filename": path.join(stories_page_folder_path, "dortome.html")
                },

            "short_story_project":
                {
                    "host": "http://www.shortstoryproject.com/he/ספרייה",
                    "action_php": "http://www.shortstoryproject.com/wp-content/themes/maaboret2016/action.php",
                    'http_arg': [("posts", "1000000"), ("offset", "0"), ("lang", "he")],
                    "filename": path.join(stories_page_folder_path, "short_story_project.html")
                }
        }
        self.__replace_bad_chars_list = replace_bad_chars_list
        self.__parser = etree.HTMLParser()
        self.__website_stories_link_folder_path = stories_page_folder_path
        self.__story_page_folder_path = website_page_folder_path

    def __create_all_stories_links_file(self):
        for website_name in self.__host_parameters_dict.keys():
            file_path = path.join(getcwd(), self.__host_parameters_dict[website_name]['filename'])
            url = str(self.__host_parameters_dict[website_name]['host'])

            if url.startswith('http://www.dortome.com') or url.startswith('http://www.kibutz-poalim.co.il'):
                self.__get_url_links_from_table_pagination(url, file_path)
            elif url.startswith('http://www.am-oved.co.il'):
                self.__save_data_file(file_path, url)
            elif url.startswith('http://www.shortstoryproject.com/he'):
                logging.debug("\nCreate {0} file".format(file_path))
                try:
                    with open(file_path, 'wb') as file:
                        file.write(self.__url_post(website_name))
                except Exception as _:
                    logging.debug("\nCann't save file: {0}".format(file_path))
                    logging.info(print_exc())

    def __url_post(self, website_name):
        header, response = BytesIO(), BytesIO()
        logging.debug("\nPost function start")
        curl = pycurl.Curl()
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.URL, self.__host_parameters_dict[website_name]['action_php'])
        curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 6.3; WOW64) "
                                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36")
        curl.setopt(pycurl.HTTPHEADER, ["Connection: keep-alive", "Expect:"])
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.SSL_VERIFYHOST, 0)
        curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
        curl.setopt(pycurl.HEADERFUNCTION, header.write)
        curl.setopt(pycurl.WRITEFUNCTION, response.write)
        curl.setopt(pycurl.HTTPPOST, self.__host_parameters_dict[website_name]['http_arg'])
        curl.perform()
        curl.close()
        logging.debug("\nPost function end")
        return response.getvalue()

    @staticmethod
    def __save_data_file(file_path, url):
        logging.debug("\nCreate {0} file".format(file_path))
        try:
            with open(file_path, mode='w', encoding='utf-8') as file:
                file.write(get(url).text)
        except Exception as e:
            if type(e) is OSError and e.errno == 36 and e.strerror == 'File name too long':
                file_path = path.split(file_path)
                root_path, file_path = file_path[0], str(file_path[1])
                file_path = file_path.split('.html')[0]
                file_path = file_path.split(' ')
                file_path = path.join(root_path, ' '.join(file_path[:4]) + '.html')
                if not path.isfile(file_path):
                    with open(file_path, mode='w', encoding='utf-8') as file:
                        file.write(get(url).text)
            else:
                logging.debug("\nCann't save file: {0}".format(file_path))
                logging.info(print_exc())
                exit()

        sleep(3)

    def __get_stories_links_from_stories_file(self, root):
        # The div containing all links stories on http://www.am-oved.co.il website
        am_oved_root = root.findall(".//div[@id='P20']")

        is_am_oved_website = False
        if len(am_oved_root) != 0:
            is_am_oved_website = True
            root = am_oved_root[0].findall(".//a")
        else:
            ''' Get story links from http://www.am-oved.co.il website  website '''
            root = root.findall(".//a")

        links_list = []
        if len(root) != 0:
            for element in root:
                ''' Check if exist 'href' attrib in element '''
                if "href" in element.attrib.keys():
                    try:
                        title_name = element.text.strip()
                    except Exception as _:
                        logging.info("\nBad url link {0}".format(unquote(element.attrib['href'])))
                        continue

                    ''' Clear bad chars '''
                    for char_replace in self.__replace_bad_chars_list:
                        title_name = title_name.replace(char_replace, "")

                    title_name = title_name.split(' - ')
                    url_host = element.attrib['href']
                    if is_am_oved_website and not url_host.startswith(r"http://www.am-oved.co.il/Media/Doc/"):
                        url_host = urljoin("http://www.am-oved.co.il/", quote(url_host, safe=''))
                        links_list.append((url_host, (title_name[0] + ' - ' + title_name[1])))
                    elif url_host.startswith(
                            r'http://www.shortstoryproject.com/he') and "title" in element.attrib.keys():
                        filename = element.attrib["title"].strip()
                        for char_replace in self.__replace_bad_chars_list:
                            filename = filename.replace(char_replace, "")
                        links_list.append((url_host, filename))

        return links_list

    def __get_url_links_from_table_pagination(self, web_url, file_path):
        url_an_title_list = []
        website_name = web_url.split('.')[1].split('.')[0].lower()
        name_of_article, url_of_article = "", ""
        i, stop_loop = 1, False

        while not stop_loop:
            request = get(web_url + str(i)).text
            tree = etree.parse(StringIO(request), self.__parser)
            root = tree.getroot()
            if web_url.startswith("http://www.kibutz-poalim.co.il/פרקים_ראשונים"):
                root = root.findall(".//table[@style='padding-top:5px']")
            elif web_url.startswith(
                    "http://www.dortome.com/site/detail/detail/detailDetail.asp?detail_id=3243030&iPageNum="):
                root = root.findall(".//tr/td/table[@cellspacing='3']")

                if len(root) != 0:
                    ''' Find all stories in page '''
                    root = root[0].findall(".//table[@cellpadding='5']")
            else:
                logging.info("\nThe inserted {0} link is invalid".format(web_url))
                url_an_title_list.clear()
                break

            if len(root) == 0:
                stop_loop = True
                i -= 1
                continue

            for root2 in root:
                if website_name == "dortome":
                    element = root2.find(".//h2/a")
                    name_of_article = element.text.split('-')[0].replace('/', '-').strip()
                    url_of_article = unquote(urljoin("http://www.dortome.com", element.attrib['href']))
                    name_of_article = name_of_article.replace('/', '-')

                elif website_name == "kibutz-poalim":
                    name_of_article = root2.find(".//b").text
                    url_of_article = root2.find(".//a[@class='title_editor']").attrib['href']
                    url_of_article = urljoin("http://www.kibutz-poalim.co.il", url_of_article)

                    # Split the name of article to by this format  article_name - translator name
                    # Split by '|' or ':' separator
                    name_of_article = name_of_article.split('|')[0:2]
                    if len(name_of_article) == 1:
                        name_of_article = name_of_article[0].split(':')

                    # # Replace the character ' - ' because it is the character we use to separate
                    # if ' - ' in name_of_article:
                    #     name_of_article = name_of_article.replace(' - ', ': ')
                    # Check if exist translator name in name of article
                    if len(name_of_article) == 1:
                        name_of_article.append("")
                    name_of_article = name_of_article[0] + '-' + name_of_article[1]

                name_of_article = name_of_article.replace("פרק ראשון", "")
                for char in self.__replace_bad_chars_list:
                    name_of_article = name_of_article.replace(char, '')

                url_an_title_list.append((url_of_article, name_of_article.strip()))
            i += 1

        if len(url_an_title_list) != 0:
            with open(file_path, mode='w', encoding='utf-8') as f:
                for url_of_article, name_of_article in url_an_title_list:
                    if website_name in url_of_article:
                        f.write("{0}---{1}\n".format(url_of_article, name_of_article))
            f.close()

    def run(self, create_new_stories_link_file_flag=False):
        charmap_list = ['\u202d', '\u202c', '\ufb35', '\u2032']
        for website_key in self.__host_parameters_dict.keys():
            website = path.split(self.__host_parameters_dict[website_key]['filename'])
            website_stories_link_path = path.join(self.__story_page_folder_path, website[-1].split('.')[0])
            ''' Create new folder to new website'''
            if not path.exists(website_stories_link_path):
                logging.debug("\nCreate {0} folder".format(website_stories_link_path))
                makedirs(website_stories_link_path)
            if create_new_stories_link_file_flag is True or len(listdir(self.__website_stories_link_folder_path)) \
                    != len(self.__host_parameters_dict.keys()):
                """ Retrieves from each site the file containing all the links of the stories """
                self.__create_all_stories_links_file()

        links_list = []
        ''' The full path of the file that contains all links stories '''
        file_names_list = [path.join(self.__website_stories_link_folder_path, filename)
                           for filename in listdir(self.__website_stories_link_folder_path)]

        for file_path in file_names_list:
            links_list.clear()
            with open(file_path, mode='r', encoding='utf-8') as file_links:
                if self.__host_parameters_dict['dortome']['filename'] == file_path or \
                                self.__host_parameters_dict['kibutz_poalim']['filename'] == file_path:
                    for line in file_links.readlines():
                        line = line.replace('\n', '')
                        url, name_of_book = line.split('---')
                        links_list.append((url, name_of_book))

                else:
                    links_list = self.__get_stories_links_from_stories_file(fromstring(file_links.read()))

            ''' Create the full path of files'''
            file_path_and_url_list = []
            for url_and_name_tuple in links_list:
                folder_name = path.split(file_path.rsplit('.')[0])[-1]
                file_path_and_url_list.append(
                    (path.join(path.join(self.__story_page_folder_path, folder_name),
                               url_and_name_tuple[1].strip() + '.html'), url_and_name_tuple[0]))

            for url_and_name_tuple in file_path_and_url_list:
                file_path = url_and_name_tuple[0]
                for charmap in charmap_list:
                    file_path = file_path.replace(charmap, '')
                # file_path = file_path.replace(":", " ")
                if not path.isfile(file_path):
                    self.__save_data_file(file_path, url_and_name_tuple[1])

