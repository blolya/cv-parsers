import spacy.cli
import nltk

spacy.cli.download("en_core_web_sm")
download_dir = "./.nltk"
nltk.download("stopwords", download_dir = download_dir)
nltk.download("punkt", download_dir = download_dir)
nltk.download("averaged_perceptron_tagger", download_dir = download_dir)
nltk.download("universal_tagset", download_dir = download_dir)
nltk.download("wordnet", download_dir = download_dir)
nltk.download("brown", download_dir = download_dir)
nltk.download("maxent_ne_chunker", download_dir = download_dir)
