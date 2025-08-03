import fitz
import os
from typing import List
from spacy.lang.en import English



class DocPreprocessor:
    def __init__(self, file_path):
        self.file_path = file_path

        self.lan = English()
        self.lan.add_pipe("sentencizer")

    def extract_text(self):
        if self.file_path is None or not os.path.exists(self.file_path):
            return
        
        doc = fitz.open(self.file_path)
        text_per_page = []

        for page in doc:
            text = page.get_text()
            cleaned_text = self.simple_preprocess(text)
            text_per_page.append(cleaned_text)

        return text_per_page


    def simple_preprocess(self, text):
        cleaned_text = text.replace("\n", " ").strip()
        cleaned_text = cleaned_text.replace("\t", "").strip()
        
        return cleaned_text
    

    def extract_info(self, text_per_page):
        info_per_page = []

        for page_no, text in enumerate(text_per_page):
            sentences = list(self.lan(text).sents)
            sentences = [str(sen) for sen in sentences]
            info_per_page.append(
                {
                    "page_number": page_no,
                    "char_count": len(text),
                    "word_count": len(text.split(" ")),
                    "sentences": sentences,
                    "sentence_count": len(sentences),
                    "token_count": len(text) / 4,
                    "text": text
                }
            )

        return info_per_page
    

    def sentence_to_chunks(self, processed_contents):
        for item in processed_contents:
            item["chunks"] = self.split_sentences_to_chunks(item["sentences"])

        return processed_contents
    

    def split_sentences_to_chunks(self, sentences, chunk_size: int = 5):
        chunks = []

        for i in range(0, len(sentences), chunk_size):
            chunks.append(sentences[i: i+chunk_size])

        return chunks
    

    def remove_invalid_sentences(self, processed_contents):
        for item in processed_contents:
            chunks = item["chunks"]
            filtered_chunks = []

            for chunk in chunks:
                temp = []
                for sentence in chunk:
                    words = sentence.split()
                    if len(words) > 3:
                        temp.append(sentence)

                if temp:
                    filtered_chunks.append(temp)

            item["chunks"] = filtered_chunks

        return processed_contents



def preprocess_pipeline(doc_path):
    preprocessor = DocPreprocessor(doc_path)

    contents = preprocessor.extract_text()
    processed_contents = preprocessor.extract_info(contents)
    processed_contents = preprocessor.sentence_to_chunks(processed_contents)
    processed_chunks = preprocessor.remove_invalid_sentences(processed_contents)

    return processed_chunks