import React from 'react';

interface Props {
  selectedCount: number;
  onSelect: (count: number) => void;
}

const PlayerCountSelector: React.FC<Props> = ({ selectedCount, onSelect }) => {
  const options = [2, 3, 4];

  return (
    <div className="flex flex-col items-center gap-6 animate-fade-in">
      <h2 className="text-2xl font-bold text-slate-300 uppercase tracking-[0.3em]">Select Player Count</h2>
      <div className="flex gap-4">
        {options.map((count) => {
          const isSelected = selectedCount === count;
          const config = {
            2: { color: 'from-green-500 to-emerald-600', glow: 'rgba(16,185,129,0.5)', label: 'Duo' },
            3: { color: 'from-yellow-500 to-orange-600', glow: 'rgba(245,158,11,0.5)', label: 'Trio' },
            4: { color: 'from-blue-500 to-indigo-600', glow: 'rgba(59,130,246,0.5)', label: 'Classic' }
          }[count as 2|3|4];

          return (
            <button
              key={count}
              onClick={() => onSelect(count)}
              className={`
                w-24 h-24 rounded-3xl flex flex-col items-center justify-center gap-1 transition-all duration-500
                ${isSelected 
                  ? `bg-gradient-to-br ${config.color} shadow-[0_0_30px_${config.glow}] scale-110 border-2 border-white/50` 
                  : 'bg-slate-800/40 border border-white/10 hover:bg-slate-800/60 scale-100 hover:scale-105'}
              `}
            >
              <span className={`text-3xl font-black ${isSelected ? 'text-white' : 'text-slate-300'}`}>{count}</span>
              <span className={`text-[10px] uppercase font-black tracking-widest ${isSelected ? 'text-white/90' : 'text-slate-500'}`}>
                {config.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default PlayerCountSelector;
