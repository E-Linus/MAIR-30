import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

################################### Dataset ##########################################

# Dataset has 15 classes (dialog acts)
    
# We want to read the dalog_acts.dat file. The first word of every line is the class label and the rest of the line is the text.
# Change accordingly, my computer does not work for relative paths
df = pd.read_csv('C:/Users/nikol/OneDrive/Desktop/UU/Period-1/Methods-in-AI/MAIR-30/TeamProject/Part1-SystemImplementation/Part1a-TextClassification/dialog_acts.dat', header=None, names=['data'])

# Apply the function to split the 'data' column into 'label' and 'text' columns
df[['label', 'text']] = df['data'].apply(lambda x: pd.Series(x.split(' ', 1)))

# Drop the original 'data' column
df.drop('data', axis=1, inplace=True)

# print(df.head(10))
df_deduplicated = df.drop_duplicates(subset=['text'])

# Features and Labels
x = df['text']
y = df['label']

x_deduplicated = df_deduplicated['text']
y_deduplicated = df_deduplicated['label']

# Splitting the dataset into training and test sets
# 85% of the data is used for training and 15% for testing
# random state is like seed I think to just keep the same split and shuffling
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.15, random_state=11, shuffle=True)

x_train_unique, x_test_unique, y_train_unique, y_test_unique = train_test_split(x_deduplicated, y_deduplicated, test_size=0.15, random_state=11, shuffle=True)

# print(x_train.shape)
# print(x_test.shape)
# print(y_train.shape)
# print(y_test.shape)

# Scikit needs numpy
x_train_unique_np = x_train_unique.values
y_train_unique_np = y_train_unique.values

x_test_unique_np = x_test_unique.values
y_test_unique_np = y_test_unique.values

# print(x_train_unique_np.shape)
# print(x_test_unique_np.shape)
# print(y_train_unique_np.shape)
# print(y_test_unique_np.shape)

################################### Dataset ##########################################

####################### Baseline majority class (inform label) #######################
# Identify the majority class (idk if its needed)
# majority_class = y_train.value_counts().idxmax()
def baseline_majority(y_test, majority_class='inform'):
    total_instances = len(y_test)
    correct_predictions = (y_test == majority_class).sum()
    
    # y_pred_baseline = np.full((total_instances), majority_class)
    # unique_labels = np.unique(y_test)

    # cm = confusion_matrix(y_test, y_pred_baseline, labels=unique_labels)
    # disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=unique_labels)
    # disp.plot()
    # plt.title("Baseline Majority Class Confusion Matrix")
    # plt.show()

    accuracy = (correct_predictions / total_instances) * 100
    c_report = classification_report(y_test, [majority_class] * total_instances, zero_division=0)

    return accuracy, c_report
####################### Baseline majority class (inform label) #######################

############################## Baseline keyword matching #############################
# The order of the rules plays a big role in the accuracy
# I tried to put the class labels first that appear the most times in the dataset. (Hence is makes sense to have inform as first rule)
rules = {
    # I put thank you first because in the text whenever theres thank you and bye at the same sentence
    # it will always be thankyou
    'inform': ['any', 'im looking'],
    'request': ['phone', 'address', 'postcode', 'post code', 'type of food', 'what', 'whats'],
    'thankyou': ['thank you'],
    'ack': ['okay','ok'],
    'affirm': ['yes', 'right', 'yeah'],
    'bye': ['good bye','bye'],
    'deny': ['wrong','not', 'dont'],
    'hello': ['hello', 'hi'],
    'negate': ['no'],
    'repeat': ['repeat', 'again', 'back'],
    'reqalts': ['is there', 'how about', 'anything else', 'what about'],
    'confirm': ['is it', 'does it'],
    'reqmore': ['more'],
    'restart': ['reset', 'start over', 'start again'],
    'null': ['cough', 'unintelligible', 'tv_noise', 'noise', 'sil', 'none']
}

def baseline_keyword(x_test, y_test, rules):

    y_pred = []

    for utterance in x_test:
        # Our default label is the inform label since it appears the most times
        predicted_label = 'inform'
        for label, keywords in rules.items():
            if any(keyword in utterance for keyword in keywords):
                predicted_label = label
                break
        y_pred.append(predicted_label)

    # Calculate the accuracy from the predictions
    total_instances = len(y_test)
    correct_predictions = (y_test == y_pred).sum()

    # unique_labels = np.unique(y_test)

    # cm = confusion_matrix(y_test, y_pred, labels=unique_labels)
    # disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=unique_labels)
    # disp.plot()
    # plt.title("Baseline Keyword Matching Confusion Matrix")
    # plt.show()

    accuracy = (correct_predictions / total_instances) * 100
    c_report = classification_report(y_test, y_pred, zero_division=0)

    return accuracy, c_report
