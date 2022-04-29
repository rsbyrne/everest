import os


def replace_all(old, new, /, *, path='.'):
    for dirpath, dirnames, filenames in os.walk(path):
        if os.path.split(dirpath)[1].startswith('.'):
            continue
        for filename in filenames:
            if filename.startswith('.'):
                continue
            if not filename.endswith('.py'):
                continue
            with open(os.path.join(dirpath, filename), mode='r') as file:
                text = file.read()
            if old not in text:
                continue
            newtext = text.replace(old, new)
            with open(os.path.join(dirpath, filename), mode='w') as file:
                file.write(newtext)


def find_all(strn, /, *, path='.'):
    out = []
    for dirpath, dirnames, filenames in os.walk(path):
        if os.path.split(dirpath)[1].startswith('.'):
            continue
        for filename in filenames:
            if filename.startswith('.'):
                continue
            if not filename.endswith('.py'):
                continue
            with open(os.path.join(dirpath, filename), mode='r') as file:
                if strn in file.read():
                    yield (dirpath, filename)
