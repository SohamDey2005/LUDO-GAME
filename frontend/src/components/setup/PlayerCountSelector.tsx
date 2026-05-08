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
        {options.map((count) => (
          <button
            key={count}
            onClick={() => onSelect(count)}
            className={`
              w-24 h-24 rounded-2xl flex flex-col items-center justify-center gap-2 transition-all duration-300
              ${selectedCount === count 
                ? 'bg-blue-500 shadow-[0_0_25px_rgba(59,130,246,0.5)] scale-110 border-2 border-white' 
                : 'glass hover:bg-white/20 scale-100'}
            `}
          >
            <span className="text-3xl font-black">{count}</span>
            <span className="text-[10px] uppercase font-bold tracking-widest opacity-70">Players</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default PlayerCountSelector;
