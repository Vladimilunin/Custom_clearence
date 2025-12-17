'use client';

import { useRef, useState } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import PartDetailModal from './PartDetailModal';

interface InvoiceItem {
    id?: number;
    designation: string;
    raw_description?: string;
    name: string;
    material: string;
    weight: number;
    dimensions: string;
    description?: string;
    found_in_db: boolean;
    image_path: string | null;
    parsing_method?: string;
    manufacturer?: string;
    condition?: string;
    quantity?: number | string;
    price?: number;
    amount?: number;
}

interface InvoiceTableProps {
    items: InvoiceItem[];
    onUpdate: (items: InvoiceItem[]) => void;
    onClear: () => void;
}

export default function InvoiceTable({ items, onUpdate, onClear }: InvoiceTableProps) {
    const parentRef = useRef<HTMLDivElement>(null);
    const [selectedPart, setSelectedPart] = useState<any>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const rowVirtualizer = useVirtualizer({
        count: items.length,
        getScrollElement: () => parentRef.current,
        estimateSize: () => 56, // Standard row height
        overscan: 5,
    });

    const handleRowClick = async (item: InvoiceItem) => {
        if (!item.found_in_db) return;
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/v1/parts/?search=${encodeURIComponent(item.designation)}&limit=1`);
            if (response.ok) {
                const parts = await response.json();
                if (parts && parts.length > 0) {
                    const part = parts.find((p: any) => p.designation === item.designation) || parts[0];
                    setSelectedPart(part);
                    setIsModalOpen(true);
                }
            }
        } catch (error) {
            console.error('Error fetching part details:', error);
        }
    };

    const handleSavePart = async (updatedPart: any) => {
        if (!selectedPart) return;
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/v1/parts/${selectedPart.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedPart),
            });
            if (!response.ok) throw new Error('Failed to update part');
            const savedPart = await response.json();
            setSelectedPart(savedPart);
            const newItems = items.map(item => {
                if (item.designation === savedPart.designation) {
                    return { ...item, name: savedPart.name, material: savedPart.material, weight: savedPart.weight, dimensions: savedPart.dimensions, manufacturer: savedPart.manufacturer, description: savedPart.description };
                }
                return item;
            });
            onUpdate(newItems);
        } catch (error) {
            console.error('Error updating part:', error);
            alert('Ошибка при сохранении детали');
        }
    };

    const handleChange = (index: number, field: keyof InvoiceItem, value: string | number) => {
        const newItems = [...items];
        newItems[index] = { ...newItems[index], [field]: value };
        onUpdate(newItems);
    };

    const handleAddRow = () => {
        const newItem: InvoiceItem = {
            id: Date.now(),
            designation: '',
            name: '',
            material: '',
            weight: 0,
            dimensions: '',
            manufacturer: '',
            condition: '',
            image_path: null,
            found_in_db: false,
            quantity: 1,
            price: 0,
            amount: 0
        };
        onUpdate([newItem, ...items]);
    };

    function handleDelete(index: number) {
        if (confirm('Вы уверены, что хотите удалить эту позицию?')) {
            const newItems = items.filter((_, i) => i !== index);
            onUpdate(newItems);
        }
    }

    const GRID_TEMPLATE = "50px 150px 250px 70px 110px 90px 110px 150px 110px 90px 110px 100px";

    return (
        <div className="bg-card rounded-lg border border-border shadow-sm mt-8 overflow-hidden">
            <div className="px-6 py-4 border-b border-border flex justify-between items-center bg-card">
                <div className="flex items-center gap-3">
                    <h2 className="text-lg font-semibold text-foreground">Список деталей</h2>
                    <span className="px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground text-xs font-medium">
                        {items.length}
                    </span>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={onClear}
                        className="px-3 py-1.5 rounded-md text-sm font-medium text-destructive hover:bg-destructive/10 transition-colors"
                    >
                        Очистить
                    </button>
                    <button
                        onClick={handleAddRow}
                        className="px-3 py-1.5 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 text-sm font-medium transition-colors shadow-sm"
                    >
                        + Добавить
                    </button>
                </div>
            </div>

            <div className="overflow-auto h-[calc(100vh-400px)] min-h-[400px]" ref={parentRef}>
                <div className="min-w-[1500px]">
                    {/* Header */}
                    <div
                        className="sticky top-0 z-20 bg-card border-b border-border text-xs font-semibold text-muted-foreground uppercase tracking-wider grid items-center shadow-sm"
                        style={{ gridTemplateColumns: GRID_TEMPLATE }}
                    >
                        <div className="p-3 text-center">№</div>
                        <div className="p-3">Обозначение</div>
                        <div className="p-3">Наименование</div>
                        <div className="p-3">Кол-во</div>
                        <div className="p-3">Материал</div>
                        <div className="p-3">Вес (кг)</div>
                        <div className="p-3">Размеры</div>
                        <div className="p-3">Производитель</div>
                        <div className="p-3">Описание</div>
                        <div className="p-3 text-center">Фото</div>
                        <div className="p-3 text-center">Статус</div>
                        <div className="p-3 text-center">Действия</div>
                    </div>

                    {/* Body */}
                    <div
                        style={{
                            height: `${rowVirtualizer.getTotalSize()}px`,
                            width: '100%',
                            position: 'relative',
                        }}
                    >
                        {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                            const index = virtualRow.index;
                            const item = items[index];
                            return (
                                <div
                                    key={virtualRow.key}
                                    data-index={virtualRow.index}
                                    ref={rowVirtualizer.measureElement}
                                    className={`absolute top-0 left-0 w-full grid items-center border-b border-border text-sm transition-colors ${item.found_in_db
                                        ? 'bg-primary/5 hover:bg-primary/10 cursor-pointer'
                                        : 'bg-card hover:bg-secondary/30'
                                        }`}
                                    style={{
                                        transform: `translateY(${virtualRow.start}px)`,
                                        gridTemplateColumns: GRID_TEMPLATE,
                                    }}
                                    onClick={(e) => {
                                        if ((e.target as HTMLElement).tagName === 'INPUT' || (e.target as HTMLElement).tagName === 'BUTTON') return;
                                        handleRowClick(item);
                                    }}
                                >
                                    <div className="p-2 text-center text-muted-foreground font-mono text-xs">{index + 1}</div>
                                    <div className="p-2">
                                        <input
                                            type="text"
                                            value={item.designation || ''}
                                            onChange={(e) => handleChange(index, 'designation', e.target.value)}
                                            className="w-full bg-transparent border-none focus:ring-0 p-0 font-medium text-foreground placeholder:text-muted-foreground/50"
                                            placeholder="Обозначение"
                                        />
                                    </div>
                                    <div className="p-2">
                                        <input
                                            type="text"
                                            value={item.name || ''}
                                            onChange={(e) => handleChange(index, 'name', e.target.value)}
                                            className="w-full bg-transparent border border-transparent hover:border-border focus:border-primary/50 focus:bg-background rounded px-2 py-1 transition-all"
                                        />
                                    </div>
                                    <div className="p-2">
                                        <input
                                            type="text"
                                            value={item.quantity || 1}
                                            onChange={(e) => handleChange(index, 'quantity', e.target.value)}
                                            className="w-full bg-transparent border border-transparent hover:border-border focus:border-primary/50 focus:bg-background rounded px-2 py-1 transition-all text-center"
                                        />
                                    </div>
                                    <div className="p-2">
                                        <input
                                            type="text"
                                            value={item.material || ''}
                                            onChange={(e) => handleChange(index, 'material', e.target.value)}
                                            className="w-full bg-transparent border border-transparent hover:border-border focus:border-primary/50 focus:bg-background rounded px-2 py-1 transition-all"
                                        />
                                    </div>
                                    <div className="p-2">
                                        <input
                                            type="number"
                                            step="0.001"
                                            value={item.weight || 0}
                                            onChange={(e) => handleChange(index, 'weight', parseFloat(e.target.value))}
                                            className="w-full bg-transparent border border-transparent hover:border-border focus:border-primary/50 focus:bg-background rounded px-2 py-1 transition-all"
                                        />
                                    </div>
                                    <div className="p-2">
                                        <input
                                            type="text"
                                            value={item.dimensions || ''}
                                            onChange={(e) => handleChange(index, 'dimensions', e.target.value)}
                                            className="w-full bg-transparent border border-transparent hover:border-border focus:border-primary/50 focus:bg-background rounded px-2 py-1 transition-all"
                                        />
                                    </div>
                                    <div className="p-2">
                                        <input
                                            type="text"
                                            value={item.manufacturer || ''}
                                            onChange={(e) => handleChange(index, 'manufacturer', e.target.value)}
                                            className="w-full bg-transparent border border-transparent hover:border-border focus:border-primary/50 focus:bg-background rounded px-2 py-1 transition-all"
                                        />
                                    </div>
                                    <div className="p-2">
                                        <input
                                            type="text"
                                            value={item.description || ''}
                                            onChange={(e) => handleChange(index, 'description', e.target.value)}
                                            className="w-full bg-transparent border border-transparent hover:border-border focus:border-primary/50 focus:bg-background rounded px-2 py-1 transition-all"
                                        />
                                    </div>
                                    <div className="p-2 text-center">
                                        {item.image_path ? (
                                            <div className="relative group/img">
                                                <img
                                                    src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/images/${item.image_path}`}
                                                    alt="Деталь"
                                                    loading="lazy"
                                                    decoding="async"
                                                    className="h-8 w-8 object-cover rounded border border-border transition-transform group-hover/img:scale-150 group-hover/img:z-10 relative bg-background"
                                                    onError={(e) => {
                                                        const target = e.target as HTMLImageElement;
                                                        target.style.display = 'none';
                                                        target.parentElement!.innerHTML = '<span class="text-muted-foreground text-[10px]">Ошибка</span>';
                                                    }}
                                                />
                                            </div>
                                        ) : (
                                            <span className="text-muted-foreground/30 text-xl">•</span>
                                        )}
                                    </div>
                                    <div className="p-2 text-center">
                                        {item.found_in_db ? (
                                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-green-100 text-green-700">
                                                Найдено
                                            </span>
                                        ) : (
                                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-yellow-100 text-yellow-700">
                                                Новое
                                            </span>
                                        )}
                                    </div>
                                    <div className="p-2 text-center">
                                        <button
                                            onClick={() => handleDelete(index)}
                                            className="p-1 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded transition-colors"
                                            title="Удалить"
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
            <PartDetailModal
                part={selectedPart}
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleSavePart}
                isEditable={true}
            />
        </div>
    );
}
