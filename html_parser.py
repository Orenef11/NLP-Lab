from lxml.html import fromstring
from codecs import open
from os import listdir, makedirs
from os.path import isfile, join, exists
from json import dumps

HTML_PAGES_DIR = r"html_pages"
ARTICLES_DIR = r"Articles"


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


def get_text_from_element(root, main_element_tag, properties_tags, json_data):
    data = ""
    # Find the element the name thg as *main_element_tag*
    element = root.findall(main_element_tag)

    if element.__len__() != 0:
        if ".//div[@class='storyTitle']" == main_element_tag:
            ''' Article name '''
            json_data[properties_tags[0][0]] = "".join(element[0].findall(".//" + properties_tags[0][1])[0]
                                                       .itertext()).strip()
            data = "".join(element[0].findall(".//" + properties_tags[1][1])[0].itertext()).split('|')
            ''' Author name '''
            json_data[properties_tags[1][0]] = data[0].strip()
            ''' Language name '''
            json_data[properties_tags[2][0]] = data[1].split(':')[1].strip()
            ''' Translator name '''
            if element[0].findall(".//" + properties_tags[3][1]).__len__() != 0:
                json_data[properties_tags[3][0]] = "".join(element[0].findall(".//" + properties_tags[3][1])[0]
                                                           .itertext()).split(':')[1].strip()

        elif ".//div[@class='mainArticle clearfix']/section[@id='examples']/div[@class='recommendation']" \
                == main_element_tag:
            ''' Introduction-title '''
            json_data[properties_tags[0][0]] = "".join(element[0].findall(".//" + properties_tags[0][1])[0]
                                                       .itertext()).strip()
            ''' Introduction-Text '''
            json_data[properties_tags[1][0]] = "".join(element[0].findall(".//" + properties_tags[1][1])[0]
                                                       .itertext()).strip()
        elif ".//div[@class='mainArticle clearfix']/article" == main_element_tag:
            data = "".join(element[0].findall(".//" + properties_tags[1])[0].itertext()).strip()
            data = data.replace("None", "")
            json_data[properties_tags[0][0]] = data


def main():
    html_files_list = [join(HTML_PAGES_DIR, html_file) for html_file in listdir(HTML_PAGES_DIR)
                       if isfile(join(HTML_PAGES_DIR, html_file))
                       and join(HTML_PAGES_DIR, html_file).split(".")[-1] == "html"]

    tags_dict = {".//div[@class='storyTitle']": (('Article-name', 'h1'), ('Author', 'h3'), ('Language', 'h4'),
                 ('Translator', 'h4')), ".//div[@class='mainArticle clearfix']/section[@id='examples']/div"
                 "[@class='recommendation']": (('Introduction-title', 'h2'), ('Introduction-Text', 'article')),
                 ".//div[@class='mainArticle clearfix']/article": ('Article-text', 'p')}


    for html_file in html_files_list:
        json_data = {}
        html_data = open_file_to_read(html_file)
        root = fromstring(html_data)

        for main_element in tags_dict.keys():
            get_text_from_element(root, main_element, tags_dict[main_element], json_data)

        check_exists_folder_and_create(join(ARTICLES_DIR, json_data['Language']))
        save_file(join(join(ARTICLES_DIR, json_data['Language']), json_data['Article-name'] + '.json'), json_data)
        print(json_data)


if __name__ == "__main__":
    main()
