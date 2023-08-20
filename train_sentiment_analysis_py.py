# -*- coding: utf-8 -*-
"""train_sentiment_analysis.py.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NRdPoJY2gdBchLwM74NqV7UE3gQivRff
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelBinarizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from wordcloud import WordCloud,STOPWORDS
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize,sent_tokenize
from bs4 import BeautifulSoup
import spacy
import re,string,unicodedata
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.stem import LancasterStemmer,WordNetLemmatizer
from sklearn.linear_model import LogisticRegression,SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from textblob import TextBlob
from textblob import Word
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score

import os
# print(os.listdir("../input"))
import warnings
warnings.filterwarnings('ignore')

imdb_data=pd.read_csv('/content/drive/MyDrive/IMDBDataset.csv')
print(imdb_data.shape)
imdb_data.head(10)

imdb_data['sentiment'].value_counts()

train_reviews=imdb_data.review[:40000]
train_sentiments=imdb_data.sentiment[:40000]
#test dataset
test_reviews=imdb_data.review[40000:]
test_sentiments=imdb_data.sentiment[40000:]
print(train_reviews.shape,train_sentiments.shape)
print(test_reviews.shape,test_sentiments.shape)

import nltk
nltk.download('stopwords')

tokenizer=ToktokTokenizer()
#Setting English stopwords
stopword_list=nltk.corpus.stopwords.words('english')

def strip_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

#Removing the square brackets
def remove_between_square_brackets(text):
    return re.sub('\[[^]]*\]', '', text)

#Removing the noisy text
def denoise_text(text):
    text = strip_html(text)
    text = remove_between_square_brackets(text)
    return text
#Apply function on review column
imdb_data['review']=imdb_data['review'].apply(denoise_text)

def remove_special_characters(text, remove_digits=True):
    pattern=r'[^a-zA-z0-9\s]'
    text=re.sub(pattern,'',text)
    return text
#Apply function on review column
imdb_data['review']=imdb_data['review'].apply(remove_special_characters)

#Stemming the text
def simple_stemmer(text):
    ps=nltk.porter.PorterStemmer()
    text= ' '.join([ps.stem(word) for word in text.split()])
    return text
#Apply function on review column
imdb_data['review']=imdb_data['review'].apply(simple_stemmer)

#set stopwords to english
stop=set(stopwords.words('english'))
print(stop)

#removing the stopwords
def remove_stopwords(text, is_lower_case=False):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    if is_lower_case:
        filtered_tokens = [token for token in tokens if token not in stopword_list]
    else:
        filtered_tokens = [token for token in tokens if token.lower() not in stopword_list]
    filtered_text = ' '.join(filtered_tokens)
    return filtered_text
#Apply function on review column
imdb_data['review']=imdb_data['review'].apply(remove_stopwords)

#normalized train reviews
norm_train_reviews=imdb_data.review[:40000]
norm_train_reviews[0]

norm_test_reviews=imdb_data.review[40000:]
norm_test_reviews[45005]

cv=CountVectorizer(min_df=0,max_df=1,binary=False,ngram_range=(1,3))
#transformed train reviews
cv_train_reviews=cv.fit_transform(norm_train_reviews)
#transformed test reviews
cv_test_reviews=cv.transform(norm_test_reviews)

print('BOW_cv_train:',cv_train_reviews.shape)
print('BOW_cv_test:',cv_test_reviews.shape)

#Tfidf vectorizer
tv=TfidfVectorizer(min_df=0,max_df=1,use_idf=True,ngram_range=(1,3))
#transformed train reviews
tv_train_reviews=tv.fit_transform(norm_train_reviews)
#transformed test reviews
tv_test_reviews=tv.transform(norm_test_reviews)
print('Tfidf_train:',tv_train_reviews.shape)
print('Tfidf_test:',tv_test_reviews.shape)

#labeling the sentient data
lb=LabelBinarizer()
#transformed sentiment data
sentiment_data=lb.fit_transform(imdb_data['sentiment'])
print(sentiment_data.shape)

train_sentiments=sentiment_data[:40000]
test_sentiments=sentiment_data[40000:]
print(train_sentiments)
print(test_sentiments)

lr=LogisticRegression(penalty='l2',max_iter=500,C=1,random_state=42)
#Fitting the model for Bag of words
lr_bow=lr.fit(cv_train_reviews,train_sentiments)
print(lr_bow)
#Fitting the model for tfidf features
lr_tfidf=lr.fit(tv_train_reviews,train_sentiments)
print(lr_tfidf)

#Predicting the model for bag of words
lr_bow_predict=lr.predict(cv_test_reviews)
print(lr_bow_predict)
##Predicting the model for tfidf features
lr_tfidf_predict=lr.predict(tv_test_reviews)
print(lr_tfidf_predict)

lr_bow_score=accuracy_score(test_sentiments,lr_bow_predict)
print("lr_bow_score :",lr_bow_score)
#Accuracy score for tfidf features
lr_tfidf_score=accuracy_score(test_sentiments,lr_tfidf_predict)
print("lr_tfidf_score :",lr_tfidf_score)

lr_bow_report=classification_report(test_sentiments,lr_bow_predict,target_names=['Positive','Negative'])
print(lr_bow_report)

#Classification report for tfidf features
lr_tfidf_report=classification_report(test_sentiments,lr_tfidf_predict,target_names=['Positive','Negative'])
print(lr_tfidf_report)





import pickle

# Save the trained models to disk
with open('lr_bow_model.pkl', 'wb') as file:
    pickle.dump(lr_bow, file)

with open('lr_tfidf_model.pkl', 'wb') as file:
    pickle.dump(lr_tfidf, file)

# Load the trained models from disk
with open('lr_bow_model.pkl', 'rb') as file:
    loaded_lr_bow_model = pickle.load(file)

with open('lr_tfidf_model.pkl', 'rb') as file:
    loaded_lr_tfidf_model = pickle.load(file)

# Now you can use the loaded models for real-time inference on new data
def predict_sentiment_bow(model, text):
    # Preprocess the input text
    processed_text = denoise_text(text)
    processed_text = remove_special_characters(processed_text)
    processed_text = simple_stemmer(processed_text)
    processed_text = remove_stopwords(processed_text)

    # Transform the processed text using the CountVectorizer
    text_vector = cv.transform([processed_text])

    # Predict sentiment using the model
    sentiment_prediction = model.predict(text_vector)

    if sentiment_prediction[0] == 1:
        return 'Positive'
    else:
        return 'Negative'

def predict_sentiment_tfidf(model, text):
    # Preprocess the input text
    processed_text = denoise_text(text)
    processed_text = remove_special_characters(processed_text)
    processed_text = simple_stemmer(processed_text)
    processed_text = remove_stopwords(processed_text)

    # Transform the processed text using the TfidfVectorizer
    text_vector = tv.transform([processed_text])

    # Predict sentiment using the model
    sentiment_prediction = model.predict(text_vector)

    if sentiment_prediction[0] == 1:
        return 'Positive'
    else:
        return 'Negative'

# Example of real-time inference using the loaded models
new_text = "It was great movie"
predicted_sentiment_bow = predict_sentiment_bow(loaded_lr_bow_model, new_text)
predicted_sentiment_tfidf = predict_sentiment_tfidf(loaded_lr_tfidf_model, new_text)

print("Predicted Sentiment using BoW model:", predicted_sentiment_bow)
print("Predicted Sentiment using TF-IDF model:", predicted_sentiment_tfidf)



svm=SGDClassifier(loss='hinge',max_iter=500,random_state=42)
#fitting the svm for bag of words
svm_bow=svm.fit(cv_train_reviews,train_sentiments)
print(svm_bow)
#fitting the svm for tfidf features
svm_tfidf=svm.fit(tv_train_reviews,train_sentiments)
print(svm_tfidf)
svm_bow_predict=svm.predict(cv_test_reviews)
print(svm_bow_predict)
#Predicting the model for tfidf features
svm_tfidf_predict=svm.predict(tv_test_reviews)
print(svm_tfidf_predict)

import pickle
from sklearn.naive_bayes import MultinomialNB

# Instantiate the MNB model
mnb = MultinomialNB()

# Fitting the MNB for Bag of Words
mnb_bow = mnb.fit(cv_train_reviews, train_sentiments)
print(mnb_bow)

# Fitting the MNB for TF-IDF features
mnb_tfidf = mnb.fit(tv_train_reviews, train_sentiments)
print(mnb_tfidf)

# Predicting using the MNB model for Bag of Words
mnb_bow_predict = mnb.predict(cv_test_reviews)
print(mnb_bow_predict)

# Predicting using the MNB model for TF-IDF features
mnb_tfidf_predict = mnb.predict(tv_test_reviews)
print(mnb_tfidf_predict)

# Calculate accuracy scores if needed
mnb_bow_score = accuracy_score(test_sentiments, mnb_bow_predict)
print("MNB Bag of Words Accuracy:", mnb_bow_score)
mnb_tfidf_score = accuracy_score(test_sentiments, mnb_tfidf_predict)
print("MNB TF-IDF Accuracy:", mnb_tfidf_score)

# Save the MNB models to disk
with open('mnb_bow_model.pkl', 'wb') as file:
    pickle.dump(mnb_bow, file)

with open('mnb_tfidf_model.pkl', 'wb') as file:
    pickle.dump(mnb_tfidf, file)

# Load the MNB models from disk
with open('mnb_bow_model.pkl', 'rb') as file:
    loaded_mnb_bow_model = pickle.load(file)

with open('mnb_tfidf_model.pkl', 'rb') as file:
    loaded_mnb_tfidf_model = pickle.load(file)

# Now you can use the loaded MNB models for real-time inference on new data
def predict_sentiment_mnb_bow(model, text):
    # Preprocess the input text
    processed_text = denoise_text(text)
    processed_text = remove_special_characters(processed_text)
    processed_text = simple_stemmer(processed_text)
    processed_text = remove_stopwords(processed_text)

    # Transform the processed text using the CountVectorizer
    text_vector = cv.transform([processed_text])

    # Predict sentiment using the model
    sentiment_prediction = model.predict(text_vector)

    if sentiment_prediction[0] == 1:
        return 'Positive'
    else:
        return 'Negative'

def predict_sentiment_mnb_tfidf(model, text):
    # Preprocess the input text
    processed_text = denoise_text(text)
    processed_text = remove_special_characters(processed_text)
    processed_text = simple_stemmer(processed_text)
    processed_text = remove_stopwords(processed_text)

    # Transform the processed text using the TfidfVectorizer
    text_vector = tv.transform([processed_text])

    # Predict sentiment using the model
    sentiment_prediction = model.predict(text_vector)

    if sentiment_prediction[0] == 1:
        return 'Positive'
    else:
        return 'Negative'

# Example of real-time inference using the loaded MNB models
new_text = "I was bad watching this movie"
predicted_sentiment_mnb_bow = predict_sentiment_mnb_bow(loaded_mnb_bow_model, new_text)
predicted_sentiment_mnb_tfidf = predict_sentiment_mnb_tfidf(loaded_mnb_tfidf_model, new_text)

print("Predicted Sentiment using MNB and BoW:", predicted_sentiment_mnb_bow)
print("Predicted Sentiment using MNB and TF-IDF:", predicted_sentiment_mnb_tfidf)

import pickle

# Save the trained models to disk
with open('svm_bow_model.pkl', 'wb') as file:
    pickle.dump(svm_bow, file)

with open('svm_tfidf_model.pkl', 'wb') as file:
    pickle.dump(svm_tfidf, file)

# Load the trained models from disk
with open('svm_bow_model.pkl', 'rb') as file:
    loaded_svm_bow_model = pickle.load(file)

with open('svm_tfidf_model.pkl', 'rb') as file:
    loaded_svm_tfidf_model = pickle.load(file)

# Now you can use the loaded SVM models for real-time inference on new data
def predict_sentiment_svm_bow(model, text):
    # Preprocess the input text
    processed_text = denoise_text(text)
    processed_text = remove_special_characters(processed_text)
    processed_text = simple_stemmer(processed_text)
    processed_text = remove_stopwords(processed_text)

    # Transform the processed text using the CountVectorizer
    text_vector = cv.transform([processed_text])

    # Predict sentiment using the model
    sentiment_prediction = model.predict(text_vector)

    if sentiment_prediction[0] == 1:
        return 'Positive'
    else:
        return 'Negative'

def predict_sentiment_svm_tfidf(model, text):
    # Preprocess the input text
    processed_text = denoise_text(text)
    processed_text = remove_special_characters(processed_text)
    processed_text = simple_stemmer(processed_text)
    processed_text = remove_stopwords(processed_text)

    # Transform the processed text using the TfidfVectorizer
    text_vector = tv.transform([processed_text])

    # Predict sentiment using the model
    sentiment_prediction = model.predict(text_vector)

    if sentiment_prediction[0] == 1:
        return 'Positive'
    else:
        return 'Negative'

# Example of real-time inference using the loaded SVM models
new_text = "it was not good!"
predicted_sentiment_svm_bow = predict_sentiment_svm_bow(loaded_svm_bow_model, new_text)
predicted_sentiment_svm_tfidf = predict_sentiment_svm_tfidf(loaded_svm_tfidf_model, new_text)

print("Predicted Sentiment using SVM and BoW:", predicted_sentiment_svm_bow)
print("Predicted Sentiment using SVM and TF-IDF:", predicted_sentiment_svm_tfidf)

mnb=MultinomialNB()
#fitting the svm for bag of words
mnb_bow=mnb.fit(cv_train_reviews,train_sentiments)
print(mnb_bow)
#fitting the svm for tfidf features
mnb_tfidf=mnb.fit(tv_train_reviews,train_sentiments)
print(mnb_tfidf)

mnb_bow_predict=mnb.predict(cv_test_reviews)
print(svm_bow_predict)
#Predicting the model for tfidf features
mnb_tfidf_predict=mnb.predict(tv_test_reviews)
print(mnb_tfidf_predict)

mnb_bow_predict=mnb.predict(cv_test_reviews)
print(mnb_bow_predict)
#Predicting the model for tfidf features
mnb_tfidf_predict=mnb.predict(tv_test_reviews)
print(mnb_tfidf_predict)

import pickle

# Save the trained models to disk
with open('lr_bow_model.pkl', 'wb') as file:
    pickle.dump(lr_bow, file)

with open('lr_tfidf_model.pkl', 'wb') as file:
    pickle.dump(lr_tfidf, file)

with open('svm_bow_model.pkl', 'wb') as file:
    pickle.dump(svm_bow, file)

with open('svm_tfidf_model.pkl', 'wb') as file:
    pickle.dump(svm_tfidf, file)

with open('mnb_bow_model.pkl', 'wb') as file:
    pickle.dump(mnb_bow, file)

with open('mnb_tfidf_model.pkl', 'wb') as file:
    pickle.dump(mnb_tfidf, file)

# Load the trained models from disk
with open('lr_bow_model.pkl', 'rb') as file:
    loaded_lr_bow_model = pickle.load(file)

with open('lr_tfidf_model.pkl', 'rb') as file:
    loaded_lr_tfidf_model = pickle.load(file)

with open('svm_bow_model.pkl', 'rb') as file:
    loaded_svm_bow_model = pickle.load(file)

with open('svm_tfidf_model.pkl', 'rb') as file:
    loaded_svm_tfidf_model = pickle.load(file)

with open('mnb_bow_model.pkl', 'rb') as file:
    loaded_mnb_bow_model = pickle.load(file)

with open('mnb_tfidf_model.pkl', 'rb') as file:
    loaded_mnb_tfidf_model = pickle.load(file)

# Now you can use the loaded models for real-time inference on new data
# (Code for predict_sentiment functions)

# Example of real-time inference using the loaded models
new_text = "I really enjoyed watching this movie. The acting was great!"
predicted_sentiment_lr_bow = predict_sentiment_bow(loaded_lr_bow_model, new_text)
predicted_sentiment_lr_tfidf = predict_sentiment_tfidf(loaded_lr_tfidf_model, new_text)
predicted_sentiment_svm_bow = predict_sentiment_svm_bow(loaded_svm_bow_model, new_text)
predicted_sentiment_svm_tfidf = predict_sentiment_svm_tfidf(loaded_svm_tfidf_model, new_text)
predicted_sentiment_mnb_bow = predict_sentiment_mnb_bow(loaded_mnb_bow_model, new_text)
predicted_sentiment_mnb_tfidf = predict_sentiment_mnb_tfidf(loaded_mnb_tfidf_model, new_text)

print("Predicted Sentiment using Logistic Regression and BoW:", predicted_sentiment_lr_bow)
print("Predicted Sentiment using Logistic Regression and TF-IDF:", predicted_sentiment_lr_tfidf)
print("Predicted Sentiment using SVM and BoW:", predicted_sentiment_svm_bow)
print("Predicted Sentiment using SVM and TF-IDF:", predicted_sentiment_svm_tfidf)
print("Predicted Sentiment using MNB and BoW:", predicted_sentiment_mnb_bow)
print("Predicted Sentiment using MNB and TF-IDF:", predicted_sentiment_mnb_tfidf)

#the results of the above are not accurate so we will try another approch



import re
import pandas as pd
from sklearn.model_selection import train_test_split as tts
from keras.layers import Dense, LSTM,Embedding, SpatialDropout1D
from keras.utils.np_utils import to_categorical
from keras.models import Sequential
from keras.preprocessing.text import Tokenizer
from keras.utils.data_utils import pad_sequences
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import string
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split as tts

#loading data from csv file
data=pd.read_csv('/content/drive/MyDrive/IMDBDataset.csv')

#showing columne
data.columns

#text preprocrdding for text classfication
def normalized_text(text):
    text=text.lower()
    text=re.sub('\[.*?\]','',text)
    text=re.sub('[%s]'%re.escape(string.punctuation),'',text)
    text=re.sub('\w*\d\w*','',text)
    return text

normalized=lambda x:normalized_text(x)#cleaned1

#applying preprocessing to loaded dataset
data['review']=pd.DataFrame(data.review.apply(normalized))

#removing certain characters from the input text.
def preprocess(text):
    text=re.sub('[''"",,,]','',text)
    text=re.sub('\n','',text)
    return text

processed=lambda x:preprocess(x)

#applied preprocessing on data
data['review']=pd.DataFrame(data.review.apply(processed))

#slecting predictor and response
x = data.iloc[0:,0].values
y = data.iloc[0:,1].values

#spliiting  the data for testing and training
xtrain,xtest,ytrain,ytest = tts(x,y,test_size = 0.25,random_state = 42)

#TfidfVectorizer  contians text processing techniques such as tokeninzaiotn
#Term Frequency
#Inverse Document Frequency (IDF)
tf = TfidfVectorizer()
print(tf)
from sklearn.pipeline import Pipeline

#perform text classification using the TF-IDF vectorizer and a Logistic Regression classifier
from sklearn.linear_model import LogisticRegression
classifier=LogisticRegression()
model=Pipeline([('vectorizer',tf),('classifier',classifier)])

model.fit(xtrain,ytrain)

#ypred to assign predicted response
ypred=model.predict(xtest)

# model score
accuracy_score(ypred,ytest)

# confusion matrix
c_matrix=confusion_matrix(ytest,ypred)
print(c_matrix)

# f1 score

recall=c_matrix[0][0]/(c_matrix[0][0]+c_matrix[1][0])
precision=c_matrix[0][0]/(c_matrix[0][0]+c_matrix[0][1])
F1=2*recall*precision/(recall+precision)
print(F1)

def predict_sentiment(sentence):
    preprocessed_sentence = preprocess(normalized_text(sentence))
    predicted_sentiment = model.predict([preprocessed_sentence])
    return predicted_sentiment[0]

# Test the function with an example sentence
example_sentence = "It was a good movie."
predicted_sentiment = predict_sentiment(example_sentence)
print("Predicted Sentiment:", predicted_sentiment)

#saving the model for pickle pile
import pickle

# Save the model weights
pickle.dump(model, open('model.pkl', 'wb'))

import pickle

# Load the model
model = pickle.load(open('model.pkl', 'rb'))

# Predict the sentiment of a new sentence
sentence = "It was a good movie."
preprocessed_sentence = preprocess(normalized_text(sentence))
predicted_sentiment = model.predict([preprocessed_sentence])

# Print the predicted sentiment
print("Predicted sentiment:", predicted_sentiment[0])

import pickle
import re
def preprocess(text):
    text=re.sub('[''"",,,]','',text)
    text=re.sub('\n','',text)
    return text
def normalized_text(text):
    text=text.lower()
    text=re.sub('\[.*?\]','',text)
    text=re.sub('[%s]'%re.escape(string.punctuation),'',text)
    text=re.sub('\w*\d\w*','',text)
    return text

normalized=lambda x:normalized_text(x)#cleaned1
# Load the model
model = pickle.load(open('model.pkl', 'rb'))

# Predict the sentiment of a new sentence
sentence = "It was a good movie."
preprocessed_sentence = preprocess(normalized_text(sentence))
predicted_sentiment = model.predict([preprocessed_sentence])

# Print the predicted sentiment
print("Predicted sentiment:", predicted_sentiment[0])

# Commented out IPython magic to ensure Python compatibility.
# %cp /content/model.pkl /content/drive/MyDrive/sentiment.pkl