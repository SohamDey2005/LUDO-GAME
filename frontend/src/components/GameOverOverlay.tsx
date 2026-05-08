import React from 'react';
import { GameState } from '../services/api';

interface Props {
  gameState: GameState;
  onRestart: () => void;
}

const GameOverOverlay: React.FC<Props> = ({ gameState, onRestart }) => {
  const medals = ['🥇', '🥈', '🥉', '🏅'];

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/90 backdrop-blur-xl animate-fade-in">
      <div className="glass-dark p-12 rounded-[3rem] border-2 border-white/10 max-w-lg w-full text-center space-y-12 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        <div className="space-y-4">
          <h2 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 uppercase italic tracking-tighter">
            Match Over!
          </h2>
          <p className="text-slate-400 font-bold uppercase tracking-[0.3em] text-sm">Final Rankings Determined</p>
        </div>

        <div className="space-y-4">
          {gameState.rankings.map((color, index) => (
            <div 
                key={color} 
                className={`flex items-center justify-between p-4 rounded-2xl border transition-all duration-500 animate-fade-in`}
                style={{ 
                    animationDelay: `${index * 0.2}s`,
                    backgroundColor: `${color}22`,
                    borderColor: `${color}44`
                }}
            >
              <div className="flex items-center gap-6">
                <span className="text-4xl">{medals[index]}</span>
                <div className="text-left">
                    <p className="text-[10px] uppercase font-black text-slate-500 tracking-widest">Position {index + 1}</p>
                    <p className="text-xl font-bold capitalize text-white">{color} Player</p>
                </div>
              </div>
              <div 
                className="w-12 h-12 rounded-full shadow-[0_0_20px_rgba(255,255,255,0.2)]" 
                style={{ backgroundColor: color }}
              />
            </div>
          ))}
        </div>

        <button 
          onClick={onRestart}
          className="btn-primary w-full py-5 text-xl rounded-2xl"
        >
          Return to Setup
        </button>
      </div>
    </div>
  );
};

export default GameOverOverlay;
