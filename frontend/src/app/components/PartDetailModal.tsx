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
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm transition-opacity duration-200"
            onClick={onClose}
        >
            <div
                className="bg-background rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col border border-border animate-in zoom-in-95 duration-200"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="px-6 py-4 border-b border-border bg-secondary/30 flex justify-between items-center">
                    <div>
                        <h2 className="text-lg font-bold text-foreground tracking-tight">{part.name}</h2>
                        <p className="text-sm text-muted-foreground font-mono mt-0.5">{part.designation}</p>
                    </div>
                    <div className="flex items-center gap-3">
                        {isElectronics && (
                            <span className="px-2.5 py-0.5 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                                Электроника
                            </span>
                        )}
                        <button
                            onClick={onClose}
                            className="p-1.5 hover:bg-secondary rounded-md transition-colors text-muted-foreground hover:text-foreground"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto flex-1 custom-scrollbar">
                    <div className="grid grid-cols-2 gap-6">
                        {/* Image */}
                        {part.image_path && (
                            <div className="col-span-2 flex justify-center mb-2">
                                <div className="relative group">
                                    <img
                                        src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/images/${part.image_path}`}
                                        alt={part.name}
                                        className="relative max-h-56 rounded-lg shadow-sm object-contain bg-secondary/10 border border-border"
                                    />
                                </div>
                            </div>
                        )}

                        {/* Basic Info */}
                        <div className="space-y-4">
                            <div className="space-y-1.5">
                                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Материал</label>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        value={editedPart.material || ''}
                                        onChange={e => setEditedPart(prev => ({ ...prev, material: e.target.value }))}
                                        className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-all"
                                    />
                                ) : (
                                    <p className="font-medium text-foreground">{part.material || '—'}</p>
                                )}
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Размеры</label>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        value={editedPart.dimensions || ''}
                                        onChange={e => setEditedPart(prev => ({ ...prev, dimensions: e.target.value }))}
                                        className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-all"
                                    />
                                ) : (
                                    <p className="font-medium text-foreground">{part.dimensions || '—'}</p>
                                )}
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Вес</label>
                                {isEditing ? (
                                    <div className="flex gap-2">
                                        <input
                                            type="number"
                                            step="0.001"
                                            value={editedPart.weight || 0}
                                            onChange={e => setEditedPart(prev => ({ ...prev, weight: parseFloat(e.target.value) }))}
                                            className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-all"
                                        />
                                        <select
                                            value={editedPart.weight_unit || 'кг'}
                                            onChange={e => setEditedPart(prev => ({ ...prev, weight_unit: e.target.value }))}
                                            className="px-3 py-2 bg-background border border-border rounded-md text-sm focus:ring-1 focus:ring-primary outline-none"
                                        >
                                            <option value="кг">кг</option>
                                            <option value="г">г</option>
                                        </select>
                                    </div>
                                ) : (
                                    <p className="font-medium text-foreground">{part.weight} {part.weight_unit || 'кг'}</p>
                                )}
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="space-y-1.5">
                                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Производитель</label>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        value={editedPart.manufacturer || ''}
                                        onChange={e => setEditedPart(prev => ({ ...prev, manufacturer: e.target.value }))}
                                        className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-all"
                                    />
                                ) : (
                                    <p className="font-medium text-foreground">{part.manufacturer || '—'}</p>
                                )}
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Состояние</label>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        value={editedPart.condition || ''}
                                        onChange={e => setEditedPart(prev => ({ ...prev, condition: e.target.value }))}
                                        className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-all"
                                    />
                                ) : (
                                    <p className="font-medium text-foreground">{part.condition || '—'}</p>
                                )}
                            </div>
                            {(part.tnved_code || isEditing) && (
                                <div className="space-y-1.5">
                                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">ТН ВЭД</label>
                                    {isEditing ? (
                                        <input
                                            type="text"
                                            value={editedPart.tnved_code || ''}
                                            onChange={e => setEditedPart(prev => ({ ...prev, tnved_code: e.target.value }))}
                                            className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-all"
                                            placeholder="Код ТН ВЭД"
                                        />
                                    ) : (
                                        <p className="font-medium text-foreground tracking-wide">{part.tnved_code}</p>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Description */}
                        {(part.description || isEditing) && (
                            <div className="col-span-2 space-y-1.5">
                                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Описание</label>
                                {isEditing ? (
                                    <textarea
                                        value={editedPart.description || ''}
                                        onChange={e => setEditedPart(prev => ({ ...prev, description: e.target.value }))}
                                        className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-all"
                                        rows={3}
                                    />
                                ) : (
                                    <p className="text-sm text-foreground/80 leading-relaxed bg-secondary/30 p-3 rounded-md border border-border">
                                        {part.description}
                                    </p>
                                )}
                            </div>
                        )}

                        {/* Specs (Electronics) */}
                        {(isElectronics || Object.keys(editedSpecs).length > 0) && (
                            <div className="col-span-2 mt-2">
                                <div className="flex justify-between items-center mb-3">
                                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                        Технические характеристики
                                    </label>
                                    {isEditing && (
                                        <button
                                            onClick={addNewSpec}
                                            className="text-xs font-medium text-primary hover:text-primary/80 transition-colors"
                                        >
                                            + Добавить параметр
                                        </button>
                                    )}
                                </div>
                                <div className="bg-secondary/20 rounded-lg p-4 space-y-2 border border-border">
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
                                                    className="flex-1 px-3 py-1.5 bg-background border border-border rounded-md text-sm focus:ring-1 focus:ring-primary outline-none"
                                                    placeholder="Параметр"
                                                />
                                                <input
                                                    type="text"
                                                    value={String(value)}
                                                    onChange={e => handleSpecChange(key, e.target.value)}
                                                    className="flex-1 px-3 py-1.5 bg-background border border-border rounded-md text-sm focus:ring-1 focus:ring-primary outline-none"
                                                    placeholder="Значение"
                                                />
                                                <button
                                                    onClick={() => removeSpec(key)}
                                                    className="text-destructive hover:text-destructive/80 px-2 transition-colors"
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                        ))
                                    ) : (
                                        part.specs && Object.entries(part.specs).map(([key, value]) => (
                                            <div key={key} className="flex justify-between text-sm py-1 border-b border-border/30 last:border-0">
                                                <span className="text-muted-foreground">{key}</span>
                                                <span className="font-medium text-foreground">{String(value)}</span>
                                            </div>
                                        ))
                                    )}
                                    {!isEditing && (!part.specs || Object.keys(part.specs).length === 0) && (
                                        <p className="text-sm text-muted-foreground italic text-center py-2">Нет характеристик</p>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                {isEditable && (
                    <div className="px-6 py-4 border-t border-border bg-secondary/30 flex justify-end gap-3">
                        {isEditing ? (
                            <>
                                <button
                                    onClick={() => setIsEditing(false)}
                                    className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                                    disabled={isSaving}
                                >
                                    Отмена
                                </button>
                                <button
                                    onClick={handleSave}
                                    disabled={isSaving}
                                    className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 text-sm font-medium shadow-sm transition-colors"
                                >
                                    {isSaving ? 'Сохранение...' : 'Сохранить'}
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={() => setIsEditing(true)}
                                className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 text-sm font-medium transition-colors border border-border"
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
