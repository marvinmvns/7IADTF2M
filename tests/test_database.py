from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Experiment
from src.database.database import get_db
import pytest

# Banco em memória para testes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_experiment(db):
    exp = Experiment(status="pending", config={"pop": 100})
    db.add(exp)
    db.commit()
    
    assert exp.id is not None
    assert exp.status == "pending"
    assert exp.config["pop"] == 100

def test_update_experiment(db):
    exp = Experiment(status="pending", config={})
    db.add(exp)
    db.commit()
    
    exp.status = "completed"
    exp.best_fitness = 10.5
    db.commit()
    
    saved = db.query(Experiment).first()
    assert saved.status == "completed"
    assert saved.best_fitness == 10.5
