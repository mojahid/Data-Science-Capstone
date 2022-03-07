import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# Read in dataframe and remove merged columns
df = pd.read_csv(r'C:\Users\brear\OneDrive\Desktop\Grad School\Data-Science-Capstone\Contextual_Features_final.csv')
df = df.drop(columns= ['long_x','lat_x','Label_x','long_y','lat_y','Label_y'])
cols_to_move = ['lat','long','Label','Point']
df = df[ cols_to_move + [ col for col in df.columns if col not in cols_to_move ] ]

# Move Target to first column
target = 'Label'
first_col = df.pop(target)
df.insert(0, target,  first_col)
#print(df.head())
#print(df['Label'].value_counts())

# define target and independent features

# full dataset
X = df.values[:, 1:]
y = df.values[:, 0]


# PCA feature selection
pca = ['Label',
      'gabor_sc3_filter_13',
      'sfs_sc71_max_line_length',
      'hog_sc7_variance',
      'orb_sc51_max',
      'lbpm_sc7_variance',
      'sfs_sc71_min_line_length',
      'ndvi_sc3_variance',
      'hog_sc7_kurtosis',
      'lsr_sc31_line_length',
      'sfs_sc31_w_mean',
      'hog_sc7_kurtosis',
      'orb_sc71_kurtosis',
      'orb_sc31_kurtosis']

df_pca = df[pca]

X = df_pca.values[:, 1:]
y = df_pca.values[:, 0]


# Logistic feature selection
log = ['Label',
 'lbpm_sc7_max',
 'hog_sc7_max',
 'lbpm_sc5_mean',
 'lbpm_sc7_mean',
 'fourier_sc71_mean',
 'pantex_sc7_min',
 'lbpm_sc3_kurtosis',
 'gabor_sc7_filter_13',
 'lbpm_sc7_kurtosis',
 'lsr_sc71_line_length',
 'sfs_sc31_min_line_length',
 'lbpm_sc3_variance',
 'lbpm_sc3_skew',
 'hog_sc3_skew',
 'orb_sc31_max',
 'lsr_sc31_line_contrast',
 'hog_sc3_kurtosis',
 'gabor_sc7_filter_14',
 'fourier_sc51_mean',
 'sfs_sc51_max_line_length',
 'sfs_sc71_mean',
 'lbpm_sc3_max',
 'hog_sc7_mean',
 'sfs_sc71_std',
 'hog_sc3_mean',
 'gabor_sc7_filter_11',
 'fourier_sc71_variance',
 'orb_sc71_mean',
 'orb_sc51_variance',
 'gabor_sc5_filter_13',
 'fourier_sc31_variance',
 'lbpm_sc7_skew',
 'sfs_sc51_w_mean',
 'gabor_sc5_filter_8',
 'gabor_sc7_filter_6',
 'gabor_sc7_filter_8',
 'lsr_sc51_line_contrast',
 'gabor_sc5_filter_11',
 'sfs_sc31_std',
 'lsr_sc31_line_length',
 'gabor_sc5_filter_6',
 'lbpm_sc5_variance',
 'gabor_sc3_filter_2',
 'sfs_sc51_mean']

df_log = df[log]

X = df_log.values[:, 1:]
y = df_log.values[:, 0]

# Random Forest feature selection
rf_features = pd.read_csv(r'C:\Users\brear\OneDrive\Desktop\Grad School\Data-Science-Capstone\random_forest_values.csv')
rf = ['Label']
for row in range(50):
    rf.append(rf_features.iloc[row,0])

df_rf= df[rf]

X = df_rf.values[:, 1:]
y = df_rf.values[:, 0]

# Decision Tree feature selection
tree_features = pd.read_csv(r'C:\Users\brear\OneDrive\Desktop\Grad School\Data-Science-Capstone\Decision_Tree_values.csv')
tree = ['Label']
for row in range(50):
    tree.append(tree_features.iloc[row,0])

df_tree = df[tree]

X = df_tree.values[:, 1:]
y = df_tree.values[:, 0]


# train test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Scaling
sc = StandardScaler()
sc.fit(X_train)
X_train = sc.transform(X_train)
X_test = sc.transform(X_test)


