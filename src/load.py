from sqlalchemy import create_engine
from tqdm import tqdm
import pandas as pd


def load_to_postgres(df, table_name, user, password, port, db_name, chunksize=10_000):
    
    url = f"postgresql+psycopg2://{user}:{password}@localhost:{port}/{db_name}"
    
    engine = create_engine(url)

    
    
    df.head(0).to_sql(name=table_name, con=engine, if_exists="replace", index=False)

    
    for i in tqdm(range(0, len(df), chunksize), desc="Uploading chunks", unit="chunk"):
        df.iloc[i : i + chunksize].to_sql(
            name=table_name,
            con=engine,
            if_exists="append",
            index=False,
        )

    engine.dispose()