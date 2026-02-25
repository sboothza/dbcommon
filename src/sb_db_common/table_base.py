from __future__ import annotations


class TableBase:
    __table_name__ = ""
    __table_exists_script__ = ""
    __table_count_script__ = ""
    __create_script__ = ""
    __insert_script__ = ""
    __update_script__ = ""
    __delete_script__ = ""
    __drop_script__ = ""
    __fetch_by_id_script__ = ""
    __item_exists_script__ = ""

    def map_row(self, row) -> TableBase:
        pass

    def get_insert_params(self) -> dict:
        pass

    def get_update_params(self) -> dict:
        pass

    def get_id_params(self) -> dict:
        pass
