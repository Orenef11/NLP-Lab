from lxml.html import fromstring
from codecs import open
from os import listdir, makedirs
from os.path import isfile, join, exists
from json import  loads, dumps

HTML_PAGES_DIR = r"html_pages"
ARTICLES_DIR = r"Articles"


def open_file_to_read(path):
    file_data = ""
    try:
        with open(path, 'r', encoding='utf8') as f:
            file_data = f.read()
    except FileNotFoundError as e:
        exit("Error: File not found error({0}): {1}".format(e.errno, e.strerror))
    except PermissionError as e:
        exit("Error: Permission denied({0}): {1}".format(e.errno, e.strerror))
    except:
        exit("Error: Unable to create the file!")

    return file_data


def save_file(path, dict_data):
    try:
        with open(path, 'w+', encoding='utf8') as f:
            f.write(dumps(dict_data, ensure_ascii=False))
    except PermissionError as e:
        exit("Error: Permission denied({0}): {1}".format(e.errno, e.strerror))
    except:
        exit("Error: Unable to create the file!")


def check_exists_folder_and_create(folder_path):
    if not exists(folder_path):
        makedirs(folder_path)


def get_text_from_element(root, properties_tags, element_tag, iter_text, json_data):
    data = ""
    # Find the element the name thg as *element_tag*
    element = root.findall(element_tag)

    if iter_text:
        data = "".join(element[0].itertext()).strip()
    else:
        data = "".join(str(element.text)).strip()

    if ".//div[@class='storyTitle']" == element_tag:
        data = data.split('\n')
        json_data[properties_tags[0]] = data[0].strip()
        json_data[properties_tags[1]] = data[1].split('|')[0].strip()
        json_data[properties_tags[2]] = data[1].split('|')[1].split(":")[1].strip()
        json_data[properties_tags[3]] = ""
        if data.__len__() == 3:
            json_data[properties_tags[3]] = data[2].split(":")[1].strip()
    elif ".//div[@class='mainArticle clearfix']/section[@id='examples']" == element_tag:
        data = data.split('\n')
        json_data[properties_tags[0]] = data[0].strip()
        introduction_text = ""
        for i in range(1, data.__len__() - 1):
            if data[i] is not "":
                introduction_text += data[i].strip()
        json_data[properties_tags[1]] = introduction_text
    elif ".//div[@class='mainArticle clearfix']/article/p" == element_tag:
        json_data[properties_tags] = data


def main():
    html_files_list = [join(HTML_PAGES_DIR, html_file) for html_file in listdir(HTML_PAGES_DIR)
                       if isfile(join(HTML_PAGES_DIR, html_file))
                       and join(HTML_PAGES_DIR, html_file).split(".")[-1] == "html"]
    tags_list = [(('Article-name', 'Author', 'Language', 'Translation'), ".//div[@class='storyTitle']", True),
                 (('Introduction-title', 'Introduction-Text'), ".//div[@class='mainArticle clearfix']/section[@id='examples']", True),
                 ('Article-Text', ".//div[@class='mainArticle clearfix']/article/p", True)]

    for html_file in html_files_list:
        json_data = {}
        html_data = open_file_to_read(html_file)
        root = fromstring(html_data)
        get_text_from_element(root, tags_list[0][0], tags_list[0][1], tags_list[0][2], json_data)
        get_text_from_element(root, tags_list[1][0], tags_list[1][1], tags_list[1][2], json_data)
        get_text_from_element(root, tags_list[2][0], tags_list[2][1], tags_list[2][2], json_data)
        check_exists_folder_and_create(join(ARTICLES_DIR, json_data['Language']))
        save_file(join(join(ARTICLES_DIR, json_data['Language']), json_data['Article-name'] + '.json'), json_data)


if __name__ == "__main__":
    main()