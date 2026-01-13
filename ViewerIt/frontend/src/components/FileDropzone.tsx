/**
 * FileDropzone Component - Drag and drop file upload with cyberpunk styling
 */
import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, File, X, CheckCircle } from 'lucide-react';

interface FileDropzoneProps {
  onFilesAccepted: (files: File[]) => void;
  acceptedTypes?: string[];
  maxFiles?: number;
  label?: string;
}

export function FileDropzone({ 
  onFilesAccepted, 
  maxFiles = 10,
  label = 'Drop your data files here'
}: FileDropzoneProps) {
  const [files, setFiles] = useState<File[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = [...files, ...acceptedFiles].slice(0, maxFiles);
    setFiles(newFiles);
  }, [files, maxFiles]);

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleUpload = () => {
    if (files.length >= 2) {
      onFilesAccepted(files);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/x-parquet': ['.parquet'],
      'application/json': ['.json'],
      'text/plain': ['.dat', '.txt'],
    },
    maxFiles,
  });

  return (
    <div className="space-y-4">
      {/* Dropzone Area */}
      <motion.div
        {...(getRootProps() as any)}
        className={`
          relative p-8 rounded-lg border-2 border-dashed cursor-pointer
          transition-all duration-300
          ${isDragActive 
            ? 'border-[#00f5ff] bg-[#00f5ff]/10' 
            : 'border-[#2a2a3a] hover:border-[#00f5ff]/50 bg-[#12121a]/50'
          }
        `}
        whileHover={{ scale: 1.01 }}
        animate={isDragActive ? { scale: 1.02 } : { scale: 1 }}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center gap-4 text-center">
          <motion.div
            animate={isDragActive ? { y: [-5, 5, -5] } : { y: 0 }}
            transition={{ repeat: isDragActive ? Infinity : 0, duration: 0.5 }}
          >
            <Upload 
              size={48} 
              className={isDragActive ? 'text-[#00f5ff]' : 'text-[#555566]'}
            />
          </motion.div>
          
          <div>
            <p 
              className="text-lg font-semibold"
              style={{ fontFamily: 'Rajdhani, sans-serif', color: '#e0e0e0' }}
            >
              {isDragActive ? 'Release to upload...' : label}
            </p>
            <p className="text-sm text-[#888899] mt-1">
              Supports: CSV, Excel, Parquet, JSON, DAT, TXT
            </p>
          </div>
        </div>

        {/* Scanline effect when active */}
        {isDragActive && (
          <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-lg">
            <motion.div
              className="absolute inset-0 bg-gradient-to-b from-transparent via-[#00f5ff]/10 to-transparent"
              initial={{ y: '-100%' }}
              animate={{ y: '100%' }}
              transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
            />
          </div>
        )}
      </motion.div>

      {/* File List */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2"
          >
            <p className="text-sm text-[#888899] uppercase tracking-wider" style={{ fontFamily: 'Orbitron, monospace' }}>
              Selected Files ({files.length})
            </p>
            
            {files.map((file, index) => (
              <motion.div
                key={`${file.name}-${index}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center justify-between p-3 rounded-lg bg-[#1a1a24] border border-[#2a2a3a]"
              >
                <div className="flex items-center gap-3">
                  <File size={20} className="text-[#00f5ff]" />
                  <div>
                    <p className="text-sm text-[#e0e0e0]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                      {file.name}
                    </p>
                    <p className="text-xs text-[#555566]">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                  className="p-1 rounded hover:bg-[#ff0080]/20 transition-colors"
                >
                  <X size={16} className="text-[#ff0080]" />
                </button>
              </motion.div>
            ))}

            {/* Upload Button */}
            <motion.button
              onClick={handleUpload}
              disabled={files.length < 2}
              className={`
                w-full py-3 rounded-lg font-bold uppercase tracking-wider transition-all duration-300
                ${files.length >= 2 
                  ? 'bg-gradient-to-r from-[#00f5ff] to-[#ff00ff] text-[#0a0a0f] hover:shadow-[0_0_20px_rgba(0,245,255,0.5)]' 
                  : 'bg-[#2a2a3a] text-[#555566] cursor-not-allowed'
                }
              `}
              style={{ fontFamily: 'Orbitron, monospace' }}
              whileHover={files.length >= 2 ? { scale: 1.02 } : {}}
              whileTap={files.length >= 2 ? { scale: 0.98 } : {}}
            >
              <span className="flex items-center justify-center gap-2">
                <CheckCircle size={18} />
                {files.length >= 2 ? 'Start Comparison' : 'Add at least 2 files'}
              </span>
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default FileDropzone;

