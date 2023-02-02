import itertools
import yaml
import argparse
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument('func', choices=['tag', 'title'], help='機能')
    p.add_argument('directory', help='検索対象ディレクトリ')
    p.add_argument('-l', '--list', action='store_true', help='tagもしくはtitleリスト表示')
    p.add_argument('-n', '--name', default='', help='検索対象のtagもしくはtitleを文字列指定')
    p.add_argument('-d', '--dir', action='store_true', help='ディレクトリを探索')

    args = p.parse_args()

    headers = []
    if args.dir:
        headers = get_headers_from_two_layer(args.directory)
    else:
        headers = get_headers_from_one_layer(args.directory)

    if args.func == 'tag':
        if args.list:
            list_tags(headers)
        else:
            display_tag_files(headers, args.name)

    elif args.func == 'title':
        if (args.list):
            list_titles(headers)

def list_tags(headers):
    tagsList = [header.tags for header in headers]
    tags = itertools.chain.from_iterable(tagsList)

    for tag in set(tags):
        print(tag)

def display_tag_files(headers, tagname):
    for header in headers:
        if tagname in header.tags:
            print(header.filepath)

def list_titles(headers):
    for header in headers:
        print(f'{header.title}:\t{header.filepath}')

def get_headers_from_two_layer(directory):
    p = Path(directory)

    dirs = [x for x in p.iterdir() if x.is_dir()]

    for secondaryDirectory in dirs:
        second = Path(secondaryDirectory)
        for filepath in second.glob("*.md"):
            lines = read_line_generator(filepath)
            cleansedLines = remove_blank_line(lines)

            if is_blank_file(cleansedLines):
                continue

            if not has_yaml_header(cleansedLines):
                continue

            yield get_header(cleansedLines, secondaryDirectory)

def get_headers_from_one_layer(directory):
    p = Path(directory)

    for filepath in p.glob("*.md"):
        lines = read_line_generator(filepath)
        cleansedLines = remove_blank_line(lines)

        if is_blank_file(cleansedLines):
            continue

        if not has_yaml_header(cleansedLines):
            continue

        yield get_header(cleansedLines, filepath)

def get_header(linesRemovedBlank, contentsPath):
    headerLines = get_yaml_header_lines(linesRemovedBlank)
    headerText = "\n".join(list(headerLines))

    header = yaml.safe_load(headerText)

    tags = header.get("tags")

    if not tags:
        tags = []

    if not isinstance(tags, list):
        tags = tags.replace(' ', '').split(',')

    return Header(
        contentsPath, 
        header.get("uid"),
        header.get("title"),
        header.get("aliases"),
        header.get("created"),
        header.get("updated"),
        tags)


def remove_blank_line(lines):
    return list(map(lambda x : x.rstrip(), filter(lambda x: x != "\n", lines)))

def read_line_generator(filepath):
    with open(filepath, encoding='utf-8') as file:
        for line in file:
            yield line

def is_blank_file(lines):
    return len(lines) == 0

def has_yaml_header(lines):
    if not "---" in lines[0]:
        return False
    
    for line in lines[1:]:
        if "---" in line:
            return True
    
    return False

def get_yaml_header_lines(lines):
    if not "---" in lines[0]:
        return False
    
    for line in lines[1:]:
        if "---" in line:
            break
        else:
            yield line

class Header:

    def __init__(
        self, 
        filepath, 
        uid, 
        title, 
        aliases,
        created,
        updated,
        tags):
        self.filepath = filepath
        self.uid = uid
        self.title = title
        self.aliases = aliases
        self.created = created
        self.updated = updated
        self.tags = tags if tags else []

    def conatins_title(self, title):
        return title in self.title

if __name__ == "__main__":
    main()
