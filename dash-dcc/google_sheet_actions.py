import gspread
import pandas as pd 

class GoogleSheetService:
    df_all_data: pd.DataFrame = None
    data_columns: list = ['codigo', 'pais', 'nombre_area_frascati_amplio', 'nombre_area_unesco_amplio', 'anio_publicacion', 'tipo_publicacion', 'nombre', 'nombres', 'departamento']

    def __init__(self, file_name, document, sheet_name):
        self.gc = gspread.service_account(filename=file_name)
        self.sh = self.gc.open(document)
        self.sheet = self.sh.worksheet(sheet_name)
        self.read_all_data()

    def get_all_countries(self):
        try:
            self.sheet = self.sh.worksheet('Paises')
            countries = pd.DataFrame(self.sheet.get_all_records())
            print(countries)
            self.sheet = self.sh.worksheet('Publicaciones')
            return countries[['nombre', 'name']]
        except Exception as e:
            print("Error al obtener los países:", e)

    def read_all_data(self):
        data = self.sheet.get_all_records()
        self.df_all_data = pd.DataFrame(data)
        self.df_all_data = self.df_all_data[self.data_columns]

    def get_unique_value_column(self, column_name: str):
        data_filter = self.df_all_data[column_name].unique().tolist()
        data_filter.insert(0, 'Todos')
        return data_filter

    def get_professors_by_department(self, department: list):
        professors = self.df_all_data[self.df_all_data['departamento'].isin(department)]['nombres'].unique().tolist()
        professors.insert(0, 'Todos')
        return professors

    def read_data_for_formula(self, formula):
        self.sheet.update_cell(1, 1, formula)
        data = self.sheet.get_all_records()
        print(data)
        return pd.DataFrame(data)

    def get_data_by_category(self, categories: list, range_year, author: list):
        if "Todos" not in author:
            filtered_data = self.df_all_data[self.df_all_data['nombres'].isin(author)]
        else:
            filtered_data = self.df_all_data

        filtered_data = filtered_data[(filtered_data['anio_publicacion'] >= range_year[0]) & (filtered_data['anio_publicacion'] <= range_year[1])]
        
        if 'codigo' in categories:
            data = filtered_data.groupby(categories).size().reset_index(name='CANTIDAD')
        else:
            data_filter_unique = filtered_data.groupby(['codigo'] + categories).size().reset_index().drop(columns=0)
            data = data_filter_unique.groupby(categories).size().reset_index(name='CANTIDAD')
        
        return data

    def get_total_by_category(self, category: str, range_year, author: list):
        print(f"Totales en {category}", author)
        
        if "Todos" not in author:
            filtered_data = self.df_all_data[self.df_all_data['nombres'].isin(author)]
        else:
            filtered_data = self.df_all_data

        filtered_data = filtered_data[(filtered_data['anio_publicacion'] >= range_year[0]) & (filtered_data['anio_publicacion'] <= range_year[1])]
        unique_count = filtered_data[category].nunique()
        
        return unique_count

    def get_by_countries(self, publication_types: list, range_year, author: list):
        filtered_data_by_category = self.get_data_by_category(['codigo', 'pais', 'tipo_publicacion'], range_year, author)
        
        if "Todos" in publication_types:
            filtered_data = filtered_data_by_category.value_counts('pais').reset_index(name='CANTIDAD')
        else:
            filtered_data = filtered_data_by_category[filtered_data_by_category['tipo_publicacion'].isin(publication_types)].value_counts('pais').reset_index(name='CANTIDAD')
        
        paises = self.get_all_countries()
        paises['nombre'] = paises['nombre'].str.lower()
        filtered_data['pais'] = filtered_data['pais'].str.lower()
        
        data = pd.merge(paises, filtered_data, left_on='nombre', right_on='pais', how='left').fillna(0)[['name', 'CANTIDAD']]
        data = data.rename(columns={'name': 'PAISES'})
        
        return data