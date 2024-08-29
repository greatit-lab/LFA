from sqlalchemy import create_engine

def get_db_engine():
    db_user = 'admin'
    db_password = 'admin'
    db_host = '10.135.77.154'
    db_port = '3306'
    db_name = 'logfusion'

    engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    return engine
