from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class Part(Base):
    __tablename__ = "parts"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    designation = Column(String, unique=True, index=True, nullable=False)  # Обозначение
    name = Column(String, nullable=True)  # Наименование
    material = Column(String, nullable=True)  # Материал
    weight = Column(Float, nullable=True)  # Масса (кг или г)
    weight_unit = Column(String, nullable=True)  # Единица массы: 'кг' или 'г'
    dimensions = Column(String, nullable=True)  # Размеры (мм)
    description = Column(Text, nullable=True)  # Спецификация / Описание
    section = Column(String, nullable=True) # Раздел (Детали/Сборочные единицы)
    image_path = Column(String, nullable=True) # Path to the image file
    manufacturer = Column(String, nullable=True) # Производитель
    condition = Column(String, nullable=True) # Состояние (New, Refurbished, etc)

    # Поля для электроники
    component_type = Column(String, nullable=True)  # 'electronics' или 'mechanical'
    specs = Column(JSONB, nullable=True)  # Гибкие характеристики: {"Род тока": "...", "Момент": "..."}

    # Deprecated/Legacy fields (kept for backward compatibility or migration)
    current_type = Column(String, nullable=True)
    input_voltage = Column(String, nullable=True)
    input_current = Column(String, nullable=True)
    processor = Column(String, nullable=True)
    ram_kb = Column(Integer, nullable=True)
    rom_mb = Column(Integer, nullable=True)
    tnved_code = Column(String, nullable=True)
    tnved_description = Column(Text, nullable=True)

