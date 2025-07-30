from .internals import Analysis, read_json
from .network import download_file_from_repo
import pandas as pd
import sys


def descarga_archivo(file_name, destination_folder, path):
    lista_analisis = read_json("analyses.json")
    for diccionario_analisis in lista_analisis:
        analisis = Analysis(**diccionario_analisis)
        if analisis.is_dependent_on_datafile(path, file_name):
            download_file_from_repo(
                analisis.get_url_to_datafile(path, file_name), destination_folder
            )
            _adapt_columns(file_name, destination_folder)


def _adapt_columns(file_name, destination_folder):
    file_path = f"{destination_folder}/{file_name}"
    file_df = pd.read_csv(file_path)
    file_df.rename(columns={"Date": "Fecha"}, inplace=True)
    file_df.to_csv(file_path, index=False)


def cli():
    descarga_archivo(*sys.argv[1:])
