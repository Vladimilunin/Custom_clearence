# План расширения базы данных

## Текущая структура таблицы `parts`

| Поле | Тип | Описание |
|------|-----|----------|
| designation | String | Обозначение (уникальный ключ) |
| name | String | Наименование |
| material | String | Материал |
| weight | Float | Масса |
| dimensions | String | Размеры |
| description | Text | Техническое описание |
| manufacturer | String | Производитель |
| condition | String | Состояние |
| image_path | String | Путь к изображению |

---

## Новые записи для электронных компонентов

### 1. ASDB2PW0001 — Delta Servo Power Supply

```sql
INSERT INTO public.parts (designation, name, material, description, manufacturer, condition, image_path) VALUES
('ASDB2PW0001', 'Блок питания сервопривода', 'Электроника', 
'Блок питания серии ASDB2 для серводвигателей Delta. Входное напряжение: 200-230В AC. Мощность: подходит для сервоусилителей до 3 кВт. Защита от перенапряжения, короткого замыкания. Корпус металлический с вентиляционными отверстиями.',
'Delta Electronics', 'Новое', 'ASDB2PW0001.webp');
```

### 2. ASDB2EN0001 — Delta Servo Driver

```sql
INSERT INTO public.parts (designation, name, material, description, manufacturer, condition, image_path) VALUES
('ASDB2EN0001', 'Сервоусилитель', 'Электроника',
'Сервоусилитель Delta серии ASDB2 с поддержкой EtherCAT. Управление положением, скоростью и моментом. Встроенный энкодер 17-бит. Диапазон мощностей: 100Вт - 3кВт. Компактный дизайн для монтажа на DIN-рейку.',
'Delta Electronics', 'Новое', 'ASDB2EN0001.webp');
```

### 3. ECMAC20604RS — Delta Servo Motor

```sql
INSERT INTO public.parts (designation, name, material, description, manufacturer, condition, image_path) VALUES
('ECMAC20604RS', 'Серводвигатель', 'Электромеханика',
'Серводвигатель Delta серии ECMA-C. Мощность: 400Вт. Номинальная скорость: 3000 об/мин. Встроенный инкрементальный энкодер 17-бит. IP65 защита. Фланец 60мм. Применение: ЧПУ станки, упаковочное оборудование, робототехника.',
'Delta Electronics', 'Новое', 'ECMAC20604RS.webp');
```

### 4. 6ES7 212-1AE40-0XB0 — Siemens S7-1200 CPU

```sql
INSERT INTO public.parts (designation, name, material, description, manufacturer, condition, image_path) VALUES
('6ES7 212-1AE40-0XB0', 'ПЛК CPU 1212C', 'Электроника',
'Программируемый логический контроллер Siemens SIMATIC S7-1200 CPU 1212C. Память: 75KB рабочая память. Входы/Выходы: 8DI/6DO/2AI. Интерфейсы: PROFINET (2-port). Напряжение питания: 24В DC. Поддержка STEP 7 (TIA Portal).',
'Siemens AG', 'Новое', '6ES7 212-1AE40-0XB0.webp');
```

### 5. 6ES7 221-3AD30-0XB0 — Digital Input Module

```sql
INSERT INTO public.parts (designation, name, material, description, manufacturer, condition, image_path) VALUES
('6ES7 221-3AD30-0XB0', 'Модуль дискретного ввода SM 1221', 'Электроника',
'Модуль дискретного ввода Siemens SIMATIC S7-1200 SM 1221. Каналы: 8 DI x 24В DC. Задержка на входе: 0.2-12.8мс (настраивается). Изоляция: 500В AC. Подключение: пружинные клеммы. Совместимость: CPU 1211C/1212C/1214C/1215C.',
'Siemens AG', 'Новое', '6ES7 221-3AD30-0XB0.webp');
```

### 6. 6ES7 231-5QD32-0XB0 — Analog Input Module

```sql
INSERT INTO public.parts (designation, name, material, description, manufacturer, condition, image_path) VALUES
('6ES7 231-5QD32-0XB0', 'Модуль аналогового ввода SM 1231', 'Электроника',
'Модуль аналогового ввода Siemens SIMATIC S7-1200 SM 1231. Каналы: 4 AI (±10В, ±5В, ±2.5В или 0-20мА). Разрешение: 16 бит. Точность: ±0.1%. Время преобразования: 0.25мс на канал. Диагностика: обрыв провода.',
'Siemens AG', 'Новое', '6ES7 231-5QD32-0XB0.webp');
```

### 7. 6AV2 123-2DB03-0AX0 — HMI KTP400 Basic

```sql
INSERT INTO public.parts (designation, name, material, description, manufacturer, condition, image_path) VALUES
('6AV2 123-2DB03-0AX0', 'Панель оператора KTP400 Basic', 'Электроника',
'Сенсорная панель оператора Siemens SIMATIC HMI KTP400 Basic. Экран: 4.3" TFT, 480x272 пикселей. 4 функциональные клавиши. Интерфейс: Ethernet (PROFINET). Конфигурация: WinCC Basic (TIA Portal). Степень защиты: IP65 (передняя панель).',
'Siemens AG', 'Новое', '6AV2 123-2DB03-0AX0.webp');
```

