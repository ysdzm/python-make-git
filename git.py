from docopt import docopt
import hashlib
import zlib
import os
import sys
import pprint

__VERSION__ = '1.0'

__DOC__ = """
Usage: 
    git hello
    git add [<pathspec>...]
    git commit [-m <msg>]
    git hash-object [-w] <file>...
    git update-index [(--cacheinfo <mode> <object> <file>)...]
    git write-tree
    git commit-tree
    git update-ref
    git ls-files [-s]

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
    
    if args["ls-files"]:
        value = ls_files(args["-s"])
        pprint.pprint(value, width=100)
    
    if args["update-index"]:
        update_index(args["--cacheinfo"],args["<mode>"],args["<object>"],args["<file>"])

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
        if w:
            # zlibで圧縮
            compressed_data = zlib.compress(full_data, level=1)
            # ディレクトリ作成
            make_directory(".git/objects/"+sha1_hash[:2])
            # ファイル保存
            write_file(".git/objects/"+sha1_hash[:2]+"/"+sha1_hash[2:],compressed_data)
        # 返り値リストに追加
        sha1_hash_list.append(sha1_hash)
    print('\n'.join(sha1_hash_list))
    return sha1_hash_list

# $ git ls-files -s
def ls_files(s):
    # indexファイルの読み取り
    index = read_file_b(".git/index2")
    
    # ヘッダー
    header = index[:12]
    # エントリ数（ヘッダーの後ろ4*8bit）
    entries = int.from_bytes(header[9:12],byteorder='big')
    print(entries)

    # 返り値用リスト
    file_list = [] 
    cur = 12
    for i in range(entries):

        # エントリの固定長部分（62*8bit）
        content = index[cur:cur+62]
        # flag
        flag = content[60:62]
        # ファイル名の長さ（flgの後ろ12bit）
        namelen = int.from_bytes(flag, byteorder='big') & 0xFFF

        # mode, sha1, name を抜き出し & 算出
        mode = oct(int(content[24:28].hex(),16))
        sha1 = "".join('{:02x}'.format(byte) for byte in content[40:60])
        name = index[cur+62:cur+62+namelen].decode('utf-8')

        # リストに追加
        if s:
            file_list.append((mode,sha1,name))
        else:
            file_list.append((name))

        # paddingを算出
        padding = calc_padding(namelen)
        cur += 62 + namelen + padding

    return file_list

def calc_padding(namelen):
    floor = (namelen - 2) // 8
    target = (floor + 1) * 8 + 2
    ret = target - namelen
    return ret

def update_index(cacheinfo,mode,object,file):

    # indexが存在しない場合、空のindexを作成する
    if not os.path.exists(".git/index2"):
        # DIRC, version, entries
        header = bytes.fromhex("44 49 52 43") + bytes.fromhex(format(2, '08x')) + bytes.fromhex(format(0, '08x'))
        write_file(".git/index2",header)

    # indexを読み取り
    list = ls_files(s = True)

    entries = b''
    entries_count = 0

    # --cacheinfo
    if cacheinfo:
        for i in range(len(list)):
            print(i)
            entrie = index_entry(list[i][0],list[i][1],list[i][2])
            entries += entrie
            entries_count += 1
        for i in range(len(mode)):
            print(i)
            entrie = index_entry(mode[i],object[i],file[i])
            entries += entrie
            entries_count += 1

    # 再構築

    print(entries_count)

    # DIRC, version, entries
    header = bytes.fromhex("44 49 52 43") + bytes.fromhex(format(2, '08x')) + bytes.fromhex(format(entries_count, '08x'))

    # sha-1チェックサム
    sha1_hash = hashlib.sha1(header+entries).hexdigest()
    sha1_check_sum = bytes.fromhex(sha1_hash)

    full_data = header + entries + sha1_check_sum
    # zlibで圧縮
    compressed_data = zlib.compress(full_data, level=1)
    # ファイル保存
    write_file(".git/index2",full_data)

def index_entry(mode,sha1,path):

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

    return entrie


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
