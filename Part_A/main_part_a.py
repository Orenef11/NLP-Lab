import sys
from os import path, getcwd
sys.path.insert(0, path.split(getcwd())[0])
from time import clock
from logger import setting_up_logger
from Stories_URL import StoriesURL
from HTML_Parser import HTMLParser
from rename_and_add_details import RenameAndAddDetails
import logging
from config_parser import config_parser
from create_meta_data import create_part_a_meta_data

CONFIG_FILE_PATH = path.join(path.split(getcwd())[0], 'config.ini')

def main():
    start_time = clock()
    config_variables_dict = config_parser(CONFIG_FILE_PATH)
    # Defines the log file, which will contain all the prints of the program.
    log_path = config_variables_dict['log_file_part_a']
    setting_up_logger('debug', 'info', log_path)
    download_new_stories_flag = config_variables_dict['download_new_stories_flag']
    # For each website, we create a file that contains for each story him link to his story page.
    html_pages_stories_folder = config_variables_dict['html_pages_stories_folder']
    website_stories_folder = config_variables_dict['website_stories_folder']
    StoriesURL(website_stories_folder, html_pages_stories_folder).run(download_new_stories_flag)
    logging.info("\nThe time taken to create for each site the file that contains all the stories is {:0.4f} seconds"
                 .format(clock() - start_time))
    html_parser_time = clock()
    HTMLParser(html_pages_stories_folder, log_path, config_variables_dict['json_stories_folder'],
               config_variables_dict['debugging_output_folder'], config_variables_dict['unsaved_stories_folder']).run()
    logging.info("\nHTML_Parser: Total runtime is {:0.4f} seconds".format(clock() - html_parser_time))
    rename_time = clock()
    unknown_folder = config_variables_dict['unknown_folder']
    separator_char_rename_file = config_variables_dict['separator_char_rename_file']
    info_stories_file = config_variables_dict['info_stories_file']
    RenameAndAddDetails(info_stories_file, unknown_folder, log_path, separator_char_rename_file).run()
    logging.info("\nRename_And_Add_Details: Total runtime is {:0.4f} seconds".format(clock() - rename_time))

    create_part_a_meta_data(config_variables_dict['json_stories_folder'],
                            path.join(config_variables_dict['meta_data_folder'], path.split(getcwd())[-1]))
    logging.info("\nThe total time taken for the program to run is {:0.4f} minutes"
                 .format((clock() - start_time) / 60.0))


if __name__ == "__main__":
    main()
