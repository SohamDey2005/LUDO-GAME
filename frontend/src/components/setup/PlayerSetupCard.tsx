import React from 'react';
import { PlayerConfig } from '../../services/api';

interface Props {
  index: number;
  config: PlayerConfig;
  availableColors: string[];
  onUpdate: (config: PlayerConfig) => void;
}

const PlayerSetupCard: React.FC<Props> = ({ index, config, availableColors, onUpdate }) => {
  const colors = [
    { name: 'red', hex: '#ff4136' },
    { name: 'green', hex: '#2ecc40' },
    { name: 'yellow', hex: '#ffdc00' },
    { name: 'blue', hex: '#0074d9' }
  ];

  return (
    <div className="glass-dark p-6 rounded-3xl w-full max-w-sm space-y-6 border border-white/5 animate-fade-in" style={{ animationDelay: `${index * 0.1}s` }}>
      <div className="flex justify-between items-center">
        <h3 className="text-sm font-black uppercase tracking-[0.2em] text-slate-300">Player {index + 1}</h3>
        <div className="flex bg-slate-900/50 p-1 rounded-xl border border-white/5">
          <button
            onClick={() => onUpdate({ ...config, player_type: 'human' })}
            className={`px-3 py-1 text-[10px] uppercase font-bold rounded-lg transition-all ${config.player_type === 'human' ? 'bg-blue-500 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            Human
          </button>
          <button
            onClick={() => onUpdate({ ...config, player_type: 'ai' })}
            className={`px-3 py-1 text-[10px] uppercase font-bold rounded-lg transition-all ${config.player_type === 'ai' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            AI
          </button>
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-[10px] uppercase font-black text-slate-400 tracking-widest">Nickname</label>
        <input
          type="text"
          value={config.name}
          onChange={(e) => onUpdate({ ...config, name: e.target.value })}
          placeholder={`Player ${index + 1}`}
          className="w-full bg-slate-950/50 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500 transition-all font-medium placeholder:text-slate-600"
        />
      </div>

      <div className="space-y-2">
        <label className="text-[10px] uppercase font-black text-slate-400 tracking-widest">Choose Color</label>
        <div className="flex justify-between gap-2">
          {colors.map((c) => {
            const isTaken = !availableColors.includes(c.name) && config.color !== c.name;
            const isSelected = config.color === c.name;
            
            return (
              <button
                key={c.name}
                disabled={isTaken}
                onClick={() => onUpdate({ ...config, color: c.name as any })}
                className={`
                  w-10 h-10 rounded-full transition-all duration-300 relative
                  ${isSelected ? 'scale-125 ring-2 ring-white ring-offset-2 ring-offset-slate-900 shadow-lg' : 'scale-100'}
                  ${isTaken ? 'opacity-20 cursor-not-allowed grayscale' : 'hover:scale-110'}
                `}
                style={{ backgroundColor: c.hex }}
              >
                {isSelected && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default PlayerSetupCard;
