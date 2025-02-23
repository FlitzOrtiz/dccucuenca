import gspread
import pandas as pd 
class GoogleSheetService:
    
    anio_publicacion_letter = 'T'
    nombres_letter = 'AS'
    name_columns = {}
    
    def __init__(self, file_name, document, sheet_name):
        self.gc = gspread.service_account(filename=file_name)
        self.sh = self.gc.open(document)
        self.sheet = self.sh.worksheet(sheet_name)
        
    def read_all_data(self):
        data = self.sheet.get_all_records()
        return pd.DataFrame(data)
    
    def read_column_names(self):
        # Obtiene los nombres de las columnas desde la primera fila
        columns = self.sheet.row_values(1)

        # Crea un diccionario con el nombre de la columna, su letra y su posición
        column_dict = {
            col: {
                'letra': gspread.utils.rowcol_to_a1(1, idx + 1)[:-1],  # Letra de la columna
                'posicion': idx + 1  # Posición de la columna
            }
            for idx, col in enumerate(columns)
        }
        
        return column_dict

    def _get_column_letter(self, n):
        """Convert a column index (1-based) to a column letter (A, B, ..., Z, AA, AB, ...)."""
        result = ''
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            result = chr(65 + remainder) + result
        return result

    def read_data_specific_columns(self, rango, query):
        string_format_query = f"=QUERY({rango}, \"{query}\")"
        print(string_format_query)
        self.sheet.update_cell(1, 1, string_format_query)
        data = self.sheet.get_all_records()
        return pd.DataFrame(data)
    
    def read_data_for_formula(self, formula):
        self.sheet.update_cell(1, 1, formula)
        data = self.sheet.get_all_records()
        print(data)
        return pd.DataFrame(data)
    
    def read_data_per_category(self, name_sheet, columns, category, name_category, range_year, author=None, final_column='AS'):
        if not columns.index(category):
            print("La categoría no existe")
            return []
        columns_data_sheet = f"UNIQUE({name_sheet}!A2:{final_column})"
        select_columns = f"SELECT Col{self.name_columns[category]['posicion']}, " + "COUNT(Col1)"
        where = "WHERE " + f"Col{self.name_columns['anio_publicacion']['posicion']} >= {range_year[0]} AND Col{self.name_columns['anio_publicacion']['posicion']} <= {range_year[1]}"
        if author:
            where += " AND " + f"Col{self.name_columns['nombres']['posicion']} = '{author}'"
        group_by = f"GROUP BY Col{self.name_columns[category]['posicion']}"     
        label = f"LABEL Col{self.name_columns[category]['posicion']} '{name_category}', COUNT(Col1) 'CANTIDAD'"     
        query = f"=QUERY({columns_data_sheet}, \"{select_columns} {where} {group_by} {label}\")"
        print("Query:", query)
        self.sheet.update_cell(1, 1, query)
        data = self.sheet.get_all_records()
        return pd.DataFrame(data)
    
    def read_data_total_per_category(self, name_sheet, range_year, author=None, final_column='AS'):
        columns_data_sheet = f"UNIQUE({name_sheet}!A2:{final_column})"
        select_columns = f"SELECT COUNT(Col1)"
        where = "WHERE " + f"Col{self.name_columns['anio_publicacion']['posicion']} >= {range_year[0]} AND Col{self.name_columns['anio_publicacion']['posicion']} <= {range_year[1]}"
        if author:
            where += " AND " + f"Col{self.name_columns['nombres']['posicion']} = '{author}'"
        label = f"LABEL COUNT(Col1) 'TOTAL'"     
        query = f"=QUERY({columns_data_sheet}, \"{select_columns} {where} {label}\")"
        print("Query:", query)
        self.sheet.update_cell(1, 1, query)
        data = self.sheet.get_all_records()
        return pd.DataFrame(data)
    
    def read_data_per_countries(self, name_sheet, range_year, author=None, final_column='AS'):
        print("Final column:", final_column)
        columns_data_sheet = f"UNIQUE({{{name_sheet}!A:{final_column}, ARRAYFORMULA(BUSCARV({name_sheet}!{self.name_columns['pais']['letra']}:{self.name_columns['pais']['letra']}, paises!A:B, 2, FALSO))}})"
        position_final_column = [col['posicion'] for posicion, col in self.name_columns.items() if col['letra'] == final_column][0] + 1
        select_columns = f"SELECT Col{self.name_columns['pais']['posicion']}, Col{position_final_column}, COUNT(Col1)"
        where = "WHERE " + f"Col{self.name_columns['anio_publicacion']['posicion']} >= {range_year[0]} AND Col{self.name_columns['anio_publicacion']['posicion']} <= {range_year[1]}"
        if author:
            where += " AND " + f"Col{self.name_columns['nombres']['posicion']} = '{author}'"
        group_by = f"GROUP BY Col{self.name_columns['pais']['posicion']}, Col{position_final_column}"
        label = f"LABEL Col{self.name_columns['pais']['posicion']} 'PAISES', Col{position_final_column} 'COUNTRIES', COUNT(Col1) 'CANTIDAD'"    
        query = f"=QUERY({columns_data_sheet}, \"{select_columns} {where} {group_by} {label}\")"
        print("Query:", query)
        self.sheet.update_cell(1, 1, query)
        dataresp = self.sheet.get_all_records()
        df = pd.DataFrame(dataresp)
        return df
    
    def read_data_all_countries(self, name_sheet, column_countries):
        query = f"=QUERY({name_sheet}!{column_countries}2:{column_countries}, \"SELECT * LABEL Col1 'COUNTRIES'\")"
        print("Query:", query)
        self.sheet.update_cell(1, 1, query)
        dataresp = self.sheet.get_all_records()
        df = pd.DataFrame(dataresp)
        return df