import importlib
import pathlib

NOT_SUPPORTED = '{filepath} is not supported'
DEFAULT_SHEET = 'Sheet1'


class FileType:
    CSV = '.csv'
    XLS = '.xls'
    XLSX = '.xlsx'


class SpreadSheet:
    """
    Class that contains the data and allows to export with to_file() or a few other operations.
    """
    def __init__(self, data: list[list], columns: list[str]):
        self.columns = columns
        self.data = data


    def to_file(self, filepath: str) -> None:
        """
        Main method of this class, this allows to export the SpreadSheet to .csv .xls or .xlsx.
        Just make sure to have the dependencies installed.
        xlwt for xls, openpyxl for xlsx.

        :param filepath: path to the file to export.
        :return: None
        """
        path = pathlib.Path(filepath)
        match path.suffix.lower():
            case FileType.CSV:
                self.to_csv(filepath)
            case FileType.XLS:
                self.to_xls(filepath)
            case FileType.XLSX:
                self.to_xlsx(filepath)
            case _:
                raise ValueError(NOT_SUPPORTED.format(filepath=filepath))

    def to_csv(self, filepath: str):
        import csv
        with open(filepath, mode='w', newline='', encoding='utf8') as file:
            writer = csv.writer(file)
            if self.columns:
                writer.writerow(self.columns)
            writer.writerows(self.data)

    def to_xls(self, filepath: str):
        xlwt = importlib.import_module('xlwt')
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(DEFAULT_SHEET)

        row_to_start = 0
        for col_idx, col_name in enumerate(self.columns):
            sheet.write(0, col_idx, col_name)
            row_to_start = 1

        for row_idx, row in enumerate(self.data, start=row_to_start):
            for col_idx, value in enumerate(row):
                sheet.write(row_idx, col_idx, value)

        workbook.save(filepath)

    def to_xlsx(self, filepath: str):
        openpyxl = importlib.import_module('openpyxl')
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = DEFAULT_SHEET

        if self.columns:
            sheet.append(self.columns)

        for row in self.data:
            sheet.append(row)

        workbook.save(filepath)

    def to_dict_records(self) -> list[dict]:
        """
        Returns a list of dicts, each dict containing the columns as keys.

        :return: list of dicts.
        """
        result = []
        for row in self.data:
            record = {self.columns[i]: cell for i, cell in enumerate(row)}
            result.append(record)
        return result

    def get_column(self, name: str) -> list:
        col = self.columns.index(name)
        result = [row[col] for row in self.data]
        return result

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self):
        return f"SpreadSheet(columns={self.columns}, rows={self.data[:3]}...)"


def read_file(filepath: str, has_columns=True) -> SpreadSheet:
    """
    Main function to allow importing from .csv, .xls, or .xlsx.
    Just make sure you have the dependencies installed:
    xlrd for .xls, openpyxl for .xlsx.

    :param filepath: path to the file to import.
    :param has_columns: boolean
    :return: SpreadSheet
    """
    path = pathlib.Path(filepath)
    match path.suffix.lower():
        case FileType.CSV:
            return import_csv(filepath, has_columns)
        case FileType.XLS:
            return import_xls(filepath, has_columns)
        case FileType.XLSX:
            return import_xlsx(filepath, has_columns)
        case _:
            raise ValueError(NOT_SUPPORTED.format(filepath=filepath))


def import_csv(filepath: str, has_columns=True):
    import csv
    with open(filepath, newline='', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile)

        if has_columns:
            columns = next(reader)
        else:
            columns = []

        data = [row for row in reader]
        return SpreadSheet(data, columns)


def import_xls(filepath: str, has_columns=True) -> SpreadSheet:
    xlrd = importlib.import_module('xlrd')
    book = xlrd.open_workbook(filepath)
    sheet = book.sheet_by_index(0)

    row_to_start = 0
    if has_columns:
        columns = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        row_to_start = 1
    else:
        columns = []

    data = []
    for row_idx in range(row_to_start, sheet.nrows):
        row = [sheet.cell_value(row_idx, col) for col in range(sheet.ncols)]
        data.append(row)

    return SpreadSheet(data=data, columns=columns)


def import_xlsx(filepath: str, has_columns=True) -> SpreadSheet:
    openpyxl = importlib.import_module('openpyxl')
    workbook = openpyxl.load_workbook(filename=filepath, data_only=True)
    sheet = workbook.active  # Get the first (active) sheet

    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return SpreadSheet(data=[], columns=[])

    row_to_start = 0
    if has_columns:
        columns = list(rows[0])
        row_to_start = 1
    else:
        columns = []
    data = [list(row) for row in rows[row_to_start:]]

    return SpreadSheet(data=data, columns=columns)


def from_records(data: list[dict]) -> SpreadSheet:
    """
    Allows to create a SpreadSheet from a list of dicts, each dict contains the columns as keys.

    :param data: a list of dicts
    :return: SpreadSheet
    """
    if not data:
        return SpreadSheet(data=[], columns=[])
    columns = list(data[0].keys())
    rows = [list(d.values()) for d in data]
    return SpreadSheet(data=rows, columns=columns)
