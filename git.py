import sys
import hashlib
import zlib
import os
import time
import stat
import configparser
import os

def main():
    args = sys.argv

    # 引数がないなら
    if len(args) <= 1:
        print("引数がありません")
        return
    
    command = args[1]

    if command == "hash-object":
        hash_object(args[2])
    
    if command == "update-index":
        update_index(0,args[2],args[3])

    if command == "mode":
        st_mode(args[2])
    
    if command == "meta-data":
        meta_data(args[2])

    if command == "write-tree":
        write_tree()

    if command == "ls-files":
        ls_files()
    
    if command == "commit-tree":
        commit_tree("first commit","161e899ffc6e06b5a8f94b77c99312c30deb9452")

    if command == "author":
        get_author()
    
    if command == "add":
        add(args[2])

    if command == "commit":
        commit(args[2])

    if command == "read-file":
        # parent_sha1 = read_file(".git/refs/heads/main")
        read_file("hello.txt")

# $ git hash-object -w <file-name>
def hash_object(file_path):
    # データの中身を取得
    data = read_file(file_path)
    # ヘッダーの用意
    header = f"blob {len(data)}\0".encode()
    # ヘッダーとデータを合わせる
    full_data = header + data.encode()
    # SHA-1ハッシュを計算
    sha1_hash = hashlib.sha1(full_data).hexdigest()
    # zlibで圧縮
    compressed_data = zlib.compress(full_data, level=1)
    # ディレクトリ作成
    make_directory(".git/objects/"+sha1_hash[:2])
    # ファイル保存
    write_file(".git/objects/"+sha1_hash[:2]+"/"+sha1_hash[2:],compressed_data)
    return sha1_hash

# $ git update-index --add --cacheinfo <モード>,<sha1>,<パス>
def update_index(mode,sha1,path):
    # ヘッダー
    DIRC = bytes.fromhex("44 49 52 43")
    version = bytes.fromhex(format(2, '08x'))
    entries = bytes.fromhex(format(1, '08x'))
    header = DIRC + version + entries
    # エントリー
    entrie = b''
    try:
        metadata = os.stat(path)
        # ctime sec
        ctime = int(metadata.st_ctime)
        entrie += bytes.fromhex(format(ctime, '08x'))
        # ctime nano sec
        ctime_nsec = int(metadata.st_ctime_ns % 1000000000)
        entrie += bytes.fromhex(format(ctime_nsec, '08x'))
        # mtime sec
        mtime = int(metadata.st_mtime)
        entrie += bytes.fromhex(format(mtime, '08x'))
        # mtime nano sec
        mtime_nsec = int(metadata.st_mtime_ns % 1000000000)
        entrie += bytes.fromhex(format(mtime_nsec, '08x'))
        # dev
        dev = 0
        entrie += bytes.fromhex(format(dev, '08x'))
        # inode
        inode = 0
        entrie += bytes.fromhex(format(inode, '08x'))
        # mode
        # object_type = "10" if os.path.isfile(path) else "12"
        object_type = "0"
        unix_permission = str(int("111755" if metadata.st_mode & os.X_OK else "100644",8))
        mode = bytes.fromhex(format(int(object_type + unix_permission), '08x'))
        entrie += mode
        # uid
        uid = int(metadata.st_uid)
        entrie += bytes.fromhex(format(uid, '08x'))
        # gid
        gid = int(metadata.st_gid)
        entrie += bytes.fromhex(format(gid, '08x'))
        # filesize
        filesize = int(metadata.st_size)
        entrie += bytes.fromhex(format(filesize, '08x'))
        # SHA-1
        entrie += bytes.fromhex(sha1)
        # flag
        assumeValid = 0b0  # 1または0、デフォルトは0
        extendedFlag = 0b0  # 1または0、デフォルトは0
        optionalFlag = (((0b0 | assumeValid) << 1) | extendedFlag) << 14
        flagRes = optionalFlag | len(path)
        entrie += bytes.fromhex(format(flagRes, '04x'))
        # filename
        entrie += path.encode("utf-8")
        # padding
        paddingCount = 8 - (len(entrie) % 8)
        padding = bytes([0] * paddingCount)
        entrie += padding
    except FileNotFoundError:
        print(f'{file} は存在しません。')
    except Exception as e:
        print(f'メタデータの取得中にエラーが発生しました: {str(e)}')

    # sha-1チェックサム
    sha1_hash = hashlib.sha1(header+entrie).hexdigest()
    sha1_check_sum = bytes.fromhex(sha1_hash)

    full_data = header + entrie + sha1_check_sum
    # zlibで圧縮
    compressed_data = zlib.compress(full_data, level=1)
    # ファイル保存
    write_file(".git/index",full_data)

