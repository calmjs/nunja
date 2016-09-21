# -*- coding: utf-8 -*-
"""
Generic dummy modules.
"""


class DummyTableData(object):
    """
    This is a data provider that feeds stuff to the table mold.
    """

    def __init__(self, columns, data, css=None):
        self.columns = columns
        self.data = data
        self.css = css or {}

    def to_jsonable(self):
        """
        Convert to a dict that can be dumped into json.
        """

        column_ids = [c[0] for c in self.columns]

        results = {
            # filter out potential JSON-LD keywords from usable column_ids
            "active_columns": [
                id_ for id_, name in self.columns if id_[0] != '@'],
            "column_map": {k: v for k, v in self.columns if k[0] != '@'},
            "data": [
                dict(zip(column_ids, datum)) for datum in self.data
            ],
            "css": self.css,
        }

        return results
