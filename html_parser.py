from lxml.html import fromstring
from codecs import open
from os import listdir, makedirs
from os.path import isfile, join, exists
from json import dumps, load
import logging
from logger import setting_up_logger

HTML_PAGES_DIR = r"html_pages"
ARTICLES_DIR = r"Articles"
OUTPUT_FILE = r"output.txt"
HOST = r"http://www.shortstoryproject.com/he/"
LOGGING_CONFIG = r"logging.conf"

''' Global variables'''
replace_bad_chars_list = ['/', '?', '"', '|']


def open_file_to_read(path):
    file_data = ""
    try:
        with open(path, 'r', encoding='utf8') as f:
            file_data = f.read()
    except Exception as e:
        logging.error(str(e))
        raise Exception

    return file_data


def save_json_file(path, dict_data):
    try:
        with open(path, 'w+', encoding='utf8') as f:
            f.write(dumps(dict_data, ensure_ascii=False, indent=4, sort_keys=True))
    except Exception as e:
        logging.info(str(e))
        raise Exception


def check_exists_folder_and_create(folder_path):
    if not exists(folder_path):
        makedirs(folder_path)


def get_text_from_element(root, main_element_tag, properties_tags, dict_data):
    # Find the element the name thg as *main_element_tag*
    element = root.findall(main_element_tag)

    if element.__len__() != 0:
        if ".//div[@class='storyTitle']" == main_element_tag:
            ''' Article name '''
            dict_data[properties_tags[0][0]] = find_all_data_in_element(element, ".//" + properties_tags[0][1])

            data = "".join(element[0].findall(".//" + properties_tags[1][1])[0].itertext()).split('|')
            ''' Author name '''
            dict_data[properties_tags[1][0]] = data[0].strip()
            ''' Language name '''
            dict_data[properties_tags[2][0]] = data[1].split(':')[1].strip()
            ''' Translator name '''
            if element[0].findall(".//" + properties_tags[3][1]).__len__() != 0:
                dict_data[properties_tags[3][0]] = find_all_data_in_element(element, ".//" + properties_tags[3][1])

        elif ".//div[@class='mainArticle clearfix']/section[@id='examples']/div[@class='recommendation']" \
                == main_element_tag:
            ''' Introduction-title '''
            dict_data[properties_tags[0][0]] = find_all_data_in_element(element, ".//" + properties_tags[0][1])

            ''' Introduction-Text '''
            dict_data[properties_tags[1][0]] = find_all_data_in_element(element, ".//" + properties_tags[1][1])

        elif ".//div[@class='mainArticle clearfix']/article" == main_element_tag:
            dict_data[properties_tags[0]] = find_all_data_in_element(element, ".//" + properties_tags[1])
            dict_data[properties_tags[0]] += find_all_data_in_element(element, ".//div/" + properties_tags[1])


def find_all_data_in_element(element, tag):
    data = ""
    for root in element:
        root = root.findall(tag)
        for element in root:
            data += "\r\n".join(element.itertext()).strip()

    data = data.replace("None", "")
    return data


def count_file_in_folder(folders_names_list):
    try:
        file = open(OUTPUT_FILE, mode="w+", encoding='UTF-8')
        all_files_count = 0
        for folder_name in folders_names_list:
            folder_name = join(ARTICLES_DIR, folder_name)
            file.write("{0}:\r\nThe amount of files in the folder is {1}\r\n".format(folder_name,
                                                                                     listdir(folder_name).__len__()))

            files_count = 0
            all_files_count += listdir(folder_name).__len__()
            for filename in listdir(folder_name):
                file2 = open(join(folder_name, filename), mode='r', encoding='UTF-8')
                json_data = load(file2)
                file2.close()
                files_count += json_data['Article-text'].split(" ").__len__()
                json_data.clear()

            file.write("The number of words that are in all the files in the folder is {0}\r\n".format(files_count))

        file.write("\r\nThe amount of files there is {0}\r\n".format(all_files_count))
        file.write("There are {0} different languages in the database".format(listdir(ARTICLES_DIR).__len__()))
        file.close()

    except Exception as e:
        logging.critical(str(e))


def main():
    setting_up_logger('debug', 'critical')
    logger = logging.getLogger(__name__)
    html_files_list = [join(HTML_PAGES_DIR, html_file) for html_file in listdir(HTML_PAGES_DIR)
                       if isfile(join(HTML_PAGES_DIR, html_file))
                       and join(HTML_PAGES_DIR, html_file).split(".")[-1] == "html"]
    tags_dict = {".//div[@class='storyTitle']": (('Article-name', 'h1'), ('Author', 'h3'), ('Language', 'h4'),
                                                 ('Translator', 'h4')),
                 ".//div[@class='mainArticle clearfix']/section[@id='examples']/div"
                 "[@class='recommendation']": (('Introduction-title', 'h2'), ('Introduction-Text', 'article')),
                 ".//div[@class='mainArticle clearfix']/article": ('Article-text', 'p')}

    for html_file in html_files_list:
        dict_data = {}
        html_data = ""
        try:
            html_data = open_file_to_read(html_file)
        except Exception as e:
            continue
        root = fromstring(html_data)

        for main_element in tags_dict.keys():
            get_text_from_element(root, main_element, tags_dict[main_element], dict_data)

        check_exists_folder_and_create(join(ARTICLES_DIR, dict_data['Language']))
        try:
            filename = join(join(ARTICLES_DIR, dict_data['Language']), dict_data['Article-name'] + '.json')
            if not isfile(filename):
                save_json_file(filename, dict_data)

        except Exception as e:
            original_filename = dict_data['Article-name']
            for char in replace_bad_chars_list:
                dict_data['Article-name'] = dict_data['Article-name'].replace(char, "")
            save_json_file(join(join(ARTICLES_DIR, dict_data['Language']), dict_data['Article-name'] + '.json'),
                           dict_data)

            # logger.critical("Could not open '{0}' file, so file changed to '%{1}'"
            #                 .format(original_filename, dict_data['Article-name']))
            continue

    count_file_in_folder(listdir(ARTICLES_DIR))


if __name__ == "__main__":
    main()
