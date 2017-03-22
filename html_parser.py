from lxml.html import fromstring
from codecs import open
from os import listdir, makedirs
from sys import exc_info
from os.path import isfile, join, exists, split
from json import dumps

HTML_PAGES_DIR = r"html_pages"
ARTICLES_DIR = r"Articles"
YELLOW_COLOR = '\033[93m'
WHITE_COLOR = '\033[0m'
HOST = r"http://www.shortstoryproject.com/he/"


def exception_handling(error_str):
    print(YELLOW_COLOR)
    print("Error using '{0}': {1}".format(error_str.split(':')[0], error_str.split(':')[1]))
    exc_type, exc_obj, exc_tb = exc_info()
    fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(WHITE_COLOR)


def open_file_to_read(path):
    file_data = ""
    try:
        with open(path, 'r', encoding='utf8') as f:
            file_data = f.read()
    except Exception as e:
        exception_handling(str(e))
        raise Exception

    return file_data


def save_file(path, dict_data):
    try:
        with open(path, 'w+', encoding='utf8') as f:
            f.write(dumps(dict_data, ensure_ascii=False, indent=4, sort_keys=True))
    except Exception as e:
        exception_handling(str(e))
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
                data += "".join(element.itertext()).strip()

        data = data.replace("None", "")
        return data


def main():
    html_files_list = [join(HTML_PAGES_DIR, html_file) for html_file in listdir(HTML_PAGES_DIR)
                       if isfile(join(HTML_PAGES_DIR, html_file))
                       and join(HTML_PAGES_DIR, html_file).split(".")[-1] == "html"]

    tags_dict = {".//div[@class='storyTitle']": (('Article-name', 'h1'), ('Author', 'h3'), ('Language', 'h4'),
                 ('Translator', 'h4')), ".//div[@class='mainArticle clearfix']/section[@id='examples']/div"
                 "[@class='recommendation']": (('Introduction-title', 'h2'), ('Introduction-Text', 'article')),
                 ".//div[@class='mainArticle clearfix']/article": ('Article-text', 'p')}

    for html_file in html_files_list:
        dict_data = {}
        html_data = ""
        try:
            html_data = open_file_to_read(html_file)
        except Exception as e:
            pass
        root = fromstring(html_data)

        for main_element in tags_dict.keys():
            get_text_from_element(root, main_element, tags_dict[main_element], dict_data)

        check_exists_folder_and_create(join(ARTICLES_DIR, dict_data['Language']))
        try:
            save_file(join(join(ARTICLES_DIR, dict_data['Language']), dict_data['Article-name'].replace() + '.json'), dict_data)
        except Exception as e:
            pass


if __name__ == "__main__":
    main()
