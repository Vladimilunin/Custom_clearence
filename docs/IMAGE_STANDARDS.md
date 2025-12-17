# Стандарты изображений - Генератор Таможенных Документов

## Текущие стандарты приложения

### Хранение изображений (`image_processor.py`)

| Параметр | Значение |
|----------|----------|
| **Формат** | WebP |
| **Максимальный размер** | 1024 × 1024 px (пропорционально) |
| **Качество сжатия** | 80% |
| **Алгоритм ресемплинга** | LANCZOS (высокое качество) |
| **Директория** | `backend/images/` |

### Отображение в UI (`InvoiceTable.tsx`)

| Контекст | Размер |
|----------|--------|
| Таблица деталей | 48 × 48 px (object-cover, rounded) |

### Отображение в документах DOCX (`generator.py`)

| Параметр | Значение |
|----------|----------|
| **Макс. ширина** | 7.0 см |
| **Макс. высота** | 4.5 см |
| **Пропорции** | Сохраняются |
| **Формат вывода** | PNG (конвертация при вставке) |

---

## Рекомендуемые характеристики исходных изображений

Для оптимального качества исходные изображения должны соответствовать:

- **Разрешение**: минимум 800 × 600 px (рекомендуется 1024 × 768 px)
- **Пропорции**: 4:3 или 16:9 (горизонтальные)
- **Фон**: белый или прозрачный
- **Объект**: по центру, занимает 70-80% кадра
- **Освещение**: равномерное, без теней
- **Формат**: PNG или JPEG высокого качества

---

## Промпты для генерации изображений (AI Image Models)

### Универсальный промпт (для всех деталей)

```
Professional product photography of a mechanical part on pure white background. 
The part is a [НАЗВАНИЕ ДЕТАЛИ] made of [МАТЕРИАЛ]. 
Studio lighting, sharp focus, centered composition.
Clean industrial style, no shadows, no reflections.
High resolution, 4:3 aspect ratio, photorealistic.
```

### Конкретные промпты для типичных деталей

#### Втулка (Bushing)
```
Professional product photo of a precision metal bushing/sleeve on white background.
Material: bronze alloy or stainless steel with visible metallic texture.
Cylindrical shape with hollow center, machined surface finish.
Studio lighting, centered, sharp industrial photography, 4:3 ratio.
```

#### Пластина (Plate)
```
Professional product photo of a flat metal plate component on white background.
Material: aluminum or steel with brushed or machined surface.
Rectangular shape with mounting holes if applicable.
Top-down or 3/4 angle view, studio lighting, sharp focus, 4:3 ratio.
```

#### Ролик (Roller)
```
Professional product photo of a precision roller/cylinder on white background.
Material: stainless steel with polished or ground surface finish.
Cylindrical shape, may have shaft holes or bearings.
Studio lighting, centered, industrial photography style, 4:3 ratio.
```

#### Вал (Shaft)
```
Professional product photo of a precision metal shaft on white background.
Material: hardened steel or stainless steel.
Long cylindrical shape with possible stepped diameters or keyways.
Horizontal orientation, studio lighting, sharp focus, 4:3 ratio.
```

#### Кронштейн (Bracket)
```
Professional product photo of a metal mounting bracket on white background.
Material: stainless steel or aluminum with visible welds or bends.
L-shaped or custom geometry with mounting holes.
3/4 angle view, studio lighting, industrial style, 4:3 ratio.
```

#### Диск (Disk)
```
Professional product photo of a precision metal disk on white background.
Material: aluminum or steel alloy.
Flat circular shape with possible center hole or pattern.
Top-down or slight angle view, studio lighting, 4:3 ratio.
```

---

## Скрипт массовой обработки существующих изображений

Для конвертации существующих JPG файлов в стандарт приложения используйте:

```python
# backend/tools/convert_all_images.py
from PIL import Image
import os

INPUT_DIR = "path/to/source_images"
OUTPUT_DIR = "backend/images"
MAX_DIM = 1024
QUALITY = 80

for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        img_path = os.path.join(INPUT_DIR, filename)
        with Image.open(img_path) as img:
            # Resize if needed
            w, h = img.size
            if w > MAX_DIM or h > MAX_DIM:
                ratio = min(MAX_DIM/w, MAX_DIM/h)
                img = img.resize((int(w*ratio), int(h*ratio)), Image.LANCZOS)
            
            # Convert to WebP
            out_name = os.path.splitext(filename)[0] + ".webp"
            out_path = os.path.join(OUTPUT_DIR, out_name)
            img.save(out_path, "WEBP", quality=QUALITY)
            print(f"Converted: {filename} -> {out_name}")
```
