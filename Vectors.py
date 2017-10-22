from os import listdir, path
from time import clock
from pickle import dumps, loads
from gzip import compress, decompress
from random import shuffle
from sklearn.feature_selection import SelectKBest
import logging


class Vectors(object):
    def __init__(self, corpos_folder_path, corpora_label_dict, debugging_output_folder, meta_data_folder_path,
                 chunk_size=5000, debugging_mode=False):
        self.__corpora_file_path_list = \
            [path.join(corpos_folder_path, filename) for filename in listdir(corpos_folder_path)]

        self.__chunk_size = chunk_size
        self.__features_vector = {}
        self.__corpora_label_dict = corpora_label_dict
        self.__debugging_output_folder = debugging_output_folder
        self.__debugging_mode = debugging_mode
        self.__meta_data_folder_path = meta_data_folder_path

    def __generate_vectors(self):
        corpora_sentences, features = [], set()
        logging.info("\nCreates the dictionary of vector features")
        for corpos_text_file_path in self.__corpora_file_path_list:
            corpora_sentences += self.__read_lines_from_file(corpos_text_file_path)

        for sentence in corpora_sentences:
            for index, char in enumerate(sentence):
                features.add(char)
                if index < len(sentence) - 1:
                    features.add(char + sentence[index + 1])
                if index < len(sentence) - 2:
                    features.add(char + sentence[index + 1] + sentence[index + 2])

        self.__features_vector = {feature: index for index, feature in enumerate(features)}
        logging.info("\nFinished creating the dictionary of vector features")

    def __get_chunks(self, corpora_lines):
        chunks = []
        last_chunk = []
        last_chunk_size = 0
        for line in corpora_lines:
            if last_chunk_size <= self.__chunk_size < last_chunk_size + len(line):
                chunks.append(last_chunk)
                last_chunk = []
                last_chunk_size = 0

            last_chunk.append(line)
            last_chunk_size += len(line)

        chunks.append(last_chunk)

        return chunks

    def __get_feature_vectors(self, chunks, corpora_label):
        feature_vectors, init_vector = [], [0] * len(self.__features_vector)

        for chunk in chunks:
            # initialize feature vector
            feature_vector = init_vector.copy()
            for sentence in chunk:
                for index, char in enumerate(sentence):
                    feature_vector[self.__features_vector[sentence[index]]] += 1
                    if index < len(sentence) - 1:
                        feature_vector[self.__features_vector[''.join(sentence[index: index + 2])]] += 1
                    if index < len(sentence) - 2:
                        feature_vector[self.__features_vector[''.join(sentence[index: index + 3])]] += 1

            feature_vectors.append((feature_vector, corpora_label))
        return feature_vectors

    @staticmethod
    def __save_pickle_file(pickle_file_path, pickle_data):
        with open(pickle_file_path, 'wb') as fp:
            fp.write(compress(dumps(pickle_data)))

    @staticmethod
    def __read_pickle_file(pickle_file_path):
        with open(pickle_file_path, 'rb') as fp:
            return loads(decompress(fp.read()))

    @staticmethod
    def __read_lines_from_file(file_path):
        with open(file_path, encoding='utf-8') as f:
           return f.readlines()

    def __best_words_features(self, feature_vectors_list, best_words_features_size=100):
        vectors_list, vectors_label_list = [], []
        file_path = path.join(self.__meta_data_folder_path, "best_features.txt")
        idx_to_features_dict = \
            dict([(vectors_idx, chars_features) for chars_features, vectors_idx in self.__features_vector.items()])
        sel = SelectKBest(k=best_words_features_size)
        for vectors_details in feature_vectors_list:
            vectors_list.append(vectors_details[0])
            vectors_label_list.append(vectors_details[1])

        sel.fit_transform(vectors_list, vectors_label_list)
        k_best_index_list = sel.get_support(indices="True")
        with open(file_path, mode='w', encoding='utf-8') as f:
            for feature_idx in sorted(k_best_index_list):
                f.write("'" + idx_to_features_dict[feature_idx] + "'\n")
        logging.info("\nThe '{}' file created successfully".format(file_path))

    def part_b_run(self, hebrew_corpora_path_file, save_vectors_file=True):
        hebrew_corpora_lines, translation_corpora_lines, translation_corpora_file_path_list, feature_vectors  \
            = [], [], self.__corpora_file_path_list.copy(), []
        translation_corpora_file_path_list.remove(hebrew_corpora_path_file)

        feature_vector_file_path = path.join(self.__debugging_output_folder, 'feature_vector.pickle.gz')
        if not self.__debugging_mode or not path.isfile(feature_vector_file_path):
            self.__generate_vectors()
            self.__save_pickle_file(feature_vector_file_path, self.__features_vector)
        else:
            self.__features_vector = self.__read_pickle_file(feature_vector_file_path)

        hebrew_corpora_lines = self.__read_lines_from_file(hebrew_corpora_path_file)
        translation_corpora_lines = []
        for corpora_file_path in translation_corpora_file_path_list:
            translation_corpora_lines += self.__read_lines_from_file(corpora_file_path)

        logging.info("\nShuffle the lines")
        shuffle(hebrew_corpora_lines)
        shuffle(translation_corpora_lines)

        logging.info("\nClump the lines into chunks smaller or equal to {} chars".format(self.__chunk_size))
        hebrew_corpora_chunks = self.__get_chunks(hebrew_corpora_lines)
        translation_corpora_chunks = self.__get_chunks(translation_corpora_lines)

        chunks_time = clock()
        logging.info("\nCalculate feature vector for each chunk")
        hebrew_label, translation_label = self.__corpora_label_dict['hebrew'], self.__corpora_label_dict['translation']
        hebrew_corpora_feature_vectors = self.__get_feature_vectors(hebrew_corpora_chunks, hebrew_label)
        translation_corpora_feature_vectors = self.__get_feature_vectors(translation_corpora_chunks, translation_label)
        logging.info("\nTotal time taken created chunk are {:0.4f} minutes".format((clock() - chunks_time) / 60))
        if save_vectors_file is True:
            logging.info("\nStore the feature vectors")
            self.__save_pickle_file(path.join(self.__debugging_output_folder, 'source_feature_vectors.pickle.gz'),
                                    hebrew_corpora_feature_vectors)
            self.__save_pickle_file(path.join(self.__debugging_output_folder, 'translation_feature_vectors.pickle.gz'),
                                    translation_corpora_feature_vectors)
            logging.info("\nFinished store the feature vectors")

        feature_vectors += hebrew_corpora_feature_vectors
        feature_vectors += translation_corpora_feature_vectors

        self.__best_words_features(feature_vectors)
        return feature_vectors

    def part_c_run(self, corpora_path_file_list, save_vectors_file=True):
        corpora_data_dict, feature_vectors_list = {}, []
        self.__corpora_file_path_list = corpora_path_file_list
        for corpora_file_path in corpora_path_file_list:
            if not path.isfile(corpora_file_path):
                logging.info("\nThe '{}' file not exist".format(corpora_file_path))
                exit()
            corpora_name = path.split(corpora_file_path)[-1].split('.')[0]
            corpora_data_dict[corpora_name] = self.__read_lines_from_file(corpora_file_path)
        feature_vector_file_path = path.join(self.__debugging_output_folder, 'feature_vector.pickle.gz')

        if not self.__debugging_mode or not path.isfile(feature_vector_file_path):
            self.__generate_vectors()
            self.__save_pickle_file(feature_vector_file_path, self.__features_vector)
        else:
            self.__features_vector = self.__read_pickle_file(feature_vector_file_path)

        logging.info("\nShuffle the lines")
        for corpora_lines in corpora_data_dict.values():
            shuffle(corpora_lines)

        logging.info("\nClump the lines into chunks smaller or equal to {} chars".format(self.__chunk_size))
        for corpora_name, corpora_lines in corpora_data_dict.items():
            corpora_data_dict[corpora_name] = self.__get_chunks(corpora_lines)

        chunks_time = clock()
        logging.info("\nCalculate feature vector for each chunk")

        for corpora_name, corpora_chunks in corpora_data_dict.items():
            temp_vector = self.__get_feature_vectors(corpora_chunks, self.__corpora_label_dict[corpora_name])
            corpora_data_dict[corpora_name] = temp_vector
            feature_vectors_list += temp_vector

        logging.info("\nTotal time taken created chunk are {:0.4f} minutes".format((clock() - chunks_time) / 60))
        if save_vectors_file is True:
            logging.info("\nStore the feature vectors")
            self.__save_pickle_file(path.join(self.__debugging_output_folder, 'corporas_feature_vectors.pickle.gz'),
                                    corpora_data_dict)
            logging.info("\nFinished store the feature vectors")

        self.__best_words_features(feature_vectors_list)
        return feature_vectors_list

    def part_d_run(self, corpora_path_files):
        languages_lines = dict()
        languages_chunks = dict()
        languages_feature_vectors = dict()

        if not path.isfile('feature_vector.pickle.gz'):
            self.__generate_vectors()
        else:
            with open('feature_vector.pickle.gz', 'rb') as fp:
                self.__features_vector = loads(decompress(fp.read()))

        for language, file in corpora_path_files.items():
            language_file_path = ''
            for file_path in self.__corpora_file_path_list:
                if file_path.endswith(file):
                    language_file_path = file_path
                    break
            with open(language_file_path, encoding='utf-8') as f:
                languages_lines[language] = f.readlines()

        logging.info("\nShuffle the lines")
        for language in languages_lines:
            shuffle(languages_lines[language])

        logging.info("\nClump the lines into chunks smaller or equal to {} chars".format(self.__chunk_size))
        for language, lines in languages_lines.items():
            languages_chunks[language] = self.__get_chunks(lines)

        chunks_time = clock()
        logging.info("\nCalculate feature vector for each chunk")
        for language, chunks in languages_chunks.items():
            languages_feature_vectors[language] = self.__get_feature_vectors(chunks,
                                                                             self.__corpora_label_dict[language])
        logging.info("\nTotal time taken created chunk are {:0.4f} minutes".format((clock() - chunks_time) / 60))

        feature_vectors_union = []
        languages = []
        for language, feature_vectors in languages_feature_vectors.items():
            # feature_vectors_union += [feature_vector[0] for feature_vector in feature_vectors]
            languages.append(language)
            mean = [0] * len(feature_vectors[0][0])
            for feature_vector, corpora_label in feature_vectors:
                for index, value in enumerate(feature_vector):
                    mean[index] += value

            for index in range(len(mean)):
                mean[index] /= len(feature_vectors)

            feature_vectors_union.append(mean)

        return feature_vectors_union, languages
