from flask import Flask, jsonify, abort,render_template_string
from elasticsearch import Elasticsearch
import time
app = Flask(__name__)


def check_elasticsearch_connection():
    es = Elasticsearch("http://elasticsearch:9200")
    return es.ping()


while not check_elasticsearch_connection():
    print("Connessione a ElasticSearch in corso...")
    time.sleep(3)  # Attendi 3 secondi prima di verificare nuovamente la connessione


es = Elasticsearch("http://elasticsearch:9200")



@app.route('/getimage/<id>', methods=['GET'])
def get_image(id):
    try:
        # Recupera il documento da Elasticsearch
        res = es.get(index="movements", id=id)
        source = res['_source']
        # return jsonify(source)
        # Verifica se i campi base64 esistono
        base641 = source.get('image')
        base642 = source.get('image2')
        
        if not base641 or not base642:
            abort(404, description="Immagini non trovate nel documento")
        
        # Template HTML
        html_content = """
        <!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Galleria Immagini</title>
    <style>
        body {
            margin: 0;
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f4;
        }
        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            gap: 20px;
        }
        .image {
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            transition: 0.3s;
            width: 40%; /* Adjusted width */
            border-radius: 5px; /* Added border radius */
        }
        .image:hover {
            box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
        }
        img {
            width: 100%;
            height: auto;
            border-radius: 5px; /* Added border radius */
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="image">
            <img src="data:image/png;base64,{{ base641 }}" alt="Immagine 1">
        </div>
        <div class="image">
            <img src="data:image/png;base64,{{ base642 }}" alt="Immagine 2">
        </div>
    </div>
</body>
</html>

        """
        
        # Renderizza il template con le immagini base64
        return render_template_string(html_content, base641=base641, base642=base642)
    
    except Exception as e:
        # Gestisce il caso in cui il documento non esista o ci sia un errore
        print(f"Errore: {e}")
        abort(404, description=e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)