############################## Baseline keyword matching #############################

############################## Baseline prompt predictions #############################
def baseline_prompt(rules):

    while True:
        utterance = input("Please enter utterance to be classified (Type 'exit' to go back): ")
        if utterance == 'exit':
            print("Exiting...")
            break

        predicted_label = 'inform'
        for label, keywords in rules.items():
            if any(keyword in utterance for keyword in keywords):
                predicted_label = label
                break

        print(f"Predicted dialog act label: {predicted_label}")
############################## Baseline prompt predictions #############################

############################## ML Decision Tree Classifier #############################

# For out-of-vocabulary words we don't have to do anything since the CountVectorizer will ignore them
def ml_decision_tree_classifier(x_train, y_train, x_test, y_test):

    # Transforming the data
    vectorizer = CountVectorizer()
    x_train_bow = vectorizer.fit_transform(x_train)
    x_test_bow = vectorizer.transform(x_test)
    
    clf = DecisionTreeClassifier(random_state=0)
    clf.fit(x_train_bow, y_train)

    y_pred = clf.predict(x_test_bow)

    # cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)
    # disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=clf.classes_)
    # disp.plot()
    # plt.title("ML Decision Tree Confusion Matrix (no Duplicates)")
    # plt.show()

    accuracy = accuracy_score(y_test, y_pred)
    c_report = classification_report(y_test, y_pred, zero_division=0)

    return accuracy * 100, c_report

def ml_decision_tree_classifier_prompt(x_train, y_train):

    vectorizer = CountVectorizer()
    x_train_bow = vectorizer.fit_transform(x_train)
    clf = DecisionTreeClassifier(random_state=0)
    clf.fit(x_train_bow, y_train)
    
    while True:
        utterance = input("Please enter utterance to be classified (Type 'exit' to go back): ")
        if utterance == 'exit':
            print("Exiting...")
            break
        
        utterance_bow = vectorizer.transform([utterance])
        predicted_label = clf.predict(utterance_bow)[0]
        
        print(f"Predicted dialog act label: {predicted_label}")

############################## ML Decision Tree Classifier #############################

########################### ML Logistic Regression Classifier ##########################

def ml_logistic_regression_classifier(x_train, y_train, x_test, y_test):

    vectorizer = CountVectorizer()
    x_train_bow = vectorizer.fit_transform(x_train)
    x_test_bow = vectorizer.transform(x_test)
    
    clf = LogisticRegression(random_state=0, max_iter=1000)
    clf.fit(x_train_bow, y_train)
    
    y_pred = clf.predict(x_test_bow)
    
    # cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)
    # disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=clf.classes_)
    # disp.plot()
    # plt.title("ML Logistic Regression Confusion Matrix (no Duplicates)")
    # plt.show()

    accuracy = accuracy_score(y_test, y_pred)
    c_report = classification_report(y_test, y_pred, zero_division=0)

    return accuracy * 100, c_report

def ml_logistic_regression_classifier_prompt(x_train, y_train):

    vectorizer = CountVectorizer()
    x_train_bow = vectorizer.fit_transform(x_train)
    
    clf = LogisticRegression(random_state=0, max_iter=1000)
    clf.fit(x_train_bow, y_train)
    
    while True:
        utterance = input("Please enter utterance to be classified (Type 'exit' to go back): ")
        if utterance == 'exit':
            print("Exiting...")
            break
        
        utterance_bow = vectorizer.transform([utterance])
        predicted_label = clf.predict(utterance_bow)[0]
        
        print(f"Predicted dialog act label: {predicted_label}")

########################### ML Logistic Regression Classifier ##########################

