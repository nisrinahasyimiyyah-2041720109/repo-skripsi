from flask import Flask, render_template, request, Response, make_response, jsonify, redirect, url_for, send_file, session
import pickle, os, glob, json
import joblib
import csv
from count import CountDF
from text_preprocessing_data import TextPreprocessingData
from text_preprocessing_avoskin import TextPreprocessingAvo
from text_preprocessing_azarine import TextPreprocessingAza
from text_preprocessing_skingame import TextPreprocessingSkingame
from text_preprocessing_somethinc import TextPreprocessingSomethinc
from sentistrength_id import SentiStrength
from model import Vectorize, Model
import pandas as pd
from shutil import copyfile
from sklearn.model_selection import train_test_split
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from whitenoise import WhiteNoise

#-- Declare Input --#
# df = 'dataset/dataframe/avoskin-df.csv'

PATH = {
    'DATASET_AVO' : 'dataset/sentistrength_id/sentimen_avoskin_terpisah.csv',
    'DATASET_AZA' : 'dataset/sentistrength_id/sentimen_azarine_terpisah.csv',
    'DATASET_SKINGAME' : 'dataset/sentistrength_id/sentimen_skingame_terpisah.csv',
    'DATASET_SOMETHINC' : 'dataset/sentistrength_id/sentimen_somethinc_terpisah.csv',
    'PREPROCESS' : 'dataset/preprocessing/dataset_preprocess.csv',
    'NORMALFILE' : 'dataset/preprocessing/colloquial-indonesian-lexicon.csv',
    'STOPWORDS' : 'dataset/preprocessing/stopwords_indonesian.txt',
    'KAMUS_EMOJI' : 'dataset/preprocessing/emoji.csv',
    'KAMUS_EMOTICON' : 'dataset/preprocessing/emoticon.json',
}
#-- Declare Input End --#

#-- Web Based Start --#
app = Flask(__name__)
app.secret_key = 'sentimensession'

app.wsgi_app = WhiteNoise(app.wsgi_app, root="static/")

@app.route('/', methods=['POST', 'GET'])
def main():
    return redirect('/dashboard', 302)

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/sidebar.html')
def sidebar():
    return render_template('sidebar.html')

@app.route('/dataset', methods=['POST', 'GET'])
def dataset():
    return render_template('dataset.html')

@app.route('/proses-data', methods=['POST', 'GET'])
def prosesdata():
    return render_template('proses_data.html')

@app.route('/prediksi-sentimen', methods=['POST', 'GET'])
def prediksisentimen():
    return render_template('prediksi_sentimen.html')

@app.route('/dashboard-avoskin', methods=['POST', 'GET'])
def dashboard_avoskin():
    return render_template("dashboard_avoskin.html")

@app.route('/dashboard-azarine', methods=['POST', 'GET'])
def dashboard_azarine():
    return render_template("dashboard_azarine.html")

@app.route('/dashboard-skingame', methods=['POST', 'GET'])
def dashboard_skingame():
    return render_template("dashboard_skingame.html")

@app.route('/dashboard-somethinc', methods=['POST', 'GET'])
def dashboard_somethinc():
    return render_template("dashboard_somethinc.html")

@app.route('/model', methods=['POST', 'GET'])
def model_manager():
    return render_template('model.html')

from flask import jsonify

@app.route('/api/file/dataset', methods=['POST'])
def handle_csv_dataset():
    if request.method == 'POST':
        # Handle POST request to upload CSV file
        data = request.files['file']
        if data:
            data.filename = 'dataset.csv'
            data.save('dataset/dataframe/' + data.filename)
            csv_data = parse_csv_file('dataset/dataframe/dataset.csv')  # Parse CSV file
            return jsonify({'result': 'upload success', 'csvData': csv_data})
        else:
            return jsonify({'result': 'cant upload file'})

def parse_csv_file(file_path):
    # Function to parse CSV file and return its data
    csv_data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            csv_data.append(row)
    return csv_data

@app.route('/api/check_dataset', methods=['GET'])
def check_dataset():
    dataset_path = 'dataset/dataframe/dataset.csv'
    file_exists = os.path.exists(dataset_path)
    return jsonify({"exists": file_exists})

@app.route('/api/delete_datasets', methods=['DELETE'])
def delete_datasets():
    try:
        paths = [
            'dataset/dataframe/dataset.csv',
            'dataset/preprocessing/dataset_hasil_preprocess.csv',
            'dataset/predict_file/hasil_prediksi.csv'
        ]
        
        # Delete each file if it exists
        for path in paths:
            if os.path.exists(path):
                os.remove(path)
        
        return jsonify({"result": "success"})
    except Exception as e:
        return jsonify({"result": "error", "message": str(e)})

@app.route('/api/count/labels/dataset', methods=['POST'])
def api_counts_labels_dataset():
    if request.method == 'POST':
        count = CountDF('dataset/dataframe/dataset.csv')
        count_json = {
            'length_df' : count.length_df()
        }
        return jsonify(count_json)
    else:
        return jsonify({'result' : 'error'})
    
@app.route('/api/count/data/preprocess', methods=['POST'])
def api_counts_data_preprocess():
    if request.method == 'POST':
        count = CountDF('dataset/preprocessing/dataset_hasil_preprocess.csv')
        count_json = {
            'length_df' : count.length_df()
        }
        return jsonify(count_json)
    else:
        return jsonify({'result' : 'error'})

