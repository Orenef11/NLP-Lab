# coding=utf-8
import sys
from os import path, getcwd, makedirs
sys.path.insert(0, getcwd())
from config_parser import config_parser
from time import clock
from logger import setting_up_logger
import logging
from pickle import load
from numpy import arange, asarray
import matplotlib.pyplot as plt


class Graphs(object):
    def __init__(self, kfold_folder_pickle_path, kfold_size, images_folder_path):
        self.__kfold_folder_pickle_path = kfold_folder_pickle_path
        self.__k_folds = kfold_size
        self.__images_folder_path = images_folder_path
        if not path.isdir(images_folder_path):
            logging.info("\nThe '{}' folder created successfully".format(images_folder_path))
            makedirs(images_folder_path)
        self.__images_variables_dict = self.__create_images_variables()

    def __create_images_variables(self):
        logging.info("\nStart analysis of classification results")
        analysis_data_dict, analysis_corpora_dict, number_samples_by_corpora_dict = {}, {}, {}
        for kfold_idx in range(self.__k_folds):
            with open(path.join(self.__kfold_folder_pickle_path, str(kfold_idx) + '.pickle'), 'rb') as fp:
                analysis_data_dict[kfold_idx] = load(fp)

        for kfold_idx in analysis_data_dict.keys():
            for classifier_name in sorted(analysis_data_dict[kfold_idx].keys()):
                if classifier_name not in analysis_corpora_dict.keys():
                    analysis_corpora_dict[classifier_name] = {}

                for corpora_name, corpora_samples in \
                        analysis_data_dict[kfold_idx][classifier_name]['test_data'].items():
                    if corpora_name not in analysis_corpora_dict[classifier_name].keys():
                        analysis_corpora_dict[classifier_name][corpora_name] = {'samples': 0, 'predict': 0}
                    analysis_corpora_dict[classifier_name][corpora_name]['samples'] += corpora_samples

                for corpora_name, corpora_data_dict in \
                        analysis_data_dict[kfold_idx][classifier_name]['predict'].items():
                    analysis_corpora_dict[classifier_name][corpora_name]['predict'] += corpora_data_dict['correct']

        return analysis_corpora_dict

    @staticmethod
    def __create_lines_bars_plot(x_data_list, y_data_list, x_label, y_label, file_path):
        folder_path, filename = path.split(file_path)
        plt.figure()
        plt.barh(arange(len(y_data_list)), x_data_list, align='center', alpha=0.5, color='b')
        plt.yticks(arange(len(y_data_list)), y_data_list)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(filename)
        if ':' in filename:
            filename = filename.replace(':', '')
        plt.savefig(path.join(folder_path, filename) + '.png')
        plt.close()
        logging.debug("\nThe image was successfully created in the next '{}' path".format(file_path))

    def run(self):
        corpora_predict_dict = {}
        for classifier_name in sorted(self.__images_variables_dict.keys()):
            if classifier_name not in corpora_predict_dict.keys():
                corpora_predict_dict[classifier_name] = {}
            for corpora_name in sorted(self.__images_variables_dict[classifier_name].keys()):
                avg_accuracy = round(self.__images_variables_dict[classifier_name][corpora_name]['predict'] /
                                     self.__images_variables_dict[classifier_name][corpora_name]['samples'], 2)
                corpora_predict_dict[classifier_name][corpora_name] = avg_accuracy

        for classifier_name in sorted(self.__images_variables_dict.keys()):
            classifier_accuracy_list, corpora_names_list = [], []
            for corpora_name in sorted(self.__images_variables_dict[classifier_name].keys()):
                classifier_accuracy_list.append(corpora_predict_dict[classifier_name][corpora_name])
                if len(corpora_name) == len(corpora_name.encode()):
                    corpora_names_list.append(corpora_name)
                else:
                    corpora_names_list.append(corpora_name[::-1])

            self.__create_lines_bars_plot(classifier_accuracy_list, corpora_names_list, 'Accuracy', 'Corpora',
                                          path.join(self.__images_folder_path, classifier_name))


def main():
    start_time = clock()
    config_dict = config_parser(path.join(getcwd(), 'config.ini'))
    setting_up_logger('debug', 'info', config_dict['log_file_graphs'])

    part_b_folder_pickle_path, kfold_size = \
        path.join(config_dict['part_b_path_folder'], 'temp'), config_dict['kfold_size']
    part_c_folder_pickle_path = path.join(config_dict['part_c_path_folder'], 'temp')
    part_b_images_folder_path = config_dict['part_b_images_folder_path']
    part_c_images_folder_path = config_dict['part_c_images_folder_path']

    logging.info("\nCreating the images (comparing the classified quality) for each language in part b")
    Graphs(part_b_folder_pickle_path, kfold_size, part_b_images_folder_path).run()
    logging.info("\nFinish creating the images in part b")

    logging.info("\nCreating the images (comparing the classified quality) for each language in part c")
    Graphs(part_c_folder_pickle_path, kfold_size, part_c_images_folder_path).run()
    logging.info("\nFinish creating the images in part c")

    logging.info("\nThe total time taken for the program to run is {:0.4f} minutes".format(
        (clock() - start_time) / 60.0))


if __name__ == '__main__':
    main()

