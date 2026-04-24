import React from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  TrendingUp, 
  CheckCircle2, 
  Zap, 
  ArrowRight, 
  BarChart3, 
  ShieldCheck, 
  LayoutDashboard,
  UploadCloud,
  MousePointerClick,
  Download
} from 'lucide-react';

const LandingPage = ({ onStart }) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="relative pt-20 pb-32 overflow-hidden">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10"
        >
          <div className="text-center">
            <motion.h1 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-5xl md:text-7xl font-black text-slate-900 tracking-tight mb-6"
            >
              Win More Tenders <br />
              <span className="text-blue-600">Without Guesswork</span>
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="text-xl text-slate-600 max-w-2xl mx-auto mb-10"
            >
              Upload a tender. Get pricing, documents, and a win strategy in minutes. 
              The AI-powered workspace for professional bidding teams.
            </motion.p>
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
              className="flex flex-col sm:flex-row justify-center gap-4"
            >
              <button 
                onClick={onStart}
                className="bg-blue-600 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:bg-blue-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-200 group"
              >
                Try Demo
                <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
              </button>
              <button 
                onClick={onStart}
                className="bg-white text-slate-900 border-2 border-slate-200 px-8 py-4 rounded-2xl font-bold text-lg hover:border-slate-300 transition-all flex items-center justify-center gap-2"
              >
                <UploadCloud size={20} />
                Upload Tender
              </button>
            </motion.div>
          </div>
        </motion.div>
        
        {/* Background blobs */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-0 opacity-10 pointer-events-none">
          <motion.div 
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.1, 0.2, 0.1]
            }}
            transition={{ duration: 8, repeat: Infinity }}
            className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-400 rounded-full blur-3xl"
          ></motion.div>
          <motion.div 
            animate={{ 
              scale: [1, 1.3, 1],
              opacity: [0.1, 0.15, 0.1]
            }}
            transition={{ duration: 10, repeat: Infinity, delay: 1 }}
            className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-400 rounded-full blur-3xl"
          ></motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={containerVariants}
            className="text-center mb-16"
          >
            <h2 className="text-3xl font-black text-slate-900 mb-4">Powerful AI Features</h2>
            <p className="text-slate-600">Everything you need to automate your tender response process.</p>
          </motion.div>
          
          <motion.div 
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={containerVariants}
            className="grid md:grid-cols-2 lg:grid-cols-4 gap-8"
          >
            {[
              { 
                title: 'AI Tender Analysis', 
                desc: 'Instant extraction of key requirements, risks, and scope.', 
                icon: <FileText className="text-blue-600" size={24} /> 
              },
              { 
                title: 'Pricing Engine', 
                desc: 'Smart margin optimization based on win probability.', 
                icon: <TrendingUp className="text-blue-600" size="24" /> 
              },
              { 
                title: 'Win Score', 
                desc: 'Data-driven probability of success for every bid.', 
                icon: <BarChart3 className="text-blue-600" size="24" /> 
              },
              { 
                title: 'Document Generator', 
                desc: 'Auto-fill compliant bid documents in seconds.', 
                icon: <Zap className="text-blue-600" size="24" /> 
              }
            ].map((feature, i) => (
              <motion.div 
                key={i} 
                variants={itemVariants}
                whileHover={{ y: -10 }}
                className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm hover:shadow-xl transition-all"
              >
                <div className="bg-blue-50 w-12 h-12 rounded-2xl flex items-center justify-center mb-6">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
                <p className="text-slate-600 text-sm leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-black text-slate-900 mb-4">How It Works</h2>
            <p className="text-slate-600">Three simple steps to a professional tender response.</p>
          </div>
          
          <div className="flex flex-col md:flex-row justify-between items-center gap-12 relative">
            <div className="hidden md:block absolute top-1/2 left-0 w-full h-0.5 bg-slate-100 -z-10"></div>
            
            {[
              { step: 'Step 1', title: 'Upload', desc: 'Drag and drop your tender documents (PDF/DOCX).', icon: <UploadCloud size={32} /> },
              { step: 'Step 2', title: 'Analyze', desc: 'Our AI extracts data and suggests pricing strategies.', icon: <MousePointerClick size={32} /> },
              { step: 'Step 3', title: 'Download & Submit', desc: 'Generate your final bid documents instantly.', icon: <Download size={32} /> }
            ].map((item, i) => (
              <motion.div 
                key={i} 
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.2 }}
                className="flex-1 text-center bg-white p-6 relative"
              >
                <div className="bg-blue-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-white shadow-lg shadow-blue-200">
                  {item.icon}
                </div>
                <div className="inline-block px-3 py-1 bg-blue-50 text-blue-600 text-xs font-bold rounded-full mb-3 uppercase tracking-wider">
                  {item.step}
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">{item.title}</h3>
                <p className="text-slate-600 text-sm">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-24 bg-slate-900 text-white rounded-[3rem] mx-4 mb-24 overflow-hidden relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-black mb-4">Simple, Transparent Pricing</h2>
            <p className="text-slate-400">Choose the plan that fits your bidding volume.</p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Free Plan */}
            <motion.div 
              whileHover={{ y: -5 }}
              className="bg-slate-800 p-8 rounded-3xl border border-slate-700 hover:border-blue-500 transition-all group"
            >
              <h3 className="text-xl font-bold mb-2">Free</h3>
              <div className="text-4xl font-black mb-6">$0<span className="text-lg text-slate-400 font-normal">/month</span></div>
              <ul className="space-y-4 mb-10">
                <li className="flex items-center gap-3 text-slate-300">
                  <CheckCircle2 className="text-blue-500" size={18} />
                  1 tender per day
                </li>
                <li className="flex items-center gap-3 text-slate-300">
                  <CheckCircle2 className="text-blue-500" size={18} />
                  Standard analysis
                </li>
                <li className="flex items-center gap-3 text-slate-300">
                  <CheckCircle2 className="text-blue-500" size={18} />
                  Basic document generation
                </li>
              </ul>
              <button 
                onClick={onStart}
                className="w-full py-4 rounded-2xl font-bold bg-slate-700 hover:bg-slate-600 transition-all"
              >
                Get Started
              </button>
            </motion.div>
            
            {/* Pro Plan */}
            <motion.div 
              whileHover={{ y: -10 }}
              className="bg-blue-600 p-8 rounded-3xl border border-blue-400 shadow-2xl shadow-blue-500/20 transform md:-translate-y-4"
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-xl font-bold">Pro</h3>
                <span className="bg-white/20 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest">Recommended</span>
              </div>
              <div className="text-4xl font-black mb-6">$99<span className="text-lg text-blue-100 font-normal">/month</span></div>
              <ul className="space-y-4 mb-10">
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="text-blue-200" size={18} />
                  Unlimited tenders
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="text-blue-200" size={18} />
                  Advanced Win Strategy insights
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="text-blue-200" size={18} />
                  Priority support
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="text-blue-200" size={18} />
                  Custom document templates
                </li>
              </ul>
              <button 
                onClick={onStart}
                className="w-full py-4 rounded-2xl font-bold bg-white text-blue-600 hover:bg-blue-50 transition-all shadow-lg shadow-blue-700/20"
              >
                Go Pro Now
              </button>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <section className="py-24 text-center">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-4xl font-black text-slate-900 mb-6">Start Winning More Tenders Today</h2>
          <p className="text-lg text-slate-600 mb-10">Join 500+ companies using TenderFlow to scale their government and private sector bidding.</p>
          <button 
            onClick={onStart}
            className="bg-blue-600 text-white px-10 py-5 rounded-2xl font-bold text-xl hover:bg-blue-700 transition-all shadow-xl shadow-blue-200"
          >
            Enter Workspace
          </button>
          
          <div className="mt-20 pt-8 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-6 text-slate-400 text-sm">
            <div className="flex items-center gap-2">
              <div className="bg-slate-200 p-1 rounded-md">
                <FileText size={14} className="text-slate-500" />
              </div>
              <span className="font-bold text-slate-900 tracking-tight">TenderFlow</span>
            </div>
            <p>© 2026 TenderFlow AI. All rights reserved.</p>
            <div className="flex gap-8">
              <a href="#" className="hover:text-slate-600">Privacy</a>
              <a href="#" className="hover:text-slate-600">Terms</a>
              <a href="#" className="hover:text-slate-600">Support</a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
