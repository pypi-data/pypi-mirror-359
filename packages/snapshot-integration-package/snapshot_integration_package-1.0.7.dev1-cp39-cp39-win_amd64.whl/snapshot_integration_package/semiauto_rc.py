import os
import pandas
import re
from collections import OrderedDict



class ReadConfigFile():

    def __init__(self,file_path: str=None,file_name: str=None):
        self.file_path = file_path
        self.file_name = file_name if file_name is not None else 'config.xlsx'
        self.sheet_dict = OrderedDict()
        self.sheet_dict_path = OrderedDict()
        self.dfs = None
        self.load_and_process_file()
        

    def load_and_process_file(self):
        if self.file_path is not None:
            if '.csv' in self.file_name:
                self._dfs = pandas.read_csv(os.path.join(self.file_path, self.file_name))
                self.dfs = self._dfs.dropna(how='all')
                self.dfs.columns = self.dfs.columns.str.strip()  # Strip column name spaces
                self.dfs.columns = [col.lower() for col in self.dfs.columns]
                self.dfs = self.dfs.rename(columns=lambda x: x.lower())
                self.dfs = self.dfs.apply(self.clean_column)  # Apply the cleaning function to each column

            elif '.xlsx' in self.file_name:
                self._dfs = pandas.read_excel(os.path.join(self.file_path, self.file_name), sheet_name=None)
                self.dfs = {sheet_name.lower(): df.dropna(how='all') for sheet_name, df in self._dfs.items()}
                self.dfs = {
                    sheet_name: df.rename(columns=lambda x: x.strip().lower())  # Strip column name spaces
                                .apply(self.clean_column)  # Apply the cleaning function to each column
                    for sheet_name, df in self.dfs.items()
                }


            column_name = 'SHEET NAME'
            column_type = 'SHEET TYPE'
            column_enabled = 'SHEET RUN ENABLED'
            column_folder_path = 'FOLDER PATH TO STORE RESULTS FOR SHEET'
        

            for key, df in self.dfs.items():
                if all(col.lower() in df.columns for col in [column_name, column_type, column_enabled]):
                    for idx in df.index:
                        sheet_name = df.at[idx, column_name.lower()]
                        sheet_type = df.at[idx, column_type.lower()]

                        sheet_enabled = df.at[idx, column_enabled.lower()]
                        sheet_folder_path = df.at[idx, column_folder_path.lower()]

                        if not pandas.isna(sheet_enabled) and (sheet_enabled or sheet_enabled == 'NOT APPLICABLE'.lower()):
                            # print(f"sheet_enabled:{sheet_enabled}")
                            self.sheet_dict[sheet_name.lower()] = sheet_type
                            for key,value in self.dfs.items():
                                if key == sheet_name and sheet_enabled == 1:
                                    self.dfs[key]['parent_path'] = sheet_folder_path

                                        
    def clean_column(self, column):
        """Helper function to clean strings in a column."""
        if column.dtype == 'object':  # Check if the column contains string data
            return column.apply(lambda x: x.strip().lower() if isinstance(x, str) else x)
        return column
    

    def _filter_sheet_dict(self, search_term):
        temp_dict = OrderedDict()
        search_term_lower = search_term.lower()
        for key, value in self.sheet_dict.items():
            values = [v.strip() for v in re.split(r'[;,]', value.lower())]
            if len(values) < 2:
                if search_term_lower in values:
                    temp_dict[key] = value.lower()
            else:
                for eachvalue in values:
                    if search_term_lower in eachvalue:
                        temp_dict[key] = eachvalue.lower()
        return temp_dict


    def get_data_frame(self):
        return self.dfs
    
    def get_soft_config_sheet(self):
        return self._filter_sheet_dict('SOFT_INPUT')
    
    def get_case_config_sheet(self):
        return self._filter_sheet_dict('CASE_INPUT')
    
    def get_main_config_sheet(self):
        return self._filter_sheet_dict('MAIN_INPUT')
    
    def get_soft_config_indexed_dict(self):
        sheet_keys = self.get_soft_config_sheet().keys()
        result = {}
        current_index = 0
        for k in sheet_keys:
            if k in self.dfs:
                indexed_rows = self.dfs[k].to_dict(orient='index')
                for idx, row in indexed_rows.items():
                    result[str(current_index)] = row
                    current_index += 1
        return result


    def get_case_config_indexed_dict(self):
        sheet_keys = self.get_case_config_sheet().keys()
        result = {}
        current_index = 0
        for k in sheet_keys:
            if k in self.dfs:
                indexed_rows = self.dfs[k].to_dict(orient='index')
                for idx, row in indexed_rows.items():
                    result[str(current_index)] = row
                    current_index += 1
        return result


    def get_main_config_indexed_dict(self):
        sheet_keys = self.get_main_config_sheet().keys()
        result = {}
        current_index = 0
        for k in sheet_keys:
            if k in self.dfs:
                indexed_rows = self.dfs[k].to_dict(orient='index')
                for idx, row in indexed_rows.items():
                    result[str(current_index)] = row
                    current_index += 1
        return result



    


