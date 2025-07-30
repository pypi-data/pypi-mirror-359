# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 04:45:35 2024

@author: nicol
"""

import time
import polars as pl
import pandas as pd
from .utils.excel_export import write_to_excel, write_to_dataframe, setup_excel_file, create_excel_sheet
from .utils.dataframe_operations import is_empty_df, ensure_polars
import warnings

# Suprimir exclusivamente FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)


def process_dataframe(df, output=None, table_name="DataFrame", limite=None):
    """
    Procesa un DataFrame y genera un informe EDA en formato Excel.

    Args:
        df (DataFrame): El DataFrame que se desea procesar.
        output (str): Ruta de salida para el archivo Excel.
        table_name (str): Nombre de la tabla para identificar los datos en el informe Excel.
        limite (int): Límite opcional de filas a procesar del DataFrame.
    """
    if is_empty_df(df):
        print("El DataFrame proporcionado está vacío. Finalizando el programa.")
        return
    
    # Convertir a un DataFrame de polars si no lo es
    df = ensure_polars(df)

    # 3) Aplicamos límite
    if limite is not None and limite > 0:
        # para LazyFrame, limit; para eager, head()
        if isinstance(df, pl.LazyFrame):
            df = df.limit(limite)
        else:
            df = df.head(limite)
        print(f"Se han procesado las primeras {limite} filas del DataFrame.")

    print("Calculando EDA...")
    # Configurar y escribir en el archivo Excel
    start_time = time.time()
    if output:
        # Configuración inicial de Excel
        writer, book, format_encabez_titulo, format_encabez_subtitulo, format_encabez_columnas, format_encabez_columnas2, format_celda_datos, format_titulo_tabla, ANCHO_COL, SALTO_LADO, ENCABEZ, format_columna_col, format_roboto_bordered, format_num_with_thousands, format_guide_text, format_nullwarning_red = setup_excel_file(output)
        create_excel_sheet(book, SALTO_LADO, ANCHO_COL, ENCABEZ, format_encabez_titulo, format_encabez_subtitulo, format_guide_text)
        
        # Escribir el DataFrame en el archivo Excel
        write_to_excel(df, table_name, writer, book, ENCABEZ, format_encabez_titulo, format_encabez_columnas, format_encabez_columnas2, format_celda_datos, format_titulo_tabla, format_roboto_bordered, format_num_with_thousands, format_nullwarning_red, ANCHO_COL, SALTO_LADO, format_columna_col)
        writer.close()
    else:
        data_into = write_to_dataframe(df, table_name)
        end_time = time.time()
        print(f"Tiempo de ejecución: {end_time - start_time} segundos")
        return data_into

    end_time = time.time()
    print(f"Tiempo de ejecución: {end_time - start_time} segundos")
    # Cerrar el archivo Excel
   
