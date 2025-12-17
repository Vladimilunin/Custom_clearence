'use client';

import { useState } from 'react';
import FileUpload from './components/FileUpload';
import InvoiceTable from './components/InvoiceTable';
import Link from 'next/link';

interface InvoiceItem {
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
  quantity?: number | string;
}

export default function Home() {
  const [items, setItems] = useState<InvoiceItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const [parsingMethod, setParsingMethod] = useState('openrouter_gemini_2_5_flash_lite');
  const [apiKey, setApiKey] = useState('');
  const [debugInfo, setDebugInfo] = useState<any>(null);

  const handleUpload = async (file: File) => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('method', parsingMethod);
    if (apiKey) {
      formData.append('api_key', apiKey);
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/invoices/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Ошибка загрузки');
      }

      const data = await response.json();

      // Append new items instead of replacing
      // Initialize manufacturer for new items with the supplier from THIS invoice
      const newInvoiceSupplier = data.metadata?.supplier || reportMetadata.supplier;

      const newItems = data.items.map((item: InvoiceItem) => ({
        ...item,
        manufacturer: newInvoiceSupplier
      }));

      setItems(prev => [...prev, ...newItems]);
      setDebugInfo(data.debug_info);

      if (data.metadata) {
        // Only update metadata if it's the first upload or if explicitly desired?
        // Maybe just update contract info but keep supplier if user set it?
        // For now, let's update if empty, or just let user edit.
        setReportMetadata(prev => ({
          ...prev,
          contract_no: data.metadata.invoice_number || prev.contract_no,
          contract_date: data.metadata.invoice_date || prev.contract_date,
          // Don't overwrite supplier if we are appending, unless it was default?
          // Let's leave supplier as is to avoid confusion when appending from different supplier.
        }));
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Не удалось загрузить инвойс');
    } finally {
      setIsLoading(false);
    }
  };

  const [reportMetadata, setReportMetadata] = useState({
    country_of_origin: 'Китай',
    contract_no: '',
    contract_date: '',
    supplier: 'Dongguan City Fangling Precision Mould Co., Ltd.',
    invoice_no: '',
    invoice_date: '',
    waybill_no: '',
  });

  const [docSelection, setDocSelection] = useState({
    gen_tech_desc: true,
    gen_non_insurance: false,
    gen_decision_130: false,
    add_facsimile: false
  });

  const handleGenerate = async () => {
    if (items.length === 0) {
      alert('Список товаров пуст!');
      return;
    }

    setIsGenerating(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/invoices/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          items: items,
          country_of_origin: reportMetadata.country_of_origin,
          contract_no: reportMetadata.contract_no,
          contract_date: reportMetadata.contract_date,
          supplier: reportMetadata.supplier,
          invoice_no: reportMetadata.invoice_no,
          invoice_date: reportMetadata.invoice_date,
          waybill_no: reportMetadata.waybill_no,
          gen_tech_desc: docSelection.gen_tech_desc,
          gen_non_insurance: docSelection.gen_non_insurance,
          gen_decision_130: docSelection.gen_decision_130,
          add_facsimile: docSelection.add_facsimile
        }),
      });

      if (!response.ok) {
        throw new Error('Ошибка генерации отчета');
      }

      // Handle file download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      // Try to get filename from header
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'report.docx';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        if (filenameMatch && filenameMatch.length === 2) {
          filename = filenameMatch[1];
        }
      } else {
        // Fallback based on selection
        const selectedCount = [
          docSelection.gen_tech_desc,
          docSelection.gen_non_insurance,
          docSelection.gen_decision_130
        ].filter(Boolean).length;

        if (selectedCount === 1) {
          if (docSelection.gen_tech_desc) filename = 'Technical_Description.docx';
          else if (docSelection.gen_non_insurance) filename = 'Non_Insurance_Letter.docx';
          else if (docSelection.gen_decision_130) filename = 'Decision_130_Notification.docx';
        } else {
          filename = 'Documents.zip';
        }
      }

      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Не удалось сгенерировать отчет');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Генератор Технического Описания</h1>
          <Link href="/parts" className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">
            База Данных Деталей &rarr;
          </Link>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
          <h2 className="text-xl font-semibold mb-4">1. Загрузка Инвойса</h2>

          <div className="mb-6 flex flex-col md:flex-row gap-4">
            <div className="w-full md:w-1/3">
              <label className="block text-sm font-medium text-gray-700 mb-1">Метод Парсинга</label>
              <select
                value={parsingMethod}
                onChange={(e) => setParsingMethod(e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
              >

                <option value="openrouter_gemini_2_5_flash_lite">OpenRouter (Gemini 2.5 Flash Lite)</option>
                <option value="siliconflow_qwen">SiliconFlow (Qwen 3 VL)</option>
                <option value="deepseek_v3">DeepSeek V3</option>

              </select>
            </div>
            <div className="w-full md:w-2/3">
              <label className="block text-sm font-medium text-gray-700 mb-1">API Key (Gemini или OpenRouter)</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Оставьте пустым для использования ключа по умолчанию"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
              />
            </div>
          </div>

          <FileUpload onUpload={handleUpload} isLoading={isLoading} />

          {debugInfo && (
            <div className="mt-4 p-4 bg-gray-50 rounded-md border text-sm">
              <h3 className="font-semibold mb-2">Детали Парсинга (Debug Info):</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div>
                  <span className="font-medium">Использованный метод:</span> {debugInfo.method_used}
                </div>
                {debugInfo.gemini_model && (
                  <div>
                    <span className="font-medium">Модель:</span> {debugInfo.gemini_model}
                  </div>
                )}
                {debugInfo.token_usage && (
                  <div className="col-span-2 mt-2">
                    <p className="font-medium">Использование токенов:</p>
                    <ul className="list-disc list-inside pl-2 text-gray-600">
                      <li>Токены промпта: {debugInfo.token_usage.prompt_tokens}</li>
                      <li>Токены кандидатов: {debugInfo.token_usage.completion_tokens || debugInfo.token_usage.candidates_tokens}</li>
                      <li>Всего токенов: {debugInfo.token_usage.total_tokens}</li>
                    </ul>
                  </div>
                )}
                {debugInfo.error && (
                  <div className="col-span-2 mt-2 text-red-600">
                    <span className="font-medium">Ошибка:</span> {debugInfo.error}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {items.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">2. Просмотр Товаров</h2>

            </div>

            <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded border">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Страна происхождения</label>
                <input
                  type="text"
                  value={reportMetadata.country_of_origin}
                  onChange={(e) => setReportMetadata({ ...reportMetadata, country_of_origin: e.target.value })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">№ Контракта</label>
                <input
                  type="text"
                  value={reportMetadata.contract_no}
                  onChange={(e) => setReportMetadata({ ...reportMetadata, contract_no: e.target.value })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Дата Контракта</label>
                <input
                  type="text"
                  value={reportMetadata.contract_date}
                  onChange={(e) => setReportMetadata({ ...reportMetadata, contract_date: e.target.value })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Поставщик</label>
                <input
                  type="text"
                  value={reportMetadata.supplier}
                  onChange={(e) => setReportMetadata({ ...reportMetadata, supplier: e.target.value })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">№ Инвойса</label>
                <input
                  type="text"
                  value={reportMetadata.invoice_no}
                  onChange={(e) => setReportMetadata({ ...reportMetadata, invoice_no: e.target.value })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Дата Инвойса</label>
                <input
                  type="text"
                  value={reportMetadata.invoice_date}
                  onChange={(e) => setReportMetadata({ ...reportMetadata, invoice_date: e.target.value })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Номер накладной</label>
                <input
                  type="text"
                  value={reportMetadata.waybill_no}
                  onChange={(e) => setReportMetadata({ ...reportMetadata, waybill_no: e.target.value })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                  placeholder="Например: 999-37041550"
                />
              </div>
            </div>

            <div className="mb-6 p-4 bg-blue-50 rounded border flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="flex flex-col gap-2">
                <h3 className="font-semibold">Выберите документы для генерации:</h3>
                <div className="flex flex-wrap gap-4 items-center">
                  <label className="inline-flex items-center">
                    <input
                      type="checkbox"
                      checked={docSelection.gen_tech_desc}
                      onChange={(e) => setDocSelection({ ...docSelection, gen_tech_desc: e.target.checked })}
                      className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    />
                    <span className="ml-2">Техническое описание</span>
                  </label>
                  <label className="inline-flex items-center">
                    <input
                      type="checkbox"
                      checked={docSelection.gen_non_insurance}
                      onChange={(e) => setDocSelection({ ...docSelection, gen_non_insurance: e.target.checked })}
                      className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    />
                    <span className="ml-2">Письмо о нестраховании</span>
                  </label>
                  <label className="inline-flex items-center">
                    <input
                      type="checkbox"
                      checked={docSelection.gen_decision_130}
                      onChange={(e) => setDocSelection({ ...docSelection, gen_decision_130: e.target.checked })}
                      className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    />
                    <span className="ml-2">Уведомление (Решение 130)</span>
                  </label>
                  <div className="border-l border-gray-300 pl-4 ml-2">
                    <label className="inline-flex items-center">
                      <input
                        type="checkbox"
                        checked={docSelection.add_facsimile}
                        onChange={(e) => setDocSelection({ ...docSelection, add_facsimile: e.target.checked })}
                        className="form-checkbox h-4 w-4 text-green-600"
                      />
                      <span className="ml-2 text-sm font-medium text-green-700">Добавить факсимиле (печать и подпись)</span>
                    </label>
                  </div>
                </div>
              </div>
              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm font-medium shadow-sm transition-colors whitespace-nowrap"
              >
                {isGenerating ? 'Генерация...' : 'Сгенерировать Отчет'}
              </button>
            </div>

            <InvoiceTable items={items} onUpdate={setItems} onClear={() => setItems([])} />
          </div>
        )}
      </div>
    </main>
  );
}
