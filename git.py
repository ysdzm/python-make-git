from docopt import docopt

__VERSION__ = '1.0'

__DOC__ = """
Usage: 
    git hello
    git add [<pathspec>...]
    git commit [-m <msg>]
    git hash-object <file>...
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

def hello():
    print("hello")

if __name__ == "__main__":
    main()
