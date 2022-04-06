import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import warnings
import path
warnings.filterwarnings("ignore")

def run_model(model='', features='', feature_count=50, classes = '', pretrained=True):


    # Read in dataframe and remove merged columns
    df = pd.read_csv(
        r'C:\Users\brear\OneDrive\Documents\GitHub\Data-Science-Capstone\Contextual_Feautures_Modeling\Grid_Search\Contextual_Features_final.csv')
    df = df.drop(columns=['long', 'lat', 'Point'])
    cols_to_move = ['Label']
    df = df[cols_to_move + [col for col in df.columns if col not in cols_to_move]]

    # Move Target to first column
    target = 'Label'
    first_col = df.pop(target)
    df.insert(0, target, first_col)

    if classes == 'all_classes':
        df = df
    elif classes == 'classes_0&1':
        # set label column equal to only 0 and 1 classes
        df = df[df['Label'].isin([0, 1])]

    # define target and independent features
    if features == 'All_Features': # full dataset, all features

        X = df.values[:, 1:]
        y = df.values[:, 0]

    elif features == 'PCA_Features': # PCA feature selection

        pca_features = pd.read_csv(r'') # pca feature list csv
        pca = ['Label']
        for row in range(feature_count):
            pca.append(pca_features.iloc[row, 0])

        df_pca = df[pca]
        X = df_pca.values[:, 1:]
        y = df_pca.values[:, 0]

    elif features == 'Random_Forest_Features':  # Random Forest feature selection

        rf_features = pd.read_csv(r'') # random forest feature list csv

        rf = ['Label']
        for row in range(feature_count):
            rf.append(rf_features.iloc[row,0])

        df_rf = df[rf]

        X = df_rf.values[:, 1:]
        y = df_rf.values[:, 0]

    elif features == 'Logistic_Regression_Features':  # logistic regression feature selection

        log_features = pd.read_csv(r'')  # logistic regression feature list csv

        log = ['Label']
        for row in range(feature_count):
            log.append(log_features.iloc[row, 0])

        df_log = df[log]

        X = df_log.values[:, 1:]
        y = df_log.values[:, 0]




    # train test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25,
                                                      random_state=42)  # 0.25 x 0.8 = 0.2

    # Feature Scaling
    sc = StandardScaler()
    sc.fit(X_train)
    X_train = sc.transform(X_train)
    X_test = sc.transform(X_test)
    X_val = sc.transform(X_val)



    if model == 'MLP':
        if pretrained == False:
            # Hyper-parameter space
            '''
            parameter_space = {
                'hidden_layer_sizes': [(60, 100, 60), (100, 100, 100), (50, 100, 50)],
                'activation': ['identity', 'relu', 'logistic', 'tanh'],
                'solver': ['sgd', 'adam', 'lbfgs'],
                'alpha': [0.0001, 0.00001, 0.000001],
                'learning_rate': ['constant', 'adaptive', 'invscaling'],
            }
            '''

            parameter_space = {
                'hidden_layer_sizes': [(60, 100, 60), (100, 100, 100), (50, 100, 50)],
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
            print(f"Test Results Using {model} Best Params, {feature_count}{features}, and {classes}: \n")
            print("Classification Report: ")
            print(classification_report(y_test, clf_pred))

            # Best parameter set
            print(f'Best parameters found for {model}:\n', clf.best_params_)

            # Save model
            filename = f'{model}_model_{features}_{classes}.sav'
            pickle.dump(clf, open(filename, 'wb'))

    elif model == "Gradient_Boosting":
        if pretrained == False:
            # Hyper-parameter space
            '''
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
            '''

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

            clf.fit(X_train, y_train)
            clf_pred = clf.predict(X_test)
            print(f"Test Results Using {model} Best Params, {feature_count}{features}, and {classes}: \n")
            print("Classification Report: ")
            print(classification_report(y_test, clf_pred))

            # Best parameter set
            print(f'Best parameters found for {model}:\n', clf.best_params_)

            # Save model
            filename = f'{model}_model_{features}_{classes}.sav'
            pickle.dump(clf, open(filename, 'wb'))

    elif model == "Logistic_Regression":
        if pretrained == False:
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

            clf.fit(X_train, y_train)
            clf_pred = clf.predict(X_test)
            print(f"Test Results Using {model} Best Params, {feature_count}{features}, and {classes}: \n")
            print("Classification Report: ")
            print(classification_report(y_test, clf_pred))

            # Best parameter set
            print(f'Best parameters found for {model}:\n', clf.best_params_)

            # Save model
            filename = f'{model}_model_{features}_{classes}.sav'
            pickle.dump(clf, open(filename, 'wb'))

    elif model == "Random_Forest":
        if pretrained == False:
            # Hyper-parameter space
            parameter_space = {
                'criterion': ['gini', 'entropy'],
                'n_estimators': [100, 200],
                "min_samples_split": np.linspace(0.1, 0.5, 3),
                "min_samples_leaf": np.linspace(0.1, 0.5, 3),
                "max_depth": [2, 10, 20],
                "max_features": ["log2", "sqrt", 'auto'],
            }

            clf = RandomForestClassifier()

            # Run Gridsearch
            clf = GridSearchCV(clf, parameter_space, n_jobs=-1, cv=3)

            clf.fit(X_train, y_train)
            clf_pred = clf.predict(X_test)
            print(f"Test Results Using {model} Best Params, {feature_count}{features}, and {classes}: \n")
            print("Classification Report: ")
            print(classification_report(y_test, clf_pred))

            # Best parameter set
            print(f'Best parameters found for {model}:\n', clf.best_params_)

            # Save model
            filename = f'{model}_model_{features}_{classes}.sav'
            pickle.dump(clf, open(filename, 'wb'))

    # Load Model
    # data_folder = path(r'C:\Users\brear\OneDrive\Desktop\Grad School\Data-Science-Capstone\Contextual_Feautres_Modeling\Code\Grid_Search')
    filename = f'{model}_model_{features}_{classes}.sav' # saved model path
    loaded_model = pickle.load(open(filename, 'rb'))

    # Predict on validation set
    val_pred = loaded_model.predict(X_val)
    print(f"Validation Results Using {model} Best Params, {feature_count}{features}, {classes}: \n")
    print("Classification Report: ")
    print(classification_report(y_val, val_pred))
    cf_matrix = confusion_matrix(y_val, val_pred)
    sns.heatmap(cf_matrix, annot=True, fmt="d")
    plt.title(f'{model} Confusion Matrix - {feature_count}{features}, {classes}')
    plt.show()




