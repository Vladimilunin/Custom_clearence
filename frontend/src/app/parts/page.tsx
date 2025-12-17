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
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

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
        <main className="min-h-screen p-8 bg-background">
            <div className="max-w-[1600px] mx-auto space-y-6">
                {/* Header */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-foreground tracking-tight">
                            База Данных
                        </h1>
                        <p className="text-muted-foreground mt-1 text-sm">
                            Управление номенклатурой и техническими описаниями
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="flex bg-secondary/50 p-1 rounded-lg border border-border">
                            <button
                                onClick={() => setViewMode('grid')}
                                className={`p-1.5 rounded-md transition-all ${viewMode === 'grid' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                                title="Сетка"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                                </svg>
                            </button>
                            <button
                                onClick={() => setViewMode('list')}
                                className={`p-1.5 rounded-md transition-all ${viewMode === 'list' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                                title="Список"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                            </button>
                        </div>
                        <Link
                            href="/"
                            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                            </svg>
                            <span>К Генератору</span>
                        </Link>
                    </div>
                </div>

                {/* Search Bar */}
                <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <svg className="h-5 w-5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </div>
                    <input
                        type="text"
                        placeholder="Поиск по обозначению, наименованию или характеристикам..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-all shadow-sm"
                    />
                </div>

                {/* Content */}
                {isLoading ? (
                    <div className="flex flex-col items-center justify-center py-20">
                        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
                        <p className="text-sm font-medium text-muted-foreground">Загрузка базы данных...</p>
                    </div>
                ) : (
                    <>
                        {viewMode === 'grid' ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
                                {filteredParts.map((part) => (
                                    <div
                                        key={part.id}
                                        onClick={() => handlePartClick(part)}
                                        className="group bg-card border border-border rounded-lg overflow-hidden hover:border-primary/50 hover:shadow-md transition-all duration-200 cursor-pointer flex flex-col h-[280px]"
                                    >
                                        {/* Image Area */}
                                        <div className="relative h-36 bg-secondary/20 p-4 flex items-center justify-center overflow-hidden border-b border-border/50">
                                            {part.image_path ? (
                                                <img
                                                    src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/images/${part.image_path}`}
                                                    alt={part.designation}
                                                    className="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105"
                                                    loading="lazy"
                                                />
                                            ) : (
                                                <div className="flex flex-col items-center justify-center text-muted-foreground/30">
                                                    <svg className="w-10 h-10 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                                    </svg>
                                                    <span className="text-xs font-medium">Нет фото</span>
                                                </div>
                                            )}

                                            {/* Badges */}
                                            <div className="absolute top-2 right-2 flex flex-col gap-1 items-end">
                                                {part.component_type === 'electronics' && (
                                                    <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 text-[10px] font-semibold rounded shadow-sm">
                                                        EL
                                                    </span>
                                                )}
                                                {part.component_type === 'cnc' && (
                                                    <span className="px-1.5 py-0.5 bg-purple-100 text-purple-700 text-[10px] font-semibold rounded shadow-sm">
                                                        ЧПУ
                                                    </span>
                                                )}
                                                {part.component_type === 'fitting' && (
                                                    <span className="px-1.5 py-0.5 bg-green-100 text-green-700 text-[10px] font-semibold rounded shadow-sm">
                                                        Фит
                                                    </span>
                                                )}
                                            </div>
                                        </div>

                                        {/* Content Area */}
                                        <div className="p-4 flex flex-col flex-1">
                                            <div className="mb-auto">
                                                <h3 className="font-semibold text-foreground text-sm line-clamp-2 mb-1 group-hover:text-primary transition-colors">
                                                    {part.name}
                                                </h3>
                                                <p className="text-xs font-mono text-muted-foreground truncate">
                                                    {part.designation}
                                                </p>
                                            </div>

                                            <div className="mt-3 pt-3 border-t border-border/50 grid grid-cols-2 gap-y-1 text-xs text-muted-foreground">
                                                <div>
                                                    <span className="block text-[10px] uppercase tracking-wider opacity-70">Материал</span>
                                                    <span className="font-medium text-foreground truncate block">{part.material || '—'}</span>
                                                </div>
                                                <div className="text-right">
                                                    <span className="block text-[10px] uppercase tracking-wider opacity-70">Вес</span>
                                                    <span className="font-medium text-foreground">{part.weight} {part.weight_unit}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="bg-card border border-border rounded-lg overflow-hidden shadow-sm">
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm text-left">
                                        <thead className="text-xs text-muted-foreground uppercase bg-secondary/50 border-b border-border">
                                            <tr>
                                                <th className="px-4 py-3 font-semibold">Обозначение</th>
                                                <th className="px-4 py-3 font-semibold">Наименование</th>
                                                <th className="px-4 py-3 font-semibold">Материал</th>
                                                <th className="px-4 py-3 font-semibold text-right">Вес</th>
                                                <th className="px-4 py-3 font-semibold">Производитель</th>
                                                <th className="px-4 py-3 font-semibold text-center">Тип</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-border">
                                            {filteredParts.map((part) => (
                                                <tr
                                                    key={part.id}
                                                    onClick={() => handlePartClick(part)}
                                                    className="bg-card hover:bg-secondary/30 cursor-pointer transition-colors"
                                                >
                                                    <td className="px-4 py-3 font-mono text-xs font-medium text-foreground">
                                                        {part.designation}
                                                    </td>
                                                    <td className="px-4 py-3 font-medium text-foreground">
                                                        {part.name}
                                                    </td>
                                                    <td className="px-4 py-3 text-muted-foreground">
                                                        {part.material || '—'}
                                                    </td>
                                                    <td className="px-4 py-3 text-right text-muted-foreground">
                                                        {part.weight} {part.weight_unit}
                                                    </td>
                                                    <td className="px-4 py-3 text-muted-foreground">
                                                        {part.manufacturer || '—'}
                                                    </td>
                                                    <td className="px-4 py-3 text-center">
                                                        {part.component_type === 'electronics' && (
                                                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-[10px] font-medium rounded-full">
                                                                Электроника
                                                            </span>
                                                        )}
                                                        {part.component_type === 'cnc' && (
                                                            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-[10px] font-medium rounded-full">
                                                                ЧПУ
                                                            </span>
                                                        )}
                                                        {part.component_type === 'fitting' && (
                                                            <span className="px-2 py-0.5 bg-green-100 text-green-700 text-[10px] font-medium rounded-full">
                                                                Фитинг
                                                            </span>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                    </>
                )}
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
