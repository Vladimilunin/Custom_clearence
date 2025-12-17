from sqlalchemy import Column, Integer, String, Float, Text
from app.db.base import Base

class Part(Base):
    __tablename__ = "parts"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    designation = Column(String, unique=True, index=True, nullable=False)  # Обозначение
    name = Column(String, nullable=True)  # Наименование
    material = Column(String, nullable=True)  # Материал
    weight = Column(Float, nullable=True)  # Масса
    dimensions = Column(String, nullable=True)  # Размеры
    description = Column(Text, nullable=True)  # Спецификация / Описание
    section = Column(String, nullable=True) # Раздел (Детали/Сборочные единицы)
    image_path = Column(String, nullable=True) # Path to the image file
