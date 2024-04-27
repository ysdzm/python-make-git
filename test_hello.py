import sys
from io import StringIO
import contextlib

def test_hello():
    # 仮想のコマンドライン引数を設定
    sys.argv = ["python", "git", "hello"]

    # gitモジュールからhello関数をimport
    from git import hello

    # stdoutをキャプチャ
    captured_output = StringIO()
    sys.stdout = captured_output

    # hello関数を呼び出す
    hello()

    # 出力を取得
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue().strip()

    # 出力が正しいことを確認
    assert output == "hello", "Output is not 'hello'"
