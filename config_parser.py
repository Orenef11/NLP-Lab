from os import path, getcwd, makedirs
from configparser import ConfigParser

def config_parser(config_file_path):
    if not path.isfile(config_file_path):
        print("The configuration file does not exist in this '{}' path".format(config_file_path))
        exit()
    config_dict, config, root_folder_path = {}, ConfigParser(), getcwd()
    config.read(config_file_path)

    part_a_folder_path = config.get('folders', 'part_a_folder_path')
    part_b_folder_path = config.get('folders', 'part_b_folder_path')
    part_c_folder_path = config.get('folders', 'part_c_folder_path')
    part_d_folder_path = config.get('folders', 'part_d_folder_path')

    if path.split(root_folder_path)[-1] in [part_a_folder_path, part_b_folder_path, part_c_folder_path,
                                            part_d_folder_path]:
        root_folder_path = path.split(root_folder_path)[0]

    # Set the variables for each folder path
    config_dict['part_a_path_folder'] = part_a_folder_path
    config_dict['part_b_path_folder'] = part_b_folder_path
    config_dict['part_c_path_folder'] = part_c_folder_path
    config_dict['part_d_path_folder'] = part_d_folder_path

    config_dict['unsaved_stories_folder'] = path.join(part_a_folder_path,
                                                      config.get('folders', 'unsaved_stories_folder'))
    config_dict['json_stories_folder'] = path.join(part_a_folder_path, config.get('folders', 'json_stories_folder'))
    config_dict['unknown_folder'] = path.join(config_dict['json_stories_folder'],
                                              config.get('folders', 'unknown_folder'))
    config_dict['html_pages_stories_folder'] = path.join(part_a_folder_path,
                                                         config.get('folders', 'html_page_stories_folder'))
    config_dict['debugging_output_folder'] = config.get('folders', 'debugging_output_folder')
    config_dict['website_stories_folder'] = path.join(part_a_folder_path,
                                                      config.get('folders', 'website_stories_folder'))
    config_dict['part_b_images_folder_path'] = path.join(part_b_folder_path,
                                                         config.get('folders', 'images_analysis_folder'))
    config_dict['part_c_images_folder_path'] = path.join(part_c_folder_path,
                                                         config.get('folders', 'images_analysis_folder'))
    config_dict['meta_data_folder'] = config.get('folders', 'meta_data_folder')
    config_dict['stories_text_files_folder'] = path.join(part_b_folder_path,
                                                         config.get('folders', 'stories_text_folder'))
    config_dict['uniting_stories_folder'] = path.join(config_dict['stories_text_files_folder'],
                                                      config.get('folders', 'uniting_stories_folder'))
    config_dict['log_file_part_a'] = path.join(config_dict['debugging_output_folder'],
                                               config.get('log files', 'log_file_part_a'))
    config_dict['log_file_part_b'] = path.join(config_dict['debugging_output_folder'],
                                               config.get('log files', 'log_file_part_b'))
    config_dict['log_file_part_c'] = path.join(config_dict['debugging_output_folder'],
                                               config.get('log files', 'log_file_part_c'))
    config_dict['log_file_graphs'] = path.join(config_dict['debugging_output_folder'],
                                                  config.get('log files', 'log_file_graphs'))
    config_dict['info_stories_file'] = path.join(part_a_folder_path, config.get('log files', 'info_stories_file'))

    # Creates the full path of the folder for each path
    config_dict = dict([(key, path.join(root_folder_path, value)) for key, value in config_dict.items()])

    config_dict['separator_char_rename_file'] = config.get('Separator characters', 'separator_char_rename_file')

    # Debugging mode for each part of the task
    config_dict['part_b_debugging_mode'] = True if config.get('Debugging mode',
                                                              'part_b_debugging_mode').lower() == 'true' else False
    config_dict['part_c_debugging_mode'] = True if config.get('Debugging mode',
                                                              'part_c_debugging_mode').lower() == 'true' else False
    config_dict['download_new_stories_flag'] = False if config.get(
        'Debugging mode', 'download_new_stories_flag').lower() == 'false' else True

    # Vectors variables
    config_dict['chunk_size'] = int(config.get('Vectors', 'chunk_size'))
    config_dict['feature_vectors_size'] = int(config.get('Vectors', 'feature_vectors_size'))
    config_dict['kfold_size'] = int(config.get('Vectors', 'kfold_size'))

    # Classifier variables
    config_dict['multi_process_flag'] = True if config.get(
        'Classifier', 'multi_process').lower() == 'true' else False
    config_dict['print_predict_analysis_flag'] = True if config.get(
        'Classifier', 'print_predict_analysis_flag').lower() == 'true' else False
    config_dict['corpora_from_file_flag'] = True if config.get(
        'Classifier', 'corpora_from_file_flag').lower() == 'true' else False
    config_dict['cores_size'] = int(config.get('Classifier', 'cores_size'))

    return config_dict
