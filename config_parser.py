from os import path, getcwd, makedirs
from configparser import ConfigParser

PART_A_FOLDER = 'Part A'


def config_parser(config_file_path):
    if not path.isfile(config_file_path):
        print("The configuration file does not exist in this '{}' path".format(config_file_path))
        exit()
    config_dict = {}
    config = ConfigParser()
    config.read(config_file_path)

    # Set the variables for each folder path
    config_dict['unsaved_stories_folder'] = config.get('folders', 'unsaved_stories_folder')
    config_dict['json_stories_folder'] = config.get('folders', 'json_stories_folder')
    config_dict['unknown_folder'] = path.join(config_dict['json_stories_folder'],
                                              config.get('folders', 'unknown_folder'))
    config_dict['website_stories_folder'] = config.get('folders', 'website_stories_folder')
    config_dict['html_pages_stories_folder'] = config.get('folders', 'html_page_stories_folder')
    part_a_folder_path = config.get('folders', 'part_a_folder_path')
    config_dict = {key: path.join(part_a_folder_path, value) for key, value in config_dict.items()}
    config_dict['debugging_output_folder'] = path.join(path.split(getcwd())[0],
                                                       config.get('folders', 'debugging_output_folder'))
    config_dict['meta_data_folder'] = path.join(config_dict['debugging_output_folder'],
                                                config.get('folders', 'meta_data_folder'))

    # Set the variables for each folder path
    if not path.isdir(config_dict['debugging_output_folder']):
        makedirs(config_dict['debugging_output_folder'])
    config_dict['log_file_part_a'] = path.join(config_dict['debugging_output_folder'],
                                               config.get('log files', 'log_file_part_a'))
    config_dict['log_file_part_b'] = path.join(config_dict['debugging_output_folder'],
                                               config.get('log files', 'log_file_part_b'))
    config_dict['info_stories_file'] = config.get('log files', 'info_stories_file')

    # Set variables for separator characters
    config_dict['separator_char_rename_file'] = config.get('Separator characters', 'separator_char_rename_file')

    return config_dict
