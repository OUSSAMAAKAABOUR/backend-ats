
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from joblib import dump
import pickle

class CustomTransformer:
    def __init__(self, vectorizer, classifier, encoder):
        self.vectorizer = vectorizer
        self.classifier = classifier
        self.encoder = encoder

    def fit(self, X, y=None):
        # Fit the vectorizer
        X_vect = self.vectorizer.fit_transform(X)
        # Fit the encoder
        self.encoder.fit(y)
        # Fit the classifier
        self.classifier.fit(X_vect, y)
        return self

    def transform(self, X):
        # Transform using the vectorizer
        X_vect = self.vectorizer.transform(X)
        return X_vect

    def predict(self, X):
        # Transform and predict using the vectorizer and classifier
        X_vect = self.transform(X)
        y_pred = self.classifier.predict(X_vect)
        # Decode the predicted labels
        y_pred_decoded = self.encoder.inverse_transform(y_pred)
        return y_pred_decoded
    
    def set_params(self, **params):
        # Set parameters for vectorizer, classifier, and encoder
        self.vectorizer.set_params(**params.get('vectorizer', {}))
        self.classifier.set_params(**params.get('classifier', {}))
        return self