@app.route('/api/proses/data', methods=['POST'])
def proses_data():
    if request.method == 'POST':
        data = pd.read_csv('dataset/dataframe/dataset.csv')
        reviews = data.iloc[:, 0]  # Mengambil kolom pertama
        text_preprocess = TextPreprocessingData(reviews, PATH)
        result = text_preprocess.output(export=True)
        return result.to_json(orient='split')
    else:
        return jsonify({"result" : "error"})

@app.route('/api/check_preprocessed_dataset', methods=['GET'])
def check_preprocessed_dataset():
    dataset_path = 'dataset/preprocessing/dataset_hasil_preprocess.csv'
    file_exists = os.path.exists(dataset_path)
    return jsonify({"exists": file_exists})

@app.route('/api/predict/file', methods=['POST'])
def predict_input_file():
    PATH_FILE = 'pretrained/'
    if request.method == 'POST':
        data = pd.read_csv('dataset/preprocessing/dataset_hasil_preprocess.csv')
        filename_model_file = PATH_FILE + 'model.pickle'
        filename_tfidf_file = PATH_FILE + 'tfidf.pickle'
        model = joblib.load(filename_model_file)
        tfidf = joblib.load(filename_tfidf_file)
        features = tfidf.transform(data['text_string_lemma']).toarray()
        data['sentimen'] = model.predict(features)
        data.to_csv('dataset/predict_file/hasil_prediksi.csv', index=False)
        count = CountDF('dataset/predict_file/hasil_prediksi.csv')
        count_result = count.count_labels(labels='sentimen')
        count_json = {
            'index' : count_result.index.values.tolist(),
            'values' : count_result.values.tolist(),
            'length_df' : count.length_df(),
        }
        return jsonify(count_json)
    else:
        return jsonify({"result" : "error"})

# @app.route('/api/predict/file/download', methods=['GET'])
# def predict_download_file():
#     if request.method == 'GET':
#         return send_file('dataset/predict_file/hasil_prediksi.csv', mimetype='text/csv', as_attachment=True)

