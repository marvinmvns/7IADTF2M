from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import json

# Garante que o diretório data existe
os.makedirs("data", exist_ok=True)

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/experiments.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Settings(Base):
    """Tabela para configurações da aplicação"""
    __tablename__ = "settings"
    
    key = Column(String(100), primary_key=True)
    value = Column(Text)


def create_tables():
    """Cria todas as tabelas se não existirem"""
    Base.metadata.create_all(bind=engine)


def get_setting(key: str, default=None):
    """Obtém uma configuração do banco de dados"""
    db = SessionLocal()
    try:
        setting = db.query(Settings).filter(Settings.key == key).first()
        if setting:
            try:
                return json.loads(setting.value)
            except:
                return setting.value
        return default
    finally:
        db.close()


def set_setting(key: str, value):
    """Salva uma configuração no banco de dados"""
    db = SessionLocal()
    try:
        setting = db.query(Settings).filter(Settings.key == key).first()
        value_str = json.dumps(value) if not isinstance(value, str) else value
        
        if setting:
            setting.value = value_str
        else:
            setting = Settings(key=key, value=value_str)
            db.add(setting)
        
        db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Cria tabelas na inicialização
create_tables()
