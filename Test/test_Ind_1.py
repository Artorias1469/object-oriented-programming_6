import os
import sys
import shutil
import tempfile
import pytest

# Добавляем путь к тестируемому модулю
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.Ind.Ind_1 import build_directory_structure, print_directory_structure, save_to_xml, load_from_xml


def create_test_environment():
    """Создает временную файловую структуру для тестов."""
    temp_dir = tempfile.mkdtemp()

    # Создаем файлы и папки
    os.makedirs(os.path.join(temp_dir, 'subdir1'))
    os.makedirs(os.path.join(temp_dir, 'subdir2'))
    with open(os.path.join(temp_dir, 'file1.txt'), 'w') as f:
        f.write('Hello, World!')
    with open(os.path.join(temp_dir, 'subdir1', 'file2.txt'), 'w') as f:
        f.write('Python Testing')

    return temp_dir


def test_build_directory_structure():
    temp_dir = create_test_environment()
    try:
        structure = build_directory_structure(temp_dir, show_files=True, show_size=True)

        assert structure.name == os.path.basename(temp_dir)
        assert len(structure.files) == 1
        assert structure.files[0].name == 'file1.txt'

        subdirs = {subdir.name: subdir for subdir in structure.subdirectories}
        assert 'subdir1' in subdirs
        assert 'subdir2' in subdirs

        subdir1 = subdirs['subdir1']
        assert len(subdir1.files) == 1
        assert subdir1.files[0].name == 'file2.txt'
    finally:
        shutil.rmtree(temp_dir)


def test_save_and_load_xml():
    temp_dir = create_test_environment()
    try:
        structure = build_directory_structure(temp_dir, show_files=True, show_size=True)
        xml_file = os.path.join(temp_dir, 'test_output.xml')

        save_to_xml(structure, xml_file)
        assert os.path.exists(xml_file)

        loaded_structure = load_from_xml(xml_file)
        assert loaded_structure.name == structure.name
        assert len(loaded_structure.files) == len(structure.files)
        assert loaded_structure.subdirectories[0].name == structure.subdirectories[0].name
    finally:
        shutil.rmtree(temp_dir)


def test_print_directory_structure(capsys):
    temp_dir = create_test_environment()
    try:
        structure = build_directory_structure(temp_dir, show_files=True, show_size=True)
        print_directory_structure(structure)

        captured = capsys.readouterr()
        assert 'file1.txt' in captured.out
        assert 'subdir1' in captured.out
        assert 'file2.txt' in captured.out
    finally:
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    pytest.main()
