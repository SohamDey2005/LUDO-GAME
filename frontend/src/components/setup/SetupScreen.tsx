import React, { useState } from 'react';
import PlayerCountSelector from './PlayerCountSelector';
import PlayerSetupCard from './PlayerSetupCard';
import { PlayerConfig, createGame, GameState } from '../../services/api';

interface Props {
  onGameCreated: (state: GameState) => void;
}

const SetupScreen: React.FC<Props> = ({ onGameCreated }) => {
  const [step, setStep] = useState<1 | 2>(1);
  const [playerCount, setPlayerCount] = useState(0);
  const [players, setPlayers] = useState<PlayerConfig[]>([
    { name: 'SOHAM', color: 'red', player_type: 'human' },
    { name: 'AI Bot 1', color: 'green', player_type: 'ai' },
    { name: 'AI Bot 2', color: 'yellow', player_type: 'ai' },
    { name: 'AI Bot 3', color: 'blue', player_type: 'ai' },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCountSelect = (count: number) => {
    setPlayerCount(count);
    // Slice or pad players list
    const newPlayers = [...players];
    if (count > players.length) {
      const defaultColors = ['red', 'green', 'yellow', 'blue'];
      const usedColors = players.map(p => p.color);
      const availableColors = defaultColors.filter(c => !usedColors.includes(c));
      
      for (let i = players.length; i < count; i++) {
        newPlayers.push({
          name: `Player ${i + 1}`,
          color: availableColors[i - players.length] as any,
          player_type: 'ai'
        });
      }
    } else {
      newPlayers.splice(count);
    }
    setPlayers(newPlayers);
    setStep(2);
  };

  const updatePlayer = (index: number, config: PlayerConfig) => {
    const newPlayers = [...players];
    newPlayers[index] = config;
    setPlayers(newPlayers);
  };

  const handleStartGame = async () => {
    // Basic validation
    const colors = players.map(p => p.color);
    if (new Set(colors).size !== colors.length) {
        setError("Each player must have a unique color!");
        return;
    }

    setLoading(true);
    setError(null);
    try {
      const state = await createGame(players);
      onGameCreated(state);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const availableColors = ['red', 'green', 'yellow', 'blue'].filter(
    c => !players.map(p => p.color).includes(c)
  );

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-5xl space-y-12">
        <div className="text-center space-y-2">
          <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 tracking-tighter uppercase italic">
            Ludo Game Setup
          </h1>
          <p className="text-slate-500 text-sm font-medium tracking-[0.2em] uppercase">Configure your match</p>
        </div>

        {step === 1 ? (
          <PlayerCountSelector selectedCount={playerCount} onSelect={handleCountSelect} />
        ) : (
          <div className="space-y-8 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 justify-center">
              {players.map((p, i) => (
                <PlayerSetupCard
                  key={i}
                  index={i}
                  config={p}
                  availableColors={availableColors}
                  onUpdate={(config) => updatePlayer(i, config)}
                />
              ))}
            </div>

            {error && (
              <div className="max-w-md mx-auto bg-red-500/20 text-red-400 p-4 rounded-2xl text-center text-sm font-bold border border-red-500/30">
                {error}
              </div>
            )}

            <div className="flex justify-center gap-4">
              <button 
                onClick={() => setStep(1)}
                className="px-8 py-4 glass hover:bg-white/20 rounded-2xl font-bold uppercase tracking-widest text-sm"
              >
                Back
              </button>
              <button 
                onClick={handleStartGame}
                disabled={loading}
                className="btn-primary min-w-[200px]"
              >
                {loading ? 'Initializing...' : 'Start Match'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SetupScreen;
