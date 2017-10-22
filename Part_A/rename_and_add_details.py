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
                    logging.info("\nInvalid structure(line {}): Each line should be from the following structure"
                                 .format(idx))
                    logging.info("\nName of the story: Name of the author: Name of the translator: The language of "
                                 "the story.\r\nIn addition, it is important to note that '{}' is part of a structure!"
                                 .format(self.__separator_char))
                    continue
                line_list = line.split(self.__separator_char)
                if '(' in line_list[0] and ')' not in line_list[0] or '(' not in line_list[0] and ')' in line_list[0]:
                    logging.info("Invalid story's name (line {}): If you want to change the name of the story, you "
                                 "must type it under parentheses, for example 'old name (new name)'.".format(idx))
                    continue
                name_of_story = None
                if '(' and ')' in line_list[0]:
                    name_of_story = line_list[0]
                    name_of_story = name_of_story.replace(')', '')
                    name_of_story = name_of_story.split('(')
                if name_of_story is not None:
                    name_of_story_key = name_of_story[0].strip()
                    details_dict[name_of_story_key] = {'new_name_for_story': name_of_story[1].strip()}
                else:
                    name_of_story_key = line_list[0].strip()
                    details_dict[name_of_story_key] = {'story_new_name': name_of_story_key}
                details_dict[name_of_story_key]['Author'] = line_list[1].strip()
                details_dict[name_of_story_key]['Translator'] = line_list[2].strip()
                details_dict[name_of_story_key]['Language'] = line_list[3].strip()

        return details_dict

    def __add_details(self, story_path, story_name):
        if not path.isfile(story_path):
            return None
        if '.json' in story_name:
            story_name = story_name.replace('.json', '')
        if story_name not in self.__details_dict.keys():
            logging.debug("\nThe '{}' story does not exist".format(story_name))
            return None
        new_name_story = story_name
        if 'new_name_for_story' in self.__details_dict[story_name].keys():
            new_name_story = self.__details_dict[story_name]['new_name_for_story']

        with open(filename=story_path, mode='r', encoding='utf8') as f:
            story_json = loads(f.read())
        story_json['Article-name'] = new_name_story
        story_json['Language'] = self.__details_dict[story_name]['Language']
        story_json['Author'] = self.__details_dict[story_name]['Author']
        story_json['Translator'] = self.__details_dict[story_name]['Translator']

        with open(filename=story_path, mode='w', encoding='utf8') as f:
            f.write(dumps(story_json, ensure_ascii=False, indent=4, sort_keys=True))
        new_story_path = path.join(path.join(path.split(self.__unknown_folder_path)[0],
                                             story_json['Language']), new_name_story + '.json')

        try:
            if not path.isdir(path.split(new_story_path)[0]):
                makedirs(path.split(new_story_path)[0])
            move(story_path, new_story_path)
        except Exception as _:
            logging.info(print_exc())
            exit()

        logging.debug("\nThe file move from '{}' to '{}'".format(story_path, new_story_path))

    def run(self):
        files_path_list = [path.join(self.__unknown_folder_path, filename) for filename in
                           listdir(self.__unknown_folder_path)]
        for file_path in files_path_list:
            self.__add_details(file_path, path.split(file_path)[1])
