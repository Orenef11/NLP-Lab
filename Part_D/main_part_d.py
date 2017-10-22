# https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/
import sys
from os import path, getcwd
sys.path.insert(0, path.split(getcwd())[0])
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, cophenet
import numpy as np
from scipy.spatial.distance import pdist
from Vectors import Vectors
from config_parser import config_parser
from logger import setting_up_logger


def get_feature_vectors(used_languages, corpora_path_files, config_dict):
    corpora_uniting_stories_folder = config_dict['uniting_stories_folder']
    debugging_output_folder = path.join(config_dict['debugging_output_folder'], path.split(getcwd())[1])
    chunk_size = config_dict['chunk_size']
    vectors = Vectors(corpora_uniting_stories_folder, used_languages, debugging_output_folder, chunk_size)

    return vectors.part_d_run(corpora_path_files)


def main():
    
    root_folder_path = path.split(getcwd())[0]
    config_dict = config_parser(path.join(root_folder_path, 'config.ini'))
    setting_up_logger('debug', 'info', config_dict['log_file_part_c'])

    used_languages = {'Italian': 1, 'English': 2, 'German': 3, 'Hungerian': 4, 'Greek': 5, 'Yiddish': 6, 'Norwegen': 7, 'Spanish': 8, 'Hebrew': 9, 'arab': 10, 'Polish': 11, 'portugese': 12, 'Chech': 13, 'French': 14, 'Russian': 15, 'Swedish': 16}
    corpora_path_files = {'Italian': 'איטלקית.txt', 'English': 'אנגלית.txt', 'German': 'גרמנית.txt', 'Hungerian': 'הונגרית.txt', 'Greek': 'יוונית.txt', 'Yiddish': 'יידיש.txt', 'Norwegen': 'נורווגית.txt', 'Spanish': 'ספרדית.txt', 'Hebrew': 'עברית.txt', 'arab': 'ערבית.txt', 'Polish': 'פולנית.txt', 'portugese': 'פורטוגזית.txt', 'Chech': 'צ\'כית.txt', 'French': 'צרפתית.txt', 'Russian': 'רוסית.txt', 'Swedish': 'שוודית.txt'}
    # x = our feature vectors (as numpy array)
    feature_vectors, languages = get_feature_vectors(used_languages, corpora_path_files, config_dict)
    x = np.array(feature_vectors)
    print(languages)
    
    # link the feature vectors
    Z = linkage(x, 'ward')
    
    # determine how well the linkage went
    c, coph_dists = cophenet(Z, pdist(x))
    print(c)
    
    # calculate full dendrogram
    plt.figure(figsize=(25, 10))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('sample index')
    plt.ylabel('distance')
    dendrogram(
        Z,
        truncate_mode='lastp',  # show only the last p merged clusters
        p=len(used_languages),  # show only the last p merged clusters
        show_leaf_counts=False,  # otherwise numbers in brackets are counts
        leaf_rotation=90.,
        leaf_font_size=12.,
        show_contracted=True,  # to get a distribution impression in truncated branches
    )
    plt.savefig('tree.png')
    plt.clf()


if __name__ == '__main__':
    main()