# -------------------------------------------------------------MLP-------------------------------------------------------------
# Hyper-parameter space
parameter_space = {
    'hidden_layer_sizes': [(60,100,60), (100,100,100), (50,100,50)],
    'activation': ['identity', 'relu', 'logistic', 'tanh'],
    'solver': ['sgd', 'adam', 'lbfgs'],
    'alpha': [0.0001, 0.00001, 0.000001],
    'learning_rate': ['constant','adaptive', 'invscaling'],
}

parameter_space = {
    'hidden_layer_sizes': [(60,100,60), (100,100,100), (50,100,50)],
    'activation': ['identity', 'relu', 'logistic', 'tanh'],
    'solver': ['adam'],
    'alpha': [0.0001],
    'learning_rate': ['invscaling'],
}

# Create network
clf = MLPClassifier(max_iter=1000000)

# Run Gridsearch
clf = GridSearchCV(clf, parameter_space, n_jobs=-1, cv=3)

clf.fit(X_train, y_train)
clf_pred = clf.predict(X_test)
print("Results Using MLP Best Params & Tree(Top 50) Features: \n")
print("Classification Report: ")
print(classification_report(y_test, clf_pred))

sns.heatmap(confusion_matrix(y_test, clf_pred), annot=True, fmt='d')
plt.title('MLP: Tree(Top 50) Features')
plt.show()

# Best parameter set
print('Best parameters found for MLP:\n', clf.best_params_)

# --------------------------------------------------------Gradient Boosting----------------------------------------------------

# Hyper-parameter space
parameter_space = {
    'loss': ['deviance'],
    'criterion': ['friedman_mse', 'squared_error', 'mse'],
    'n_estimators': [100, 200, 50],
    'subsample': [1.0, 0.8, 0.6],
    "learning_rate": [0.01, 0.025, 0.05],
    "min_samples_split": np.linspace(0.1, 0.5, 12),
    "min_samples_leaf": np.linspace(0.1, 0.5, 12),
    "max_depth": [3, 5, 8],
    "max_features": ["log2", "sqrt"],
}

parameter_space = {
    'loss': ['deviance'],
    'criterion': ['friedman_mse', 'mse'],
    'n_estimators': [100],
    'subsample': [1.0, 0.6],
    "learning_rate": [0.01, 0.05],
    "min_samples_split": np.linspace(0.1, 0.5, 3),
    "min_samples_leaf": np.linspace(0.1, 0.5, 3),
    "max_depth": [3, 8],
    "max_features": ["log2", "sqrt"],
}

clf = GradientBoostingClassifier()

# Run Gridsearch
clf = GridSearchCV(clf, parameter_space, n_jobs=-1, cv=3)

# Gradient Boosting Predictions
clf.fit(X_train, y_train)
clf_pred = clf.predict(X_test)

# Gradient Boosting Results
print("\n")
print("Results Using Gradient Boosting & Tree(Top 50) Features: \n")
print("Classification Report: ")
print(classification_report(y_test, clf_pred))

sns.heatmap(confusion_matrix(y_test, clf_pred), annot=True, fmt='d')
plt.title('Gradient Boosting: Tree(Top 50) Features')
plt.show()

print('Best parameters found for Gradient Boosting:\n', clf.best_params_)

# --------------------------------------------------------Logistic Regression----------------------------------------------------

# Hyper-parameter space
parameter_space = {
    'penalty': ['l1', 'l2','elasticnet', 'none'],
    'dual': [True, False],
    'C': [0.001, 0.01, 0.1, 1, 10],
    'class_weight': ['dict', 'balanced', None],
    'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga']
}

clf = LogisticRegression()

# Run Gridsearch
clf = GridSearchCV(clf, parameter_space, n_jobs=-1, cv=3)

# Logistic Regression Predictions
clf.fit(X_train, y_train)
clf_pred = clf.predict(X_test)

# Logistic Regression Results
print("\n")
print("Results Using Logistic Regression & Tree(Top 50) Features: \n")
print("Classification Report: ")
print(classification_report(y_test, clf_pred))

sns.heatmap(confusion_matrix(y_test, clf_pred), annot=True, fmt='d')
plt.title('Logistic Regression: Tree(Top 50) Features')
plt.show()

print('Best parameters found for Logistic Regression:\n', clf.best_params_)