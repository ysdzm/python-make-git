import sys
import subprocess
import os

def test_hash_object():
    # hello.txtを作成
    with open("hello.txt", "w") as f:
        f.write("Hello, world!")

    # -wオプションなしの場合のテスト
    output_without_w = subprocess.check_output(["python", "git.py", "hash-object", "hello.txt"]).decode().strip()

    # -wオプションありの場合のテスト
    output_with_w = subprocess.check_output(["python", "git.py", "hash-object", "-w", "hello.txt"]).decode().strip()

    # gitのhash-objectを実行してハッシュ値を取得
    git_hash_output = subprocess.check_output(["git", "hash-object", "./hello.txt"]).decode().strip()

    # Test
    assert output_without_w == git_hash_output, "Output mismatch: without the -w option, the output does not match the output of the git command"
    assert output_with_w == git_hash_output, "Output mismatch: with the -w option, the output does not match the output of the git command"

    print("All tests passed successfully.")

if __name__ == "__main__":
    test_hash_object()
