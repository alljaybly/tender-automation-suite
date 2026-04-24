import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import UploadPanel from '../components/UploadPanel';
import ProgressPanel from '../components/ProgressPanel';
import ResultsPanel from '../components/ResultsPanel';
import WinScore from '../components/WinScore';
import ComplianceChecklist from '../components/ComplianceChecklist';
import ClausePanel from '../components/ClausePanel';
import EditDraftModal from '../components/EditDraftModal';
import Skeleton from '../components/ui/Skeleton';
import ErrorMessage from '../components/ui/ErrorMessage';
import { Trophy, AlertCircle, Clock } from 'lucide-react';

const Dashboard = () => {
  const { tenderId } = useParams();
  const [activeFilename, setActiveFilename] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [logs, setLogs] = useState([]);
  const [results, setResults] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const socketRef = useRef(null);
  const timeoutRef = useRef(null);

  useEffect(() => {
    if (tenderId) {
      loadHistoricalTender(tenderId);
    }
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [tenderId]);

  const loadHistoricalTender = async (id) => {
    setIsLoading(true);
    setError(null);
    setStatus('Loading historical tender...');
    setProgress(20);
    try {
      const response = await fetch(`/api/tender/${id}`);
      if (!response.ok) throw new Error('Tender not found');
      const data = await response.json();
      
      setResults({
        tender_data: data.tender_data || data,
        pricing: data.pricing || {},
        debate_result: data.debate_result || {},
        documents: data.documents || {}
      });
      setProgress(100);
      setStatus('Historical Tender Loaded');
      setLogs([{ message: `Loaded historical tender: ${data.reference || id}`, type: 'info' }]);
      toast.success('Historical tender loaded');
    } catch (error) {
      console.error('Error loading tender:', error);
      setError(error.message);
      setStatus('Error Loading Tender');
      toast.error('Failed to load historical tender');
    } finally {
      setIsLoading(false);
    }
  };

  const startProcessing = (filename) => {
    setActiveFilename(filename);
    setResults(null);
    setProgress(0);
    setStatus('Initializing...');
    setError(null);
    setLogs([{ message: `File received: ${filename}`, type: 'info' }]);

    if (socketRef.current) {
      socketRef.current.close();
    }

    // Set a timeout for 60 seconds
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      if (progress < 100 && !results) {
        setError('Processing is taking longer than expected. The AI might be handling a complex document.');
        toast.error('Processing timeout');
      }
    }, 60000);

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/process`;
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      socket.send(JSON.stringify({ filename }));
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.step === 'error') {
        setStatus('Error Occurred');
        setError(data.message || 'Processing failed');
        setLogs(prev => [...prev, { message: data.message, type: 'error' }]);
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        return;
      }

      if (data.progress) setProgress(data.progress);
      if (data.message) {
        setStatus(data.message);
        setLogs(prev => [...prev, { message: data.message, type: 'info' }]);
      }

      if (data.step === 'complete' || data.pricing) {
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        setResults({
          tender_data: data.tender_data || data.data,
          pricing: data.pricing || data.result?.pricing,
          debate_result: data.debate_result || {},
          documents: data.documents || {}
        });
        setProgress(100);
        setStatus('Processing Complete');
        toast.success('Tender processing complete!');
      }
    };

    socket.onerror = () => {
      setError('Connection lost. Please check your internet and try again.');
      toast.error('WebSocket connection error');
    };
  };

  const handleSaveDraft = (updatedTenderData, updatedPricing, newDocuments) => {
    setResults(prev => ({
      ...prev,
      tender_data: updatedTenderData,
      pricing: updatedPricing,
      documents: newDocuments || prev.documents
    }));
    toast.success('Draft saved successfully');
  };

  const handleReprice = (newPricing) => {
    setResults(prev => ({
      ...prev,
      pricing: newPricing
    }));
    toast.success('Pricing strategy applied');
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="grid grid-cols-1 lg:grid-cols-12 gap-8 p-4 md:p-0"
    >
      {/* LEFT PANEL: Upload & Demos */}
      <div className="lg:col-span-3 space-y-6 order-2 lg:order-1">
        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm sticky top-24">
          <UploadPanel 
            onUploadSuccess={startProcessing}
            onDemoStart={startProcessing}
          />
        </div>
      </div>

      {/* CENTER PANEL: Processing & Progress */}
      <div className="lg:col-span-6 space-y-6 order-1 lg:order-2">
        <AnimatePresence mode="wait">
          {error ? (
            <motion.div
              key="error"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
            >
              <ErrorMessage 
                message={error} 
                onRetry={() => activeFilename ? startProcessing(activeFilename) : window.location.reload()} 
              />
            </motion.div>
          ) : (
            <motion.div
              key="content"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <ProgressPanel 
                progress={progress}
                status={status}
                logs={logs}
              />
              
              {results ? (
                <ResultsPanel 
                  results={results} 
                  onEditDraft={() => setIsEditModalOpen(true)}
                  onReprice={handleReprice}
                />
              ) : activeFilename && (
                <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm space-y-4">
                  <Skeleton className="h-8 w-1/3 mb-4" />
                  <div className="grid grid-cols-2 gap-4">
                    <Skeleton className="h-24 rounded-2xl" />
                    <Skeleton className="h-24 rounded-2xl" />
                  </div>
                  <Skeleton className="h-48 rounded-2xl" />
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* RIGHT PANEL: Intelligence Panels */}
      <div className="lg:col-span-3 space-y-6 order-3">
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div key="loading" className="space-y-6">
              <Skeleton className="h-[120px] rounded-3xl" />
              <Skeleton className="h-[200px] rounded-3xl" />
              <Skeleton className="h-[150px] rounded-3xl" />
            </motion.div>
          ) : !results ? (
            <motion.div 
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm border-dashed border-2 flex flex-col items-center justify-center min-h-[400px] text-center"
            >
              <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-6">
                <Trophy className="text-slate-200" size={32} />
              </div>
              <h4 className="text-slate-500 font-bold text-lg mb-2">AI Intelligence</h4>
              <p className="text-slate-400 text-sm px-4">
                Upload a tender to see win probability, compliance analysis, and clause warnings.
              </p>
            </motion.div>
          ) : (
            <motion.div 
              key="results"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
            >
              <WinScore results={results} />
              <ComplianceChecklist results={results} />
              <ClausePanel results={results} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Modals */}
      {results && (
        <EditDraftModal 
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          tenderData={results.tender_data}
          pricing={results.pricing}
          onSave={handleSaveDraft}
        />
      )}
    </motion.div>
  );
};

export default Dashboard;
