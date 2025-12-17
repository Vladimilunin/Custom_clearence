'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Part {
    id: number;
    designation: string;
    name: string;
    material: string;
    weight: number;
    dimensions: string;
    description: string;
    section: string;
    image_path: string | null;
}

export default function PartsPage() {
    const [parts, setParts] = useState<Part[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [search, setSearch] = useState('');

    useEffect(() => {
        fetchParts();
    }, []);

    const fetchParts = async () => {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/v1/parts/?limit=1000`);
            if (!response.ok) throw new Error('Failed to fetch parts');
            const data = await response.json();
            setParts(data);
        } catch (error) {
            console.error('Error fetching parts:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleUpdate = async (id: number, field: keyof Part, value: string | number) => {
        // Optimistic update
        setParts(parts.map(p => p.id === id ? { ...p, [field]: value } : p));

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/v1/parts/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ [field]: value }),
            });
            if (!response.ok) throw new Error('Failed to update part');
        } catch (error) {
            console.error('Error updating part:', error);
            // Revert on error (could be improved)
            fetchParts();
        }
    };

    const filteredParts = parts.filter(part =>
        part.designation.toLowerCase().includes(search.toLowerCase()) ||
        (part.name && part.name.toLowerCase().includes(search.toLowerCase()))
    );

    return (
        <main className="min-h-screen p-8 bg-gray-50">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">База Данных Деталей</h1>
                    <Link href="/" className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">
                        &larr; Назад к Генератору
                    </Link>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm">
                    <div className="mb-4">
                        <input
                            type="text"
                            placeholder="Поиск по обозначению или наименованию..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full p-2 border rounded-md"
                        />
                    </div>

                    {isLoading ? (
                        <div className="text-center py-4">Загрузка...</div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left text-gray-500">
                                <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3">Обозначение</th>
                                        <th className="px-6 py-3">Наименование</th>
                                        <th className="px-6 py-3">Фото</th>
                                        <th className="px-6 py-3">Материал</th>
                                        <th className="px-6 py-3">Вес (кг)</th>
                                        <th className="px-6 py-3">Размеры</th>
                                        <th className="px-6 py-3">Описание</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredParts.map((part) => (
                                        <tr key={part.id} className="bg-white border-b hover:bg-gray-50">
                                            <td className="px-6 py-4 font-medium text-gray-900">{part.designation}</td>
                                            <td className="px-6 py-4">
                                                <input
                                                    type="text"
                                                    value={part.name || ''}
                                                    onChange={(e) => handleUpdate(part.id, 'name', e.target.value)}
                                                    className="bg-transparent border-b border-transparent focus:border-blue-500 focus:outline-none w-full"
                                                />
                                            </td>
                                            <td className="px-6 py-4">
                                                {part.image_path ? (
                                                    <a href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/images/${part.image_path}`} target="_blank" rel="noopener noreferrer">
                                                        <img
                                                            src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/images/${part.image_path}`}
                                                            alt={part.designation}
                                                            className="h-10 w-10 object-cover rounded border border-gray-200"
                                                        />
                                                    </a>
                                                ) : (
                                                    <span className="text-gray-400 text-xs">Нет</span>
                                                )}
                                            </td>
                                            <td className="px-6 py-4">
                                                <input
                                                    type="text"
                                                    value={part.material || ''}
                                                    onChange={(e) => handleUpdate(part.id, 'material', e.target.value)}
                                                    className="bg-transparent border-b border-transparent focus:border-blue-500 focus:outline-none w-full"
                                                />
                                            </td>
                                            <td className="px-6 py-4">
                                                <input
                                                    type="number"
                                                    step="0.001"
                                                    value={part.weight || 0}
                                                    onChange={(e) => handleUpdate(part.id, 'weight', parseFloat(e.target.value))}
                                                    className="bg-transparent border-b border-transparent focus:border-blue-500 focus:outline-none w-20"
                                                />
                                            </td>
                                            <td className="px-6 py-4">
                                                <input
                                                    type="text"
                                                    value={part.dimensions || ''}
                                                    onChange={(e) => handleUpdate(part.id, 'dimensions', e.target.value)}
                                                    className="bg-transparent border-b border-transparent focus:border-blue-500 focus:outline-none w-full"
                                                />
                                            </td>
                                            <td className="px-6 py-4">
                                                <input
                                                    type="text"
                                                    value={part.description || ''}
                                                    onChange={(e) => handleUpdate(part.id, 'description', e.target.value)}
                                                    className="bg-transparent border-b border-transparent focus:border-blue-500 focus:outline-none w-full"
                                                />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
}
