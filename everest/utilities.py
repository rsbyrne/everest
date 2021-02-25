import os

def add_headers(path, header = '#' * 80, footer = '#' * 80):
    path = os.path.abspath(path)
    for filename in os.listdir(path):
        subPath = os.path.join(path, filename)
        if os.path.isdir(subPath):
            add_headers(subPath)
        filename, ext = os.path.splitext(filename)
        if ext == '.py':
            with open(subPath, mode = 'r+') as file:
                content = file.read()
                file.seek(0, 0)
                if not content.strip('\n').startswith(header):
                    content = f"{header}\n\n{content}"
                if not content.strip('\n').endswith(footer):
                    content = f"{content}\n\n{footer}\n"
                file.write(content)