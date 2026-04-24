import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Cpu, Terminal, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

const ProgressPanel = ({ progress, status, logs }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  if (progress === 0 && !status) return (
    <div className="h-[400px] flex flex-col items-center justify-center text-slate-400 bg-white rounded-3xl border border-slate-100 border-dashed border-2">
      <div className="p-6 bg-slate-50 rounded-full mb-4">
        <Cpu className="w-12 h-12 text-slate-200" />
      </div>
      <p className="font-medium">Ready to process your tender</p>
      <p className="text-xs text-slate-300 mt-1">Upload a document to begin AI analysis</p>
    </div>
  );

  return (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm"
      >
        <div className="flex justify-between items-end mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              {progress === 100 ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              ) : (
                <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
              )}
              <span className="text-xs font-bold text-blue-600 uppercase tracking-widest">
                {progress === 100 ? 'Analysis Complete' : 'AI Processing'}
              </span>
            </div>
            <h3 className="text-xl font-black text-slate-900 leading-tight">
              {status || 'Starting engine...'}
            </h3>
          </div>
          <div className="text-right">
            <span className="text-3xl font-black text-slate-900">{progress}%</span>
          </div>
        </div>
        
        <div className="w-full h-4 bg-slate-100 rounded-full overflow-hidden p-1 shadow-inner">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ type: "spring", stiffness: 50, damping: 15 }}
            className={`h-full rounded-full shadow-lg ${
              progress === 100 ? 'bg-emerald-500 shadow-emerald-200' : 'bg-blue-600 shadow-blue-200'
            }`}
          />
        </div>
      </motion.div>

      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-slate-900 rounded-3xl p-6 shadow-2xl overflow-hidden flex flex-col h-[350px] border border-slate-800"
      >
        <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/80 shadow-lg shadow-red-500/20"></div>
              <div className="w-3 h-3 rounded-full bg-amber-500/80 shadow-lg shadow-amber-500/20"></div>
              <div className="w-3 h-3 rounded-full bg-emerald-500/80 shadow-lg shadow-emerald-500/20"></div>
            </div>
            <div className="flex items-center gap-2 ml-4">
              <Terminal className="w-4 h-4 text-slate-500" />
              <span className="text-xs font-mono text-slate-500 uppercase tracking-[0.2em] font-bold">Process Logs</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span className="text-[10px] font-mono text-emerald-500 uppercase font-bold tracking-wider">Live</span>
          </div>
        </div>

        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto font-mono text-sm space-y-2 custom-scrollbar pr-2"
        >
          <AnimatePresence initial={false}>
            {logs.map((log, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex gap-4 items-start group"
              >
                <span className="text-slate-600 select-none text-xs pt-0.5 min-w-[65px]">
                  {new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
                <div className="flex-1">
                  <span className={log.type === 'error' ? 'text-red-400' : 'text-blue-400'}>
                    <span className="text-slate-600 mr-2 group-hover:text-blue-400 transition-colors">$</span>
                    {log.message}
                  </span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          <div className="flex items-center gap-2 mt-2">
            <span className="text-slate-600 select-none text-xs pt-0.5 min-w-[65px]">
              {new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </span>
            <span className="text-blue-400">$</span>
            <div className="w-2 h-4 bg-blue-500 animate-pulse rounded-sm"></div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ProgressPanel;
