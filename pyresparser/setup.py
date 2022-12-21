import spacy.cli
import nltk

spacy.cli.download("en_core_web_sm")
nltk.download("words", download_dir = "./.nltk")
nltk.download("stopwords", download_dir = "./.nltk")
