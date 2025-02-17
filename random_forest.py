from collections import Counter
from pickle import NONE
from typing import Optional, Sequence, Mapping
import numpy as np
import pandas as pd
import random


class Node(object):
    def __init__(self, node_size: int, node_class: str, depth: int, single_class:bool = False):
        # Every node is a leaf unless you set its 'children'
        self.is_leaf = True
        # Each 'decision node' has a name. It should be the feature name
        self.name = None
        # All children of a 'decision node'. Note that only decision nodes have children
        self.children = {}
        # Whether corresponding feature of this node is numerical or not. Only for decision nodes.
        self.is_numerical = None
        # Threshold value for numerical decision nodes. If the value of a specific data is greater than this threshold,
        # it falls under the 'ge' child. Other than that it goes under 'l'. Please check the implementation of
        # get_child_node for a better understanding.
        self.threshold = None
        # The class of a node. It determines the class of the data in this node. In this assignment it should be set as
        # the mode of the classes of data in this node.
        self.node_class = node_class
        # Number of data samples in this node
        self.size = node_size
        # Depth of a node
        self.depth = depth
        # Boolean variable indicating if all the data of this node belongs to only one class. This is condition that you
        # want to be aware of so you stop expanding the tree.
        self.single_class = single_class

    def set_children(self, children):
        self.is_leaf = False
        self.children = children

    def get_child_node(self, feature_value)-> 'Node':
        if not self.is_numerical:
            return self.children[feature_value]
        else:
            if feature_value >= self.threshold:
                return self.children['ge'] # ge stands for greater equal
            else:
                return self.children['l'] # l stands for less than


class RandomForest(object):
    def __init__(self, n_classifiers: int,
                 criterion: Optional['str'] = 'gini',
                 max_depth: Optional[int] = None,
                 min_samples_split: Optional[int] = None,
                 max_features: Optional[int] = None):
        """
        :param n_classifiers:
            number of trees to generated in the forrest
        :param criterion:
            The function to measure the quality of a split. Supported criteria are “gini” for the Gini
            impurity and “entropy” for the information gain.
        :param max_depth:
            The maximum depth of the trees.
        :param min_samples_split:
            The minimum number of samples required to be at a leaf node
        :param max_features:
            The number of features to consider for each tree.
        """
        self.n_classifiers = n_classifiers
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.trees = []
        self.criterion_func = self.entropy if criterion == 'entropy' else self.gini


    def fit(self, X: pd.DataFrame, y_col: str)->float:
        """
        :param X: data
        :param y_col: label column in X
        :return: accuracy of training dataset
        """
        features = self.process_features(X, y_col)
        # Your code
        num_featre = X.shape[1]
        if X.shape[0] < 1:
            raise ValueError("Not enough samples in the given dataset")
        if self.max_features == None:
            self.max_features = int(np.sqrt(num_featre))
        for i in range(self.n_classifiers):
            #get random feature
            feature_name, data_X = features[i]
            idx = np.random.choice(num_featre, self.max_features, replace=True)
            data_X = data_X[:, idx]
            self.trees[i].fit(data_X, feature_name)
            self.trees[i].feature_index = idx
        return self.evaluate(X, y_col)

    def predict(self, X: pd.DataFrame)->np.ndarray:
        """
        :param X: data
        :return: aggregated predictions of all trees on X. Use voting mechanism for aggregation.
        """
        predictions = []
        # Your code
        for row in X.iterrows():
            pred_list = []
            for tree in self.trees:
                pred_list.append(tree.calc_predict_value(row))
            pred_label_counts = Counter(pred_list)
            pred_label = max(zip(pred_label_counts.values(), pred_label_counts.keys()))
            predictions.append(pred_label[1])
    
        return np.array(predictions)

    def evaluate(self, X: pd.DataFrame, y_col: str)-> int:
        """
        :param X: data
        :param y_col: label column in X
        :return: accuracy of predictions on X
        """
        preds = self.predict(X)
        acc = sum(preds == X[y_col]) / len(preds)
        return acc

    def generate_tree(self, X: pd.DataFrame, y_col: str, features: Sequence[Mapping])->Node:
        """
        Method to generate a decision tree. This method uses self.split_tree() method to split a node.
        :param X:
        :param y_col:
        :param features:
        :return: root of the tree
        """
        root = Node(X.shape[0], X[y_col].mode(), 0)
        # Your code
        self.split_node(root, X, y_col, features)
        return root

    def split_node(self, node: Node, X: pd.DataFrame, y_col:str, features: Sequence[Mapping]) -> None:
        """
        This is probably the most important function you will implement. This function takes a node, uses criterion to
        find the best feature to slit it, and splits it into child nodes. I recommend to use revursive programming to
        implement this function but you are of course free to take any programming approach you want to implement it.
        :param node:
        :param X:
        :param y_col:
        :param features:
        :return:
        """


    def gini(self, X: pd.DataFrame, feature: Mapping, y_col: str) -> float:
        """
        Returns gini index of the give feature
        :param X: data
        :param feature: the feature you want to use to get compute gini score
        :param y_col: name of the label column in X
        :return:
        """
        gini = 0.0
        for y in X[y_col].unique():
            size=len(X[X[y_col]==y])
            if size == 0:
                continue
            score = 0.0
            for x in X[feature].unique():
                dat=X[X[feature]==x]
                score =(list(dat[y_col]).count(y))/len(dat)    
                gini+=((1-score)*score)

 
    def entropy(self, X: pd.DataFrame, feature: Mapping, y_col: str) ->float:
        """
        Returns gini index of the give feature
        :param X: data
        :param feature: the feature you want to use to get compute gini score
        :param y_col: name of the label column in X
        :return:
        """
        length = len(X)
        target_class = []
        for entry in X.dtypes.items():
            target_class.append(entry)
        counter_entropy = Counter(target_class)
        count_zero = float(counter_entropy[0.0]) / length
        count_one = float(counter_entropy[1.0]) / length
        if count_zero == 0:
            entropy_score = -1 * (count_one * np.log(count_one,2))
        elif count_one == 0:
            entropy_score = -1 * (count_zero * np.log(count_zero,2))
        else:
            entropy_score = -1 * (count_zero * np.log(count_zero,2)) + -1 * (count_one * np.log(count_one,2))
        return entropy_score       


    def process_features(self, X: pd.DataFrame, y_col: str)->Sequence[Mapping]:
        """
        :param X: data
        :param y_col: name of the label column in X
        :return:
        """
        features = []
        for n,t in X.dtypes.items():
            if n == y_col:
                continue
            f = {'name': n, 'dtype': t}
            features.append(f)
        return features