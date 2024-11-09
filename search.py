import json
import requests
import sys

# 要素データと説明データを読み込む関数
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

# エディターモードでデータを編集・追加する関数
def editor_mode(elements_data, descriptions_data):
    print("エディターモードです。データを入力してください。")
    num_entries = int(input("何件のデータを入力しますか？: "))

    for _ in range(num_entries):
        search_key = input("検索ワードを入力してください（例: 鉄, 金属）: ")
        hit_point = int(input(f"『{search_key}』のヒットポイントを入力してください（例: 1）: "))
        elements_data[search_key] = hit_point

        description = input(f"『{search_key}』の説明を入力してください: ")
        descriptions_data[search_key] = description

    # 入力されたデータをファイルに保存
    with open('elements.json', 'w', encoding='utf-8') as elem_file:
        json.dump(elements_data, elem_file, ensure_ascii=False, indent=4)

    with open('descriptions.json', 'w', encoding='utf-8') as desc_file:
        json.dump(descriptions_data, desc_file, ensure_ascii=False, indent=4)

    print("データが保存されました。")

# 検索モードでデータを検索する関数
def search_mode(elements_data, descriptions_data):
    search_query = input("検索したいワードを入力してください: ")
    results = []

    # 検索対象データ（elements.json）の中から部分一致を探す
    for key in elements_data:
        match_score = sum(1 for char in search_query if char in key)

        if match_score > 0:
            results.append((key, elements_data[key], match_score))

    # ヒットしたデータを表示
    if results:
        results.sort(key=lambda x: x[2], reverse=True)

        print(f"\n検索結果: {len(results)}件が見つかりました。")
        for i, result in enumerate(results, 1):
            key = result[0]
            hit_point = result[1]
            match_score = result[2]
            print(f"\n{str(i)}. 検索ワード: {key}\nヒットポイント: {hit_point}（マッチ数: {match_score}）")
            print(f"説明: {descriptions_data.get(key, '説明はありません。')}")

        # Wikipediaからデータを取得して説明を追加
        wiki_description = get_wikipedia_data(search_query)
        print(f"\nWikipediaからの説明: {wiki_description}")

        # ユーザーに再編集または戻るを選択させる
        action = input("\n再編集するには番号を入力、戻るには 'b' を入力してください: ").strip()

        if action == 'b':
            print("戻ります。")
            return
        else:
            try:
                selected_index = int(action) - 1
                if 0 <= selected_index < len(results):
                    selected_key = results[selected_index][0]
                    print(f"『{selected_key}』の再編集を行います。")
                    edit_entry(selected_key, elements_data, descriptions_data)
                else:
                    print("無効な番号が選ばれました。")
            except ValueError:
                print("無効な入力です。")
    else:
        print("検索結果はありませんでした。")

# 再編集モードでデータを編集する関数
def edit_entry(selected_key, elements_data, descriptions_data):
    print(f"『{selected_key}』の再編集を行います。")

    new_hit_point = int(input(f"現在のヒットポイント: {elements_data[selected_key]}. 新しいヒットポイントを入力してください: "))
    elements_data[selected_key] = new_hit_point

    new_description = input(f"現在の説明: {descriptions_data.get(selected_key, '説明はありません。')} 新しい説明を入力してください: ")
    descriptions_data[selected_key] = new_description

    with open('elements.json', 'w', encoding='utf-8') as elem_file:
        json.dump(elements_data, elem_file, ensure_ascii=False, indent=4)

    with open('descriptions.json', 'w', encoding='utf-8') as desc_file:
        json.dump(descriptions_data, desc_file, ensure_ascii=False, indent=4)

    print("データが再編集されました。")

# メインのプログラム
def main():
    # コマンドライン引数でモードを決定
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = "editor"  # デフォルトは "editor" モード

    elements_data, descriptions_data = load_data()

    if mode == 'editor':
        editor_mode(elements_data, descriptions_data)
    elif mode == 'search':
        search_mode(elements_data, descriptions_data)
    else:
        print("無効なモードが選ばれました。")

# 実行
if __name__ == "__main__":
    main()
