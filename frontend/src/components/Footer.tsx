import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="fixed bottom-4 left-0 right-0 flex justify-center pointer-events-none z-50">
      <div className="animate-fade-in transition-opacity duration-1000">
        <p className="text-[10px] md:text-xs font-medium tracking-[0.2em] uppercase text-slate-400 opacity-60 hover:opacity-100 transition-all duration-300 pointer-events-auto cursor-default select-none">
          Created & Developed by <span className="text-blue-400 font-bold">SOHAM DEY</span>
        </p>
      </div>
    </footer>
  );
};

export default Footer;
