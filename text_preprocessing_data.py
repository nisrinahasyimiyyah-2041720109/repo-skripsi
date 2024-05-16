import string
import re
import pandas as pd
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

factory = StemmerFactory()
stemmer = factory.create_stemmer()

class CustomStopWordRemover:
    def __init__(self, stop_words):
        self.stop_words = stop_words

    def remove(self, text):
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        return ' '.join(filtered_words)
        
class TextPreprocessingData():
    def __init__(self, text, config):
        self.path = config
        self.text = text

    def casefolding(self, text):
        if isinstance(text, str):  # Pastikan input adalah string tunggal
            return text.lower().strip()
        elif isinstance(text, pd.Series):  # Jika input adalah Series, gunakan apply untuk menerapkan fungsi ke setiap elemen
            return text.apply(lambda x: x.lower().strip())
        elif isinstance(text, pd.DataFrame):  # Jika input adalah DataFrame, gunakan applymap untuk menerapkan fungsi ke setiap sel
            return text.applymap(lambda x: x.lower().strip())
        else:
            raise TypeError("Input harus berupa string tunggal, Series, atau DataFrame.")

    def cleaning(self, text):
        if isinstance(text, str):  # Pastikan input adalah string tunggal
            # remove tab, new line, and back slice
            text = text.replace('\\t'," ").replace('\\n', " ").replace('\\u', " ").replace('\\',"")
            # remove non ASCII (emoticon, chinese word, etc)
            text = text.encode('ascii', 'replace').decode('ascii')
            # remove mention, link, hashtag
            text = ' '.join(re.sub("([@#][A-Za-z0-9]+)|(\w+:\/\/\S+)"," ", text).split())
            # remove incomplete URL
            text = text.replace("http://", " ").replace("https://", " ")
            # remove number
            text = re.sub(r"\d+", "", text)
            # remove punctuation and replace with space
            text = re.sub(r'[.,]', ' ', text)
            # remove punctuation
            # Menghapus simbol-simbol tidak standar dan menggantinya dengan spasi
            cleaned_text = re.sub(r'[^\w\s]', ' ', text)
            # Menghapus multiple whitespace
            text = re.sub('\s+', ' ', cleaned_text).strip()
            # Menentukan ambang batas panjang string acak
            threshold_length = 20
            # menghapus string acak berdasarkan panjangnya
            text = ' '.join(word for word in text.split() if len(word) <= threshold_length)
            #remove whitespace leading & trailing
            text = text.strip()
            #remove multiple whitespace into single whitespace
            text = re.sub('\s+',' ',text)
            # remove single char
            text = re.sub(r"\b[a-zA-Z]\b", "", text)
            # remove laughter pattern
            laughter_patterns = r'\b((ha)+h*|(he)+h*|(hi)+h*|(wk)+w*k*|(eh)+e*|(ah)+a*|(ih)+i*|(kw)+k*w*|(hem)+m*)\b'
            text = re.sub(laughter_patterns, '', text, flags=re.IGNORECASE)
            text = re.sub('@[^\s]+','',text) #Menghapus Username
            text = ' '.join(re.sub("(rt )"," ", text).split()) #Menghapus kata 'rt'
            text = re.sub('((www\S+)|(http\S+))', ' ', text) #Menghapus URL
            text = text.replace('\\t'," ").replace('\\n'," ").replace('\\u'," ").replace('\\',"") #remove tab, new line, ans back slice
            text = text.translate(str.maketrans('','',string.punctuation)).lower() #Menghapus Punctuation
            return text
        elif isinstance(text, pd.Series):
            # Jika input adalah Series, gunakan apply untuk menerapkan fungsi ke setiap elemen
            return text.apply(self.cleaning)
        elif isinstance(text, pd.DataFrame):
            # Jika input adalah DataFrame, gunakan applymap untuk menerapkan fungsi ke setiap sel
            return text.applymap(self.cleaning)
        else:
            raise TypeError("Input harus berupa string tunggal, Series, atau DataFrame.")
    
    def remove_duplicate(self, text):
        unique_reviews = set()  # Set untuk menyimpan teks ulasan yang sudah unik
        unique_data = []  # Daftar untuk menyimpan data unik
        for review in text:
            cleaned_review = review.strip()  # Membersihkan teks ulasan dan menghapus spasi tambahan
            if cleaned_review not in unique_reviews:
                unique_reviews.add(cleaned_review)  # Menambahkan teks ulasan ke dalam set unik
                unique_data.append(cleaned_review)  # Menambahkan teks ulasan yang unik ke dalam daftar
        
        # Buat DataFrame baru dari data unik
        unique_df = pd.DataFrame({'Review': unique_data})
        
        # Konversi kolom 'Review' ke tipe data string
        unique_df['Review'] = unique_df['Review'].astype(str)
        
        # Reset index dan hapus baris yang kosong atau hanya terdiri dari spasi
        unique_df = unique_df.dropna(subset=['Review'])
        unique_df = unique_df[unique_df['Review'].str.strip() != '']

        return unique_df
    
    def normalisasi(self, text):
        slang_dictionary = pd.read_csv(self.path['NORMALFILE'])
        slang_dict = pd.Series(slang_dictionary['formal'].values, index=slang_dictionary['slang']).to_dict()

        def apply_normalization(text, slang_dict):
            for word in text.split():
                if word in slang_dict:
                    text = re.sub(r'\b{}\b'.format(re.escape(word)), slang_dict[word], text)
            text = re.sub('@[\w]+', '', text)
            return text

        return apply_normalization(text, slang_dict)
    
    def tokenize(self, text):
        return word_tokenize(text)

    def remove_stopwords(self, text):
        # Baca isi file stopword
        with open(self.path['STOPWORDS'], 'r', encoding='utf-8') as file:
            stopwords = file.read().splitlines()
            
        # Kata-kata yang ingin dikecualikan
        exceptions = ["belum", "tidak", "tanpa"]

        # Buat daftar stopword baru tanpa kata-kata pengecualian
        custom_stopwords = [word.lower() for word in stopwords if word.lower() not in exceptions]

        # Buat instance custom stopword remover
        custom_stopword_remover = CustomStopWordRemover(custom_stopwords)

        # Hapus stopword
        filtered_words = [custom_stopword_remover.remove(w) for w in text]
        filtered_words = [word for word in filtered_words if word != '']  # Memfilter kata-kata kosong
        return filtered_words

    def lemmatization(self, text):
        return [stemmer.stem(word) for word in text]

    
    def output(self, export):
        self.dataframe = pd.DataFrame()
        self.dataframe['case_folding'] = self.text.apply(self.casefolding)
        self.dataframe['cleaned'] = self.dataframe['case_folding'].apply(self.cleaning)
        self.dataframe.drop_duplicates(subset=['cleaned'], inplace=True)
        self.dataframe['normalization'] = self.dataframe['cleaned'].apply(self.normalisasi)
        self.dataframe['tokenize'] = self.dataframe['normalization'].apply(self.tokenize)
        self.dataframe['remove_stopwords'] = self.dataframe['tokenize'].apply(self.remove_stopwords)
        self.dataframe['lemmatization'] = self.dataframe['remove_stopwords'].apply(self.lemmatization)
        self.dataframe['text_string_lemma'] = self.dataframe['lemmatization'].apply(lambda x: ' '.join(x))

        # Menghapus baris yang kosong atau hanya berisi spasi pada kolom 'text_string_lemma'
        self.dataframe = self.dataframe.dropna(subset=['text_string_lemma'])
        self.dataframe = self.dataframe[self.dataframe['text_string_lemma'] != '']  # Hanya menyimpan baris yang tidak kosong

        if export == True:
            # self.dataframe['label'] = self.label
            self.dataframe = self.dataframe.dropna()
            self.dataframe = self.dataframe.reset_index(drop=True)
            self.dataframe.to_csv('dataset/preprocessing/dataset_hasil_preprocess.csv', index=False)
            return self.dataframe
        elif export == False:
            self.dataframe = self.dataframe.dropna()
            self.dataframe = self.dataframe.reset_index(drop=True)
            return self.dataframe
        else:
            print('Error')