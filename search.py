from flask import Flask, render_template, request
import json
import requests

app = Flask(__name__)

# Wikipedia APIを使って情報を取得する関数
def get_wikipedia_data(search_query):
    url = f"https://ja.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": search_query,
        "prop": "extracts",
        "exintro": True,  # 初めの部分を取得
        "explaintext": True  # プレーンテキストとして取得
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        pages = data["query"]["pages"]

        for page_id, page in pages.items():
            if "extract" in page:
                return page["extract"]
            else:
                return "情報が見つかりませんでした。"
    else:
        return "Wikipedia APIへのリクエストに失敗しました。"

# データを読み込む関数
def load_data():
    try:
        with open('elements.json', 'r', encoding='utf-8') as elem_file:
            elements_data = json.load(elem_file)
    except FileNotFoundError:
        elements_data = {}

    try:
        with open('descriptions.json', 'r', encoding='utf-8') as desc_file:
            descriptions_data = json.load(desc_file)
    except FileNotFoundError:
        descriptions_data = {}

    return elements_data, descriptions_data

# 検索モードでデータを検索する関数
def search_data(search_query, elements_data, descriptions_data):
    results = []

    # 検索対象データ（elements.json）の中から部分一致を探す
    for key in elements_data:
        match_score = sum(1 for char in search_query if char in key)

        if match_score > 0:
            results.append((key, elements_data[key], match_score))

    # Wikipediaからデータを取得して説明を追加
    wiki_description = get_wikipedia_data(search_query)

    return results, wiki_description

@app.route("/", methods=["GET", "POST"])
def home():
    elements_data, descriptions_data = load_data()
    results = []
    wiki_description = ""
    
    if request.method == "POST":
        search_query = request.form["search_query"]
        results, wiki_description = search_data(search_query, elements_data, descriptions_data)

    return render_template("index.html", results=results, wiki_description=wiki_description)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)  # ポート番号を5001に変更
