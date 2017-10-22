from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
import logging
from time import clock
from multiprocessing import Pool, cpu_count
from traceback import print_exc
from numpy import asarray
from collections import Counter
from os import path, getcwd, makedirs
from pickle import loads, load, dumps, dump
from gzip import decompress, compress


class Classify(object):
    def __init__(self, feature_vectors, language_type_dict, multi_process=False, k_fold_value=10,
                 print_predict_analysis_flag=False, cores_size=2):
        self.__feature_vectors = asarray(feature_vectors)
        self.__language_type_dict = language_type_dict
        self.__language_label_to_name_dict = dict([(corpora_label, corpora_name) for corpora_name, corpora_label
                                                   in self.__language_type_dict.items()])
        self.__k_folds = k_fold_value
        self.__multi_process = multi_process
        self.__accuracy_list = []
        self.__print_predict_analysis_flag = print_predict_analysis_flag
        self.__cores_size = min(cores_size, cpu_count())

        if not path.isdir('temp'):
            makedirs('temp')

    def __initial_classifier(self):
        classifiers_name_list, classifiers_obj_list = [], []
        classifiers_name_list.append("SVM:One-Vs-One")
        classifiers_obj_list.append(SVC())
        if len(self.__language_type_dict) > 2:
            classifiers_name_list.append("SVM:One-Vs-All")
            classifiers_obj_list.append(LinearSVC())
        naive_bayes_classifier = MultinomialNB()
        decision_tree_classifier = DecisionTreeClassifier()
        knn_classifier = KNeighborsClassifier()

        return classifiers_name_list + ["Navie-Bayes", "Decision-Tree", "KNN"], \
            classifiers_obj_list + [naive_bayes_classifier, decision_tree_classifier, knn_classifier]

    def create_data_to_classifier(self, k_fold_indexes):
        train_indexes, test_indexes = k_fold_indexes[0], k_fold_indexes[1]
        training_data_set_label, test_data_set, train_data_set, testing_data_set_label = [], [], [], []

        for vector_details in self.__feature_vectors[train_indexes]:
            train_data_set.append(vector_details[0])
            training_data_set_label.append(vector_details[1])

        for vector_details in self.__feature_vectors[test_indexes]:
            test_data_set.append(vector_details[0])
            testing_data_set_label.append(vector_details[1])

        return [train_data_set, training_data_set_label, test_data_set, testing_data_set_label]

    def __k_fold_indexes_list(self):
        kfold_obj, folds_list = KFold(n_splits=self.__k_folds, shuffle=True), []

        for train_indexes, test_indexes in kfold_obj.split(self.__feature_vectors):
            folds_list.append((train_indexes, test_indexes))

        return folds_list

    def __predict(self, classifier_obj, train_data_set, training_data_set_label, test_data_set, testing_data_set_label):
        classifier_obj.fit(train_data_set, training_data_set_label)
        predict_labels = classifier_obj.predict(test_data_set)
        analysis_data_dict = {}
        if self.__print_predict_analysis_flag is True:
            analysis_data_dict = {"train_data": {}, 'test_data': {}, 'predict': {}}
            for corpora_label, corpora_samples_size in Counter(training_data_set_label).items():
                analysis_data_dict["train_data"][self.__language_label_to_name_dict[corpora_label]] = \
                    corpora_samples_size
            for corpora_label, corpora_samples_size in Counter(testing_data_set_label).items():
                analysis_data_dict["test_data"][self.__language_label_to_name_dict[corpora_label]] = \
                    corpora_samples_size

            for correct_label, predict_label in zip(testing_data_set_label, predict_labels):
                corpora_name = self.__language_label_to_name_dict[correct_label]
                if corpora_name not in analysis_data_dict["predict"].keys():
                    analysis_data_dict["predict"][corpora_name] = {"correct": 0,
                                                                   "corpora_of_wrong_identification": set()}

                if correct_label == predict_label:
                    analysis_data_dict["predict"][corpora_name]['correct'] += 1
                else:
                    analysis_data_dict["predict"][corpora_name]['corpora_of_wrong_identification'].add(
                        self.__language_label_to_name_dict[predict_label])

        return accuracy_score(testing_data_set_label, predict_labels), analysis_data_dict

    def __print_analysis_predict(self):
        classifier_analysis_file_path = path.join(getcwd(), "classifier_analysis.txt")
        logging.info("\nStart analysis of classification results")
        analysis_lines, analysis_data_dict = [], {}
        for kfold_idx in range(self.__k_folds):
            with open(path.join('temp', str(kfold_idx) + '.pickle'), 'rb') as fp:
                analysis_data_dict[kfold_idx] = load(fp)

        for kfold_idx in analysis_data_dict.keys():
            for classifier_name in analysis_data_dict[kfold_idx].keys():
                classifier_data_dict = analysis_data_dict[kfold_idx][classifier_name]
                for corpora_name in classifier_data_dict['predict'].keys():
                    train_vectors_size = classifier_data_dict['train_data'][corpora_name]
                    test_vectors_size = classifier_data_dict['test_data'][corpora_name]
                    true_predict = classifier_data_dict['predict'][corpora_name]['correct']
                    wrong_langs_list = \
                        list(classifier_data_dict['predict'][corpora_name]['corpora_of_wrong_identification'])
                    analysis_lines.append("Kfold number '{}', '{}' classifier name, '{}' corpora name:\n"
                                          "".format(kfold_idx, classifier_name, corpora_name))
                    analysis_lines.append("The number of the vectors learned '{}'\n".format(train_vectors_size))
                    analysis_lines.append("The number of the vectors tested '{}'\n".format(test_vectors_size))
                    analysis_lines.append("The list of the wrong languages has been identified '{}'\n"
                                          "".format(true_predict))
                    if len(wrong_langs_list) != 0:
                        analysis_lines.append(
                            "The number of vectors identified correctly '{}'\n".format(wrong_langs_list))

        with open(classifier_analysis_file_path, mode='w', encoding='utf-8') as f:
            f.writelines(analysis_lines)
            logging.info("\nThe '{}' file Successfully created".format(classifier_analysis_file_path))
        logging.info("\nFinish analysis of classification results")

    def create_kfold_split_data(self):
        try:
            start_time = clock()
            logging.info("\nCreates the division of the data into {} parts (kfold = {})"
                         "".format(self.__k_folds, self.__k_folds))
            k_fold_indexes_list, k_fold_split_data_list = self.__k_fold_indexes_list(), []
            if self.__multi_process:
                with Pool(processes=self.__cores_size) as p:
                    k_fold_split_data_list = p.map(self.create_data_to_classifier, k_fold_indexes_list)
            else:
                for k_fold_indexes in k_fold_indexes_list:
                    k_fold_split_data_list.append(self.create_data_to_classifier(k_fold_indexes))

            logging.info("\nFinished created the division, The time it took to created the division was {:0.4f} "
                         "mins".format((clock() - start_time) / 60))

            return k_fold_split_data_list
        except Exception as e:
            logging.info(print_exc())
            raise e

    @staticmethod
    def __save_pickle_file(pickle_file_path, pickle_data):
        with open(pickle_file_path, 'wb') as fp:
            fp.write(compress(dumps(pickle_data)))

    @staticmethod
    def __read_pickle_file(pickle_file_path):
        with open(pickle_file_path, 'rb') as fp:
            return loads(decompress(fp.read()))

    def single_core_classifier(self, classifier_variables):
        classifiers_name_list, classifiers_obj_list = self.__initial_classifier()
        kfold_data, kfold_idx, accuracy_list = classifier_variables[0], classifier_variables[1], []
        train_data_set, training_data_set_label, test_data_set, testing_data_set_label = \
            kfold_data[0], kfold_data[1], kfold_data[2], kfold_data[3]
        analysis_data_dict = {}
        for idx, classifier_obj in enumerate(classifiers_obj_list):
            t = clock()
            classifier_name = classifiers_name_list[idx]
            logging.info("\nStart classifier: KFold number {} - {} ".format(kfold_idx, classifier_name))
            classifier_accuracy, analysis_data = self.__predict(
                classifier_obj, train_data_set, training_data_set_label, test_data_set, testing_data_set_label)
            analysis_data_dict[classifier_name] = analysis_data
            accuracy_list.append(classifier_accuracy)
            logging.info("\nFinish classifier: KFold number {} - {}".format(kfold_idx, classifier_name))
            logging.info("\n{} - total time is {:0.4f} mins".format(classifier_name, (clock() - t) / 60))
        logging.info("\nThe classifier result {}".format(accuracy_list))
        
        with open(path.join('temp', str(kfold_idx) + '.pickle'), mode='wb') as fp:
            dump(analysis_data_dict, fp)

        return accuracy_list

    def run_classifier(self, k_fold_split_data_list):
        classifiers_name_list, _ = self.__initial_classifier()
        if self.__multi_process is True:
            multi_process_time = clock()
            logging.info("\nStart multi-process classifier")
            logging.info("\nThe estimated running time is between 40-60 minutes")
            multi_classifier_variables_tuple = []
            for kfold_idx, kfold_data in enumerate(k_fold_split_data_list):
                multi_classifier_variables_tuple.append((kfold_data, kfold_idx))

            multi_classifier_variables_tuple = tuple(multi_classifier_variables_tuple)
            with Pool(self.__cores_size) as p:
                self.__accuracy_list = p.map(self.single_core_classifier, multi_classifier_variables_tuple)

            logging.info("\nThe total time taken for the multi-process classifier to run was {:0.4f} seconds"
                         "".format(clock() - multi_process_time))
        else:
            single_process_time = clock()
            logging.info("\nStart single-process classifier")
            classifiers_name_list, classifiers_obj_list = self.__initial_classifier()
            for kfold_idx, kfold_data in enumerate(k_fold_split_data_list):
                self.__accuracy_list.append(self.single_core_classifier([kfold_data, kfold_idx]))

            logging.info("\nThe total time taken for the single-process classifier to run was {:0.4f} seconds"
                         "".format(clock() - single_process_time))
        if self.__print_predict_analysis_flag is True:
            self.__print_analysis_predict()

        idx = 0
        accuracy_dict = {}
        for accuracy_list in zip(*self.__accuracy_list):
            accuracy_list = asarray(accuracy_list)
            logging.info("\n{} - avg {:0.4f}".format(classifiers_name_list[idx], accuracy_list.sum() / self.__k_folds))
            accuracy_dict[classifiers_name_list[idx]] = accuracy_list.sum() / self.__k_folds
            idx += 1

        with open(path.join('temp',  'accuracy_result.pickle.'), mode='wb') as fp:
            dump(accuracy_dict, fp)

