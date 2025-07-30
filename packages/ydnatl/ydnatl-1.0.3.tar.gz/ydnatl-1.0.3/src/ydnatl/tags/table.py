import csv
import json

from ydnatl.core.element import HTMLElement


class Table(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "table"})

    @classmethod
    def from_csv(cls, file_path: str, encoding: str = "utf-8") -> "Table":
        table = cls()
        try:
            with open(file_path, mode="r", encoding=encoding) as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    table_row = TableRow()
                    for cell in row:
                        table_row.append(TableDataCell(cell))
                    table.append(table_row)
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except csv.Error as e:
            raise ValueError(f"CSV error occurred: {e}")
        except UnicodeDecodeError:
            raise ValueError(f"Encoding error: {encoding} is not suitable for the file")
        return table

    @classmethod
    def from_json(cls, file_path: str, encoding: str = "utf-8") -> "Table":
        table = cls()
        try:
            with open(file_path, mode="r", encoding=encoding) as file:
                data = json.load(file)
                if not isinstance(data, list):
                    raise ValueError("JSON data must be a list of rows")
                for row in data:
                    if not isinstance(row, list):
                        raise ValueError("Each row in JSON data must be a list")
                    table_row = TableRow()
                    for cell in row:
                        table_row.append(TableDataCell(str(cell)))
                    table.append(table_row)
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON decoding error: {e}")
        except UnicodeDecodeError:
            raise ValueError(f"Encoding error: {encoding} is not suitable for the file")
        return table


class TableFooter(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "tfoot"})


class TableHeaderCell(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "th"})


class TableHeader(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "thead"})


class TableBody(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "tbody"})


class TableDataCell(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "td"})


class TableRow(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "tr"})
