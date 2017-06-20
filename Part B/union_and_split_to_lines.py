from config_parser import config_parser
from os import path, getcwd, listdir, makedirs, remove
from json import load
from pandas import DataFrame
from logger import setting_up_logger
from traceback import print_exc
import logging


def create_meta_data_csv_files(stories_folder_path, meta_data_path):
    if not path.isdir(meta_data_path):
        makedirs(meta_data_folder_path)
        logging.debug("\nCreate folder in the following '{}' path.".format(meta_data_path))
    folders_names_list = listdir(stories_folder_path)
    folders_names_list.remove('unknown')

    language_details_list = []
    files_details_list = []

    try:
        for folder_name in folders_names_list:
            folder_path = path.join(stories_folder_path, folder_name)
            lang_name, stories_count, words_count, translators_names, authors_names = \
                folder_name, len(listdir(folder_path)), 0, [], []

            for filename in listdir(folder_path):
                file_path = path.join(folder_path, filename)
                if '.json' not in file_path:
                    remove(file_path)
                    logging.debug("Remove '{}' file, because it is not formatted json".format(file_path))
                    continue
                with open(file_path, mode='r', encoding='UTF-8') as file2:
                    try:
                        json_data = load(file2)
                        # Count the number of words
                        words_count_in_story = len(json_data['Article-text'].split(" "))
                        words_count += words_count_in_story
                        # List of duplicates of authors' names
                        authors_names.append(json_data["Author"])
                        # List of duplicates of translators' name
                        translator_name = 'empty'
                        if "Translator" in json_data.keys():
                            translator_name = json_data["Translator"]
                            translators_names.append(translator_name)
                        files_details_list.append([folder_name, filename, json_data["Author"], translator_name,
                                                   words_count_in_story])
                    except Exception as _:
                        logging.info(print_exc())
                        continue

            translators_names, authors_names = set(translators_names), set(authors_names)
            translators_names_count, authors_names_count = len(translators_names), len(authors_names)
            translators_names = '\n'.join(translators_names)
            authors_names = '\n'.join(authors_names)
            language_details_list.append([lang_name, stories_count, words_count, translators_names,
                                          translators_names_count, authors_names, authors_names_count])
        language_details_list.sort(key=lambda lang_list: lang_list[0])
        files_details_list.sort(key=lambda lang_list: lang_list[0])
        DataFrame(data=language_details_list,
                  columns=['lang', 'stories count', 'words count', 'translators names', 'translators count',
                           'authors names', 'authors count'])\
            .to_csv(path.join(meta_data_path, 'lang_details.csv'), index=False)
        DataFrame(data=files_details_list,
                  columns=['lang', 'story', 'author', 'translator', 'words count'])\
            .to_csv(path.join(meta_data_path, 'files_details.csv'), index=False)

    except Exception as _:
        logging.info(print_exc())


if __name__ == '__main__':
    config_dict = config_parser(path.join(getcwd(), 'config.ini'))

    setting_up_logger('debug', 'info', config_dict['log_file_part_b'])
    unknown_folder_path = config_dict['unknown_folder']
    json_stories_folder_path = config_dict['json_stories_folder']
    meta_data_folder_path = config_dict['meta_data_folder']
    create_meta_data_csv_files(json_stories_folder_path, meta_data_folder_path)


