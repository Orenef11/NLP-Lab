from time import clock
from logger import setting_up_logger, logger_print_msg
from os import path, makedirs
from Stories_URL import StoriesURL
from HTML_Parser import HTMLParser
from rename_and_add_details import RenameAndAddDetails
from shutil import rmtree

DEBUGGING_OUTPUT_FOLDER = 'Debugging Files'
LOG_FILE = 'log.log'
UNSAVED_STORIES_FILE = 'Unsaved Stories Files'
HTML_STORIES_FOLDER = 'Website stories page'
LINK_STORIES_FOLDER = 'Data page stories'
JSON_STORIES_FOLDER = 'Json stories'
UNKNOWN_FOLDER_PATH = path.join(JSON_STORIES_FOLDER, 'unknown')
INFO_STORIES_FILE = 'unknown files dictionary.txt'


def create_important_folders(folders_path_list):
    for folder_path in folders_path_list:
        if path.isdir(folder_path):
            rmtree(folder_path)
        logger_print_msg("Crate '{}' folder".format(folder_path))
        makedirs(folder_path)


def main():
    start_time = clock()
    # Defines the log file, which will contain all the prints of the program.
    log_path = path.join(DEBUGGING_OUTPUT_FOLDER, LOG_FILE)
    setting_up_logger('debug', 'info', log_path)
    # JSON_STORIES_FOLDER
    create_important_folders([UNSAVED_STORIES_FILE])
    # For each website, we create a file that contains for each story him link to his story page.
    StoriesURL(HTML_STORIES_FOLDER, LINK_STORIES_FOLDER).run(False)
    logger_print_msg("The time taken to create for each site the file that contains all the stories is {} seconds"
                     .format(clock() - start_time))

    html_parser_time = clock()
    HTMLParser(LINK_STORIES_FOLDER, path.join(DEBUGGING_OUTPUT_FOLDER, "report_stories.txt"),
               log_path, JSON_STORIES_FOLDER, DEBUGGING_OUTPUT_FOLDER, UNSAVED_STORIES_FILE).run()
    logger_print_msg("HTML_Parser: Total runtime is {:0.4f} seconds".format(clock() - html_parser_time))
    rename_time = clock()

    RenameAndAddDetails(INFO_STORIES_FILE, UNKNOWN_FOLDER_PATH, LOG_FILE).run()
    logger_print_msg("RenameAndAddDetails: Total runtime is {:0.4f} seconds".format(clock() - rename_time))

    logger_print_msg("The total time taken for the program to run is {:0.4f} minutes"
                     .format((clock() - start_time) / 60.0))

if __name__ == "__main__":
    main()
