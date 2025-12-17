'use client';

import { useState, useEffect } from 'react';

interface PartSpecs {
    [key: string]: string | number;
}

interface PartDetails {
    id: number;
    designation: string;
    name: string;
    material: string;
    weight: number;
    weight_unit: string;
    dimensions: string;
    description: string;
    manufacturer: string;
    condition: string;
    component_type: string;
    specs: PartSpecs | null;
    image_path: string | null;
    tnved_code: string | null;
    tnved_description: string | null;
}

interface PartDetailModalProps {
    part: PartDetails | null;
    isOpen: boolean;
    onClose: () => void;
    onSave?: (updatedPart: Partial<PartDetails>) => Promise<void>;
    isEditable?: boolean;
}

export default function PartDetailModal({
    part,
    isOpen,
    onClose,
    onSave,
    isEditable = false
}: PartDetailModalProps) {
    const [isEditing, setIsEditing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [editedPart, setEditedPart] = useState<Partial<PartDetails>>({});
    const [editedSpecs, setEditedSpecs] = useState<PartSpecs>({});

    useEffect(() => {
        if (part) {
            setEditedPart({
                material: part.material,
                dimensions: part.dimensions,
                weight: part.weight,
                weight_unit: part.weight_unit,
                description: part.description,
                manufacturer: part.manufacturer,
                condition: part.condition,
                tnved_code: part.tnved_code,
                tnved_description: part.tnved_description,
            });
            setEditedSpecs(part.specs || {});
        }
    }, [part]);

    if (!isOpen || !part) return null;

    const isElectronics = part.component_type === 'electronics' ||
        (part.specs && Object.keys(part.specs).length > 0);

    const handleSave = async () => {
        if (!onSave) return;
        setIsSaving(true);
        try {
            await onSave({
                ...editedPart,
                specs: Object.keys(editedSpecs).length > 0 ? editedSpecs : null,
            });
            setIsEditing(false);
        } catch (error) {
            console.error('Failed to save:', error);
        } finally {
            setIsSaving(false);
        }
    };

    const handleSpecChange = (key: string, value: string) => {
        setEditedSpecs(prev => ({ ...prev, [key]: value }));
    };

    const addNewSpec = () => {
        const newKey = `Параметр ${Object.keys(editedSpecs).length + 1}`;
        setEditedSpecs(prev => ({ ...prev, [newKey]: '' }));
    };

    const removeSpec = (key: string) => {
        setEditedSpecs(prev => {
            const updated = { ...prev };
            delete updated[key];
            return updated;
        });
    };

    return (
        <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="px-6 py-4 border-b bg-gray-50 flex justify-between items-center">
                    <div>
                        <h2 className="text-lg font-semibold text-gray-900">{part.name}</h2>
                        <p className="text-sm text-gray-500 font-mono">{part.designation}</p>
                    </div>
                    <div className="flex items-center gap-2">
                        {isElectronics && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                Электроника
                            </span>
                        )}
                        <button
                            onClick={onClose}
                            className="p-1 hover:bg-gray-200 rounded transition-colors"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[60vh]">
                    <div className="grid grid-cols-2 gap-4">
                        {/* Image */}
                        {part.image_path && (
                            <div className="col-span-2 flex justify-center mb-4">
                                <img
                                    src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/images/${part.image_path}`}
                                    alt={part.name}
                                    className="max-h-48 rounded-lg shadow-md object-contain"
                                />
                            </div>
                        )}

                        {/* Basic Info */}
                        <div className="space-y-3">
                            <div>
                                <label className="text-xs text-gray-500 uppercase">Материал</label>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        value={editedPart.material || ''}
                                        onChange={e => setEditedPart(prev => ({ ...prev, material: e.target.value }))}
                                        className="w-full px-3 py-2 border rounded-lg text-sm"
                                    />
                                ) : (
                                    <p className="font-medium">{part.material || '-'}</p>
                                )}
                            </div>
                            <div>
                                <label className="text-xs text-gray-500 uppercase">Размеры</label>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        value={editedPart.dimensions || ''}
                                        onChange={e => setEditedPart(prev => ({ ...prev, dimensions: e.target.value }))}
                                        className="w-full px-3 py-2 border rounded-lg text-sm"
                                    />
                                ) : (
                                    <p className="font-medium">{part.dimensions || '-'}</p>
                                )}
                            </div>
                            <div>
                                <label className="text-xs text-gray-500 uppercase">Вес</label>
                                {isEditing ? (
                                    <div className="flex gap-2">
                                        <input
                                            type="number"
                                            step="0.001"
                                            value={editedPart.weight || 0}
                                            onChange={e => setEditedPart(prev => ({ ...prev, weight: parseFloat(e.target.value) }))}
                                            className="w-full px-3 py-2 border rounded-lg text-sm"
                                        />
                                        <select
                                            value={editedPart.weight_unit || 'кг'}
                                            onChange={e => setEditedPart(prev => ({ ...prev, weight_unit: e.target.value }))}
                                            className="px-3 py-2 border rounded-lg text-sm"
                                        >
                                            <option value="кг">кг</option>
                                            <option value="г">г</option>
                                        </select>
                                    </div>
                                ) : (
                                    <p className="font-medium">{part.weight} {part.weight_unit || 'кг'}</p>
                                )}
                            </div>
                        </div>

                        <div className="space-y-3">
                            <div>
                                <label className="text-xs text-gray-500 uppercase">Производитель</label>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        value={editedPart.manufacturer || ''}
                                        onChange={e => setEditedPart(prev => ({ ...prev, manufacturer: e.target.value }))}
                                        className="w-full px-3 py-2 border rounded-lg text-sm"
                                    />
                                ) : (
                                    <p className="font-medium">{part.manufacturer || '-'}</p>
                                )}
                            </div>
                            <div>
                                <label className="text-xs text-gray-500 uppercase">Состояние</label>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        value={editedPart.condition || ''}
                                        onChange={e => setEditedPart(prev => ({ ...prev, condition: e.target.value }))}
                                        className="w-full px-3 py-2 border rounded-lg text-sm"
                                    />
                                ) : (
                                    <p className="font-medium">{part.condition || '-'}</p>
                                )}
                            </div>
                            {(part.tnved_code || isEditing) && (
                                <div>
                                    <label className="text-xs text-gray-500 uppercase">ТН ВЭД</label>
                                    {isEditing ? (
                                        <input
                                            type="text"
                                            value={editedPart.tnved_code || ''}
                                            onChange={e => setEditedPart(prev => ({ ...prev, tnved_code: e.target.value }))}
                                            className="w-full px-3 py-2 border rounded-lg text-sm"
                                            placeholder="Код ТН ВЭД"
                                        />
                                    ) : (
                                        <p className="font-medium">{part.tnved_code}</p>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Description */}
                        {(part.description || isEditing) && (
                            <div className="col-span-2">
                                <label className="text-xs text-gray-500 uppercase">Описание</label>
                                {isEditing ? (
                                    <textarea
                                        value={editedPart.description || ''}
                                        onChange={e => setEditedPart(prev => ({ ...prev, description: e.target.value }))}
                                        className="w-full px-3 py-2 border rounded-lg text-sm"
                                        rows={3}
                                    />
                                ) : (
                                    <p className="text-sm text-gray-700">{part.description}</p>
                                )}
                            </div>
                        )}

                        {/* Specs (Electronics) */}
                        {(isElectronics || Object.keys(editedSpecs).length > 0) && (
                            <div className="col-span-2 mt-4">
                                <div className="flex justify-between items-center mb-2">
                                    <label className="text-xs text-gray-500 uppercase font-semibold">
                                        Технические характеристики
                                    </label>
                                    {isEditing && (
                                        <button
                                            onClick={addNewSpec}
                                            className="text-xs text-blue-600 hover:text-blue-800"
                                        >
                                            + Добавить параметр
                                        </button>
                                    )}
                                </div>
                                <div className="bg-gray-50 rounded-lg p-3 space-y-2">
                                    {isEditing ? (
                                        Object.entries(editedSpecs).map(([key, value]) => (
                                            <div key={key} className="flex gap-2">
                                                <input
                                                    type="text"
                                                    value={key}
                                                    onChange={e => {
                                                        const newSpecs = { ...editedSpecs };
                                                        delete newSpecs[key];
                                                        newSpecs[e.target.value] = value;
                                                        setEditedSpecs(newSpecs);
                                                    }}
                                                    className="flex-1 px-2 py-1 border rounded text-sm"
                                                    placeholder="Параметр"
                                                />
                                                <input
                                                    type="text"
                                                    value={String(value)}
                                                    onChange={e => handleSpecChange(key, e.target.value)}
                                                    className="flex-1 px-2 py-1 border rounded text-sm"
                                                    placeholder="Значение"
                                                />
                                                <button
                                                    onClick={() => removeSpec(key)}
                                                    className="text-red-500 hover:text-red-700 px-2"
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                        ))
                                    ) : (
                                        part.specs && Object.entries(part.specs).map(([key, value]) => (
                                            <div key={key} className="flex justify-between text-sm">
                                                <span className="text-gray-600">{key}</span>
                                                <span className="font-medium">{String(value)}</span>
                                            </div>
                                        ))
                                    )}
                                    {!isEditing && (!part.specs || Object.keys(part.specs).length === 0) && (
                                        <p className="text-sm text-gray-400 italic">Нет характеристик</p>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                {isEditable && (
                    <div className="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3">
                        {isEditing ? (
                            <>
                                <button
                                    onClick={() => setIsEditing(false)}
                                    className="px-4 py-2 text-gray-600 hover:text-gray-800"
                                    disabled={isSaving}
                                >
                                    Отмена
                                </button>
                                <button
                                    onClick={handleSave}
                                    disabled={isSaving}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                                >
                                    {isSaving ? 'Сохранение...' : 'Сохранить'}
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={() => setIsEditing(true)}
                                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                            >
                                Редактировать
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