@app.route('/api/predict/file/download', methods=['GET'])
def predict_download_file():
    if request.method == 'GET':
        # Buka file hasil prediksi dengan encoding utf-8
        with open('dataset/predict_file/hasil_prediksi.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  # Simpan baris header
            # Ubah nilai sentimen yang asli menjadi label yang diinginkan
            updated_lines = []
            for row in reader:
                # Ambil nilai sentimen dari kolom "sentimen" (indeks 7)
                sentiment = row[7]

                # Ubah nilai 0, 1, dan 2 menjadi 'negatif', 'netral', dan 'positif' 
                if sentiment == '0':
                    sentiment = 'negatif'
                elif sentiment == '1':
                    sentiment = 'netral'
                elif sentiment == '2':
                    sentiment = 'positif'

                # Perbarui nilai sentimen dan tambahkan baris yang diperbarui ke daftar
                row[7] = sentiment
                updated_lines.append(row)

        # Debugging: Cetak isi updated_lines sebelum penulisan ke file
        # print("Isi updated_lines sebelum penulisan ke file:", updated_lines)

        # Tulis kembali ke file dengan nilai sentimen yang telah diubah
        with open('dataset/predict_file/hasil_prediksi_updated.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Tulis baris header
            writer.writerow(header)
            # Tulis baris data yang telah diperbarui
            writer.writerows(updated_lines)

        # Kirim file yang telah diperbarui ke pengguna sebagai unduhan
        return send_file('dataset/predict_file/hasil_prediksi_updated.csv', mimetype='text/csv', as_attachment=True)

@app.route('/api/check_predicted_file', methods=['GET'])
def check_predicted_file():
    dataset_path = 'dataset/predict_file/hasil_prediksi.csv'
    file_exists = os.path.exists(dataset_path)
    return jsonify({"exists": file_exists})

@app.route('/api/count/labels/pred', methods=['POST'])
def api_counts_labels_pred():
    if request.method == 'POST':
        count = CountDF('dataset/predict_file/hasil_prediksi.csv')
        count_result = count.count_labels(labels='sentimen')
        count_json = {
            'index' : count_result.index.values.tolist(),
            'values' : count_result.values.tolist(),
            'length_df' : count.length_df(),
        }
        return jsonify(count_json)
    else:
        return jsonify({'result' : 'error'})

@app.route('/api/count/words/pred', methods=['POST'])
def api_counts_words_pred():
    if request.method == 'POST':
        df = pd.read_csv('dataset/predict_file/hasil_prediksi.csv')
        count = CountDF('dataset/predict_file/hasil_prediksi.csv')
        count_result = count.count_words(labels='text_string_lemma', words=10)
        count_result_positive = count.count_words_label(df['text_string_lemma'].loc[df['sentimen'] == 2], words=10)
        count_result_neutral = count.count_words_label(df['text_string_lemma'].loc[df['sentimen'] == 1], words=10)
        count_result_negative = count.count_words_label(df['text_string_lemma'].loc[df['sentimen'] == 0], words=10)
        count_json = {
            'index' : list(count_result.keys()),
            'values' : list(count_result.values()),
            'length_df' : count.length_df(),
            'positive_words' : {
                'label' : list(count_result_positive.keys()),
                'value' : list(count_result_positive.values()),
            },
            'neutral_words' : {
                'label' : list(count_result_neutral.keys()),
                'value' : list(count_result_neutral.values()),
            },
            'negative_words' : {
                'label' : list(count_result_negative.keys()),
                'value' : list(count_result_negative.values()),
            }
        }
        return jsonify(count_json)
    else:
        return jsonify({'result' : 'error'})
    
@app.route('/api/predict', methods=['POST', 'GET'])
def predict_input():
    PATH_FILE = 'pretrained/'
    if request.method == 'POST':
        data = request.get_json()
        filename_model = PATH_FILE + data['model_name']
        filename_tfidf = PATH_FILE + data['tfidf_name']
        tfidf = pickle.load(open(filename_tfidf, 'rb'))
        model = pickle.load(open(filename_model, 'rb'))
        if data['type'] == 'text':
            text_dataframe = pd.DataFrame()
            text_dataframe['text'] = [data['input_text']]
            text_preprocess = TextPreprocessingAvo(text_dataframe['text'], None, PATH)
            result = text_preprocess.output(export=False)
            features_req_input = tfidf.transform(result['text_string_stemmed']).toarray()
            pred = model.predict(features_req_input)
            return jsonify({'result' : pred.tolist()})
        else:
            return jsonify({'result' : 'error'})


@app.route('/api/file/dataset/avoskin', methods=['GET', 'POST'])
def file_upload_dataset_avoskin():
    if request.method == 'GET':
        return send_file('dataset/dataframe/dataset-avoskin.csv', mimetype='text/csv', attachment_filename='dataset-avoskin.csv', as_attachment=True)
    elif request.method == 'POST':
        data = request.files['file']
        if data != '' or data != None:
            data.filename = 'dataset-avoskin.csv'
            data.save('dataset/dataframe/'+data.filename)
            PATH['DATASET'] = 'dataset/dataframe/dataset-avoskin.csv'
            return jsonify({'result' : 'upload success'})
        else:
            return jsonify({'result' : 'cant upload file'})
    else:
        return jsonify({'result' : 'error request'})
    
@app.route('/api/preprocess/avoskin', methods=['POST'])
def preprocess_data_avoskin():
    if request.method == 'POST':
        data = pd.read_csv('dataset/dataframe/dataset-avoskin.csv')
        reviews = data['Review']  # Memilih hanya kolom 'Review'
        text_preprocess = TextPreprocessingAvo(reviews, PATH)
        # data['Review'] = data['Review'].astype(str)
        result = text_preprocess.output(export=True)
        return result.to_json(orient='records')
    else:
        return jsonify({"result" : "error"})

@app.route('/api/preprocess/avoskin/download', methods=['GET'])
def preprocess_download_file_avoskin():
    if request.method == 'GET':
        return send_file('dataset/preprocessing/dataset_preprocess_avoskin.csv', mimetype='text/csv', attachment_filename='dataset_preprocess.csv', as_attachment=True)
    
@app.route('/api/sentistrength/avoskin', methods=['POST'])
def sentistrength_avoskin():
    if request.method == 'POST':
        config = dict()
        config["negation"] = True
        config["booster"] = True
        config["ungkapan"] = True
        config["consecutive"] = True
        config["repeated"] = True
        config["emoticon"] = True
        config["question"] = True
        config["exclamation"] = True
        config["punctuation"] = True
        senti = SentiStrength(config)
        data = pd.read_csv('dataset/preprocessing/dataset_preprocess_avoskin.csv')
        nama_kolom = 'text_string_lemma'

        def analisis_sentimen(sentence):
            result = senti.main(sentence)
            return result
        
        data['sentimen'] = data[nama_kolom].apply(analisis_sentimen)

        # Menyimpan perubahan ke dalam file CSV
        data.to_csv('dataset/sentistrength_id/sentimen_avoskin.csv', index=False)

        # Membaca file CSV hasil analisis sentimen
        data = pd.read_csv('dataset/sentistrength_id/sentimen_avoskin.csv')

        # Nama kolom yang berisi data sentimen
        nama_kolom_sentimen = 'sentimen'

        # Fungsi untuk memisahkan data JSON dalam kolom sentimen
        def parse_sentimen(sentimen_str):
            try:
                sentimen_dict = json.loads(sentimen_str.replace("'", "\""))
                return pd.Series(sentimen_dict)
            except:
                return pd.Series({})

        # Memisahkan data dalam kolom 'sentimen' menjadi kolom-kolom terpisah
        data_sentimen = data[nama_kolom_sentimen].apply(parse_sentimen)

        # Menggabungkan DataFrame baru dengan DataFrame asli
        data = pd.concat([data, data_sentimen], axis=1)

        # Menyimpan perubahan ke dalam file CSV
        data.to_csv('dataset/sentistrength_id/sentimen_avoskin_terpisah.csv', index=False)
        # Ubah DataFrame menjadi format JSON
        json_data = data.to_json(orient='records')

        return Response(json_data, mimetype='application/json')
    else:
        return jsonify({"result" : "error"})

@app.route('/api/sentistrength/avoskin/download', methods=['GET'])
def sentistrength_download_avoskin():
    if request.method == 'GET':
        return send_file('dataset/sentistrength_id/sentimen_avoskin_terpisah.csv', mimetype='text/csv', attachment_filename='sentimen_avoskin_terpisah.csv', as_attachment=True)

@app.route('/api/file/dataset/azarine', methods=['GET', 'POST'])
def file_upload_dataset_azarine():
    if request.method == 'GET':
        return send_file('dataset/dataframe/dataset-azarine.csv', mimetype='text/csv', attachment_filename='dataset-azarine.csv', as_attachment=True)
    elif request.method == 'POST':
        data = request.files['file']
        if data != '' or data != None:
            data.filename = 'dataset-azarine.csv'
            data.save('dataset/dataframe/'+data.filename)
            PATH['DATASET'] = 'dataset/dataframe/dataset-azarine.csv'
            return jsonify({'result' : 'upload success'})
        else:
            return jsonify({'result' : 'cant upload file'})
    else:
        return jsonify({'result' : 'error request'})
    
@app.route('/api/preprocess/azarine', methods=['POST'])
def preprocess_data_azarine():
    if request.method == 'POST':
        data = pd.read_csv('dataset/dataframe/dataset-azarine.csv')
        reviews = data['Review']  # Memilih hanya kolom 'Review'
        text_preprocess = TextPreprocessingAza(reviews, PATH)
        # data['Review'] = data['Review'].astype(str)
        result = text_preprocess.output(export=True)
        return result.to_json(orient='records')
    else:
        return jsonify({"result" : "error"})

@app.route('/api/preprocess/azarine/download', methods=['GET'])
def preprocess_download_file_azarine():
    if request.method == 'GET':
        return send_file('dataset/preprocessing/dataset_preprocess_azarine.csv', mimetype='text/csv', attachment_filename='dataset_preprocess_azarine.csv', as_attachment=True)
    
@app.route('/api/sentistrength/azarine', methods=['POST'])
def sentistrength_azarine():
    if request.method == 'POST':
        config = dict()
        config["negation"] = True
        config["booster"] = True
        config["ungkapan"] = True
        config["consecutive"] = True
        config["repeated"] = True
        config["emoticon"] = True
        config["question"] = True
        config["exclamation"] = True
        config["punctuation"] = True
        senti = SentiStrength(config)
        data = pd.read_csv('dataset/preprocessing/dataset_preprocess_azarine.csv')
        nama_kolom = 'text_string_lemma'

        def analisis_sentimen(sentence):
            result = senti.main(sentence)
            return result
        
        data['sentimen'] = data[nama_kolom].apply(analisis_sentimen)

        # Menyimpan perubahan ke dalam file CSV
        data.to_csv('dataset/sentistrength_id/sentimen_azarine.csv', index=False)

        # Membaca file CSV hasil analisis sentimen
        data = pd.read_csv('dataset/sentistrength_id/sentimen_azarine.csv')

        # Nama kolom yang berisi data sentimen
        nama_kolom_sentimen = 'sentimen'

        # Fungsi untuk memisahkan data JSON dalam kolom sentimen
        def parse_sentimen(sentimen_str):
            try:
                sentimen_dict = json.loads(sentimen_str.replace("'", "\""))
                return pd.Series(sentimen_dict)
            except:
                return pd.Series({})

        # Memisahkan data dalam kolom 'sentimen' menjadi kolom-kolom terpisah
        data_sentimen = data[nama_kolom_sentimen].apply(parse_sentimen)

        # Menggabungkan DataFrame baru dengan DataFrame asli
        data = pd.concat([data, data_sentimen], axis=1)

        # Menyimpan perubahan ke dalam file CSV
        data.to_csv('dataset/sentistrength_id/sentimen_azarine_terpisah.csv', index=False)
        # Ubah DataFrame menjadi format JSON
        json_data = data.to_json(orient='records')

        return Response(json_data, mimetype='application/json')
    else:
        return jsonify({"result" : "error"})

@app.route('/api/sentistrength/azarine/download', methods=['GET'])
def sentistrength_download_azarine():
    if request.method == 'GET':
        return send_file('dataset/sentistrength_id/sentimen_azarine_terpisah.csv', mimetype='text/csv', attachment_filename='sentimen_azarine_terpisah.csv', as_attachment=True)
    
@app.route('/api/file/dataset/skingame', methods=['GET', 'POST'])
def file_upload_dataset_skingame():
    if request.method == 'GET':
        return send_file('dataset/dataframe/dataset-skingame.csv', mimetype='text/csv', attachment_filename='dataset-skingame.csv', as_attachment=True)
    elif request.method == 'POST':
        data = request.files['file']
        if data != '' or data != None:
            data.filename = 'dataset-skingame.csv'
            data.save('dataset/dataframe/'+data.filename)
            PATH['DATASET'] = 'dataset/dataframe/dataset-skingame.csv'
            return jsonify({'result' : 'upload success'})
        else:
            return jsonify({'result' : 'cant upload file'})
    else:
        return jsonify({'result' : 'error request'})
    
@app.route('/api/preprocess/skingame', methods=['POST'])
def preprocess_data_skingame():
    if request.method == 'POST':
        data = pd.read_csv('dataset/dataframe/dataset-skingame.csv')
        reviews = data['Review']  # Memilih hanya kolom 'Review'
        text_preprocess = TextPreprocessingSkingame(reviews, PATH)
        # data['Review'] = data['Review'].astype(str)
        result = text_preprocess.output(export=True)
        return result.to_json(orient='records')
    else:
        return jsonify({"result" : "error"})

@app.route('/api/preprocess/skingame/download', methods=['GET'])
def preprocess_download_file_skingame():
    if request.method == 'GET':
        return send_file('dataset/preprocessing/dataset_preprocess_skingame.csv', mimetype='text/csv', attachment_filename='dataset_preprocess_skingame.csv', as_attachment=True)
    
@app.route('/api/sentistrength/skingame', methods=['POST'])
def sentistrength_skingame():
    if request.method == 'POST':
        config = dict()
        config["negation"] = True
        config["booster"] = True
        config["ungkapan"] = True
        config["consecutive"] = True
        config["repeated"] = True
        config["emoticon"] = True
        config["question"] = True
        config["exclamation"] = True
        config["punctuation"] = True
        senti = SentiStrength(config)
        data = pd.read_csv('dataset/preprocessing/dataset_preprocess_skingame.csv')
        nama_kolom = 'text_string_lemma'

        def analisis_sentimen(sentence):
            result = senti.main(sentence)
            return result
        
        data['sentimen'] = data[nama_kolom].apply(analisis_sentimen)

        # Menyimpan perubahan ke dalam file CSV
        data.to_csv('dataset/sentistrength_id/sentimen_skingame.csv', index=False)

        # Membaca file CSV hasil analisis sentimen
        data = pd.read_csv('dataset/sentistrength_id/sentimen_skingame.csv')

        # Nama kolom yang berisi data sentimen
        nama_kolom_sentimen = 'sentimen'

        # Fungsi untuk memisahkan data JSON dalam kolom sentimen
        def parse_sentimen(sentimen_str):
            try:
                sentimen_dict = json.loads(sentimen_str.replace("'", "\""))
                return pd.Series(sentimen_dict)
            except:
                return pd.Series({})

        # Memisahkan data dalam kolom 'sentimen' menjadi kolom-kolom terpisah
        data_sentimen = data[nama_kolom_sentimen].apply(parse_sentimen)

        # Menggabungkan DataFrame baru dengan DataFrame asli
        data = pd.concat([data, data_sentimen], axis=1)

        # Menyimpan perubahan ke dalam file CSV
        data.to_csv('dataset/sentistrength_id/sentimen_skingame_terpisah.csv', index=False)
        # Ubah DataFrame menjadi format JSON
        json_data = data.to_json(orient='records')

        return Response(json_data, mimetype='application/json')
    else:
        return jsonify({"result" : "error"})

@app.route('/api/sentistrength/skingame/download', methods=['GET'])
def sentistrength_download_skingame():
    if request.method == 'GET':
        return send_file('dataset/sentistrength_id/sentimen_skingame_terpisah.csv', mimetype='text/csv', attachment_filename='sentimen_skingame_terpisah.csv', as_attachment=True)
    
@app.route('/api/file/dataset/somethinc', methods=['GET', 'POST'])
def file_upload_dataset_somethinc():
    if request.method == 'GET':
        return send_file('dataset/dataframe/dataset-somethinc.csv', mimetype='text/csv', attachment_filename='dataset-somethinc.csv', as_attachment=True)
    elif request.method == 'POST':
        data = request.files['file']
        if data != '' or data != None:
            data.filename = 'dataset-somethinc.csv'
            data.save('dataset/dataframe/'+data.filename)
            PATH['DATASET'] = 'dataset/dataframe/dataset-somethinc.csv'
            return jsonify({'result' : 'upload success'})
        else:
            return jsonify({'result' : 'cant upload file'})
    else:
        return jsonify({'result' : 'error request'})
    
@app.route('/api/preprocess/somethinc', methods=['POST'])
def preprocess_data_somethinc():
    if request.method == 'POST':
        data = pd.read_csv('dataset/dataframe/dataset-somethinc.csv')
        reviews = data['Review']  # Memilih hanya kolom 'Review'
        text_preprocess = TextPreprocessingSomethinc(reviews, PATH)
        # data['Review'] = data['Review'].astype(str)
        result = text_preprocess.output(export=True)
        return result.to_json(orient='records')
    else:
        return jsonify({"result" : "error"})

@app.route('/api/preprocess/somethinc/download', methods=['GET'])
def preprocess_download_file_somethinc():
    if request.method == 'GET':
        return send_file('dataset/preprocessing/dataset_preprocess_somethinc.csv', mimetype='text/csv', attachment_filename='dataset_preprocess_somethinc.csv', as_attachment=True)
    
@app.route('/api/sentistrength/somethinc', methods=['POST'])
def sentistrength_somethinc():
    if request.method == 'POST':
        config = dict()
        config["negation"] = True
        config["booster"] = True
        config["ungkapan"] = True
        config["consecutive"] = True
        config["repeated"] = True
        config["emoticon"] = True
        config["question"] = True
        config["exclamation"] = True
        config["punctuation"] = True
        senti = SentiStrength(config)
        data = pd.read_csv('dataset/preprocessing/dataset_preprocess_somethinc.csv')
        nama_kolom = 'text_string_lemma'

        def analisis_sentimen(sentence):
            result = senti.main(sentence)
            return result
        
        data['sentimen'] = data[nama_kolom].apply(analisis_sentimen)

        # Menyimpan perubahan ke dalam file CSV
        data.to_csv('dataset/sentistrength_id/sentimen_somethinc.csv', index=False)

        # Membaca file CSV hasil analisis sentimen
        data = pd.read_csv('dataset/sentistrength_id/sentimen_somethinc.csv')

        # Nama kolom yang berisi data sentimen
        nama_kolom_sentimen = 'sentimen'

        # Fungsi untuk memisahkan data JSON dalam kolom sentimen
        def parse_sentimen(sentimen_str):
            try:
                sentimen_dict = json.loads(sentimen_str.replace("'", "\""))
                return pd.Series(sentimen_dict)
            except:
                return pd.Series({})

        # Memisahkan data dalam kolom 'sentimen' menjadi kolom-kolom terpisah
        data_sentimen = data[nama_kolom_sentimen].apply(parse_sentimen)

        # Menggabungkan DataFrame baru dengan DataFrame asli
        data = pd.concat([data, data_sentimen], axis=1)

        # Menyimpan perubahan ke dalam file CSV
        data.to_csv('dataset/sentistrength_id/sentimen_somethinc_terpisah.csv', index=False)
        # Ubah DataFrame menjadi format JSON
        json_data = data.to_json(orient='records')

        return Response(json_data, mimetype='application/json')
    else:
        return jsonify({"result" : "error"})

@app.route('/api/sentistrength/somethinc/download', methods=['GET'])
def sentistrength_download_somethinc():
    if request.method == 'GET':
        return send_file('dataset/sentistrength_id/sentimen_somethinc_terpisah.csv', mimetype='text/csv', attachment_filename='sentimen_somethinc_terpisah.csv', as_attachment=True)
    
@app.route('/api/file/stopwords', methods=['GET', 'POST'])
def file_stopwords_replace():
    if request.method == 'GET':
        return send_file('dataset/preprocessing/stopwords_id.txt', mimetype='text/*', attachment_filename='stopwords_id.txt', as_attachment=True)
    elif request.method == 'POST':
        data = request.files['file']
        if data != '' or data != None:
            data.filename = 'stopwords_id.txt'
            data.save('dataset/preprocessing/'+data.filename)
            PATH['STOPWORDS'] = 'dataset/preprocessing/stopwords_id.txt'
            return jsonify({'result' : 'replace stopwords success'})
        else:
            return jsonify({'result' : 'cant replace stopwords'})
    else:
        return jsonify({'result' : 'error request'})

@app.route('/api/file/emoji', methods=['GET', 'POST'])
def file_emoji_replace():
    if request.method == 'GET':
        return send_file('dataset/preprocessing/emoji.csv', mimetype='text/csv', attachment_filename='emoji.csv', as_attachment=True)
    elif request.method == 'POST':
        data = request.files['file']
        if data != '' or data != None:
            data.filename = 'emoji.csv'
            data.save('dataset/preprocessing/'+data.filename)
            PATH['KAMUS_EMOJI'] = 'dataset/preprocessing/emoji.csv'
            return jsonify({'result' : 'replace emoji success'})
        else:
            return jsonify({'result' : 'cant replace emoji'})
    else:
        return jsonify({'result' : 'error request'})

@app.route('/api/file/emoticon', methods=['GET', 'POST'])
def file_emoticon_replace():
    if request.method == 'GET':
        return send_file('dataset/preprocessing/emoticon.json', mimetype='application/json', attachment_filename='emoticon.json', as_attachment=True)
    elif request.method == 'POST':
        data = request.files['file']
        if data != '' or data != None:
            data.filename = 'emoticon.json'
            data.save('dataset/preprocessing/'+data.filename)
            PATH['KAMUS_EMOTICON'] = 'dataset/preprocessing/emot.json'
            return jsonify({'result' : 'replace emoticon success'})
        else:
            return jsonify({'result' : 'cant replace emoticon'})
    else:
        return jsonify({'result' : 'error request'})

@app.route('/api/file/normalization', methods=['GET', 'POST'])
def file_normalization_replace():
    if request.method == 'GET':
        return send_file('dataset/preprocessing/normalisasi.csv', mimetype='text/csv', attachment_filename='normalisasi.csv', as_attachment=True)
    elif request.method == 'POST':
        data = request.files['file']
        if data != '' or data != None:
            data.filename = 'normalisasi.csv'
            data.save('dataset/preprocessing/'+data.filename)
            PATH['NORMALFILE'] = 'dataset/preprocessing/normalisasi.csv'
            return jsonify({'result' : 'replace stopwords success'})
        else:
            return jsonify({'result' : 'cant replace stopwords'})
    else:
        return jsonify({'result' : 'error request'})

@app.route('/api/count/labels/avoskin', methods=['POST'])
def api_counts_labels_avoskin():
    if request.method == 'POST':
        count = CountDF(PATH['DATASET_AVO'])
        count_result = count.count_labels(labels='kelas')
        count_json = {
            'index' : count_result.index.values.tolist(),
            'values' : count_result.values.tolist(),
            'length_df' : count.length_df(),
        }
        return jsonify(count_json)
    else:
        return jsonify({'result' : 'error'})

@app.route('/api/count/words/avoskin', methods=['POST'])
def api_counts_words_avoskin():
    if request.method == 'POST':
        df = pd.read_csv('dataset/sentistrength_id/sentimen_avoskin_terpisah.csv')
        count = CountDF('dataset/sentistrength_id/sentimen_avoskin_terpisah.csv')
        count_result = count.count_words(labels='text_string_lemma', words=10)
        count_result_positive = count.count_words_label(df['text_string_lemma'].loc[df['kelas'] == 'positif'], words=10)
        count_result_neutral = count.count_words_label(df['text_string_lemma'].loc[df['kelas'] == 'netral'], words=10)
        count_result_negative = count.count_words_label(df['text_string_lemma'].loc[df['kelas'] == 'negatif'], words=10)
        count_json = {
            'index' : list(count_result.keys()),
            'values' : list(count_result.values()),
            'length_df' : count.length_df(),
            'positive_words' : {
                'label' : list(count_result_positive.keys()),
                'value' : list(count_result_positive.values()),
            },
            'neutral_words' : {
                'label' : list(count_result_neutral.keys()),
                'value' : list(count_result_neutral.values()),
            },
            'negative_words' : {
                'label' : list(count_result_negative.keys()),
                'value' : list(count_result_negative.values()),
            }
        }
        return jsonify(count_json)
    else:
        return jsonify({'result' : 'error'})

@app.route('/api/info/avoskin', methods=['GET'])
def api_get_info_avoskin():
    if request.method == 'GET':
        arr_stop = []
        count = CountDF(PATH['DATASET_AVO'])
        #Get All Words
        get_all_words = count.count_words(labels='case_folding', words='all')
        # Get All Stopwords
        txt_stopword = pd.read_csv(PATH['STOPWORDS'], names=['stopwords_id'], header=None)
        arr_stop.append(txt_stopword['stopwords_id'][0].split(' '))
        # Get Normalization Data
        load_word = pd.read_csv(PATH['NORMALFILE'])
        return jsonify({
            'all_words' : len(get_all_words.keys()),
            'total_stopwords' : len(arr_stop[0]),
            'total_normalization' : len(load_word),
        })
    
@app.route('/api/count/labels/azarine', methods=['POST'])
def api_counts_labels_azarine():
    if request.method == 'POST':
        count = CountDF(PATH['DATASET_AZA'])
        count_result = count.count_labels(labels='kelas')
        count_json = {
            'index' : count_result.index.values.tolist(),
            'values' : count_result.values.tolist(),
            'length_df' : count.length_df(),
        }
        return jsonify(count_json)
    else:
        return jsonify({'result' : 'error'})

@app.route('/api/count/words/azarine', methods=['POST'])
def api_counts_words_azarine():
    if request.method == 'POST':
        df = pd.read_csv('dataset/sentistrength_id/sentimen_azarine_terpisah.csv')
        count = CountDF('dataset/sentistrength_id/sentimen_azarine_terpisah.csv')
        count_result = count.count_words(labels='text_string_lemma', words=10)
        count_result_positive = count.count_words_label(df['text_string_lemma'].loc[df['kelas'] == 'positif'], words=10)
        count_result_neutral = count.count_words_label(df['text_string_lemma'].loc[df['kelas'] == 'netral'], words=10)
        count_result_negative = count.count_words_label(df['text_string_lemma'].loc[df['kelas'] == 'negatif'], words=10)
        count_json = {
            'index' : list(count_result.keys()),
            'values' : list(count_result.values()),
            'length_df' : count.length_df(),
            'positive_words' : {
                'label' : list(count_result_positive.keys()),
                'value' : list(count_result_positive.values()),
            },
            'neutral_words' : {
                'label' : list(count_result_neutral.keys()),
                'value' : list(count_result_neutral.values()),
            },
            'negative_words' : {
                'label' : list(count_result_negative.keys()),
                'value' : list(count_result_negative.values()),
            }
        }
        return jsonify(count_json)
    else:
        return jsonify({'result' : 'error'})

@app.route('/api/info/azarine', methods=['GET'])
def api_get_info_azarine():
    if request.method == 'GET':
        arr_stop = []
        count = CountDF(PATH['DATASET_AZA'])
        #Get All Words
        get_all_words = count.count_words(labels='case_folding', words='all')
        # Get All Stopwords
        txt_stopword = pd.read_csv(PATH['STOPWORDS'], names=['stopwords_id'], header=None)
        arr_stop.append(txt_stopword['stopwords_id'][0].split(' '))
        # Get Normalization Data
        load_word = pd.read_csv(PATH['NORMALFILE'])
        return jsonify({
            'all_words' : len(get_all_words.keys()),
            'total_stopwords' : len(arr_stop[0]),
            'total_normalization' : len(load_word),
        })
    
@app.route('/api/count/labels/skingame', methods=['POST'])
def api_counts_labels_skingame():
    if request.method == 'POST':
        count = CountDF(PATH['DATASET_SKINGAME'])
        count_result = count.count_labels(labels='kelas')
        count_json = {
            'index' : count_result.index.values.tolist(),
            'values' : count_result.values.tolist(),
            'length_df' : count.length_df(),
        }
        return jsonify(count_json)
    else:
        return jsonify({'result' : 'error'})

@app.route('/api/count/words/skingame', methods=['POST'])
def api_counts_words_skingame():
    if request.method == 'POST':
        df = pd.read_csv('dataset/sentistrength_id/sentimen_skingame_terpisah.csv')
        count = CountDF('dataset/sentistrength_id/sentimen_skingame_terpisah.csv')
        count_result = count.count_words(labels='text_string_lemma', words=10)
        count_result_positive = count.count_words_label(df['text_string_lemma'].loc[df['kelas'] == 'positif'], words=10)
        count_result_neutral = count.count_words_label(df['text_string_lemma'].loc[df['kelas'] == 'netral'], words=10)
        count_result_negative = count.count_words_label(df['text_string_lemma'].loc[df['kelas'] == 'negatif'], words=10)
        count_json = {
            'index' : list(count_result.keys()),
            'values' : list(count_result.values()),
            'length_df' : count.length_df(),
            'positive_words' : {
                'label' : list(count_result_positive.keys()),
                'value' : list(count_result_positive.values()),
            },
            'neutral_words' : {
                'label' : list(count_result_neutral.keys()),
                'value' : list(count_result_neutral.values()),
            },
            'negative_words' : {
                'label' : list(count_result_negative.keys()),
                'value' : list(count_result_negative.values()),
            }
        }
        return jsonify(count_json)
    else:
        return jsonify({'result' : 'error'})

@app.route('/api/info/skingame', methods=['GET'])
def api_get_info_skingame():
    if request.method == 'GET':
        arr_stop = []
        count = CountDF(PATH['DATASET_SKINGAME'])
        #Get All Words
        get_all_words = count.count_words(labels='case_folding', words='all')
        # Get All Stopwords
        txt_stopword = pd.read_csv(PATH['STOPWORDS'], names=['stopwords_id'], header=None)
        arr_stop.append(txt_stopword['stopwords_id'][0].split(' '))
        # Get Normalization Data
        load_word = pd.read_csv(PATH['NORMALFILE'])
        return jsonify({
            'all_words' : len(get_all_words.keys()),
            'total_stopwords' : len(arr_stop[0]),
            'total_normalization' : len(load_word),
        })
    
@app.route('/api/count/labels/somethinc', methods=['POST'])
def api_counts_labels_somethinc():
    if request.method == 'POST':
        count = CountDF(PATH['DATASET_SOMETHINC'])
        count_result = count.count_labels(labels='kelas')
        count_json = {
            'index' : count_result.index.values.tolist(),
            'values' : count_result.values.tolist(),
            'length_df' : count.length_df(),
        }
        return jsonify(count_json)
    else:
        return jsonify({'result' : 'error'})

@app.route('/api/count/words/somethinc', methods=['POST'])
def api_counts_words_somethinc():
    if request.method == 'POST':
        df = pd.read_csv('dataset/sentistrength_id/sentimen_somethinc_terpisah.csv')
        count = CountDF('dataset/sentistrength_id/sentimen_somethinc_terpisah.csv')
        count_result = count.count_words(labels='text_string_lemma', words=10)
        count_result_positive = count.count_words_label(df['text_string_lemma'].loc[df['kelas'] == 'positif'], words=10)
        count_result_neutral = count.count_words_label(df['text_string_lemma'].loc[df['kelas'] == 'netral'], words=10)
        count_result_negative = count.count_words_label(df['text_string_lemma'].loc[df['kelas'] == 'negatif'], words=10)
        count_json = {
            'index' : list(count_result.keys()),
            'values' : list(count_result.values()),
            'length_df' : count.length_df(),
            'positive_words' : {
                'label' : list(count_result_positive.keys()),
                'value' : list(count_result_positive.values()),
            },
            'neutral_words' : {
                'label' : list(count_result_neutral.keys()),
                'value' : list(count_result_neutral.values()),
            },
            'negative_words' : {
                'label' : list(count_result_negative.keys()),
                'value' : list(count_result_negative.values()),
            }
        }
        return jsonify(count_json)
    else:
        return jsonify({'result' : 'error'})

@app.route('/api/info/somethinc', methods=['GET'])
def api_get_info_somethinc():
    if request.method == 'GET':
        arr_stop = []
        count = CountDF(PATH['DATASET_SOMETHINC'])
        #Get All Words
        get_all_words = count.count_words(labels='case_folding', words='all')
        # Get All Stopwords
        txt_stopword = pd.read_csv(PATH['STOPWORDS'], names=['stopwords_id'], header=None)
        arr_stop.append(txt_stopword['stopwords_id'][0].split(' '))
        # Get Normalization Data
        load_word = pd.read_csv(PATH['NORMALFILE'])
        return jsonify({
            'all_words' : len(get_all_words.keys()),
            'total_stopwords' : len(arr_stop[0]),
            'total_normalization' : len(load_word),
        })

@app.route('/api/file/', methods=['GET'])
def api_file_manager_get():
    get_size = []
    folder_file = 'pretrained'
    for file_data in os.listdir(folder_file):
        file_stat = os.stat(folder_file + file_data)
        size = file_stat.st_size / (1024 * 1024)
        get_size.append(round(size, 2))
    return jsonify({
        'list_files' : os.listdir(folder_file),
        'list_files_size' : get_size,
        'total_size_file' : sum(get_size),
        'total_file' : len(os.listdir(folder_file)),
    })

@app.route('/api/file/merge', methods=['POST', 'GET'])
def api_file_merge():
    if request.method == 'POST' and 'file' in request.files:
        file_upload = request.files['file']
        if file_upload != '' or file_upload != None:
            file_upload.save(os.path.join('dataset/dataframe', file_upload.filename))
            if len(glob.glob('dataset/dataframe/*.csv')) != 0:
                all_filenames = [i for i in glob.glob('dataset/dataframe/*.csv')]
                combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
                combined_csv.to_csv("dataset/dataframe/df.csv", index=False, encoding='utf-8-sig')
                return jsonify({'result' : 'upload and merge success'})
            else:
                return jsonify({'result' : 'no file'})
        else:
            return jsonify({'status' : 'error'})
    elif request.method == 'POST' and 'file' not in request.files:
        data = request.get_json()
        if data['command'] == 'reset':
            for file_name in glob.glob('dataset/dataframe/*.csv'):
                os.remove(file_name)
            copyfile('dataset/dataframe/backup/df.csv', 'dataset/dataframe/df.csv')
            return jsonify({'result' : 'reset success'})
        else:
            return jsonify({'result' : 'fail to reset or split'})
    else:
        return jsonify({'result' : 'error'})
    
@app.route('/api/model/info', methods=['GET'])
def api_model_info():
    file_json = open('info/data.json', 'r')
    data = json.load(file_json)
    file_json.close()
    return data

@app.route('/api/model/train', methods=['POST'])
def api_model_train():
    if request.method == 'POST':
        start_time = time.time()
        df_csv = pd.read_csv('dataset/dataframe/df.csv')
        full_text_pre = TextPreprocessingAvo(df_csv['text'], df_csv['sentiment'], PATH)
        result = full_text_pre.output(export=True)
        tfidf_train = Vectorize(result['text_string_stemmed'])
        tfidf_train.export()
        text_feature = tfidf_train.get_transform()
        text_feature_label = result['label']
        X_train, X_test, y_train, y_test = train_test_split(text_feature, text_feature_label, random_state=1, test_size=0.2)
        model = Model(X_train, X_test, y_train, y_test)
        model.export()
        time_result = round((time.time() - start_time)/60,2)
        return jsonify({
            'status' : 'Export Model and TFIDF Success',
            'training_time' : time_result,
        })
    else:
        return jsonify({'status' : 'error request'})

if __name__ == '__main__':
    app.run(debug=True, port=33507)
#-- Web Based End --#