# $ git ls-files -s
def ls_files():
    # indexファイルの読み取り
    index = read_file_b(".git/index")
    # ヘッダーの読みより
    header = index[:12]
    # エントリの読み取り
    entries = int.from_bytes(header[9:12],byteorder='big')
    file_list = []  # 返り値用リスト
    top = 12
    for i in range(entries):
        content = index[top:top+62]
        flag = content[60:62]
        namelen = int.from_bytes(flag, byteorder='big') & 0xFFF
        # mode, sha1, name を抜き出し & 算出
        mode = oct(int(content[24:28].hex(),16))
        sha1 = "".join('{:02x}'.format(byte) for byte in content[40:60])
        name = index[top+62:top+62+namelen].decode('utf-8')
        # print(f"{mode} {sha1} {name}")
        # paddingを算出
        padding = calc_padding(namelen)
        top += 62 + namelen + padding
        # リストに追加
        file_list.append((mode,sha1,name))
    return file_list

# $ git write-tree
def write_tree():
    # .git/indexの読み取り
    file_list = ls_files()

    # 今回は1ファイルのみを対象にする
    file_info = file_list[0]

    # treeオブジェクトの中身
    mode, sha1, name = file_info
    hash = bytes.fromhex(sha1)
    content = f'{mode[2:]} {name}\0'.encode('utf-8') + hash
    header = f'tree {len(content)}\0'.encode('utf-8')
    store = header + content
    # print(" ".join('{:02x}'.format(byte) for byte in store))
    # SHA-1ハッシュ
    sha1_hash = hashlib.sha1(store).hexdigest()  
    # zlibで圧縮
    compressed_data = zlib.compress(store, level=1)  
    # ディレクトリ作成
    make_directory(".git/objects/"+sha1_hash[:2])
    # ファイル保存
    write_file(".git/objects/"+sha1_hash[:2]+"/"+sha1_hash[2:],compressed_data)

    return sha1_hash

# $ git commit-tree -m <message> <hash>
def commit_tree(message,hash):
    tree_sha1 = hash
    commit_message = message
    # unixタイム
    commit_time = int(time.time())
    # 著者情報の取得
    user_name,user_email = get_author()
    commit_author = f"{user_name} <{user_email}>"
    # 親コミットの取得
    parent_sha1 = read_file(".git/refs/heads/main")
    parent = "" if parent_sha1 is None else f"parent {parent_sha1}\n"
    # commitオブジェクトの中身
    content = f"tree {tree_sha1}\n" \
          f"{parent}" \
          f"author {commit_author} {commit_time} +0900\n" \
          f"committer {commit_author} {commit_time} +0900\n\n" \
          f"{commit_message}\n"
    header = f"commit {len(content)}\0"
    store = header + content
    # SHA-1ハッシュ
    shasum = hashlib.sha1()
    shasum.update(store.encode('utf-8'))
    sha1_hash = shasum.hexdigest()
    # zlibで圧縮
    compressed_data = zlib.compress(store.encode(), level=1)
    # ディレクトリ作成
    make_directory(".git/objects/"+sha1_hash[:2])
    # ファイル保存
    write_file(".git/objects/"+sha1_hash[:2]+"/"+sha1_hash[2:],compressed_data)
    # HEAD更新
    write_file(".git/refs/heads/main",sha1_hash.encode())

