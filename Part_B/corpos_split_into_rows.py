from config_parser import config_parser
from os import path, getcwd, listdir, makedirs
from json import load
from logger import setting_up_logger
import logging


class SplitCorposToLines(object):
    def __init__(self, stories_folder_path, folder_destination_path, folder_uniting_corpos_path):
        if not path.isdir(folder_destination_path):
            makedirs(folder_destination_path)
            logging.debug("\r\nCreated the '{}' folder successfully".format(folder_destination_path))
        self.__stories_folder_path = [folder_path for folder_path in stories_folder_path if path.isdir(folder_path)]
        self.__folder_destination_path = folder_destination_path
        self.__folder_uniting_corpos_path = folder_uniting_corpos_path
        if not path.isdir(self.__folder_uniting_corpos_path):
            makedirs(self.__folder_uniting_corpos_path)

    @staticmethod
    def __uniting_stories(folder_path):
        file_path_list = [path.join(folder_path, file_name) for file_name in listdir(folder_path)]

        data = ''
        for file_path in file_path_list:
            with open(file_path, encoding='utf-8') as f:
                data += load(f)['Article-text']
        return data

    @staticmethod
    def __read_story_data(story_file_path):
        with open(story_file_path, encoding='utf-8') as f:
            return load(f)['Article-text']

    @staticmethod
    def __save_file_data(corpos_data, file_path):
        data = corpos_data.replace('\xa0', '')
        data = data.replace('\t', ' ')
        data = data.replace('  ', ' ')
        data = ';\r\n'.join(data.split('; '))
        data = '.\r\n'.join(data.split('. '))
        data = '?!\r\n'.join(data.split('?! '))
        data = '!?\r\n'.join(data.split('?! '))
        data = '!\r\n'.join(data.split('! '))
        data = '?\r\n'.join(data.split('? '))
        data = ':\r\n'.join(data.split(': '))
        data = '\r\n'.join(data.split('\n\n'))
        data = '\r\n'.join(data.split('\n'))
        data = '\r\n'.join(data.split('\r\n\n'))
        data = '\r\n'.join(data.split('\r\r\n'))

        lines = data.split('\r\n')
        data_list, temp, idx = [], '', 1
        for line in lines:
            # for char_split in ['']
            if line == '':
                continue

            if '?!' in line or '?!' in line or '!' in line or '?' in line or ';' in line or ':' in line:
                if temp != '':
                    if '.' not in temp:
                        data_list.append(temp + ' ' + line + '\r\n')
                        temp = ''
                        # idx += 1
                        continue
                    data_list.append(temp + '\r\n')
                    temp = ''
                    # idx += 1

                data_list.append(line + '\r\n')

            elif '.' not in line or '.' in line and line[line.index('.') - 1].isdigit():
                if temp == '':
                    temp += line
                else:
                    temp += ' ' + line
            else:
                if temp != '':
                    if '.' not in temp:
                        data_list.append(temp + ' ' + line + '\r\n')
                        temp = ''
                        # idx += 1
                        continue
                    data_list.append(temp + '\r\n')
                    temp = ''
                data_list.append(line)
        data_list = [line.strip() for line in data_list if line.strip() != '']
        data = '\r\n'.join(data_list)
        with open(file_path, 'w', encoding='UTF-8') as f:
            f.write(data)

        if '\u2032' in file_path:
            file_path = file_path.replace('\u2032', '')
        logging.debug("\r\nCreated the '{}' file successfully".format(file_path))

    def run(self):
        for folder_source_path in self.__stories_folder_path:
            # The name of the folder in Hebrew should therefore be done 'encode'
            folder_name = path.split(folder_source_path.encode())[-1].decode()
            folder_destination_path = path.join(self.__folder_destination_path, folder_name)
            if not path.isdir(folder_destination_path):
                makedirs(folder_destination_path)
                logging.debug("\r\nCreated the '{}' folder successfully".format(folder_destination_path))

            for file_name in listdir(folder_source_path):
                story_source_file_path = path.join(folder_source_path, file_name)
                file_name = path.split(file_name.encode())[-1].decode()
                file_name = file_name.replace('.json', '.txt')
                story_file_path = path.join(folder_destination_path, file_name)
                story_data = self.__read_story_data(story_source_file_path)
                self.__save_file_data(story_data, story_file_path)

            corpos_data = self.__uniting_stories(folder_source_path)
            self.__save_file_data(corpos_data, path.join(self.__folder_uniting_corpos_path, folder_name) + '.txt')
