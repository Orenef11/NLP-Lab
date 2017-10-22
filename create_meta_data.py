from os import path, listdir, makedirs, remove
from json import load
from pandas import DataFrame
from traceback import print_exc
import logging


def __get_chunks_size(lines, chunk_size):
    chunks_count, last_chunk, last_chunk_size = 0, [], 0
    for line in lines:
        if last_chunk_size <= chunk_size < last_chunk_size + len(line):
            chunks_count += 1
            last_chunk = []
            last_chunk_size = 0

        last_chunk.append(line)
        last_chunk_size += len(line)

    chunks_count += 1
    return chunks_count


def create_part_a_meta_data(stories_folder_path, meta_data_folder_path):
    if not path.isdir(meta_data_folder_path):
        makedirs(meta_data_folder_path)
        logging.debug("\nCrate '{}' folder".format(meta_data_folder_path))
    folders_names_list = listdir(stories_folder_path)
    if 'unknown' in folders_names_list:
        folders_names_list.remove('unknown')

    language_details_list, files_details_list = [], []
    try:
        for folder_name in folders_names_list:
            if not path.isdir(folder_name):
                continue
            folder_path = path.join(stories_folder_path, folder_name)
            lang_name, stories_count, words_count, translators_names, authors_names = \
                folder_name, len(listdir(folder_path)), 0, [], []

            for filename in listdir(folder_path):
                json_file_path = path.join(folder_path, filename)

                if '.json' not in json_file_path:
                    remove(json_file_path)
                    logging.debug("Remove '{}' file, because it is not formatted json".format(json_file_path))
                    continue
                with open(json_file_path, encoding='UTF-8') as file2:
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

                        filename = filename.replace('.json', '')
                        files_details_list.append([folder_name, filename, json_file_path,
                                                   json_data["Author"], translator_name, words_count_in_story])
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
        temp = DataFrame(data=language_details_list,
                  columns=['lang', 'stories count', 'words count', 'translators names',
                           'translators count', 'authors names', 'authors count']).sort_values('lang')
        temp.to_csv(path.join(meta_data_folder_path, 'lang_details.csv'), index=False)

        temp = DataFrame(data=files_details_list,columns=['lang', 'story name', 'json story path', 'author',
                                                          'translator', 'words count']).sort_values('lang')
        temp.to_csv(path.join(meta_data_folder_path, 'stories_details.csv'), index=False)
    except Exception as _:
        logging.info(print_exc())


def create_part_b_meta_data(stories_text_folder_path, corpos_language_folder_path, meta_data_folder_path, chunks_size):
    if not path.isdir(meta_data_folder_path):
        makedirs(meta_data_folder_path)
        logging.debug("\nCrate '{}' folder".format(meta_data_folder_path))
    folders_path_list = [path.join(stories_text_folder_path, folder_name) for folder_name in listdir(
        stories_text_folder_path) if path.isdir(path.join(stories_text_folder_path, folder_name))]
    folders_path_list.remove(corpos_language_folder_path)

    stories_details_list, stories_number_each_lang_dict = [], {}
    for folder_path in folders_path_list:
        stories_number_each_lang_dict[path.split(folder_path)[-1]] = len(listdir(folder_path))
        for file_path in [path.join(folder_path, filename) for filename in listdir(folder_path)]:
            with open(file_path, encoding='utf-8') as story_file:
                story_data = story_file.readlines()

            lang, story_name, story_chunks_size = path.split(folder_path)[-1], str(path.split(file_path)[-1]).replace(
                '.txt', ''), __get_chunks_size(story_data, chunks_size)
            stories_details_list.append([lang, story_name, file_path, len(story_data), story_chunks_size])

    corpora_details_list = []
    for corpora_file_path in [path.join(corpos_language_folder_path, corpos_file_mane) for corpos_file_mane in
                              listdir(corpos_language_folder_path)]:
        corpora_name = path.split(corpora_file_path)[-1].replace('.txt', '')
        with open(corpora_file_path, encoding='utf-8') as story_file:
            corpora_data = story_file.readlines()
        corpora_details_list.append([corpora_name, corpora_file_path, stories_number_each_lang_dict[corpora_name],
                                     len(corpora_data), __get_chunks_size(corpora_data, chunks_size)])

    temp = DataFrame(data=stories_details_list,
              columns=['lang', 'story name', 'story path', 'lines number', 'chunks number']).sort_values('lang')
    temp.to_csv(path.join(meta_data_folder_path, 'stories_details.csv'), index=False)

    temp = DataFrame(data=corpora_details_list, columns=['lang', 'corpora name', 'stories number', 'lines number',
                                                         'chunks number']).sort_values('lang')
    temp.to_csv(path.join(meta_data_folder_path, 'corpora_details.csv'), index=False)
