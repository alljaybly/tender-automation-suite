import React, { useState, useEffect } from 'react';
import { AlertTriangle, Clock, ShieldCheck, ChevronDown, ChevronUp } from 'lucide-react';

const ClausePanel = ({ results }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOpen, setIsOpen] = useState(true);

  useEffect(() => {
    if (!results) return;

    const fetchClauses = async () => {
      try {
        setLoading(true);
        const { tender_data } = results;
        const rawText = tender_data.raw_text || '';
        
        const response = await fetch('/api/clauses', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ raw_text: rawText })
        });

        if (!response.ok) throw new Error('Failed to fetch clauses');
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchClauses();
  }, [results]);

  if (loading) return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm animate-pulse">
      <div className="h-4 w-32 bg-slate-100 rounded mb-4"></div>
      <div className="space-y-4">
        {[1, 2].map(i => <div key={i} className="h-20 w-full bg-slate-100 rounded"></div>)}
      </div>
    </div>
  );

  if (error || !data) return null;

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm hover:shadow-md transition-shadow group">
      <div className="flex justify-between items-center mb-6 cursor-pointer" onClick={() => setIsOpen(!isOpen)}>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-rose-50 rounded-lg flex items-center justify-center text-rose-600 group-hover:bg-rose-600 group-hover:text-white transition-colors">
            <AlertTriangle size={18} />
          </div>
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Clause Warnings</h3>
        </div>
        <button className="text-slate-400 hover:text-slate-600">
          {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>
      </div>

      {isOpen && (
        <div className="space-y-6 animate-in slide-in-from-top-2 duration-300">
          {/* Penalties */}
          <div>
            <div className="flex items-center gap-2 text-rose-600 mb-3">
              <AlertTriangle size={14} />
              <span className="text-xs font-bold uppercase tracking-widest">Penalties</span>
            </div>
            <div className="space-y-2">
              {data.penalties.map((penalty, i) => (
                <div key={i} className="text-sm p-3 bg-rose-50 rounded-xl border border-rose-100 text-rose-700 font-medium">
                  {penalty}
                </div>
              ))}
            </div>
          </div>

          {/* Deadlines */}
          <div>
            <div className="flex items-center gap-2 text-amber-600 mb-3">
              <Clock size={14} />
              <span className="text-xs font-bold uppercase tracking-widest">Deadlines</span>
            </div>
            <div className="space-y-2">
              {data.deadlines.map((deadline, i) => (
                <div key={i} className="text-sm p-3 bg-amber-50 rounded-xl border border-amber-100 text-amber-700 font-medium">
                  {deadline}
                </div>
              ))}
            </div>
          </div>

          {/* Compliance */}
          <div>
            <div className="flex items-center gap-2 text-blue-600 mb-3">
              <ShieldCheck size={14} />
              <span className="text-xs font-bold uppercase tracking-widest">Compliance Sections</span>
            </div>
            <div className="space-y-1.5">
              {data.compliance_clauses.map((clause, i) => (
                <div key={i} className="text-xs p-2.5 bg-slate-50 rounded-lg text-slate-600 leading-relaxed border border-slate-100 italic">
                  "{clause}"
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClausePanel;
