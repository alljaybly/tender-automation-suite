import React, { useState, useEffect } from 'react';
import { Trophy, AlertTriangle, Lightbulb, ShieldCheck } from 'lucide-react';

const WinScore = ({ results }) => {
  const [score, setScore] = useState(0);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!results) return;

    const fetchWinScore = async () => {
      try {
        setLoading(true);
        const { tender_data, pricing } = results;
        const params = new URLSearchParams({
          tender_type: tender_data.sector || tender_data.tender_type || 'cleaning',
          price: pricing.total_monthly || 0,
          duration_months: tender_data.duration_months || 12,
          workers: tender_data.workforce?.total_workers || 0,
          area_sqm: tender_data.scope?.area_sqm || 0
        });

        const response = await fetch(`/api/win-score?${params.toString()}`);
        if (!response.ok) throw new Error('Failed to fetch win score');
        const result = await response.json();
        setData(result);
        
        // Animate score
        let start = 0;
        const end = result.win_probability;
        const duration = 1500;
        const increment = end / (duration / 16);
        
        const timer = setInterval(() => {
          start += increment;
          if (start >= end) {
            setScore(end);
            clearInterval(timer);
          } else {
            setScore(Math.floor(start));
          }
        }, 16);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchWinScore();
  }, [results]);

  if (loading) return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm animate-pulse">
      <div className="h-4 w-24 bg-slate-100 rounded mb-4"></div>
      <div className="h-12 w-32 bg-slate-100 rounded mb-4 mx-auto"></div>
      <div className="space-y-2">
        <div className="h-3 w-full bg-slate-100 rounded"></div>
        <div className="h-3 w-full bg-slate-100 rounded"></div>
      </div>
    </div>
  );

  if (error) return null;
  if (!data) return null;

  const getRiskColor = (level) => {
    switch (level.toLowerCase()) {
      case 'low': return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'medium': return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'high': return 'bg-rose-100 text-rose-700 border-rose-200';
      default: return 'bg-slate-100 text-slate-700';
    }
  };

  const getScoreColor = (s) => {
    if (s >= 75) return 'text-emerald-600';
    if (s >= 50) return 'text-amber-600';
    return 'text-rose-600';
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm hover:shadow-md transition-shadow group">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
            <Trophy size={18} />
          </div>
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Win Probability</h3>
        </div>
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${getRiskColor(data.risk_level)}`}>
          {data.risk_level} Risk
        </span>
      </div>

      <div className="text-center mb-8">
        <div className={`text-5xl font-black mb-1 ${getScoreColor(score)}`}>
          {score}<span className="text-2xl opacity-50">%</span>
        </div>
        <p className="text-xs text-slate-500 font-medium">Estimated Success Rate</p>
      </div>

      <div className="space-y-4">
        {data.issues?.length > 0 && (
          <div>
            <div className="flex items-center gap-2 text-rose-600 mb-2">
              <AlertTriangle size={14} />
              <span className="text-xs font-bold uppercase tracking-widest">Key Issues</span>
            </div>
            <ul className="space-y-1.5">
              {data.issues.map((issue, i) => (
                <li key={i} className="text-sm text-slate-600 flex gap-2">
                  <span className="text-rose-400 mt-1">•</span>
                  {issue}
                </li>
              ))}
            </ul>
          </div>
        )}

        {data.suggestions?.length > 0 && (
          <div className="pt-3 border-t border-slate-50">
            <div className="flex items-center gap-2 text-blue-600 mb-2">
              <Lightbulb size={14} />
              <span className="text-xs font-bold uppercase tracking-widest">Suggestions</span>
            </div>
            <ul className="space-y-1.5">
              {data.suggestions.map((sug, i) => (
                <li key={i} className="text-sm text-slate-600 flex gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  {sug}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default WinScore;
