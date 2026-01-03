from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, running, completed, failed
    
    # Configurações (JSON para flexibilidade, mas poderíamos normalizar)
    config = Column(JSON)
    
    # Resultados
    best_fitness = Column(Float, nullable=True)
    generations_run = Column(Integer, nullable=True)
    execution_time = Column(Float, nullable=True)
    
    # Detalhes da solução (rotas, etc)
    result_details = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Experiment(id={self.id}, status={self.status}, fitness={self.best_fitness})>"
