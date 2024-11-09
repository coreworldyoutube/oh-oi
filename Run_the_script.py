import os

def main():
    # 環境変数からモードを取得する
    mode = os.getenv("MODE", "editor").strip()  # デフォルトを 'editor' に設定

    elements_data, descriptions_data = load_data()

    if mode == 'editor':
        editor_mode(elements_data, descriptions_data)
    elif mode == 'search':
        search_mode(elements_data, descriptions_data)
    else:
        print("無効なモードが選ばれました。")

if __name__ == "__main__":
    main()
