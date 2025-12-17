'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import PartDetailModal from '../components/PartDetailModal';

interface Part {
    id: number;
    designation: string;
    name: string;
    material: string;
    weight: number;
    weight_unit: string;
    dimensions: string;
    description: string;
    section: string;
    image_path: string | null;
    manufacturer: string;
    condition: string;
    component_type: string;
    specs: any;
    tnved_code: string | null;
    tnved_description: string | null;
}

export default function PartsPage() {
    const [parts, setParts] = useState<Part[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [selectedPart, setSelectedPart] = useState<Part | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

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

    const handlePartClick = (part: Part) => {
        setSelectedPart(part);
        setIsModalOpen(true);
    };

    const handleSavePart = async (updatedPart: Partial<Part>) => {
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

            // Update local state
            setParts(parts.map(p => p.id === savedPart.id ? savedPart : p));
            setSelectedPart(savedPart); // Update modal with saved data

        } catch (error) {
            console.error('Error updating part:', error);
            alert('Ошибка при сохранении детали');
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
                                        <th className="px-6 py-3">Вес</th>
                                        <th className="px-6 py-3">Размеры</th>
                                        <th className="px-6 py-3">Тип</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredParts.map((part) => (
                                        <tr
                                            key={part.id}
                                            className="bg-white border-b hover:bg-blue-50 cursor-pointer transition-colors"
                                            onClick={() => handlePartClick(part)}
                                        >
                                            <td className="px-6 py-4 font-medium text-gray-900">{part.designation}</td>
                                            <td className="px-6 py-4">{part.name}</td>
                                            <td className="px-6 py-4">
                                                {part.image_path ? (
                                                    <img
                                                        src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/images/${part.image_path}`}
                                                        alt={part.designation}
                                                        className="h-10 w-10 object-cover rounded border border-gray-200"
                                                        loading="lazy"
                                                    />
                                                ) : (
                                                    <span className="text-gray-400 text-xs">Нет</span>
                                                )}
                                            </td>
                                            <td className="px-6 py-4">{part.material}</td>
                                            <td className="px-6 py-4">{part.weight} {part.weight_unit}</td>
                                            <td className="px-6 py-4">{part.dimensions}</td>
                                            <td className="px-6 py-4">
                                                {part.component_type === 'electronics' ? (
                                                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                                        Электроника
                                                    </span>
                                                ) : (
                                                    <span className="text-gray-500">-</span>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            <PartDetailModal
                part={selectedPart}
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleSavePart}
                isEditable={true}
            />
        </main>
    );
}
