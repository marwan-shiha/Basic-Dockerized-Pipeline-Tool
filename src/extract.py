from pathlib import Path
import pandas as pd



def extract_dataset(source):
    source = str(source)

    if source.lower().startswith(("http://", "https://")):
        
        
        if source.lower().endswith(".csv"):
            dataframe = pd.read_csv(source)
            return dataframe
        
        elif source.lower().endswith(".parquet"):
            dataframe = pd.read_parquet(source)
            return dataframe
        
        else: 
            raise ValueError("Unsupported file format. Please provide a .csv or .parquet file.")


    else:
        file_path = Path(source)
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found at path: {file_path}")

        
        extension = file_path.suffix.lower()
        
        if extension == ".csv":
            
            dataframe = pd.read_csv(source)
            return dataframe
        
        elif extension == ".parquet":
            
            dataframe = pd.read_parquet(source)
            return dataframe
        
        else: 
            raise ValueError("Unsupported file format. Please provide a .csv or .parquet file.")