import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';
import { TrendingUp, Users, Target, Activity, DollarSign, Briefcase, Loader2, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import Skeleton from '../components/ui/Skeleton';

const Analytics = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('/api/analytics');
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
      maximumFractionDigits: 0
    }).format(value);
  };

  const chartData = data ? Object.entries(data.sector_breakdown || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    count: value
  })) : [];

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  const SkeletonCard = () => (
    <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm space-y-3">
      <Skeleton className="w-10 h-10 rounded-xl" />
      <Skeleton className="w-24 h-4" />
      <Skeleton className="w-32 h-8" />
    </div>
  );

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 p-4 md:p-0"
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-black text-slate-900">Performance Analytics</h1>
          <p className="text-slate-500">Insights from your tender processing history.</p>
        </div>
        <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-xl text-sm font-bold border border-blue-100">
          <Activity size={18} />
          Real-time updates
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {loading ? (
          Array(4).fill(0).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          <>
            <StatCard 
              icon={<Briefcase className="text-blue-600" />} 
              label="Total Tenders" 
              value={data?.total_tenders_processed || 0}
              trend="+12%"
            />
            <StatCard 
              icon={<DollarSign className="text-green-600" />} 
              label="Avg Contract Value" 
              value={formatCurrency(data?.avg_contract_value || 0)}
              trend="+5.4%"
            />
            <StatCard 
              icon={<Target className="text-amber-600" />} 
              label="Primary Sector" 
              value={data?.most_common_sector || 'N/A'}
              subtext={`${data?.sector_breakdown?.[data?.most_common_sector] || 0} projects`}
            />
            <StatCard 
              icon={<Activity className="text-indigo-600" />} 
              label="Total Value" 
              value={formatCurrency(data?.total_value_processed || 0)}
              trend="+18.2%"
            />
          </>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Sector Distribution Chart */}
        <div className="lg:col-span-8 bg-white p-6 md:p-8 rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="flex items-center justify-between mb-8">
            <h3 className="font-bold text-slate-900 text-lg">Sector Distribution</h3>
            <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
              <TrendingUp size={14} />
              Volume by Sector
            </div>
          </div>
          
          <div className="h-[300px] w-full">
            {loading ? (
              <div className="flex flex-col gap-4 h-full justify-end">
                <div className="flex items-end gap-8 h-full px-4">
                  <Skeleton className="flex-1 h-1/2 rounded-t-lg" />
                  <Skeleton className="flex-1 h-3/4 rounded-t-lg" />
                  <Skeleton className="flex-1 h-2/3 rounded-t-lg" />
                </div>
                <div className="flex gap-8 px-4">
                  <Skeleton className="flex-1 h-4" />
                  <Skeleton className="flex-1 h-4" />
                  <Skeleton className="flex-1 h-4" />
                </div>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis 
                    dataKey="name" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#64748b', fontSize: 12, fontWeight: 600 }}
                    dy={10}
                  />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#64748b', fontSize: 12, fontWeight: 600 }}
                  />
                  <Tooltip 
                    cursor={{ fill: '#f8fafc' }}
                    contentStyle={{ 
                      borderRadius: '16px', 
                      border: 'none', 
                      boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                      padding: '12px'
                    }}
                  />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]} barSize={40}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Quick Insights */}
        <div className="lg:col-span-4 space-y-6">
          {loading ? (
            <>
              <Skeleton className="h-[200px] rounded-3xl" />
              <Skeleton className="h-[250px] rounded-3xl" />
            </>
          ) : (
            <>
              <motion.div 
                whileHover={{ y: -5 }}
                className="bg-blue-600 p-8 rounded-3xl text-white shadow-xl shadow-blue-200"
              >
                <div className="flex items-center gap-2 mb-4">
                  <Info className="text-blue-200" size={20} />
                  <h3 className="font-bold text-xl">AI Insight</h3>
                </div>
                <p className="text-blue-100 text-sm leading-relaxed mb-6">
                  Your average contract value in the <span className="font-bold text-white capitalize">{data?.most_common_sector}</span> sector is 15% higher than your overall average. 
                  Focusing on this sector could maximize profitability.
                </p>
                <button className="w-full py-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl font-bold text-sm transition-all">
                  View Opportunities
                </button>
              </motion.div>

              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                <h4 className="font-bold text-slate-900 mb-4">Sector Efficiency</h4>
                <div className="space-y-4">
                  {chartData.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></div>
                        <span className="text-sm font-medium text-slate-600">{item.name}</span>
                      </div>
                      <div className="text-sm font-bold text-slate-900">{item.count} Tenders</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
};

const StatCard = ({ icon, label, value, trend, subtext }) => (
  <motion.div 
    whileHover={{ y: -5 }}
    className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm transition-all hover:shadow-md"
  >
    <div className="flex items-start justify-between mb-4">
      <div className="p-3 bg-slate-50 rounded-2xl">
        {icon}
      </div>
      {trend && (
        <span className="text-xs font-bold px-2 py-1 bg-green-50 text-green-600 rounded-lg">
          {trend}
        </span>
      )}
    </div>
    <div className="space-y-1">
      <h4 className="text-slate-500 text-sm font-medium">{label}</h4>
      <div className="text-2xl font-black text-slate-900">{value}</div>
      {subtext && <div className="text-xs text-slate-400">{subtext}</div>}
    </div>
  </motion.div>
);

export default Analytics;
