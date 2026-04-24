import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, Shield, HardHat, Loader2, Sparkles } from 'lucide-react';
import { toast } from 'react-hot-toast';

const UploadPanel = ({ onUploadSuccess, onDemoStart }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = async (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      await uploadFiles(files);
    }
  };

  const uploadFiles = async (files) => {
    setIsUploading(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    const toastId = toast.loading('Uploading documents...');

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      toast.success('Documents uploaded successfully', { id: toastId });
      onUploadSuccess(response.data.filename);
    } catch (error) {
      console.error('Upload failed:', error);
      const errorMsg = error.response?.data?.detail || 'Upload failed. Please try again.';
      toast.error(errorMsg, { id: toastId });
    } finally {
      setIsUploading(false);
    }
  };

  const startDemo = async (type) => {
    const toastId = toast.loading(`Starting ${type} demo...`);
    try {
      const response = await axios.post(`/api/demo?tender_type=${type}`);
      toast.success(`${type.charAt(0).toUpperCase() + type.slice(1)} demo loaded`, { id: toastId });
      onDemoStart(response.data.filename);
    } catch (error) {
      console.error('Demo failed:', error);
      toast.error('Failed to start demo', { id: toastId });
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div
        className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer group
          ${isDragging 
            ? 'border-blue-500 bg-blue-50 scale-[1.02] shadow-lg ring-4 ring-blue-100' 
            : 'border-slate-200 hover:border-blue-400 hover:bg-slate-50'}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          uploadFiles(e.dataTransfer.files);
        }}
        onClick={() => document.getElementById('file-input').click()}
      >
        <input
          type="file"
          id="file-input"
          className="hidden"
          multiple
          onChange={handleFileChange}
        />
        <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 transition-transform duration-300 ${isDragging ? 'scale-110 bg-blue-200' : 'bg-blue-100'}`}>
          {isUploading ? (
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
          ) : (
            <Upload className={`w-8 h-8 text-blue-600 ${isDragging ? 'animate-bounce' : 'group-hover:-translate-y-1 transition-transform'}`} />
          )}
        </div>
        <h3 className="text-lg font-bold text-slate-900 mb-1">
          {isUploading ? 'Uploading...' : 'Upload Tender Documents'}
        </h3>
        <p className="text-sm text-slate-500">Drag and drop PDFs or images here, or click to browse</p>
        
        {isDragging && (
          <div className="absolute inset-0 bg-blue-500/5 rounded-2xl pointer-events-none" />
        )}
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="w-4 h-4 text-amber-500" />
          <h4 className="text-sm font-semibold text-slate-700 uppercase tracking-wider">Quick Demos</h4>
        </div>
        <div className="grid grid-cols-1 gap-2">
          {[
            { id: 'cleaning', label: 'Cleaning Demo', icon: FileText, color: 'hover:bg-emerald-50 text-slate-700 hover:text-emerald-700 border-slate-200 hover:border-emerald-200' },
            { id: 'security', label: 'Security Demo', icon: Shield, color: 'hover:bg-blue-50 text-slate-700 hover:text-blue-700 border-slate-200 hover:border-blue-200' },
            { id: 'construction', label: 'Construction Demo', icon: HardHat, color: 'hover:bg-amber-50 text-slate-700 hover:text-amber-700 border-slate-200 hover:border-amber-200' }
          ].map((demo) => (
            <button
              key={demo.id}
              onClick={() => startDemo(demo.id)}
              className={`flex items-center gap-3 p-3 rounded-xl border font-medium transition-all hover:shadow-sm group ${demo.color}`}
            >
              <demo.icon className="w-5 h-5 transition-transform group-hover:scale-110" />
              {demo.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default UploadPanel;
