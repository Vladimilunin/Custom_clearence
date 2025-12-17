# Промпты для AI-генерации изображений деталей

## Стандарт изображений приложения

**Технические требования:**
- Размер: 1024×768 px (4:3) или 1024×576 px (16:9)
- Формат: WebP, качество 80%
- Фон: чистый белый (#FFFFFF)

**Стиль фотографии:**
- Студийное освещение, мягкие тени
- Деталь в центре кадра, занимает 70-80% площади
- Ракурс: изометрический (3/4 сверху-сбоку) для объёмных деталей
- Ракурс: вид сверху для плоских деталей (пластины, диски)

---

## Базовый промпт (шаблон)

```
Professional industrial product photography on pure white background.
Subject: [НАЗВАНИЕ ДЕТАЛИ] made of [МАТЕРИАЛ].
Camera angle: [РАКУРС].
Composition: centered, object fills 75% of frame.
Lighting: soft studio lighting from top-left, subtle shadow on right.
Style: clean technical catalog photo, sharp focus, photorealistic.
Dimensions: 4:3 aspect ratio, high resolution.
No reflections, no gradients, no additional objects.
```

---

## Готовые промпты по типам деталей

### 1. Втулка / Bushing (цилиндрическая с отверстием)

```
Professional industrial product photography on pure white background.
Subject: precision bronze bushing/sleeve with hollow center.
Material: ZCuSn10Pb1 bronze alloy with golden-brown metallic surface.
Camera angle: isometric 3/4 view from top-right, showing both outer cylinder and inner hole.
Composition: centered, single object fills 75% of frame.
Lighting: soft studio lighting from top-left, subtle shadow on bottom-right.
Style: clean technical catalog photo, sharp focus on machined surface texture.
Dimensions: 4:3 aspect ratio, 1024x768 pixels.
No reflections, no gradients, pure white background #FFFFFF.
```

### 2. Вал / Shaft (длинный цилиндр)

```
Professional industrial product photography on pure white background.
Subject: precision metal shaft with polished surface.
Material: SUS304 stainless steel with mirror-like metallic finish.
Camera angle: horizontal position, slight 15-degree tilt upward to show roundness.
Composition: centered horizontally, shaft extends across 80% of frame width.
Lighting: soft studio lighting from top, even highlights along length.
Style: clean technical catalog photo, sharp focus on surface finish.
Dimensions: 16:9 aspect ratio, 1024x576 pixels (for long parts).
No reflections, no gradients, pure white background #FFFFFF.
```

### 3. Пластина / Plate (плоская деталь)

```
Professional industrial product photography on pure white background.
Subject: flat rectangular metal plate with mounting holes.
Material: 2024-T4 aluminum alloy with matte machined surface.
Camera angle: top-down view at 90 degrees, or slight 10-degree tilt to show thickness.
Composition: centered, plate fills 70% of frame.
Lighting: even soft lighting from above, minimal shadow.
Style: clean technical catalog photo, visible surface texture and edge finish.
Dimensions: 4:3 aspect ratio, 1024x768 pixels.
No reflections, no gradients, pure white background #FFFFFF.
```

### 4. Ролик / Roller (короткий цилиндр)

```
Professional industrial product photography on pure white background.
Subject: precision cylindrical roller with ground surface.
Material: SUS316L stainless steel with satin finish.
Camera angle: isometric 3/4 view showing both flat end and curved surface.
Composition: centered, roller fills 65% of frame.
Lighting: soft studio lighting from top-left, highlight on curved surface.
Style: clean technical catalog photo, sharp focus on surface quality.
Dimensions: 4:3 aspect ratio, 1024x768 pixels.
No reflections, no gradients, pure white background #FFFFFF.
```

### 5. Кронштейн / Bracket (L-образная или сложная форма)

```
Professional industrial product photography on pure white background.
Subject: L-shaped metal mounting bracket with screw holes.
Material: SUS304 stainless steel with brushed finish.
Camera angle: isometric 3/4 view showing all three dimensions and mounting holes.
Composition: centered, bracket fills 70% of frame with main angle facing camera.
Lighting: soft studio lighting from two sources, showing form and depth.
Style: clean technical catalog photo, visible welds/bends if present.
Dimensions: 4:3 aspect ratio, 1024x768 pixels.
No reflections, no gradients, pure white background #FFFFFF.
```

### 6. Диск / Disk (плоский круглый)

```
Professional industrial product photography on pure white background.
Subject: flat circular metal disk with center hole.
Material: 2024-T4 aluminum alloy with machined surface.
Camera angle: slight 20-degree angle from top showing thickness and hole.
Composition: centered, disk fills 65% of frame.
Lighting: soft ring light effect, even illumination.
Style: clean technical catalog photo, visible concentric machining marks.
Dimensions: 4:3 aspect ratio, 1024x768 pixels.
No reflections, no gradients, pure white background #FFFFFF.
```

### 7. Фиксатор / Fixator (мелкая крепёжная деталь)

```
Professional industrial product photography on pure white background.
Subject: small precision fixator/retainer clip.
Material: stainless steel or bronze alloy with functional surface.
Camera angle: isometric 3/4 view, macro photography style.
Composition: centered, part fills 60% of frame with clear detail visibility.
Lighting: soft macro lighting, sharp shadows for depth perception.
Style: clean technical catalog photo, extreme sharpness on small features.
Dimensions: 4:3 aspect ratio, 1024x768 pixels.
No reflections, no gradients, pure white background #FFFFFF.
```

### 8. Корпус / Housing (сложная 3D форма)

```
Professional industrial product photography on pure white background.
Subject: precision machined metal housing/enclosure.
Material: aluminum alloy with anodized or machined finish.
Camera angle: isometric 3/4 view from front-top-right showing openings and features.
Composition: centered, housing fills 75% of frame.
Lighting: three-point studio lighting, showing all cavities and surfaces.
Style: clean technical catalog photo, visible internal features if open.
Dimensions: 4:3 aspect ratio, 1024x768 pixels.
No reflections, no gradients, pure white background #FFFFFF.
```

---

## Материалы и их визуальные описания

| Материал | Визуальное описание для промпта |
|----------|--------------------------------|
| **SUS304/SUS316L** | polished stainless steel, mirror-like silver surface |
| **2024-T4** | matte aluminum, light gray with subtle texture |
| **ZCuSn10Pb1** | bronze alloy, golden-brown with slight patina |
| **Steel (hardened)** | dark steel, deep gray with slight blue tint |
| **Brass** | bright yellow-gold metallic surface |

---

## Примеры использования

**Для детали R1.06.01.003 (Втулка из ZCuSn10Pb1):**
```
Professional industrial product photography on pure white background.
Subject: precision bronze bushing R1.06.01.003 with hollow center bore.
Material: ZCuSn10Pb1 bronze alloy, golden-brown with machined texture.
Camera angle: isometric 3/4 view from top-right, showing cylindrical form and hole.
Composition: centered, fills 70% of frame.
Lighting: soft studio from top-left, subtle warm shadow.
Style: technical catalog, sharp focus, photorealistic.
4:3 ratio, 1024x768px, pure white #FFFFFF background.
```
