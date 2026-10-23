from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Processo(Base):
    __tablename__ = 'processos'

    id = Column(Integer, primary_key=True, index=True)
    numero_processo = Column(String(50), index=True, nullable=False)
    data_processo = Column(Date, nullable=True)
    assunto = Column(Text, nullable=True)
    tipo_processo = Column(String(100), nullable=True)
    url = Column(Text, nullable=False)
    data_coleta = Column(DateTime, default=datetime.utcnow)

    # Relationship to documentos
    documentos = relationship("Documento", back_populates="processo", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Processo(numero='{self.numero_processo}', assunto='{self.assunto[:30]}...')>"

class Documento(Base):
    __tablename__ = 'documentos'

    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey('processos.id'), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    tipo = Column(String(50), nullable=True)  # PDF, DOCX, HTML, etc.
    caminho = Column(Text, nullable=False)  # local file path
    texto_extraido = Column(Text, nullable=True)
    data_coleta = Column(DateTime, default=datetime.utcnow)

    processo = relationship("Processo", back_populates="documentos")

    def __repr__(self):
        return f"<Documento(nome='{self.nome_arquivo}', tipo='{self.tipo}')>"