from codecs import open
from json import loads, dumps
from os import path, listdir, makedirs
from shutil import move
from traceback import print_exc
import logging


class RenameAndAddDetails(object):
    def __init__(self, info_stories_file, unknown_folder_path, log_path, separator_char):
        self.__separator_char = separator_char
        self.__details_dict = self.__parser_file(info_stories_file)
        self.__unknown_folder_path = unknown_folder_path
        self.__log_path = log_path

    def __parser_file(self, file_path):
        details_dict = {}
        with open(file_path, mode='r', encoding='utf-8') as f:
            for idx, line in enumerate(f.readlines()):
                idx += 1
                if self.__separator_char not in line or len(line.split(self.__separator_char)) != 4:
                    logging.info("Invalid structure(line {}): Each line should be from the following structure"
                                 .format(idx))
                    logging.info("Name of the story: Name of the author: Name of the translator: The language of "
                                 "the story.\r\nIn addition, it is important to note that '{}' is part of a structure!"
                                 .format(self.__separator_char))
                    continue
                line_list = line.split(':')
                if '(' in line_list[0] and ')' not in line_list[0] or '(' not in line_list[0] and ')' in line_list[0]:
                    logging.info("Invalid book's name (line {}): If you want to change the name of the book, you must "
                                 "type it under parentheses, for example 'old name (new name)'.".format(idx))
                    continue
                name_of_book = None
                if '(' and ')' in line_list[0]:
                    name_of_book = line_list[0]
                    name_of_book = name_of_book.replace(')', '')
                    name_of_book = name_of_book.split('(')
                if name_of_book is not None:
                    name_of_book_key = name_of_book[0].strip()
                    details_dict[name_of_book_key] = {
                        'new_name_for_book': name_of_book[1].strip()
                    }
                else:
                    name_of_book_key = line_list[0].strip()
                    details_dict[name_of_book_key] = {
                        'book_new_name': name_of_book_key
                    }
                details_dict[name_of_book_key]['Author'] = line_list[1].strip()
                details_dict[name_of_book_key]['Translator'] = line_list[2].strip()
                details_dict[name_of_book_key]['Language'] = line_list[3].strip()

        return details_dict

    def __add_details(self, book_path, book_name):
        if not path.isfile(book_path):
            return None
        if '.json' in book_name:
            book_name = book_name.replace('.json', '')
        if book_name not in self.__details_dict.keys():
            logging.debug("\nThe '{}' book does not exist".format(book_name))
            return None
        new_name_book = book_name
        if 'new_name_for_book' in self.__details_dict[book_name].keys():
            new_name_book = self.__details_dict[book_name]['new_name_for_book']

        with open(filename=book_path, mode='r', encoding='utf8') as f:
            book_json = loads(f.read())
        book_json['Article-name'] = new_name_book
        book_json['Language'] = self.__details_dict[book_name]['Language']
        book_json['Author'] = self.__details_dict[book_name]['Author']
        book_json['Translator'] = self.__details_dict[book_name]['Translator']

        with open(filename=book_path, mode='w', encoding='utf8') as f:
            f.write(dumps(book_json, ensure_ascii=False, indent=4, sort_keys=True))
        new_book_path = path.join(path.join(path.split(self.__unknown_folder_path)[0],
                                            book_json['Language']), new_name_book + '.json')
        
        try:
            if not path.isdir(path.split(new_book_path)[0]):
                makedirs(path.split(new_book_path)[0])
            move(book_path, new_book_path)
        except Exception as _:
            logging.info(print_exc())
            exit()

        logging.debug("\nThe file move from '{}' to '{}'".format(book_path, new_book_path))

    def run(self):
        files_path_list = [path.join(self.__unknown_folder_path, filename) for filename in
                           listdir(self.__unknown_folder_path)]
        for file_path in files_path_list:
            self.__add_details(file_path, path.split(file_path)[1])
