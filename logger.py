import logging

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

level = LEVELS['debug']
LOG_FILE = r"logs.log"


def setting_up_logger(file_logging_level, console_logging_level):
    file_logging_level = str(file_logging_level).lower()
    console_logging_level = str(console_logging_level).lower()
    if not file_logging_level in LEVELS or not console_logging_level in LEVELS:
        print("Error level logging: The values to be inserted are: ", LEVELS.keys())
        exit()

    # set up logging to file - see previous section for more details
    logging.basicConfig(level=LEVELS[file_logging_level],
                        format='%(asctime)s\t[%(threadName)-12.12s] %(msecs)d %(name)s [%(levelname)-5.5s]  '
                               '%(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', filename=LOG_FILE, filemode='a')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(LEVELS[console_logging_level])
    # set a format which is simpler for console use
    formatter = logging.Formatter(
        '%(asctime)s\t[%(threadName)s] %(msecs)d %(name)s [%(levelname)s]  %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
