import sys
from os import path, getcwd, makedirs, listdir
sys.path.insert(0, path.split(getcwd())[0])
from config_parser import config_parser
from logger import setting_up_logger
from traceback import print_exc
import logging
from time import clock
from Vectors import Vectors
from Classify import Classify
from pickle import loads, dumps
from gzip import decompress, compress


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


def __save_pickle_file(pickle_file_path, pickle_data):
    with open(pickle_file_path, 'wb') as fp:
        fp.write(compress(dumps(pickle_data)))


def __read_pickle_file(pickle_file_path):
    with open(pickle_file_path, 'rb') as fp:
        return loads(decompress(fp.read()))


def main():
    try:
        start_time = clock()
        root_folder_path = path.split(getcwd())[0]
        config_dict = config_parser(path.join(root_folder_path, 'config.ini'))
        setting_up_logger('debug', 'info', config_dict['log_file_part_c'])

        kfold_size, chunk_size, corpora_names_list = config_dict['kfold_size'], config_dict['chunk_size'], []
        corpora_uniting_stories_folder = config_dict['uniting_stories_folder']
        corpora_from_file_flag = config_dict['corpora_from_file_flag']
        if corpora_from_file_flag is True:
            if not path.isfile("corpora_names_to_classifier.txt"):
                logging.info("\nThe '{}' file missing".format('corpora_names_to_classifier.txt'))
                exit()
            else:
                with open("corpora_names_to_classifier.txt", encoding='utf-8') as f:
                    corpora_names_list = [corpora_name.strip() for corpora_name in f.readlines()]
        else:
            for corpora_file_name in listdir(corpora_uniting_stories_folder):
                corpora_path_file = path.join(corpora_uniting_stories_folder, corpora_file_name)
                with open(corpora_path_file, encoding='utf-8') as f:
                    if __get_chunks_size(f.readlines(), chunk_size) >= kfold_size:
                        corpora_names_list.append(corpora_file_name)

        feature_vectors_dict, debugging_mode, mini_features_vectors_list, k_fold_split_data = \
            {}, config_dict['part_c_debugging_mode'], [], []
        multi_process_flag, cores_size = config_dict['multi_process_flag'], config_dict['cores_size']
        debugging_output_folder = path.join(config_dict['debugging_output_folder'], path.split(getcwd())[1])
        if not path.isdir(debugging_output_folder):
            makedirs(debugging_output_folder)
            logging.info("\nThe '{}' folder created successfully".format(debugging_output_folder))
        corporas_feature_vectors_file_path = path.join(debugging_output_folder, "corporas_feature_vectors.pickle.gz")
        mini_features_vectors_file_path = path.join(debugging_output_folder, "mini_features_vectors.pickle.gz")
        corpora_label_dict = dict([(corpora_name.split('.')[0], idx + 1) for idx, corpora_name in
                                   enumerate(sorted(corpora_names_list))])

        if not debugging_mode or not path.isfile(corporas_feature_vectors_file_path):
            feature_vectors_time = clock()
            logging.info("\nStart create feature vectors for hebrew abd translation corpora")
            corpora_path_file_list = [path.join(corpora_uniting_stories_folder, corpora_name) for corpora_name in
                                      corpora_names_list]

            meta_data_folder = path.join(config_dict['meta_data_folder'], path.split(getcwd())[1])
            if not path.isdir(meta_data_folder):
                makedirs(meta_data_folder)
                logging.debug("\n The '{}' folder created successfully".format(meta_data_folder))
            feature_vectors_list = \
                Vectors(corpora_uniting_stories_folder, corpora_label_dict, debugging_output_folder,
                        meta_data_folder, chunk_size, debugging_mode).part_c_run(corpora_path_file_list, True)
            logging.info("\nThe time taken created feature vectors for hebrew abd translation corpora was {:0.4f} "
                         "mins".format((clock() - feature_vectors_time) / 60.0))
        if debugging_mode is True:
            if not path.isfile(mini_features_vectors_file_path):
                logging.info("\n** Debugging mode **: the data uploaded may be old and therefore the test "
                             "is incorrect!")
                feature_vectors_dict = __read_pickle_file(corporas_feature_vectors_file_path)

                mini_features_vectors_list = []
                for corpora_name, chunk_feature_vectors in feature_vectors_dict.items():
                    chunk_feature_vectors_size = len(chunk_feature_vectors)
                    corpora_number_samples = int(0.2 * len(chunk_feature_vectors))
                    if chunk_feature_vectors_size < kfold_size:
                        logging.info("\n In '{}' corpora: Cannot have number of splits n_splits='{}' greater than the"
                                     " number of samples: {}".format(corpora_name, kfold_size,
                                                                     chunk_feature_vectors_size))
                        exit()
                    if corpora_number_samples < kfold_size:
                        corpora_number_samples = kfold_size
                    mini_features_vectors_list += chunk_feature_vectors[:corpora_number_samples]

                logging.info("\n Save mini features vectors (20 percent of the total chunks features vectors)")
                __save_pickle_file(mini_features_vectors_file_path, mini_features_vectors_list)
                feature_vectors_list = mini_features_vectors_list
            else:
                logging.info("\n** Debugging mode **: the data uploaded may be old and therefore the test "
                             "is incorrect!")
                feature_vectors_list = __read_pickle_file(mini_features_vectors_file_path)

            logging.info("\n** Debugging mode **: total feature vectors are {}"
                         "".format(len(mini_features_vectors_list)))
        else:
            logging.info("\nTotal feature vectors are {}".format(len(mini_features_vectors_list)))

        classify_obj = Classify(feature_vectors_list, corpora_label_dict, multi_process_flag, kfold_size,
                                config_dict['print_predict_analysis_flag'], cores_size)
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
