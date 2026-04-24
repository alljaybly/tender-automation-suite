import React from 'react';
import RepriceControls from './RepriceControls';
import ComparisonCard from './ComparisonCard';
import { Edit3, Download, FileArchive } from 'lucide-react';

const ResultsPanel = ({ results, onEditDraft, onReprice }) => {
  if (!results) return null;

  const { tender_data, pricing } = results;

  const downloadFile = (url) => {
    window.open(url, '_blank');
  };

  const handleZipDownload = () => {
    const wordFile = results.documents?.word || `tender_${tender_data.reference}.docx`;
    const excelFile = results.documents?.excel || `pricing_${tender_data.reference}.xlsx`;
    window.open(`/api/download/zip?word=${wordFile}&excel=${excelFile}`, '_blank');
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Pricing Card */}
      <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-8 text-white shadow-xl shadow-blue-200">
        <div className="flex justify-between items-start mb-6">
          <div>
            <span className="text-blue-100 text-xs font-bold uppercase tracking-widest opacity-80">Total Quote</span>
            <h3 className="text-4xl font-black mt-1">
              R {pricing.total_contract_value?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </h3>
          </div>
          <div className="bg-white/20 backdrop-blur-md px-4 py-2 rounded-xl text-sm font-bold">
            {tender_data.duration_months} Months
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white/10 rounded-xl p-4">
            <p className="text-blue-100 text-xs font-medium uppercase opacity-70 mb-1">Monthly Rate</p>
            <p className="text-xl font-bold">R {pricing.total_monthly?.toLocaleString()}</p>
          </div>
          <div className="bg-white/10 rounded-xl p-4">
            <p className="text-blue-100 text-xs font-medium uppercase opacity-70 mb-1">Profit Margin</p>
            <p className="text-xl font-bold">{pricing.profit_percent || '15'}%</p>
          </div>
        </div>

        {/* Reprice Controls Integration */}
        <div className="mt-8 pt-6 border-t border-white/10">
          <RepriceControls pricing={pricing} onReprice={onReprice} />
        </div>
      </div>

      {/* Market Comparison Integration */}
      <ComparisonCard 
        tenderType={tender_data.sector || tender_data.tender_type}
        location={tender_data.location}
        userMonthly={pricing.total_monthly}
      />

      {/* Summary Details */}
      <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm relative">
        <div className="flex justify-between items-center mb-4 border-b border-slate-50 pb-2">
          <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            Tender Summary
          </h4>
          <button 
            onClick={onEditDraft}
            className="flex items-center gap-1.5 text-xs font-bold text-blue-600 hover:text-blue-700 transition-colors"
          >
            <Edit3 size={14} />
            Edit Draft
          </button>
        </div>
        <div className="grid grid-cols-2 gap-y-4 gap-x-6">
          <div>
            <p className="text-xs text-slate-500 uppercase font-bold mb-1">Reference</p>
            <p className="text-sm font-semibold text-slate-800">{tender_data.reference}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase font-bold mb-1">Sector</p>
            <p className="text-sm font-semibold text-slate-800 capitalize">{tender_data.sector || tender_data.tender_type}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase font-bold mb-1">Location</p>
            <p className="text-sm font-semibold text-slate-800">{tender_data.location}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase font-bold mb-1">Staffing</p>
            <p className="text-sm font-semibold text-slate-800">{tender_data.workforce?.total_workers} Personnel</p>
          </div>
        </div>
      </div>

      {/* Downloads */}
      <div className="grid grid-cols-1 gap-3">
        <button 
          onClick={() => downloadFile(`/api/download/word/${results.documents?.word || 'tender_' + tender_data.reference + '.docx'}`)}
          className="w-full flex items-center justify-between p-4 bg-white border border-slate-200 rounded-xl hover:border-blue-500 hover:shadow-md transition-all group"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
              <Download size={20} />
            </div>
            <div className="text-left">
              <p className="text-sm font-bold text-slate-900">Download Submission</p>
              <p className="text-xs text-slate-500">Microsoft Word (.docx)</p>
            </div>
          </div>
          <Download className="text-slate-300 group-hover:text-blue-500" size={18} />
        </button>

        <button 
          onClick={() => downloadFile(`/api/download/excel/${results.documents?.excel || 'pricing_' + tender_data.reference + '.xlsx'}`)}
          className="w-full flex items-center justify-between p-4 bg-white border border-slate-200 rounded-xl hover:border-emerald-500 hover:shadow-md transition-all group"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-50 rounded-lg flex items-center justify-center text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
              <Download size={20} />
            </div>
            <div className="text-left">
              <p className="text-sm font-bold text-slate-900">Pricing Workbook</p>
              <p className="text-xs text-slate-500">Microsoft Excel (.xlsx)</p>
            </div>
          </div>
          <Download className="text-slate-300 group-hover:text-emerald-500" size={18} />
        </button>

        <button 
          onClick={handleZipDownload}
          className="w-full py-4 bg-slate-900 text-white rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-slate-800 transition-all shadow-lg shadow-slate-200"
        >
          <FileArchive size={20} />
          Download Submission Pack (.zip)
        </button>
      </div>
    </div>
  );
};

export default ResultsPanel;

