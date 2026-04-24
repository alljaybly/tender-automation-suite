import React, { useState, useEffect } from 'react';
import { ShieldCheck, XCircle, CheckCircle, Info, ChevronDown, ChevronUp } from 'lucide-react';

const ComplianceChecklist = ({ results }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOpen, setIsOpen] = useState(true);

  useEffect(() => {
    if (!results) return;

    const fetchCompliance = async () => {
      try {
        setLoading(true);
        const { tender_data } = results;
        const tenderType = tender_data.sector || tender_data.tender_type || 'cleaning';
        const response = await fetch(`/api/compliance-checklist?tender_type=${tenderType}`);
        if (!response.ok) throw new Error('Failed to fetch compliance checklist');
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCompliance();
  }, [results]);

  if (loading) return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm animate-pulse">
      <div className="h-4 w-40 bg-slate-100 rounded mb-4"></div>
      <div className="space-y-3">
        {[1, 2, 3].map(i => <div key={i} className="h-8 w-full bg-slate-100 rounded"></div>)}
      </div>
    </div>
  );

  if (error || !data) return null;

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm hover:shadow-md transition-shadow group">
      <div className="flex justify-between items-center mb-6 cursor-pointer" onClick={() => setIsOpen(!isOpen)}>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-emerald-50 rounded-lg flex items-center justify-center text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
            <ShieldCheck size={18} />
          </div>
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Compliance Checklist</h3>
        </div>
        <button className="text-slate-400 hover:text-slate-600">
          {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>
      </div>

      {isOpen && (
        <div className="space-y-6 animate-in slide-in-from-top-2 duration-300">
          <div className="space-y-2">
            {data.required_documents.map((doc, i) => {
              const isMissing = data.missing.includes(doc);
              return (
                <div key={i} className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${isMissing ? 'bg-rose-50 border-rose-100 text-rose-700' : 'bg-emerald-50 border-emerald-100 text-emerald-700 opacity-60'}`}>
                  {isMissing ? <XCircle size={16} className="shrink-0" /> : <CheckCircle size={16} className="shrink-0" />}
                  <span className="text-sm font-medium">{doc}</span>
                </div>
              );
            })}
          </div>

          {data.notes?.length > 0 && (
            <div className="bg-blue-50/50 p-4 rounded-xl border border-blue-100/50">
              <div className="flex items-center gap-2 text-blue-600 mb-2">
                <Info size={14} />
                <span className="text-xs font-bold uppercase tracking-widest">Industry Notes</span>
              </div>
              <ul className="space-y-2">
                {data.notes.map((note, i) => (
                  <li key={i} className="text-xs text-slate-600 leading-relaxed flex gap-2">
                    <span className="text-blue-400">•</span>
                    {note}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ComplianceChecklist;