### 8. ASD-B2-0421-B — Delta Servo Drive

```sql
INSERT INTO public.parts (designation, name, material, description, manufacturer, condition, image_path) VALUES
('ASD-B2-0421-B', 'Сервопривод ASD-B2', 'Электроника',
'Сервопривод Delta серии ASD-B2. Мощность: 400Вт. Входное напряжение: 200-230В AC однофазное. Режимы управления: положение, скорость, момент. Функция автонастройки. Встроенное торможение. Индикаторы состояния LED. Монтаж: настенный или на DIN-рейку.',
'Delta Electronics', 'Новое', 'ASD-B2-0421-B.webp');
```

---

## Полный SQL скрипт для добавления

```sql
-- Расширение БД: электронные компоненты Delta и Siemens
-- Дата: 2025-12-17

INSERT INTO public.parts (designation, name, material, description, manufacturer, condition, image_path) VALUES
('ASDB2PW0001', 'Блок питания сервопривода', 'Электроника', 'Блок питания серии ASDB2 для серводвигателей Delta. Входное напряжение: 200-230В AC. Мощность: подходит для сервоусилителей до 3 кВт. Защита от перенапряжения, короткого замыкания.', 'Delta Electronics', 'Новое', 'ASDB2PW0001.webp'),
('ASDB2EN0001', 'Сервоусилитель', 'Электроника', 'Сервоусилитель Delta серии ASDB2 с поддержкой EtherCAT. Управление положением, скоростью и моментом. Встроенный энкодер 17-бит. Диапазон мощностей: 100Вт - 3кВт.', 'Delta Electronics', 'Новое', 'ASDB2EN0001.webp'),
('ECMAC20604RS', 'Серводвигатель ECMA-C', 'Электромеханика', 'Серводвигатель Delta серии ECMA-C. Мощность: 400Вт. Номинальная скорость: 3000 об/мин. Встроенный инкрементальный энкодер 17-бит. IP65 защита. Фланец 60мм.', 'Delta Electronics', 'Новое', 'ECMAC20604RS.webp'),
('6ES7 212-1AE40-0XB0', 'ПЛК CPU 1212C', 'Электроника', 'ПЛК Siemens SIMATIC S7-1200 CPU 1212C. Память: 75KB. Входы/Выходы: 8DI/6DO/2AI. Интерфейсы: PROFINET (2-port). Напряжение: 24В DC.', 'Siemens AG', 'Новое', '6ES7 212-1AE40-0XB0.webp'),
('6ES7 221-3AD30-0XB0', 'Модуль дискретного ввода SM 1221', 'Электроника', 'Модуль дискретного ввода Siemens S7-1200. Каналы: 8 DI x 24В DC. Задержка: 0.2-12.8мс. Изоляция: 500В AC. Пружинные клеммы.', 'Siemens AG', 'Новое', '6ES7 221-3AD30-0XB0.webp'),
('6ES7 231-5QD32-0XB0', 'Модуль аналогового ввода SM 1231', 'Электроника', 'Модуль аналогового ввода Siemens S7-1200. Каналы: 4 AI. Разрешение: 16 бит. Точность: ±0.1%. Диагностика обрыва провода.', 'Siemens AG', 'Новое', '6ES7 231-5QD32-0XB0.webp'),
('6AV2 123-2DB03-0AX0', 'Панель оператора KTP400 Basic', 'Электроника', 'HMI панель Siemens KTP400 Basic. Экран: 4.3" TFT 480x272. 4 функциональные клавиши. PROFINET. Степень защиты: IP65.', 'Siemens AG', 'Новое', '6AV2 123-2DB03-0AX0.webp'),
('ASD-B2-0421-B', 'Сервопривод ASD-B2', 'Электроника', 'Сервопривод Delta ASD-B2. Мощность: 400Вт. Вход: 200-230В AC. Режимы: положение, скорость, момент. Автонастройка.', 'Delta Electronics', 'Новое', 'ASD-B2-0421-B.webp')
ON CONFLICT (designation) DO UPDATE SET
  name = EXCLUDED.name,
  material = EXCLUDED.material,
  description = EXCLUDED.description,
  manufacturer = EXCLUDED.manufacturer,
  condition = EXCLUDED.condition,
  image_path = EXCLUDED.image_path;
```

---

## Инструкция по применению

1. Подключитесь к PostgreSQL базе данных
2. Выполните SQL скрипт выше
3. Переименуйте изображения в папке `_изображения`:
   - `ECMAC20604RS.jpg` → `ECMAC20604RS.webp` (конвертировать)
   - `6ES7 212-1AE40-0XB0.jpg` → `6ES7 212-1AE40-0XB0.webp`
   - и т.д.
4. Проверьте что изображения доступны через API
