import sys
import hashlib
import zlib
import os
import datetime
import stat

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
    
    if command == "update-index":
        update_index(0,args[2],args[3])
        # print("update-index!")

    if command == "mode":
        st_mode(args[2])
    
    if command == "meta-data":
        meta_data(args[2])


# $ git hash-object -w <file-name>
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
    
    return sha1_hash

# $ git update-index --add --cacheinfo <モード>,<sha1>,<パス>
def update_index(mode,sha1,path):
    # print("hoge")

    # ヘッダー（12byte）
    # エントリー（可変）
    # sha-1チェックサム（20byte）

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
        # print(f'ctime:{ctime}')
        entrie += bytes.fromhex(format(ctime, '08x'))

        # ctime nano sec
        ctime_nsec = int(metadata.st_ctime_ns % 1000000000)
        # print(f'ctime_nsec:{ctime_nsec}')
        entrie += bytes.fromhex(format(ctime_nsec, '08x'))

        # mtime sex
        mtime = int(metadata.st_mtime)
        # print(f'mtime:{mtime}')
        entrie += bytes.fromhex(format(mtime, '08x'))

        # mtime nano sec
        mtime_nsec = int(metadata.st_mtime_ns % 1000000000)
        # print(f'mtime_nsec:{mtime_nsec}')
        entrie += bytes.fromhex(format(mtime_nsec, '08x'))

        # dev
        dev = 0
        # print(f'dev:{dev}')
        entrie += bytes.fromhex(format(dev, '08x'))

        # inode
        inode = 0
        # print(f'inode:{inode}')
        entrie += bytes.fromhex(format(inode, '08x'))

        # mode
        # object_type = "10" if os.path.isfile(path) else "12"
        object_type = "0"
        unix_permission = str(int("111755" if metadata.st_mode & os.X_OK else "100644",8))
        mode = bytes.fromhex(format(int(object_type + unix_permission), '08x'))
        # print(f'mode:{mode}')
        entrie += mode

        # uid
        uid = int(metadata.st_uid)
        # print(f'uid:{uid}')
        entrie += bytes.fromhex(format(uid, '08x'))

        # gid
        gid = int(metadata.st_gid)
        # print(f'gid:{gid}')
        entrie += bytes.fromhex(format(gid, '08x'))
        
        # filesize
        filesize = int(metadata.st_size)
        # print(f'filesize:{filesize}')
        entrie += bytes.fromhex(format(filesize, '08x'))

        # SHA-1
        entrie += bytes.fromhex(sha1)

        # flag
        assumeValid = 0b0  # 1または0、デフォルトは0
        extendedFlag = 0b0  # 1または0、デフォルトは0
        optionalFlag = (((0b0 | assumeValid) << 1) | extendedFlag) << 14
        flagRes = optionalFlag | len(path)
       #  print(flagRes)
        entrie += bytes.fromhex(format(flagRes, '04x'))

        # filename
        # print(path.encode("utf-8"))
        entrie += path.encode("utf-8")

        # padding
        paddingCount = 8 - (len(entrie) % 8)
        padding = bytes([0] * paddingCount)
        # print(paddingCount)
        # print(padding)

        entrie += padding

    except FileNotFoundError:
        print(f'{file} は存在しません。')
    except Exception as e:
        print(f'メタデータの取得中にエラーが発生しました: {str(e)}')

    # sha-1チェックサム

    sha1_hash = hashlib.sha1(header+entrie).hexdigest()
    sha1_check_sum = bytes.fromhex(sha1_hash)

    with open("output", "wb") as file:
        file.write(header + entrie + sha1_check_sum)


def add(files):
    for file_path in files:
        # $ git hash-object -w <file-name>
        sha1 = hash_object(file_path)
        # $ git update-index --add --cacheinfo <モード>,<sha1>,<パス>
        # modeいらない？
        update_index(sha1,file_path)

def st_mode(file_path):
    file_info = os.stat(file_path)
    # ファイルのモード情報を取得
    file_mode = file_info.st_mode
    # モード情報を8進数で表示
    octal_mode = oct(file_mode & 0o777)
    print(file_mode)

def meta_data(file_path):

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