def main_menu():
    while True:
        print("\nChoose an option:")
        print("1. Run Baseline Majority Class")
        print("2. Run Baseline Keyword Matching")
        print("3. Run Baseline Keyword Matching Prompt Predictions")
        print("4. Run ML Decision Tree Classifier Algorithm (with Duplicates)")
        print("5. Run ML Decision Tree Classifier Algorithm (without Duplicates)")
        print("6. Run ML Logistic Regression Classifier Algorithm (with Duplicates)")
        print("7. Run ML Logistic Regression Classifier Algorithm (without Duplicates)")
        print("8. Run everything - Classification Reports")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            baseline_majority_accuracy, c_report = baseline_majority(y_test)
            print(f"Baseline majority accuracy: {baseline_majority_accuracy:.2f}%")
        elif choice == '2':
            baseline_keyword_accuracy, c_report = baseline_keyword(x_test, y_test, rules)
            print(f"Baseline keyword accuracy: {baseline_keyword_accuracy:.2f}%")
        elif choice == '3':
            baseline_prompt(rules)
        elif choice == '4':
            ml_decision_tree_classifier_accuracy_dups, c_report = ml_decision_tree_classifier(x_train, y_train, x_test, y_test)
            print(f"Machine Learing Decision Tree Classifier accuracy (with Duplicates): {ml_decision_tree_classifier_accuracy_dups:.2f}%")

            ml_decision_tree_classifier_prompt(x_train, y_train)
        elif choice == '5':
            ml_decision_tree_classifier_accuracy_nodups, c_report = ml_decision_tree_classifier(x_train_unique_np, y_train_unique_np, x_test_unique_np, y_test_unique_np)
            print(f"Machine Learing Decision Tree Classifier accuracy (without Duplicates): {ml_decision_tree_classifier_accuracy_nodups:.2f}%")

            ml_decision_tree_classifier_prompt(x_train_unique_np, y_train_unique_np)
        elif choice == '6':
            ml_logistic_regression_classifier_accuracy_dups, c_report = ml_logistic_regression_classifier(x_train, y_train, x_test, y_test)
            print(f"Machine Learing Logistic Regression Classifier accuracy (with Duplicates): {ml_logistic_regression_classifier_accuracy_dups:.2f}%")
            
            ml_logistic_regression_classifier_prompt(x_train, y_train)
        elif choice == '7':
            ml_logistic_regression_classifier_accuracy_nodups, c_report = ml_logistic_regression_classifier(x_train_unique_np, y_train_unique_np, x_test_unique_np, y_test_unique_np)
            print(f"Machine Learing Logistic Regression Classifier accuracy (without Duplicates): {ml_logistic_regression_classifier_accuracy_nodups:.2f}%")

            ml_logistic_regression_classifier_prompt(x_train_unique_np, y_train_unique_np)
        elif choice == '8':
            baseline_majority_accuracy, c_report1 = baseline_majority(y_test)
            print(f"Baseline majority accuracy: {baseline_majority_accuracy:.2f}%")
            print(c_report1)
            baseline_keyword_accuracy, c_report2 = baseline_keyword(x_test, y_test, rules)
            print(f"Baseline keyword accuracy: {baseline_keyword_accuracy:.2f}%")
            print(c_report2)
            ml_decision_tree_classifier_accuracy_dups, c_report3 = ml_decision_tree_classifier(x_train, y_train, x_test, y_test)
            print(f"Machine Learing Decision Tree Classifier accuracy (with Duplicates): {ml_decision_tree_classifier_accuracy_dups:.2f}%")
            print(c_report3)
            ml_decision_tree_classifier_accuracy_nodups, c_report4 = ml_decision_tree_classifier(x_train_unique_np, y_train_unique_np, x_test_unique_np, y_test_unique_np)
            print(f"Machine Learing Decision Tree Classifier accuracy (without Duplicates): {ml_decision_tree_classifier_accuracy_nodups:.2f}%")
            print(c_report4)
            ml_logistic_regression_classifier_accuracy_dups, c_report5 = ml_logistic_regression_classifier(x_train, y_train, x_test, y_test)
            print(f"Machine Learing Logistic Regression Classifier accuracy (with Duplicates): {ml_logistic_regression_classifier_accuracy_dups:.2f}%")
            print(c_report5)
            ml_logistic_regression_classifier_accuracy_nodups, c_report6 = ml_logistic_regression_classifier(x_train_unique_np, y_train_unique_np, x_test_unique_np, y_test_unique_np)
            print(f"Machine Learing Logistic Regression Classifier accuracy (without Duplicates): {ml_logistic_regression_classifier_accuracy_nodups:.2f}%")
            print(c_report6)
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()