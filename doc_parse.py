import re
from pathlib import Path
from typing import List
import PyPDF2
from PyPDF2.utils import PdfReadError
from PIL import Image
import pytesseract

"""
Форматы файлов: 2 PDF JPEG
Шаблоны данных: N
Количество номеров в 1 файле: N
"""


# TODO: PDF _> Image
def pdf_image_extract(pdf_path: Path, images_path: Path) -> List[Path]:
    results = []
    with pdf_path.open("rb") as file:
        try:
            pdf_file = PyPDF2.PdfFileReader(file)
        except PdfReadError as error:
            print(error)
            # TODO: Записать ошибку чтения файла в БД
            return results
        for page_num, page in enumerate(pdf_file.pages, 1):
            image_name = f"{pdf_path.name}_num_{page_num}"
            image_path = images_path.joinpath(image_name)
            image_path.write_bytes(page["/Resources"]["/XObject"]["/Im0"]._data)
            results.append(image_path)
    return results


# TODO: Image _> Numbers
def get_serial_numbers(image_path: Path) -> List[str]:
    results = []
    image = Image.open(image_path)
    text_rus = pytesseract.image_to_string(image, "rus")
    pattern = re.compile(r"([з|З]аводской.*[номер|№])")
    matches = len(re.findall(pattern, text_rus))
    if matches:
        text_eng = pytesseract.image_to_string(image, "eng").split("\n")
        for idx, line in enumerate(text_rus.split("\n")):
            if re.match(pattern, line):
                number = text_eng[idx].split()[-1]
                results.append(number)
                if len(results) == matches:
                    break
    return results


def get_dir_path(dir_name):
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path


if __name__ == "__main__":
    images_path = get_dir_path("images")
    pdf_path = Path(__file__).parent.joinpath("8416_4.pdf")
    images = pdf_image_extract(pdf_path, images_path)
    s_numbers = list(map(get_serial_numbers, images))
    print(1)
