import React, { useState, useEffect } from 'react';
import { BarChart3, AlertCircle, CheckCircle2, TrendingUp, TrendingDown, Loader2 } from 'lucide-react';

const ComparisonCard = ({ tenderType, location, userMonthly }) => {
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (tenderType && location && userMonthly) {
      fetchComparison();
    }
  }, [tenderType, location, userMonthly]);

  const fetchComparison = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        tender_type: tenderType,
        location: location,
        user_monthly: userMonthly
      });
      const response = await fetch(`/api/tender-comparison?${params.toString()}`);
      const data = await response.json();
      setComparison(data);
    } catch (error) {
      console.error('Comparison error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 flex items-center justify-center min-h-[150px]">
        <Loader2 className="animate-spin text-blue-600" size={24} />
      </div>
    );
  }

  if (!comparison || comparison.similar_tenders_found === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="text-blue-600" size={20} />
          <h3 className="font-bold text-slate-800">Market Comparison</h3>
        </div>
        <div className="text-center py-4">
          <AlertCircle className="mx-auto text-slate-300 mb-2" size={32} />
          <p className="text-sm text-slate-500">Insufficient historical data for {tenderType} in {location}.</p>
        </div>
      </div>
    );
  }

  const isOverpriced = comparison.position === 'Overpriced';
  const isUnderpriced = comparison.position === 'Underpriced';
  const isCompetitive = comparison.position === 'Competitive';

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
      <div className="flex justify-between items-start mb-6">
        <div className="flex items-center gap-2">
          <BarChart3 className="text-blue-600" size={20} />
          <h3 className="font-bold text-slate-800">Market Comparison</h3>
        </div>
        <div className={`
          px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider
          ${isOverpriced ? 'bg-rose-100 text-rose-700' : 
            isUnderpriced ? 'bg-amber-100 text-amber-700' : 
            'bg-emerald-100 text-emerald-700'}
        `}>
          {comparison.position}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-3 bg-slate-50 rounded-lg">
          <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Market Avg</div>
          <div className="text-lg font-bold text-slate-800">R {comparison.avg_monthly?.toLocaleString()}</div>
        </div>
        <div className="p-3 bg-slate-50 rounded-lg border border-blue-100">
          <div className="text-[10px] text-blue-600 uppercase font-bold mb-1">Your Price</div>
          <div className="text-lg font-bold text-slate-800">R {comparison.user_monthly?.toLocaleString()}</div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-600">Price Difference</span>
          <span className={`font-bold flex items-center gap-1 ${comparison.difference_percent > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
            {comparison.difference_percent > 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            {Math.abs(comparison.difference_percent)}%
          </span>
        </div>
        
        <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
          <div 
            className={`h-full transition-all duration-1000 ${isOverpriced ? 'bg-rose-500' : isUnderpriced ? 'bg-amber-500' : 'bg-emerald-500'}`}
            style={{ width: `${Math.min(100, Math.max(0, 50 + (comparison.difference_percent || 0)))}%` }}
          />
        </div>

        <div className={`p-3 rounded-lg text-xs leading-relaxed ${isCompetitive ? 'bg-emerald-50 text-emerald-800 border border-emerald-100' : 'bg-slate-50 text-slate-600 border border-slate-100'}`}>
          <div className="flex gap-2">
            {isCompetitive ? <CheckCircle2 size={16} className="shrink-0" /> : <AlertCircle size={16} className="shrink-0" />}
            <p>{comparison.advice}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonCard;
