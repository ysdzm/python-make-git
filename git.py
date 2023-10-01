import sys
import hashlib
import zlib
import os

def main():
    args = sys.argv

    # 引数がないなら
    if len(args) <= 1:
        print("引数がありません")
        return
    
    command = args[1]

    if command == "hash-object":
        # print("hash-object!")
        hash_object(args[2])


def hash_object(file_path):
    # データの中身を取得
    data = read_file(file_path)
    # ヘッダーの用意
    obj_type = "blob"
    header = f"{obj_type} {len(data)}\0".encode()
    # ヘッダーとデータを合わせる
    full_data = header + data.encode()
    # SHA-1ハッシュを計算
    sha1_hash = hashlib.sha1(full_data).hexdigest()
    # zlibで圧縮
    compressed_data = zlib.compress(full_data, level=1)

    # print(sha1_hash)
    # print(bytes.hex(compressed_data))
    # print(sha1_hash[:2])
    # print(sha1_hash[2:])

    make_directory(".git/objects/"+sha1_hash[:2])
    write_file(".git/objects/"+sha1_hash[:2]+"/"+sha1_hash[2:],compressed_data)

# ファイル読み込み
def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_contents = file.read()
            return file_contents
    except FileNotFoundError:
        print(f"ファイル '{file_path}' が見つかりませんでした。")
    except Exception as e:
        print(f"ファイルの読み取り中にエラーが発生しました: {str(e)}")

# ファイル書き込み
def write_file(file_path,data_to_save):
    try:
        with open(file_path, "wb") as file:
            file.write(data_to_save)
        print(f"ファイル '{file_path}' が上書き保存されました。")
    except Exception as e:
        print(f"ファイルの保存中にエラーが発生しました: {str(e)}")

# ディレクトリ作成
def make_directory(directory_path):
    try:
        os.makedirs(directory_path)
        print(f"ディレクトリ '{directory_path}' が作成されました。")
    except FileExistsError:
        print(f"ディレクトリ '{directory_path}' は既に存在します。")
    except Exception as e:
        print(f"ディレクトリの作成中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()