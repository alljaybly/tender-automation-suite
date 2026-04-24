import React, { useState } from 'react';
import { TrendingDown, TrendingUp, Target, Loader2 } from 'lucide-react';

const RepriceControls = ({ pricing, onReprice }) => {
  const [loadingMode, setLoadingMode] = useState(null);

  const handleReprice = async (mode) => {
    setLoadingMode(mode);
    try {
      const response = await fetch('/api/reprice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pricing, mode })
      });
      const newPricing = await response.json();
      onReprice(newPricing);
    } catch (error) {
      console.error('Reprice error:', error);
    } finally {
      setLoadingMode(null);
    }
  };

  const strategies = [
    {
      id: 'optimize_win',
      label: 'Optimize for Win',
      icon: Target,
      bg: 'bg-blue-100',
      text: 'text-blue-600',
      borderHover: 'hover:border-blue-300',
      bgHover: 'hover:bg-blue-50',
      description: 'Competitive pricing to maximize win probability'
    },
    {
      id: 'maximize_profit',
      label: 'Maximize Profit',
      icon: TrendingUp,
      bg: 'bg-emerald-100',
      text: 'text-emerald-600',
      borderHover: 'hover:border-emerald-300',
      bgHover: 'hover:bg-emerald-50',
      description: 'Pricing with higher margin for better profitability'
    },
    {
      id: 'reduce_margin',
      label: 'Reduce Margin',
      icon: TrendingDown,
      bg: 'bg-rose-100',
      text: 'text-rose-600',
      borderHover: 'hover:border-rose-300',
      bgHover: 'hover:bg-rose-50',
      description: 'Aggressive reduction for price-sensitive contracts'
    }
  ];

  return (
    <div className="mt-6 space-y-3">
      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Pricing Strategies</h4>
      <div className="grid grid-cols-1 gap-3">
        {strategies.map((strat) => (
          <button
            key={strat.id}
            onClick={() => handleReprice(strat.id)}
            disabled={loadingMode !== null}
            className={`
              flex items-center gap-3 p-3 rounded-xl border transition-all text-left
              ${loadingMode === strat.id 
                ? 'bg-slate-50 border-slate-200' 
                : `${strat.borderHover} ${strat.bgHover} border-slate-100 bg-white shadow-sm hover:shadow`
              }
              disabled:opacity-50
            `}
          >
            <div className={`p-2 rounded-lg ${strat.bg} ${strat.text}`}>
              {loadingMode === strat.id ? <Loader2 className="animate-spin" size={18} /> : <strat.icon size={18} />}
            </div>
            <div>
              <div className="text-sm font-bold text-slate-800">{strat.label}</div>
              <div className="text-[10px] text-slate-500 leading-tight">{strat.description}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default RepriceControls;
