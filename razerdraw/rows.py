from PIL import Image
import csv


def get_rows(file):
    gen = row_image(file)
    if gen:
        return gen
    gen = row_csv(file)
    if gen:
        return gen
    raise ValueError("Unknown file type " + file)


def row_image(file):
    try:
        img = Image.open(file)  # type: Image.Image
    except IOError:
        return None

    def generator():
        for y in range(img.height):
            row = []
            for x in range(img.width):
                row.append(img.getpixel((x, y)))

            yield row

    return generator()


def row_csv(file):
    with open(file) as fp:
        csv_reader = csv.reader(fp, dialect='unix')

        data = list(csv_reader)

    def generator():
        for row in data:
            condensed = []
            for i in range(0, len(row), 3):
                condensed.append(tuple(map(int, row[i:i + 3])))
            yield condensed

    return generator()

__all__ = ['get_rows']
