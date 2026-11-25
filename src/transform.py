import pandas as pd

def inspect_dataset(df):
    
    stats =  {
        "rows" : df.shape[0],
        "columns" : df.shape[1],
        "null_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    }

    return stats

def clean_dataset(df, null_strategy="keep", custom_fill=None, drop_duplicates=True):
    df_copy = df.copy()
    df_copy.columns = [str(col).strip().lower().replace(" ", "_") for col in df_copy.columns]

    if null_strategy.lower() != "keep":
        if null_strategy.lower() == "zero":
            df_copy = df_copy.fillna(0)
            
        elif null_strategy.lower() == "custom":
            df_copy = df_copy.fillna(custom_fill)
            
        else:
            raise ValueError("Please choose a supported choice")

    if drop_duplicates: 

        df_copy = df_copy.drop_duplicates()

    return df_copy



    

