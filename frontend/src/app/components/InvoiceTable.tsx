'use client';

import { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';

interface InvoiceItem {
    id?: number; // Added optional ID for keying if needed, though index is used often
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
    // Virtualization setup
    const parentRef = useRef<HTMLDivElement>(null);

    const rowVirtualizer = useVirtualizer({
        count: items.length,
        getScrollElement: () => parentRef.current,
        estimateSize: () => 60, // Reduced height as we don't have stacked buttons anymore
        overscan: 5,
    });

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
        // Add to the beginning of the list
        onUpdate([newItem, ...items]);
    };

    function handleDelete(index: number) {
        if (confirm('Вы уверены, что хотите удалить эту позицию?')) {
            const newItems = items.filter((_, i) => i !== index);
            onUpdate(newItems);
        }
    }

    // Adjusted template: Added Quantity column (60px) after Name, Reduced Dimensions column
    const GRID_TEMPLATE = "50px 150px 250px 60px 100px 80px 100px 150px 100px 80px 100px 100px";

    return (
        <div
            ref={parentRef}
            className="overflow-auto shadow-md sm:rounded-lg mt-6 h-[calc(100vh-400px)] min-h-[400px] border border-gray-200"
        >
            <div className="p-4 bg-white border-b flex justify-between items-center sticky left-0 top-0 z-20">
                <h2 className="text-lg font-semibold text-gray-700">Список деталей</h2>
                <div className="flex gap-2">
                    <button
                        onClick={onClear}
                        className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 text-sm font-medium shadow-sm transition-colors"
                    >
                        Очистить список
                    </button>
                    <button
                        onClick={handleAddRow}
                        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-sm font-medium shadow-sm transition-colors"
                    >
                        + Добавить строку
                    </button>
                </div>
            </div>

            <div className="min-w-[1400px]">
                {/* Header */}
                <div
                    className="sticky top-0 z-10 bg-gray-50 border-b border-gray-200 text-xs font-bold text-gray-700 uppercase grid items-center"
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
                                className="absolute top-0 left-0 w-full grid items-center border-b border-gray-100 hover:bg-gray-50 bg-white text-sm"
                                style={{
                                    transform: `translateY(${virtualRow.start}px)`,
                                    gridTemplateColumns: GRID_TEMPLATE,
                                }}
                            >
                                <div className="p-2 text-center text-gray-500">{index + 1}</div>
                                <div className="p-2 font-medium text-gray-900">
                                    <input
                                        type="text"
                                        value={item.designation || ''}
                                        onChange={(e) => handleChange(index, 'designation', e.target.value)}
                                        className="bg-transparent border-none focus:ring-0 w-full p-0 font-medium text-gray-900"
                                        placeholder="Обозначение"
                                    />
                                </div>
                                <div className="p-2">
                                    <input
                                        type="text"
                                        value={item.name || ''}
                                        onChange={(e) => handleChange(index, 'name', e.target.value)}
                                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2"
                                    />
                                </div>
                                <div className="p-2">
                                    <input
                                        type="text"
                                        value={item.quantity || 1}
                                        onChange={(e) => handleChange(index, 'quantity', e.target.value)}
                                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2"
                                    />
                                </div>
                                <div className="p-2">
                                    <input
                                        type="text"
                                        value={item.material || ''}
                                        onChange={(e) => handleChange(index, 'material', e.target.value)}
                                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2"
                                    />
                                </div>
                                <div className="p-2">
                                    <input
                                        type="number"
                                        step="0.001"
                                        value={item.weight || 0}
                                        onChange={(e) => handleChange(index, 'weight', parseFloat(e.target.value))}
                                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2"
                                    />
                                </div>
                                <div className="p-2">
                                    <input
                                        type="text"
                                        value={item.dimensions || ''}
                                        onChange={(e) => handleChange(index, 'dimensions', e.target.value)}
                                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2"
                                    />
                                </div>
                                <div className="p-2">
                                    <input
                                        type="text"
                                        value={item.manufacturer || ''}
                                        onChange={(e) => handleChange(index, 'manufacturer', e.target.value)}
                                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2"
                                    />
                                </div>
                                <div className="p-2">
                                    <input
                                        type="text"
                                        value={item.description || ''}
                                        onChange={(e) => handleChange(index, 'description', e.target.value)}
                                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2"
                                    />
                                </div>
                                <div className="p-2 text-center">
                                    {item.image_path ? (
                                        <img
                                            src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/images/${item.image_path}`}
                                            alt="Деталь"
                                            loading="lazy"
                                            decoding="async"
                                            className="h-12 w-12 object-cover rounded mx-auto border border-gray-200 shadow-sm"
                                            onError={(e) => {
                                                const target = e.target as HTMLImageElement;
                                                target.style.display = 'none';
                                                target.parentElement!.innerHTML = '<span class="text-gray-400 text-xs">Ошибка</span>';
                                            }}
                                        />
                                    ) : (
                                        <span className="text-gray-400 text-xs">Нет</span>
                                    )}
                                </div>
                                <div className="p-2 text-center">
                                    {item.found_in_db ? (
                                        <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded border border-green-200">Найдено</span>
                                    ) : (
                                        <span className="bg-yellow-100 text-yellow-800 text-xs font-medium px-2.5 py-0.5 rounded border border-yellow-200">Новое</span>
                                    )}
                                </div>
                                <div className="p-2 text-center">
                                    <button
                                        onClick={() => handleDelete(index)}
                                        className="text-white bg-red-600 hover:bg-red-700 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-xs px-3 py-2 focus:outline-none transition-colors shadow-sm"
                                    >
                                        Удалить
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
