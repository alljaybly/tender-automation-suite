import React, { useState, useEffect } from 'react';
import { X, Save, FileText, Loader2 } from 'lucide-react';

const EditDraftModal = ({ isOpen, onClose, tenderData, pricing, onSave }) => {
  const [formData, setFormData] = useState({
    executive_summary: '',
    scope_description: '',
    pricing_notes: ''
  });
  const [isSaving, setIsSaving] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);

  useEffect(() => {
    if (tenderData) {
      setFormData({
        executive_summary: tenderData.executive_summary || '',
        scope_description: tenderData.scope_description || '',
        pricing_notes: pricing?.notes || ''
      });
    }
  }, [tenderData, pricing]);

  const handleAction = async (regenerate = false) => {
    if (regenerate) setIsRegenerating(true);
    else setIsSaving(true);

    try {
      const payload = {
        tender_data: {
          ...tenderData,
          executive_summary: formData.executive_summary,
          scope_description: formData.scope_description
        },
        pricing: {
          ...pricing,
          notes: formData.pricing_notes
        },
        regenerate
      };

      const response = await fetch('/api/edit-draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      if (result.success) {
        onSave(payload.tender_data, payload.pricing, result.documents);
        if (!regenerate) onClose();
      }
    } catch (error) {
      console.error('Error saving draft:', error);
    } finally {
      setIsSaving(false);
      setIsRegenerating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl flex flex-col max-h-[90vh]">
        <div className="p-6 border-b flex justify-between items-center">
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <FileText className="text-blue-600" size={24} />
            Edit Tender Draft
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X size={24} />
          </button>
        </div>

        <div className="p-6 overflow-y-auto space-y-6">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Executive Summary
            </label>
            <textarea
              className="w-full h-32 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              value={formData.executive_summary}
              onChange={(e) => setFormData({ ...formData, executive_summary: e.target.value })}
              placeholder="A high-level overview of your proposal..."
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Scope Description
            </label>
            <textarea
              className="w-full h-32 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              value={formData.scope_description}
              onChange={(e) => setFormData({ ...formData, scope_description: e.target.value })}
              placeholder="Details on what exactly will be delivered..."
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Pricing Notes
            </label>
            <textarea
              className="w-full h-24 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              value={formData.pricing_notes}
              onChange={(e) => setFormData({ ...formData, pricing_notes: e.target.value })}
              placeholder="Any assumptions or exclusions regarding the price..."
            />
          </div>
        </div>

        <div className="p-6 border-t bg-slate-50 rounded-b-xl flex justify-between gap-4">
          <button
            onClick={() => handleAction(true)}
            disabled={isRegenerating || isSaving}
            className="flex-1 px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 font-medium flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            {isRegenerating ? <Loader2 className="animate-spin" size={20} /> : <FileText size={20} />}
            Regenerate Documents
          </button>
          
          <button
            onClick={() => handleAction(false)}
            disabled={isSaving || isRegenerating}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center justify-center gap-2 shadow-md transition-colors disabled:opacity-50"
          >
            {isSaving ? <Loader2 className="animate-spin" size={20} /> : <Save size={20} />}
            Save Draft
          </button>
        </div>
      </div>
    </div>
  );
};

export default EditDraftModal;
