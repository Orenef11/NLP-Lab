from json import dumps
from os import listdir, stat, remove, rename, path
from logger import *
import logging
from traceback import print_exc
from lxml.html import fromstring
from shutil import copyfile, move


class Singleton(object):
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it

    def init(self, *args, **kwds):
        pass


class HTMLParser(Singleton):
    def __init__(self, stories_html_pages_folder_path, log_path, json_stories_path,
                 debugging_output_folder_path, unsaved_stoires_path, replace_bad_chars_list=None):
        if replace_bad_chars_list is None:
            replace_bad_chars_list = ['/', '\\', '?', '"', '|', '(', ')', '.', "'", '"']
        self.__replace_bad_chars_list = replace_bad_chars_list
        self.__tags_dict = {
            'short_story_project':
                {
                    ".//div[@class='storyTitle']":
                        (('Article-name', 'h1'), ('Author', 'h3'), ('Language', 'h4'),
                         ('Translator', 'h4')),
                    ".//div[@class='mainArticle clearfix']/section[@id='examples']/div"
                    "[@class='recommendation']": (
                        ('Introduction-title', 'h2'), ('Introduction-Text', 'article'))
                        , ".//div[@class='mainArticle clearfix']/article": ('Article-text', 'p')
                 },
            'am_oved_hebrew':
                {
                    ".//div[@class='normal']/p[@class='MsoNormal']": (
                        ('Article-name', 'span'), ('Author', 'span'), ('Language', 'עברית'), ('Article-text', 'span'))
                },
            'am_oved':
                {
                    ".//div[@class='normal']/p[@class='MsoNormal']": (
                        ('Article-name', 'span'), ('Author', 'span'), ('Language', 'unknown'), ('Article-text', 'span'))
                },
            'dortome':
                {".//div[@class='normal']/p[@class='MsoNormal']": (
                    ('Article-name', 'span'), ('Author', 'span'), ('Language', 'unknown'), ('Article-text', 'span'))
                },
            "kibutz_poalim":
                {
                    ".//div[@class='normal']": (
                        ('Article-name', 'strong', 0), ('Author', 'strong', 1), ('Language', 'unknown'),
                        ('Article-text', 'span'))
                }
        }
        self.__story_data_dict = {}
        self.__stories_html_pages_folder_path = stories_html_pages_folder_path
        self.__log_path = log_path
        self.__json_stories_path = json_stories_path
        self.__debugging_output_folder_path = debugging_output_folder_path
        self.__unsaved_stories_path = unsaved_stoires_path

    def __get_text_from_element(self, root, web_name, main_element_tag, properties_tags, filename):
        # Find the element the name thg as *main_element_tag*
        element = root.findall(main_element_tag)
        # element = ""
        if web_name == "short_story_project":
            if element.__len__() != 0:
                if ".//div[@class='storyTitle']" == main_element_tag:
                    ''' Article name '''
                    self.__story_data_dict[properties_tags[0][0]] = \
                        self.__find_all_data_in_element(element, ".//" + properties_tags[0][1]).replace('\r\n', '')

                    data = "".join(element[0].findall(".//" + properties_tags[1][1])[0].itertext()).split('|')
                    ''' Author name '''
                    self.__story_data_dict[properties_tags[1][0]] = data[0].strip().replace('\r\n', '')
                    ''' Language name '''
                    self.__story_data_dict[properties_tags[2][0]] = data[1].split(':')[1].strip().replace('\r\n', '')
                    ''' Translator name '''
                    if element[0].findall(".//" + properties_tags[3][1]).__len__() != 0:
                        self.__story_data_dict[properties_tags[3][0]] = \
                            self.__find_all_data_in_element(element, ".//" + properties_tags[3][1]).replace('\r\n', '')
                        self.__story_data_dict[properties_tags[3][0]] = \
                            self.__story_data_dict[properties_tags[3][0]].replace('תרגום : ', '')

                elif ".//div[@class='mainArticle clearfix']/section[@id='examples']/div[@class='recommendation']" \
                        == main_element_tag:
                    ''' Introduction-title '''
                    self.__story_data_dict[properties_tags[0][0]] = \
                        self.__find_all_data_in_element(element, ".//" + properties_tags[0][1]).replace('\r\n', '')

                    ''' Introduction-Text '''
                    self.__story_data_dict[properties_tags[1][0]] = \
                        self.__find_all_data_in_element(element, ".//" + properties_tags[1][1])

                elif ".//div[@class='mainArticle clearfix']/article" == main_element_tag:
                    self.__story_data_dict[properties_tags[0]] = \
                        self.__find_all_data_in_element(element, ".//" + properties_tags[1])
                    self.__story_data_dict[properties_tags[0]] += \
                        self.__find_all_data_in_element(element, ".//div/" + properties_tags[1])

        elif web_name in ["am_oved", "am_oved_hebrew"]:
            if ".//div[@class='normal']/p[@class='MsoNormal']" == main_element_tag:
                text_element_idx = 2
                language_name = properties_tags[2][1]
                if len(element) < 2:
                    element = root.findall(".//div[@class='floating']/div[@class='normal']")
                    # The web page is pdf or image
                    if len(element) == 0:
                        self.__story_data_dict = None
                        return
                    element = element[0].findall(".//p")
                    text_element_idx = 1
                else:
                    language_name = element[1]
                    language_name = language_name.findall(".//" + properties_tags[1][1])[0].text
                    if language_name is not None:
                        language_name = language_name.split('(')
                        if len(language_name) > 1:
                            language_name = language_name[1].split('תרגום מ')
                            if len(language_name) == 2:
                                language_name = language_name[1]
                                for char in self.__replace_bad_chars_list:
                                    language_name = language_name.replace(char, "")
                    else:
                        language_name = properties_tags[2][1]
                    if type(language_name) is not str:
                        language_name = properties_tags[2][1]

                # Article name
                self.__story_data_dict[properties_tags[0][0]] = filename.split(' - ')[0]

                # Author of article
                self.__story_data_dict[properties_tags[1][0]] = filename.split(' - ')[1]

                # The source language in which the article was written
                self.__story_data_dict[properties_tags[2][0]] = language_name

                article_text = element[text_element_idx:]
                article_text = self.__find_all_data_in_element(article_text, './/' + properties_tags[3][1])

                if article_text == "" or len(article_text.split(' ')) < 500:
                    self.__story_data_dict = None
                    return

                self.__story_data_dict[properties_tags[3][0]] = article_text

        elif web_name == "kibutz_poalim":
            if ".//div[@class='normal']" == main_element_tag:
                article_name_tags = [".//a[@class='H1']", ".//span[@class='oneandhalf']/a/strong",
                                     ".//span[@class='H1']", ".//span[@class='oneandhalf']/strong/a",
                                     ".//span[@class='product_title']/a", ".//span[@class='product_title']"]

                # Pulls out all the headlines (usually the writer's name appears there)
                headers_list = self.__find_all_data_in_element(element, './/' + properties_tags[0][1]).split('\n')
                headers_list = [header.strip() for header in headers_list if header.strip() != '']

                article_name, article_author, article_text, article_name_from_url = '', '', '', ''

                # Get from article url the name of article
                for title_tag in article_name_tags:
                    article_name_from_url = self.__find_all_data_in_element(element, title_tag)
                    if article_name_from_url.strip() == '':
                        continue
                    break
                if article_name_from_url == '':
                    article_name_from_url = None
                else:
                    article_name_from_url = article_name_from_url.strip()

                article_and_author = filename.split(' - ')

                if type(article_and_author) is list and len(article_and_author) >= 2:
                    article_name = article_and_author[0].strip()
                    article_author = article_and_author[-1].strip()
                    # Sometimes there can be 3 names.
                    # Therefore, if the author's name contains no space, it is most likely not the author's name
                    if " " not in article_author:
                        article_author = article_and_author[1].strip()
                else:
                    article_name = article_and_author[0].replace('-', '').strip()

                # The name of the file is reversed, first the name of the author followed by the name of the book
                if article_name_from_url == article_author:
                    article_author = article_name
                    article_name = article_name_from_url
                # Sometimes the name of the file or book is written in short, we look for
                #  the full name in the headers list
                for header in headers_list:
                    if article_name in header:
                        if " " in header and len(header.split(" ")) > 6:
                            continue
                        article_name = header
                        if '-' in article_name:
                            article_name = article_name.split('-')[1]
                        break

                if article_author != '':
                    for header in headers_list:
                        if article_author in header:
                            if " " in header and len(header.split(" ")) > 4:
                                continue
                            article_author = header
                            if 'מאת' in article_author:
                                article_author = article_author.replace('מאת', '')
                            break
                # Remove redundant information, for example - information written in brackets
                if '(' in article_author:
                    article_author = article_author.split('(')[0].strip()

                # Because we have tried to search for the full article name, we sometimes make it and
                # the author name the same thing
                if article_name == article_author:
                    article_name = filename.split(' - ')[0]
                    article_author = filename.split(' - ')[1]

                if len(article_name) > 1 and article_name[-1] in self.__replace_bad_chars_list:
                    article_name = article_name[:-1]

                article_text_list = [self.__find_all_data_in_element(element, './/tbody/tr/td[@class="normal"]'),
                                     self.__find_all_data_in_element(element, './/span[@class="oneandhalf"]'),
                                     self.__find_all_data_in_element(element, './/p[@class="oneandhalf"]'),
                                     self.__find_all_data_in_element(element, './/p[@class="MsoNormal"]'),
                                     self.__find_all_data_in_element(element, './/span[@style="font-size: 10pt;"]'),
                                     self.__find_all_data_in_element(element, './/div/span'),
                                     self.__find_all_data_in_element(element, './/p/span[@style="font-size: 13px;"]'),
                                     self.__find_all_data_in_element(element, './/p/span/span'),
                                     self.__find_all_data_in_element(root, './/font[@class="oneandhalf"]')]
                article_text = max(article_text_list, key=len)
                if len(article_text) < 100:
                    article_text = self.__find_all_data_in_element(element, './/p')

                original_article_size = len(article_text)
                article_text_list = [line.strip() for line in article_text.split('\r\n') if line.strip() != '']
                try:
                    titles_and_indexes_data = [(idx, line.split('\n\n')) for idx, line in
                                               enumerate(article_text_list) if '\n\n' in line]
                except:
                    titles_and_indexes_data = []
                titles_data_list = []
                for titles_list in titles_and_indexes_data:
                    titles_data_list += titles_list[1]
                if article_author == '':
                    article_author = [author.replace('מאת ', '') for author in titles_data_list
                                      if author.startswith('מאת ')]
                    if type(article_author) is list:
                        if len(article_author) != 0:
                            article_author = article_author[-1]
                        else:
                            article_author = "unknown"

                language = 'unknown'
                for language_idx, lang in enumerate(titles_data_list):
                    if lang.startswith('מ') and ':' in lang and ' ' not in lang.split(':')[0]:
                        language = lang.split(':')[0].replace('מ', '')
                        break

                self.__story_data_dict[properties_tags[0][0]] = article_name.strip()

                # Author of article
                self.__story_data_dict[properties_tags[1][0]] = article_author.strip()

                # The source language in which the article was written
                self.__story_data_dict[properties_tags[2][0]] = language.strip()

                article_text = []
                for line in article_text_list:
                    line = line.strip()
                    if len(line) != 0:
                        if '\n' in line:
                            article_text.append(line.split('\n'))
                        else:
                            article_text.append(line)

                article_text_list = []
                for lines_list in article_text:
                    if type(lines_list) is list:
                        article_text_list += lines_list
                    else:
                        article_text_list.append(lines_list)

                removed_indexes_list = []
                if len(titles_data_list) > 0 and len('\r\n'.join(titles_data_list)) <= int(0.1 * original_article_size):
                    for line_idx, line in enumerate(article_text_list):
                        if titles_data_list[-1] == line:
                            removed_indexes_list.append(line_idx + 1)
                for title_idx in removed_indexes_list:
                    if len('\r\n'.join(article_text_list[title_idx:])) >= int(0.9 * original_article_size):
                            article_text_list = article_text_list[title_idx:]
                    elif len(removed_indexes_list) >= 2 and title_idx == removed_indexes_list[-1]:
                        article_text_list = article_text_list[:title_idx - 2 * removed_indexes_list[0]]

                article_text = article_text_list
                headers_list = [article_name, article_author] + headers_list
                for header in reversed(headers_list):
                    if header in article_text_list:
                        header_idx = article_text_list.index(header) + 1
                        if len('\r\n'.join(article_text_list[:header_idx])) <= int(0.10 * original_article_size):
                            article_text = article_text_list[header_idx:]
                            break

                # Consolidate all sub-lists into one list
                article_text_list = []
                for lines_list in article_text:
                    if type(lines_list) is list:
                        article_text_list.append('\r\n'.join(lines_list))
                    else:
                        article_text_list.append(lines_list)

                # Removes paragraphs unrelated to the story, such as links to purchase the book
                # or information about the writer.
                remove_parag_list = ['קישורים:', 'לפרק הראשון >>', 'לדף הספר באתר']
                for remove_parag in remove_parag_list:
                    if remove_parag in article_text_list:
                        article_text_list = article_text_list[:article_text_list.index(remove_parag)]
                article_text = '\r\n'.join(article_text_list)

                # Article name
                self.__story_data_dict[properties_tags[0][0]] = article_name.strip()
                # Author of article
                self.__story_data_dict[properties_tags[1][0]] = article_author.strip()

                # The source language in which the article was written
                self.__story_data_dict[properties_tags[2][0]] = properties_tags[2][1]

                self.__story_data_dict[properties_tags[3][0]] = article_text

        elif web_name == "dortome":
            # Because there is no compatibility between all the story pages, there are 2 main tags:
            # 1. './/div[@style='text-align: justify;']'
            # 2. './/td[@class='sortableLayout']'
            element = root.findall(".//div[@style='text-align: justify;']")
            article_text = self.__find_all_data_in_element(element, './/')

            element2 = root.findall(".//td[@class='sortableLayout']")
            article_text2 = self.__find_all_data_in_element(element2, './/')
            if len(article_text2) > len(article_text):
                element = element2
                article_text = article_text2
            # Some pages contain story content as an image, so in this case we check if this is the case and remove
            #  the 'הזמן עכשיו!' message to see if this is the case.
            if article_text != '' and len(article_text) < 100:
                article_text = article_text.replace('\r\nהזמן עכשיו!', '')
            if article_text == '':
                self.__story_data_dict = None
                return
            # For some reason, we do not know, we get a list that contains several times the text of the story.
            # To deal with this, we are looking for the largest string
            article_text = article_text.split('\r\n')
            article_text = max(article_text, key=len)
            title = root.findall(".//font[@class='changeText14']")
            title = self.__find_all_data_in_element(title, './/')
            headers_list = self.__find_all_data_in_element(element, './/strong')
            if headers_list != "":
                headers_list = headers_list.split('\r\n')

            for header in headers_list:
                article_text = article_text.replace(header, '')
            article_text = article_text.strip()

            bad_words_in_article_author_list = ['פרק ראשון', 'טעימת קריאה', 'פרק לטעימה', 'פרק לקריאה', 'פרק 18',
                                                'פרקים ראושנים', 'פתיחה', 'פרק לדוגמא', 'טעימות קריאה', 'פרקים ראשונים',
                                                'מבוא', 'טעימתה קריאה', 'טעימתה', 'פרק קריאה', 'פרק דוגמא', 'פתח דבר',
                                                'טעימה', 'פרק']
            # Not all file names have the name of the author, so if the author does not exist,
            # we will take the name of the book and author from the page
            if '-' in filename:
                article_name, article_author = filename.split('-')[0].strip(), filename.split('-')[1].strip()
            else:
                if '/' not in title:
                    self.__story_data_dict = None
                    return
                article_name, article_author = title.split('/')[0].strip(), title.split('/')[1].strip()
                if '-' in article_name:
                    article_name = article_name.split('-')[0].strip()
                if '-' in article_author:
                    article_author = article_author.split('-')[0].strip()
            # Sometimes the name of the author contains more words from the list that appear in variable
            # bad_words_in_article_author_list (we will delete these words and leave only the author's name)
            for bad_word in bad_words_in_article_author_list:
                article_author = article_author.replace(bad_word, '')

            article_author = article_author.strip()

            # Article name
            self.__story_data_dict[properties_tags[0][0]] = article_name.strip()
            # Author of article
            self.__story_data_dict[properties_tags[1][0]] = article_author.strip()

            # The source language in which the article was written
            self.__story_data_dict[properties_tags[2][0]] = properties_tags[2][1]

            self.__story_data_dict[properties_tags[3][0]] = article_text

    def __save_json_file(self, file_path):
        try:
            logging.debug("\nWrite data to {0} file".format(file_path))
            with open(file_path, 'w', encoding='utf8') as f:
                f.write(dumps(self.__story_data_dict, ensure_ascii=False, indent=4, sort_keys=True))

            logging.debug("\nFinish write data to {0} file".format(file_path))

        except Exception as e:
            if type(e) is OSError and e.errno == 36 and e.strerror == 'File name too long':
                file_path_list = path.split(file_path)
                filename = ' '.join(str(file_path_list[1]).split('.')[0].split(' ')[: 4]) + '.json'
                file_path = path.join(file_path_list[0], filename)
                with open(file_path, 'w', encoding='utf8') as f:
                    f.write(dumps(self.__story_data_dict, ensure_ascii=False, indent=4, sort_keys=True))

                logging.debug("\nFinish write data to {0} file".format(file_path))
            else:
                raise Exception

    @staticmethod
    def __check_exists_folder_and_create(folder_path):
        if not path.exists(folder_path):
            logging.debug("\nCreate {0} in Articles folder".format(folder_path))
            makedirs(folder_path)
            logging.debug("\nFinish create {0} in Articles folder".format(folder_path))

    @staticmethod
    def __open_file_to_read(filename_path):
        try:
            with open(filename_path, 'r', encoding='utf8') as f:
                file_data = f.read()
        except Exception as e:
            # logging.info(str(e), print_exc())
            raise Exception

        return file_data

    @staticmethod
    def __find_all_data_in_element(element, tag):
        all_data = ""
        for node in element:
            node = node.findall(tag)
            for element in node:
                data = "".join(element.itertext()).strip()
                if data != "":
                    all_data = all_data + "\r\n" + data

        all_data = all_data.replace("None", "")
        return all_data

    def __copy_unsaved_story_file(self, file_path):
        copyfile(file_path, path.join(self.__unsaved_stories_path, path.split(file_path)[1]))

    def __get_all_html_file_path(self):
        charmap_list = ['\u202d', '\u202c', '\ufb35', '\u2032']
        folders_path_list = [path.join(self.__stories_html_pages_folder_path, folder_name) for folder_name in
                             listdir(self.__stories_html_pages_folder_path)]
        html_files_list = []
        for folder_path in folders_path_list:
            if not path.isdir(folder_path):
                logging.info("\nThe '{}' not is folder".format(folder_path))
                continue
            for html_file in listdir(folder_path):
                new_html_file = html_file
                for charmap in charmap_list:
                    if charmap in html_file:
                        new_html_file = new_html_file.replace(charmap, '').strip()
                if new_html_file != html_file:
                    if path.isfile(path.join(folder_path, new_html_file)):
                        continue
                    rename(path.join(folder_path, html_file), path.join(folder_path, new_html_file))
                    html_file = new_html_file
                file_path = path.join(folder_path, html_file)
                if html_file.split('.')[-1] != "html" or not html_file.endswith('html') or stat(file_path).st_size == 0:
                    try:
                        remove(file_path)
                        logging.debug("\nThe '{}' file Is not in html format".format(file_path))
                    except Exception as _:
                        logging.info("\nNo permission to delete the '{}' file".format(file_path))
                        continue

                html_files_list.append(file_path)

        logging.debug("\nThere are {} html files".format(len(html_files_list)))

        return html_files_list

    def run(self):
        unsaved_json_files_path = path.join(self.__debugging_output_folder_path, 'unsaved_stories_log.log')
        if not path.isdir(self.__unsaved_stories_path):
            makedirs(self.__unsaved_stories_path)
        html_files_list = self.__get_all_html_file_path()
        num_of_create_new_json, unsaved_json_files_count = 0, 0
        for html_file in html_files_list:
            self.__story_data_dict = {}
            if html_file.split('.')[-1] != "html" or not html_file.endswith('html') or stat(html_file).st_size == 0:
                logging.info("\nThe '{}' file is invalid, extension that is not an HTML file or file is empty!"
                             "".format(html_file))
                try:
                    remove(html_file)
                except Exception as _:
                    logging.info("\nNo permission to delete the '{}' file".format(html_file))
                    continue
                continue
            html_data = self.__open_file_to_read(html_file)
            root = fromstring(html_data)

            story_data_dict_flag = False
            web_name = path.split(path.split(html_file)[0])[-1]
            filename = ''
            for main_element in self.__tags_dict[web_name].keys():
                filename = path.split(html_file)[-1].split('.html')[0]
                self.__get_text_from_element(root, web_name, main_element, self.__tags_dict[web_name][main_element],
                                             filename)

            if self.__story_data_dict is None or type(self.__story_data_dict) is not dict:
                story_data_dict_flag = True
                self.__copy_unsaved_story_file(html_file)

            if not story_data_dict_flag:
                self.__check_exists_folder_and_create(path.join(self.__json_stories_path,
                                                                self.__story_data_dict['Language']))

            try:
                if story_data_dict_flag:
                    change_logger_file(self.__log_path, unsaved_json_files_path)
                    unsaved_json_files_count += 1
                    logging.debug("\nThe '{}' file unsaved".format(html_file))
                    change_logger_file(unsaved_json_files_path, self.__log_path)
                    continue

                filename = filename.split(' -')[0]
                if ' ' in filename[-1]:
                    filename = filename[:-1]
                for char in self.__replace_bad_chars_list:
                    filename = filename.replace(char, "")

                file_path = path.join(path.join(self.__json_stories_path,
                                                self.__story_data_dict['Language']), filename + '.json')
                if '\ufb35' in file_path:
                    file_path = file_path.replace('\ufb35', '')

                if path.split(file_path)[0] == self.__json_stories_path:
                    folder_path, filename = path.split(file_path)
                    file_path = path.join(folder_path, path.join('unknown'), filename)
                    logging.info("\nMove the '{}' file from folder '{}' to folder '{}'"
                                 "".format(filename, folder_path, file_path))
                if not path.isfile(file_path):
                    self.__save_json_file(file_path)
                    num_of_create_new_json += 1

            except Exception as e:
                print(str(e))
                logging.debug(print_exc())
                continue

        change_logger_file(self.__log_path, unsaved_json_files_path)
        logging.info("\nThe number of unsaved file are {} files".format(unsaved_json_files_count))
        change_logger_file(unsaved_json_files_path, self.__log_path)
        logging.info("\nCreate {0} new json files".format(num_of_create_new_json))
