import sys
from os import path, getcwd, listdir, makedirs
sys.path.insert(0, path.split(getcwd())[0])
from config_parser import config_parser
from logger import setting_up_logger
from traceback import print_exc
import logging
from corpos_split_into_rows import SplitCorposToLines
from time import clock
from Vectors import Vectors
from Classify import Classify
from pickle import loads, dumps
from gzip import decompress, compress
from create_meta_data import create_part_b_meta_data


def __save_pickle_file(pickle_file_path, pickle_data):
    with open(pickle_file_path, 'wb') as fp:
        fp.write(compress(dumps(pickle_data)))


def __read_pickle_file(pickle_file_path):
    with open(pickle_file_path, 'rb') as fp:
        return loads(decompress(fp.read()))


def __import_feature_vectors(source_feature_vectors_file_path, translation_feature_vectors_file_path):
    feature_vectors = []
    feature_vectors += __read_pickle_file(source_feature_vectors_file_path)
    feature_vectors += __read_pickle_file(translation_feature_vectors_file_path)

    return feature_vectors


def main():
    try:
        start_time = clock()
        root_folder_path = path.split(getcwd())[0]
        config_dict = config_parser(path.join(root_folder_path, 'config.ini'))
        setting_up_logger('debug', 'info', config_dict['log_file_part_b'])

        feature_vectors, debugging_mode, mini_features_vectors, k_fold_split_data, feature_vectors_size = \
            [], config_dict['part_b_debugging_mode'], [], [], config_dict['feature_vectors_size']
        kfold_size, multi_process_flag = config_dict['kfold_size'], config_dict['multi_process_flag']
        debugging_output_folder = path.join(config_dict['debugging_output_folder'], path.split(getcwd())[1])
        if not path.isdir(debugging_output_folder):
            makedirs(debugging_output_folder)
            logging.info("\nThe '{}' folder created successfully".format(debugging_output_folder))
        source_feature_vectors_file_path = path.join(debugging_output_folder, "source_feature_vectors.pickle.gz")
        translation_feature_vectors_file_path = path.join(debugging_output_folder, "translation_feature_vectors"
                                                                                   ".pickle.gz")
        mini_features_vectors_file_path = path.join(debugging_output_folder, "mini_features_vectors.pickle.gz")
        chunk_size = config_dict['chunk_size']

        if not debugging_mode or not path.isfile(source_feature_vectors_file_path) or \
                not path.isfile(translation_feature_vectors_file_path):
            unknown_folder_path = path.join(root_folder_path, config_dict['unknown_folder'])
            json_folder_path = path.join(root_folder_path, config_dict['json_stories_folder'])
            stories_text_files_folder_path = path.join(root_folder_path, config_dict['stories_text_files_folder'])
            corpora_uniting_stories_folder = config_dict['uniting_stories_folder']
            hebrew_corpora_folder_path = path.join(corpora_uniting_stories_folder, 'עברית.txt')
            folder_path_list = [path.join(json_folder_path, file_name) for file_name in listdir(json_folder_path)]
            folder_path_list.remove(unknown_folder_path)

            split_corpos_time = clock()
            logging.info("\nStart of split corpus into rows")
            SplitCorposToLines(folder_path_list, stories_text_files_folder_path, corpora_uniting_stories_folder).run()
            logging.info("\nThe time taken to split each story and contains all the stories was {:0.4f} seconds"
                         .format(clock() - split_corpos_time))

            meta_data_time = clock()
            logging.info("\nStart create meta data")
            create_part_b_meta_data(stories_text_files_folder_path, corpora_uniting_stories_folder,
                                    path.join(config_dict['meta_data_folder'], path.split(getcwd())[-1]), chunk_size)
            logging.info("\nThe time taken to created meta data for stories and corpos was {:0.4f} seconds".format(
                clock() - meta_data_time))

            feature_vectors_time = clock()
            logging.info("\nStart create feature vectors for hebrew abd translation corpora")
            corpora_label_dict = {'hebrew': 1, 'translation': 2}
            meta_data_folder = path.join(config_dict['meta_data_folder'], path.split(getcwd())[1])
            feature_vectors = \
                Vectors(corpora_uniting_stories_folder, corpora_label_dict, debugging_output_folder, meta_data_folder,
                        chunk_size, debugging_mode).part_b_run(hebrew_corpora_folder_path, True)
            logging.info("\nThe time taken created feature vectors for hebrew abd translation corpora was {:0.4f} "
                         "mins".format((clock() - feature_vectors_time) / 60.0))

        if debugging_mode is True:
            if not path.isfile(mini_features_vectors_file_path):
                logging.info("\n** Debugging mode **: the data uploaded may be old and therefore the test "
                             "is incorrect!")
                feature_vectors = __import_feature_vectors(source_feature_vectors_file_path,
                                                           translation_feature_vectors_file_path)
                mini_features_vectors = \
                    feature_vectors[: feature_vectors_size] + feature_vectors[-feature_vectors_size:]
                logging.info("\n Save '{}' features vectors from each corpora".format(feature_vectors_size))
                __save_pickle_file(mini_features_vectors_file_path, mini_features_vectors)
                feature_vectors = mini_features_vectors
            else:
                logging.info("\n** Debugging mode **: the data uploaded may be old and therefore the test "
                             "is incorrect!")
                feature_vectors += __read_pickle_file(mini_features_vectors_file_path)

            logging.info("\n** Debugging mode **: total feature vectors are {}".format(len(feature_vectors)))
        else:
            logging.info("\nTotal feature vectors are {}".format(len(feature_vectors)))

        classify_obj = Classify(feature_vectors, {'hebrew': 1, 'other': 2}, multi_process_flag, kfold_size,
                                config_dict['print_predict_analysis_flag'])
        kfold_split_time = clock()
        logging.info("\nCreate kfold split indexes")
        k_fold_split_data = classify_obj.create_kfold_split_data()
        logging.info("\nThe time taken created {}-kfold split was {:0.4f} mins"
                     "".format(kfold_size, (clock() - kfold_split_time) / 60.0))

        classify_time = clock()
        if debugging_mode is True:
            logging.info("\n** Debugging mode **: Start classify")
        else:
            logging.info("\nStart classify")
        classify_obj.run_classifier(k_fold_split_data)
        if debugging_mode is True:
            logging.info("\n** Debugging mode **: Finished classify, it taken {:0.4f} mins"
                         "".format((clock() - classify_time) / 60.0))
        else:
            logging.info("\nFinished classify, it taken {:0.4f} mins".format((clock() - classify_time) / 60.0))

        logging.info("\nThe total time taken for the program to run is {:0.4f} minutes".format(
            (clock() - start_time) / 60.0))
    except Exception as e:
        print_exc()


if __name__ == '__main__':
    main()
