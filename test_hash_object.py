import sys
import subprocess
import os

def test_hash_object():
    # hello.txtを作成
    with open("hello.txt", "w") as f:
        f.write("Hello, world!")
    with open("hoge.txt", "w") as f:
        f.write("hogehoge")

    output = subprocess.check_output(["python", "git.py", "hash-object", "hello.txt"], universal_newlines=True).strip()
    git_hash_output = subprocess.check_output(["git", "hash-object", "./hello.txt"], universal_newlines=True).strip()
    assert output == git_hash_output, "Output mismatch: without the -w option, the output does not match the output of the git command"

    output = subprocess.check_output(["python", "git.py", "hash-object", "-w", "hello.txt"], universal_newlines=True).strip()
    git_hash_output = subprocess.check_output(["git", "hash-object", "-w", "./hello.txt"], universal_newlines=True).strip()
    assert output == git_hash_output, "Output mismatch: with the -w option, the output does not match the output of the git command"

    output = subprocess.check_output(["python", "git.py", "hash-object", "hello.txt", "hoge.txt"], universal_newlines=True).strip()
    git_hash_output = subprocess.check_output(["git", "hash-object", "./hello.txt", "./hoge.txt"], universal_newlines=True).strip()
    assert output == git_hash_output, "Output mismatch: without the -w option, the output does not match the output of the git command"

    print("All tests passed successfully.")