def add(file_path):
    # $ git hash-object -w <file-name>
    # blobオブジェクトの作成と、作成したオブジェクトの参照(SHA-1ハッシュ)を取得
    sha1 = hash_object(file_path)
    # $ git update-index
    # indexファイル(ステージングエリア)の更新
    update_index(calc_mode(file_path),sha1,file_path)

def commit(message):
    # $ git write-tree 
    # index(ステージングエリア)をもとにtreeオブジェクトを作成し、作成したオブジェクトの参照(SHA-1ハッシュ)を取得
    sha1 = write_tree()
    # $ git commit-tree -m <message> <hash>
    # コミットメッセージを添えてコミット
    commit_tree(message,sha1)

def st_mode(file_path):
    # デバッグ用
    file_info = os.stat(file_path)
    # ファイルのモード情報を取得
    file_mode = file_info.st_mode
    # モード情報を8進数で表示
    octal_mode = oct(file_mode & 0o777)
    print(file_mode)

def meta_data(file_path):
    # デバッグ用
    try:
        # ファイルのメタデータ情報を取得
        metadata = os.stat(file_path)
        # ファイルの作成時刻とナノ秒単位の時刻を取得
        ctime = int(metadata.st_ctime)
        ctime_nsec = int(metadata.st_ctime_ns)
        # ファイルの最終変更時刻とナノ秒単位の時刻を取得
        mtime = int(metadata.st_mtime)
        mtime_nsec = int(metadata.st_mtime_ns)
        # ファイルのデバイスIDを取得
        dev = int(metadata.st_dev)
        # ファイルのiノード番号を取得
        ino = int(metadata.st_ino)
        # ファイルのモード（パーミッション）を取得
        mode = int(metadata.st_mode)
        # ファイルの所有者のユーザーIDを取得
        uid = int(metadata.st_uid)
        # ファイルの所有者のグループIDを取得
        gid = int(metadata.st_gid)
        # ファイルサイズを取得
        filesize = int(metadata.st_size)
        print(f'ctime: {ctime}')
        # print( datetime.datetime.fromtimestamp(metadata.st_ctime))
        print(f'ctime_nsec: {ctime_nsec}')
        print(f'mtime: {mtime}')
        print(f'mtime_nsec: {mtime_nsec}')
        print(f'atime: {metadata.st_atime}')
        print(f'atime_nsec: {metadata.st_atime_ns}')
        print(f'dev: {dev}')
        print(f'ino: {ino}')
        print(f'mode: {oct(mode)}')
        print(f'uid: {uid}')
        print(f'gid: {gid}')
        print(f'filesize: {filesize}')
        print(oct(stat.S_IMODE(metadata.st_mode)))

        # 取得したメタデータ情報を使用して作業を続けることができます
    except FileNotFoundError:
        print(f'{file_path} は存在しません。')
    except Exception as e:
        print(f'メタデータの取得中にエラーが発生しました: {str(e)}')

def calc_padding(n):
    floor = (n - 2) // 8
    target = (floor + 1) * 8 + 2
    ret = target - n
    return ret

def calc_mode(path):
    metadata = os.stat(path)
    mode = "111755" if metadata.st_mode & os.X_OK else "100644"
    return mode

def get_author():
    # ユーザーのホームディレクトリを取得
    home_directory = os.path.expanduser("~")
    # Gitのグローバル設定ファイルのパス
    gitconfig_path = os.path.join(home_directory, ".gitconfig")
    # .gitconfigファイルを読み込む
    config = configparser.ConfigParser()
    config.read(gitconfig_path)
    # Author情報を取得
    user_name = config.get('user', 'name', fallback=None)
    user_email = config.get('user', 'email', fallback=None)
    return (user_name,user_email)

# ファイル読み込み
def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_contents = file.read()
            return file_contents
    except FileNotFoundError:
        # print(f"ファイル '{file_path}' が見つかりませんでした。")
        print()
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
        os.makedirs(directory_path)
        # print(f"ディレクトリ '{directory_path}' が作成されました。")
    except FileExistsError:
        print(f"ディレクトリ '{directory_path}' は既に存在します。")
    except Exception as e:
        print(f"ディレクトリの作成中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()