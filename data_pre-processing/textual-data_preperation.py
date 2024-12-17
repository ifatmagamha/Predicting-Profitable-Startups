import pandas as pd
import numpy as np
import re
import os
from datetime import datetime
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')


class TextPreprocessor:
    """
    Classe pour nettoyer et vectoriser les données textuelles.
    """
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.vectorizer = TfidfVectorizer(max_features=1000)  

    def clean_text(self, text):
        """
        Nettoie le texte : suppression des caractères spéciaux, mots courts, stopwords et lemmatisation.
        """
        text = re.sub(r"[^a-zA-Z]", " ", text)  
        text = text.lower()  
        words = word_tokenize(text)  # Tokenisation
        words = [self.lemmatizer.lemmatize(word) for word in words 
                 if word not in self.stop_words and len(word) > 2]  
        return " ".join(words)

    def vectorize_text(self, df, column_name):
        """
        Vectorise le texte nettoyé en utilisant TF-IDF.
        """
        tfidf_matrix = self.vectorizer.fit_transform(df[column_name])
        feature_names = self.vectorizer.get_feature_names_out()
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names, index=df.index)
        return tfidf_df


class DataPreprocessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.cleaned_data = None
        self.tfidf_vectorizer = None
        self.scaler = None
        self.encoder = None
        self.text_preprocessor = TextPreprocessor()

    def log(self, message):
        print(f"[INFO] {message}")

    def process_dates(self):
        self.log("Processing dates...")
        self.data['creation date'] = pd.to_datetime(self.data['creation date'], format='%m-%Y', errors='coerce')
        current_year = datetime.now().year
        self.data['creation year'] = self.data['creation date'].dt.year
        self.data['company age'] = current_year - self.data['creation year']

    def preprocess_text(self):
        self.log("Preprocessing text data with advanced cleaning...")
        self.data['description_cleaned'] = self.data['description'].fillna("").apply(self.text_preprocessor.clean_text)
        
        # Vectorisation TF-IDF
        tfidf_df = self.text_preprocessor.vectorize_text(self.data, "description_cleaned")
        
        # Intégration des nouvelles caractéristiques TF-IDF
        self.data = pd.concat([self.data, tfidf_df], axis=1)
        self.data.drop(columns=["description", "description_cleaned"], inplace=True)

    def encode_categorical_data(self):
        self.log("Encoding categorical data...")
        categorical_columns = ['Stage', 'Dealflow', 'region']
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        encoded_features = self.encoder.fit_transform(self.data[categorical_columns])
        encoded_columns = self.encoder.get_feature_names_out()#il ne prend plus d'argument c lui qui estime les features les plus pertienentes
        encoded_df = pd.DataFrame(encoded_features, columns=encoded_columns)
        self.data = pd.concat([self.data.reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)

    def process_markets(self):
        self.log("Processing markets column...")
        markets_expanded = self.data['markets'].str.strip("[]").str.replace("'", "").str.split(", ")
        markets_dummies = pd.get_dummies(markets_expanded.apply(pd.Series).stack()).groupby(level=0).sum()
        self.data = pd.concat([self.data.reset_index(drop=True), markets_dummies.reset_index(drop=True)], axis=1)

    def parse_investment(self, investment_str):
        try:
            investment_str = investment_str.replace("'", "").replace("{", "").replace("}", "")
            return {k.strip(): float(v.strip('%')) / 100 for k, v in (x.split(':') for x in investment_str.split(','))}
        except Exception as e:
            self.log(f"Error parsing investment: {e}")
            return {}

    def process_investments(self):
        self.log("Processing investment by stage...")
        investment_data = self.data['investment by stage'].apply(self.parse_investment).apply(pd.Series)
        self.data[['seed_investment', 'early_investment', 'growth_investment']] = investment_data

    def normalize_numeric_data(self):

        self.log("Normalizing numeric data...")
        numeric_columns = ['number of deals (12months)', 'market value', 'company age']

        # Vérification avant nettoyage
        self.log("Checking market value before cleaning...")
        print(self.data['market value'].head(10))  # Afficher les premières valeurs pour diagnostic

        # Nettoyage : suppression des caractères
        self.data['market value'] = self.data['market value'].replace({'M\$': '', '\$': '', ',': ''}, regex=True)
        # Conversion en numérique
        self.data['market value'] = pd.to_numeric(self.data['market value'], errors='coerce')
        # Afficher les valeurs après conversion pour vérifier les NaN
        self.log("Checking market value after cleaning...")
        print(self.data['market value'].head(10))
        # Remplacement des NaN par une valeur par défaut (ex. médiane ou moyenne calculée uniquement si possible)
        if self.data['market value'].notna().any():
            self.data['market value'].fillna(self.data['market value'].median(), inplace=True)
        else:
            self.log("Warning: market value column is entirely NaN!")
            self.data['market value'].fillna(0, inplace=True)  # Valeur par défaut

        # Normalisation
        self.scaler = StandardScaler()
        self.data[numeric_columns] = self.scaler.fit_transform(self.data[numeric_columns])

    def preprocess(self):
        self.log("Starting preprocessing pipeline...")
        self.process_dates()
        self.preprocess_text()
        self.encode_categorical_data()
        self.process_markets()
        self.process_investments()
        self.normalize_numeric_data()
        
        # Suppression des colonnes inutiles
        self.cleaned_data = self.data.drop(columns=['markets', 'creation date', 'investment by stage'])
        self.log("Preprocessing pipeline completed.")

    def get_cleaned_data(self):
        self.log("Retrieving cleaned data...")
        return self.cleaned_data

    def save_to_csv(self, output_file_path):
        self.log(f"Saving cleaned data to {output_file_path}...")
        self.cleaned_data.to_csv(output_file_path, index=False)
        self.log("Data saved successfully.")


if __name__ == "__main__":
    file_path = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\data_pre-processing\cleaned_data.csv"
    output_file_path = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\data_pre-processing\processed_textual-data_TF-IDF.csv"

    # process
    preprocessor = DataPreprocessor(file_path)
    preprocessor.preprocess()
    cleaned_data = preprocessor.get_cleaned_data()
    print(cleaned_data.head())
    preprocessor.save_to_csv(output_file_path)
