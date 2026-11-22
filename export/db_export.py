"""
Database export module
"""

from typing import Dict, List


class DatabaseExporter:
    """Exports datapoints to various databases."""
    
    def export_to_sqlite(self, datapoints: List[Dict], db_path: str, table_name: str = "data"):
        try:
            from sqlalchemy import create_engine, Column, Integer, JSON
            from sqlalchemy.ext.declarative import declarative_base
            from sqlalchemy.orm import sessionmaker
            
            engine = create_engine(f'sqlite:///{db_path}')
            Base = declarative_base()
            
            class DataPoint(Base):
                __tablename__ = table_name
                id = Column(Integer, primary_key=True)
                data = Column(JSON)
            
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            try:
                for dp in datapoints:
                    session.add(DataPoint(data=dp))
                session.commit()
            finally:
                session.close()
        except ImportError:
            raise ImportError("sqlalchemy not installed")
    
    def export_to_mongodb(self, datapoints: List[Dict], uri: str, 
                         db_name: str, collection_name: str):
        try:
            import pymongo
            
            client = pymongo.MongoClient(uri)
            db = client[db_name]
            collection = db[collection_name]
            
            try:
                collection.insert_many(datapoints)
            finally:
                client.close()
        except ImportError:
            raise ImportError("pymongo not installed")
