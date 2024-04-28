import sys
import subprocess
import os

def test_hash_object():
    # hello.txtを作成
    with open("hello.txt", "w") as f:
        f.write("Hello, world!")

    # カスタムのhash-objectを実行してハッシュ値を取得
    output = subprocess.check_output(["python", "git.py", "hash-object", "-w", "hello.txt"]).decode().strip()
    print("Custom hash:", output)

    # gitのhash-objectを実行してハッシュ値を取得
    git_hash_output = subprocess.check_output(["git", "hash-object", "./hello.txt"]).decode().strip()
    print("Git hash:", git_hash_output)

    # ハッシュ値が一致するかを確認
    assert output == git_hash_output, "Output mismatch: custom hash is different from git hash"

    print("Test passed: Output matches git hash")
