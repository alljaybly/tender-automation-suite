import React, { useState, useEffect } from 'react';
import { Search, Filter, ArrowUpDown, Copy, ExternalLink, FileText, Calendar, DollarSign, Loader2, MoreVertical } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import Skeleton from '../components/ui/Skeleton';

const TenderLibrary = () => {
  const [tenders, setTenders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('All');
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, [searchTerm, filterType, sortBy, sortOrder]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        search: searchTerm,
        tender_type: filterType === 'All' ? '' : filterType,
        sort_by: sortBy,
        sort_order: sortOrder
      });
      const response = await fetch(`/api/history?${params}`);
      const data = await response.json();
      setTenders(data);
    } catch (error) {
      console.error('Error fetching history:', error);
      toast.error('Failed to load tender history');
    } finally {
      setLoading(false);
    }
  };

  const handleDuplicate = async (tenderId) => {
    const toastId = toast.loading('Duplicating tender...');
    try {
      const response = await fetch('/api/duplicate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tender_id: tenderId })
      });
      if (response.ok) {
        toast.success('Tender duplicated successfully', { id: toastId });
        fetchHistory();
      } else {
        throw new Error('Failed to duplicate');
      }
    } catch (error) {
      console.error('Error duplicating tender:', error);
      toast.error('Failed to duplicate tender', { id: toastId });
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
    }).format(value);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-ZA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusColor = (confidence) => {
    if (confidence >= 0.8) return 'bg-emerald-100 text-emerald-700';
    if (confidence >= 0.6) return 'bg-blue-100 text-blue-700';
    return 'bg-amber-100 text-amber-700';
  };

  const SkeletonRow = () => (
    <tr className="border-b border-slate-100">
      <td className="px-6 py-4"><Skeleton className="h-4 w-32" /></td>
      <td className="px-6 py-4"><Skeleton className="h-4 w-20" /></td>
      <td className="px-6 py-4"><Skeleton className="h-4 w-24" /></td>
      <td className="px-6 py-4"><Skeleton className="h-4 w-24" /></td>
      <td className="px-6 py-4"><Skeleton className="h-6 w-16 rounded-full" /></td>
      <td className="px-6 py-4 text-right"><Skeleton className="h-8 w-20 ml-auto rounded-lg" /></td>
    </tr>
  );

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 p-4 md:p-0"
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-black text-slate-900">Tender Library</h1>
          <p className="text-slate-500">Manage and track your historical tender responses.</p>
        </div>
        
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 md:flex-none">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input
              type="text"
              placeholder="Search references..."
              className="pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 w-full md:w-64 shadow-sm"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <select
            className="px-4 py-2.5 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none shadow-sm min-w-[140px]"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="All">All Sectors</option>
            <option value="cleaning">Cleaning</option>
            <option value="security">Security</option>
            <option value="construction">Construction</option>
          </select>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-sm overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Reference</th>
              <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">
                <button 
                  className="flex items-center gap-1 hover:text-blue-600 transition-colors"
                  onClick={() => {
                    setSortBy('value');
                    setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
                  }}
                >
                  Value <ArrowUpDown size={14} />
                </button>
              </th>
              <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">
                <button 
                  className="flex items-center gap-1 hover:text-blue-600 transition-colors"
                  onClick={() => {
                    setSortBy('date');
                    setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
                  }}
                >
                  Date <ArrowUpDown size={14} />
                </button>
              </th>
              <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              Array(5).fill(0).map((_, i) => <SkeletonRow key={i} />)
            ) : tenders.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-20 text-center">
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-2">
                      <FileText className="text-slate-300" size={32} />
                    </div>
                    <span className="text-slate-500 font-medium text-lg">No tenders found</span>
                    <p className="text-slate-400 max-w-xs mx-auto">Try adjusting your search or filters to find what you're looking for.</p>
                  </div>
                </td>
              </tr>
            ) : (
              <AnimatePresence>
                {tenders.map((tender, index) => (
                  <motion.tr 
                    key={tender.id || index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="hover:bg-slate-50 transition-colors group"
                  >
                    <td className="px-6 py-4">
                      <div className="font-bold text-slate-900">{tender.reference}</div>
                      <div className="text-xs text-slate-400 truncate max-w-[200px]">{tender.filename}</div>
                    </td>
                    <td className="px-6 py-4 capitalize">
                      <span className="inline-flex items-center gap-1.5 py-1 px-2.5 rounded-lg bg-slate-100 text-slate-600 text-xs font-bold">
                        {tender.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-700">
                      {formatCurrency(tender.pricing?.total_contract_value || tender.total_value)}
                    </td>
                    <td className="px-6 py-4 text-slate-500 text-sm">
                      {formatDate(tender.date)}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusColor(tender.confidence)}`}>
                        {Math.round(tender.confidence * 100)}% Match
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => handleDuplicate(tender.reference)}
                          className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                          title="Duplicate"
                        >
                          <Copy size={18} />
                        </button>
                        <button
                          onClick={() => navigate(`/dashboard/${tender.reference}`)}
                          className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700 transition-all shadow-sm"
                        >
                          Open <ExternalLink size={14} />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
            )}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

export default TenderLibrary;
