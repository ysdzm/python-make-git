from docopt import docopt
import hashlib
import zlib
import os

__VERSION__ = '1.0'

__DOC__ = """
Usage: 
    git hello
    git add [<pathspec>...]
    git commit [-m <msg>]
    git hash-object [-w] <file>...
    git update-index
    git write-tree
    git commit-tree
    git update-ref

Options:
    -m <msg>    Use the given <msg> as the commit message when using 'git commit'
    --version   Show version information
    -h, --help  Show this help message and exit
"""

def main():
    args = docopt(__DOC__, version=__VERSION__)

    if args["hello"]:
        hello()
    
    if args["hash-object"]:
        hash_object(args["<file>"],args["-w"])

def hello():
    print("hello")

def hash_object(file_list,w):
    sha1_hash_list = []
    for file in file_list:
        # データの中身を取得
        data = read_file(file)
        # ヘッダーの用意
        header = f"blob {len(data)}\0".encode()
        # ヘッダーとデータを合わせる
        full_data = header + data.encode()
        # SHA-1ハッシュを計算
        sha1_hash = hashlib.sha1(full_data).hexdigest()
        print(sha1_hash)
        if w:
            # zlibで圧縮
            compressed_data = zlib.compress(full_data, level=1)
            # ディレクトリ作成
            make_directory(".git/objects/"+sha1_hash[:2])
            # ファイル保存
            write_file(".git/objects/"+sha1_hash[:2]+"/"+sha1_hash[2:],compressed_data)
        # 返り値リストに追加
        sha1_hash_list.append(sha1_hash)
    return sha1_hash

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

# バイナリファイル読み込み
def read_file_b(file_path):
    try:
        with open(file_path, "rb") as file:
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
        # print(f"ファイル '{file_path}' が上書き保存されました。")
    except Exception as e:
        print(f"ファイルの保存中にエラーが発生しました: {str(e)}")

# ディレクトリ作成
def make_directory(directory_path):
    try:
        os.makedirs(directory_path, exist_ok=True)
        # print(f"ディレクトリ '{directory_path}' が作成されました。")
    except Exception as e:
        print(f"ディレクトリの作成中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()
