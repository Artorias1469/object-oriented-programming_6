#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import argparse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FileItem:
    name: str
    size: Optional[int] = None
    path: str = ""  

@dataclass
class Directory:
    name: str
    files: List[FileItem] = field(default_factory=list)
    subdirectories: List["Directory"] = field(default_factory=list)


def build_directory_structure(directory, max_depth=None, level=0, show_files=True, filter_ext=None, show_size=False):

    if max_depth is not None and level >= max_depth:
        return None

    directory_structure = Directory(name=os.path.basename(directory))

    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                subdir = build_directory_structure(item_path, max_depth, level + 1, show_files, filter_ext, show_size)
                if subdir:
                    directory_structure.subdirectories.append(subdir)
            elif show_files and (filter_ext is None or item.endswith(filter_ext)):
                size = os.path.getsize(item_path) if show_size else None
                directory_structure.files.append(FileItem(name=item, size=size, path=item_path))
    except PermissionError:
        pass

    return directory_structure


def print_directory_structure(directory: Directory, level=0):

    print("│   " * level + "├── " + directory.name)
    for file in directory.files:
        file_info = f" ({file.size} bytes)" if file.size is not None else ""
        print("│   " * (level + 1) + f"├── {file.name}{file_info}")

    for subdir in directory.subdirectories:
        print_directory_structure(subdir, level + 1)


def save_to_xml(directory: Directory, filename: str):

    def create_xml_element(directory: Directory):
        dir_element = ET.Element("directory", name=directory.name)
        for file in directory.files:
            file_element = ET.SubElement(dir_element, "file", name=file.name)
            if file.size is not None:
                file_element.set("size", str(file.size))
            file_element.set("path", file.path)
        for subdir in directory.subdirectories:
            dir_element.append(create_xml_element(subdir))
        return dir_element

    root = create_xml_element(directory)
    tree = ET.ElementTree(root)
    with open(filename, "wb") as fout:
        tree.write(fout, encoding="utf8", xml_declaration=True)


def load_from_xml(filename: str) -> Directory:

    def parse_directory(element):
        dir_obj = Directory(name=element.get("name"))
        for file_element in element.findall("file"):
            name = file_element.get("name")
            size = int(file_element.get("size")) if file_element.get("size") else None
            path = file_element.get("path", "")
            dir_obj.files.append(FileItem(name=name, size=size, path=path))
        for subdir_element in element.findall("directory"):
            dir_obj.subdirectories.append(parse_directory(subdir_element))
        return dir_obj

    tree = ET.parse(filename)
    root = tree.getroot()
    return parse_directory(root)


def main():
    parser = argparse.ArgumentParser(description="Показать структуру каталога в виде дерева.")
    parser.add_argument("directory", nargs="?", default=".", help="Каталог для отображения (по умолчанию текущий).")
    parser.add_argument("-d", "--max-depth", type=int, help="Максимальная глубина отображения каталога.")
    parser.add_argument("-f", "--files", action="store_true", help="Отображать файлы (по умолчанию только каталоги).")
    parser.add_argument("-e", "--extension", help="Фильтровать файлы по расширению (например, .txt).")
    parser.add_argument("-s", "--size", action="store_true", help="Отображать размер файлов.")
    parser.add_argument("-o", "--output", help="Сохранить структуру каталога в XML файл.")
    parser.add_argument("-i", "--input", help="Загрузить структуру каталога из XML файла.")
    args = parser.parse_args()

    if args.input:
        directory = load_from_xml(args.input)
        print(f"Структура каталога, загруженная из {args.input}:")
        print_directory_structure(directory)
    else:
        directory = build_directory_structure(
            args.directory,
            max_depth=args.max_depth,
            show_files=args.files,
            filter_ext=args.extension,
            show_size=args.size
        )
        print_directory_structure(directory)

        if args.output:
            save_to_xml(directory, args.output)
            print(f"Структура каталога сохранена в {args.output}.")


if __name__ == "__main__":
    main()
