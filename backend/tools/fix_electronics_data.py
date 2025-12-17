"""
Скрипт для исправления данных электроники в БД
Обходит проблему кодировки docker exec
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/tamozh_db"

# Данные для обновления (из образца техописания)
ELECTRONICS_DATA = [
    {
        "designation": "6ES7 212-1AE40-0XB0",
        "name": "Компактное ЦПУ",
        "material": "Пластик, сталь, медь",
        "manufacturer": "Siemens AG",
        "current_type": "Постоянный",
        "input_voltage": "24",
        "input_current": "12",
        "processor": "CPU 1212C",
        "ram_kb": 75,
        "rom_mb": 2,
        "dimensions": "90x100x175",
        "weight": 0.37,
        "weight_unit": "кг",
        "tnved_code": "8537109100",
        "tnved_description": "ПРОГРАММИРУЕМЫЕ КОНТРОЛЛЕРЫ С ПАМЯТЬЮ НА НАПРЯЖЕНИЕ НЕ БОЛЕЕ 1000 В",
        "condition": "Новое",
        "component_type": "electronics"
    },
    {
        "designation": "6ES7 221-3AD30-0XB0",
        "name": "Сигнальная плата дискретного ввода/вывода",
        "material": "Пластик, сталь, медь",
        "manufacturer": "Siemens AG",
        "current_type": "Постоянный",
        "input_voltage": "24",
        "input_current": "12",
        "dimensions": "38x62x21",
        "weight": 35,
        "weight_unit": "г",
        "tnved_code": "8538909200",
        "tnved_description": "ЧАСТИ, ПРЕДНАЗНАЧЕННЫЕ ИСКЛЮЧИТЕЛЬНО ИЛИ В ОСНОВНОМ ДЛЯ АППАРАТУРЫ ТОВАРНОЙ ПОЗИЦИИ 8535, 8536 ИЛИ 8537, ПРОЧИЕ, ЭЛЕКТРОННЫЕ МОДУЛИ",
        "condition": "Новое",
        "component_type": "electronics"
    },
    {
        "designation": "6ES7 231-5QD32-0XB0",
        "name": "Модуль аналогового ввода",
        "material": "Пластик, сталь, медь",
        "manufacturer": "Siemens AG",
        "current_type": "Постоянный",
        "input_voltage": "24",
        "input_current": "12",
        "dimensions": "100x75x45",
        "weight": 180,
        "weight_unit": "г",
        "tnved_code": "8538909908",
        "tnved_description": "ЧАСТИ, ПРЕДНАЗНАЧЕННЫЕ ИСКЛЮЧИТЕЛЬНО ИЛИ В ОСНОВНОМ ДЛЯ АППАРАТУРЫ ТОВАРНОЙ ПОЗИЦИИ 8535, 8536 ИЛИ 8537, ПРОЧИЕ",
        "condition": "Новое",
        "component_type": "electronics"
    },
    {
        "designation": "6AV2 123-2DB03-0AX0",
        "name": "Широкоэкранный дисплей TFT (4,3дюйма)",
        "material": "Пластик, сталь, медь",
        "manufacturer": "Siemens AG",
        "current_type": "Постоянный",
        "input_voltage": "24",
        "input_current": "125",
        "dimensions": "140x116x33",
        "weight": 0.36,
        "weight_unit": "кг",
        "tnved_code": "8537101000",
        "tnved_description": "ЦИФРОВЫЕ ПАНЕЛИ УПРАВЛЕНИЯ СО ВСТРОЕННОЙ ВЫЧИСЛИТЕЛЬНОЙ МАШИНОЙ НА НАПРЯЖЕНИЕ НЕ БОЛЕЕ 1000 В",
        "condition": "Новое",
        "component_type": "electronics"
    },
    {
        "designation": "ASD-B2-0421-B",
        "name": "Сервопривод ASD-B2",
        "material": "Электроника",
        "manufacturer": "Delta Electronics",
        "dimensions": "152x130x170",
        "weight": 1.07,
        "weight_unit": "кг",
        "condition": "Новое",
        "component_type": "electronics",
        "tnved_code": "9032890000",
        "tnved_description": "ПРИБОРЫ И УСТРОЙСТВА ДЛЯ АВТОМАТИЧЕСКОГО РЕГУЛИРОВАНИЯ ИЛИ УПРАВЛЕНИЯ",
        "specs": {
            "Род тока": "Переменный",
            "Входное напряжение, В": "220",
            "Входной ток, А": "2.6",
            "Управляющий сигнал": "Pulse/Analog",
            "Мощность, Вт": "400"
        }
    },
    {
        "designation": "ASDB2PW0001",
        "name": "Кабель питания сервопривода",
        "material": "Электроника",
        "manufacturer": "Delta Electronics",
        "condition": "Новое",
        "component_type": "electronics",
        "tnved_code": "8544429009",
        "tnved_description": "ПРОВОДНИКИ ЭЛЕКТРИЧЕСКИЕ НА НАПРЯЖЕНИЕ НЕ БОЛЕЕ 1000 В, ОСНАЩЕННЫЕ СОЕДИНИТЕЛЬНЫМИ ПРИСПОСОБЛЕНИЯМИ",
        "specs": {
            "Род тока": "Переменный",
            "Входное напряжение, В": "200-230"
        }
    },
    {
        "designation": "ASDB2EN0001",
        "name": "Кабель энкодера",
        "material": "Электроника",
        "manufacturer": "Delta Electronics",
        "condition": "Новое",
        "component_type": "electronics",
        "tnved_code": "8544429007",
        "tnved_description": "ПРОВОДНИКИ ЭЛЕКТРИЧЕСКИЕ НА НАПРЯЖЕНИЕ НЕ БОЛЕЕ 80 В, ОСНАЩЕННЫЕ СОЕДИНИТЕЛЬНЫМИ ПРИСПОСОБЛЕНИЯМИ",
        "specs": {
            "Род тока": "Постоянный",
            "Входное напряжение, В": "24"
        }
    },
    {
        "designation": "ECMA-C20604RS",
        "name": "Серводвигатель ECMA-C",
        "material": "Электромеханика",
        "manufacturer": "Delta Electronics",
        "dimensions": "60x60x166.8",
        "weight": 1.6,
        "weight_unit": "кг",
        "condition": "Новое",
        "component_type": "electronics",
        "tnved_code": "8501510000",
        "tnved_description": "ДВИГАТЕЛИ ПЕРЕМЕННОГО ТОКА МНОГОФАЗНЫЕ, МОЩНОСТЬЮ НЕ БОЛЕЕ 750 ВТ",
        "specs": {
            "Род тока": "Переменный",
            "Мощность, кВт": "0.4",
            "Напряжение, В": "220",
            "Номинальная скорость, об/мин": "3000",
            "Максимальная скорость, об/мин": "5000",
            "Номинальный момент, Нм": "1.27",
            "Максимальный момент, Нм": "3.82",
            "Тип энкодера": "Инкрементальный, 17 бит (160000 имп/об)",
            "Фланец, мм": "60",
            "Диаметр вала, мм": "14",
            "Особенности": "С сальником, без тормоза, шпоночный паз"
        }
    }
]

async def update_parts():
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        for part in ELECTRONICS_DATA:
            # Формируем SET часть запроса динамически
            set_parts = []
            params = {"designation": part["designation"]}
            
            import json
            for key, value in part.items():
                if key != "designation" and value is not None:
                    if key == "specs":
                        set_parts.append(f"{key} = CAST(:{key} AS JSONB)")
                        params[key] = json.dumps(value, ensure_ascii=False)
                    else:
                        set_parts.append(f"{key} = :{key}")
                        params[key] = value
            
            if set_parts:
                query = text(f"""
                    UPDATE public.parts 
                    SET {', '.join(set_parts)}
                    WHERE designation = :designation
                """)
                result = await conn.execute(query, params)
                print(f"Updated {part['designation']}: {result.rowcount} row(s)")
    
    await engine.dispose()
    print("\nDone! All parts updated.")

if __name__ == "__main__":
    asyncio.run(update_parts())
