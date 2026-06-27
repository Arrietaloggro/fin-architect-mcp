import React, { useRef, useState } from 'react';

interface FileUploadProps {
  onChange: (files: File[]) => void;
  maxFiles?: number;
  maxSizeMb?: number;
  accept?: string;
  label?: string;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileUpload({
  onChange,
  maxFiles = 5,
  maxSizeMb = 10,
  accept = 'image/*,.pdf,.doc,.docx,.xls,.xlsx',
  label = 'Archivos adjuntos',
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  const addFiles = (incoming: FileList | null) => {
    if (!incoming) return;
    setError(null);
    const toAdd: File[] = [];
    for (const f of Array.from(incoming)) {
      if (files.length + toAdd.length >= maxFiles) {
        setError(`Máximo ${maxFiles} archivos permitidos.`);
        break;
      }
      if (f.size > maxSizeMb * 1024 * 1024) {
        setError(`"${f.name}" supera el límite de ${maxSizeMb}MB.`);
        continue;
      }
      toAdd.push(f);
    }
    const updated = [...files, ...toAdd];
    setFiles(updated);
    onChange(updated);
  };

  const removeFile = (index: number) => {
    const updated = files.filter((_, i) => i !== index);
    setFiles(updated);
    onChange(updated);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    addFiles(e.dataTransfer.files);
  };

  return (
    <div className="flex flex-col gap-2">
      <span className="text-sm font-medium text-gray-700">{label}</span>

      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors duration-150
          ${dragging ? 'border-loggro-400 bg-loggro-50' : 'border-gray-300 hover:border-loggro-400 hover:bg-gray-50'}
        `}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        <svg className="mx-auto h-8 w-8 text-gray-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p className="text-sm text-gray-600">
          <span className="text-loggro-600 font-medium">Haz clic para subir</span> o arrastra aquí
        </p>
        <p className="text-xs text-gray-400 mt-1">PDF, Word, Excel, Imágenes — Máx. {maxSizeMb}MB por archivo, {maxFiles} archivos</p>
        <input ref={inputRef} type="file" multiple accept={accept} className="hidden" onChange={(e) => addFiles(e.target.files)} />
      </div>

      {error && <p className="text-xs text-red-600">⚠ {error}</p>}

      {files.length > 0 && (
        <ul className="flex flex-col gap-1.5 mt-1">
          {files.map((file, i) => (
            <li key={i} className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2 text-sm">
              <svg className="h-4 w-4 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="flex-1 truncate text-gray-700">{file.name}</span>
              <span className="text-gray-400 text-xs">{formatSize(file.size)}</span>
              <button
                type="button"
                onClick={() => removeFile(i)}
                className="text-gray-400 hover:text-red-500 transition-colors ml-1"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
