import { useState, useEffect } from 'react';
import PhaserGameComponent from './components/PhaserGameComponent';
import Dice from './components/Dice';
import { createGame, rollDice, moveToken, GameState } from './services/api';
import { socketManager } from './services/socket';
import { audioManager } from './services/audio';

import SetupScreen from './components/setup/SetupScreen';

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [phase, setPhase] = useState<'setup' | 'playing'>('setup');
  const [isRolling, setIsRolling] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [clientId] = useState<string>(Math.random().toString(36).substring(7));

  useEffect(() => {
    // Listen for real-time state updates
    socketManager.onUpdate((state) => {
        setGameState(state);
    });

    return () => {
        socketManager.disconnect();
    };
  }, []);

  useEffect(() => {
    // Only connect if we have a game state
    if (gameState?.id) {
        socketManager.connect(gameState.id, clientId);
    }
  }, [gameState?.id, clientId]);

  // Handle AI turns automatically
  useEffect(() => {
    if (gameState && gameState.status === 'in_progress' && !isRolling) {
      const currentPlayer = gameState.players[gameState.current_turn];
      if (currentPlayer && currentPlayer.player_type === 'ai') {
        // Add a small delay for realism
        const timer = setTimeout(async () => {
          try {
            await fetch(`https://ludo-backend-175911647281.us-central1.run.app/api/game/${gameState.id}/ai-move`, { method: 'POST' });
            // The socket will handle the state update
          } catch (e) {
            console.error("AI move failed", e);
          }
        }, 1000);
        return () => clearTimeout(timer);
      }
    }
  }, [gameState, isRolling]);

  const handleRollDice = async () => {
    if (!gameState) return;
    setIsRolling(true);
    setError(null);
    try {
        const newState = await rollDice(gameState.id);
        setGameState(newState);
    } catch (e: any) {
        setError(e.message);
    } finally {
        setIsRolling(false);
    }
  };

  const handleTokenClick = async (tokenId: string) => {
      if (!gameState) return;
      setError(null);
      audioManager.play('move');
      try {
          const newState = await moveToken(gameState.id, gameState.current_turn, tokenId);
          setGameState(newState);
      } catch (e: any) {
          setError(e.message);
      }
  };

  const handleGameCreated = (state: GameState) => {
    setGameState(state);
    setPhase('playing');
  };

  if (phase === 'setup' || !gameState) {
    return <SetupScreen onGameCreated={handleGameCreated} />;
  }

  return (
    <div className="min-h-screen flex flex-col lg:flex-row items-center justify-center lg:gap-12 p-4 sm:p-8 bg-gradient-to-br from-slate-900 to-slate-800 overflow-x-hidden">
      
      {/* HUD Container */}
      <div className="flex flex-col items-center gap-4 sm:gap-8 bg-slate-800/50 p-6 sm:p-8 rounded-3xl backdrop-blur-md border border-slate-700 shadow-2xl w-full max-w-sm lg:max-w-xs xl:max-w-sm mb-8 lg:mb-0">
        <h1 className="text-3xl sm:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 tracking-tight">
            LUDO GAME
        </h1>
        
        <div className="w-full space-y-3 sm:space-y-4">
            <div className="bg-slate-700/50 p-3 sm:p-4 rounded-xl border border-slate-600">
                <h3 className="text-slate-300 text-[10px] sm:text-xs font-bold uppercase tracking-wider mb-1 sm:mb-2">Current Turn</h3>
                <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 sm:w-4 sm:h-4 rounded-full shadow-[0_0_10px_rgba(255,255,255,0.5)]`} style={{backgroundColor: gameState.current_turn}}></div>
                    <span className="text-white text-sm sm:text-base font-medium capitalize">{gameState.current_turn} Player</span>
                </div>
            </div>

            {gameState.last_action && (
                <div className="bg-slate-800/80 p-2 sm:p-3 rounded-lg text-[11px] sm:text-sm text-slate-300 border border-slate-700">
                    {gameState.last_action}
                </div>
            )}
            
            {error && (
                <div className="bg-red-500/20 text-red-300 p-2 sm:p-3 rounded-lg text-[11px] sm:text-sm border border-red-500/50">
                    {error}
                </div>
            )}
            
            {gameState.rankings && gameState.rankings.length > 0 && (
                <div className="bg-slate-800/80 p-4 rounded-xl border border-slate-700 space-y-2">
                    <h3 className="text-slate-300 text-[10px] font-bold uppercase tracking-[0.2em] mb-3">Leaderboard</h3>
                    {gameState.rankings.map((color, index) => (
                        <div key={color} className="flex items-center justify-between group">
                            <div className="flex items-center gap-3">
                                <span className={`text-xs font-bold ${index === 0 ? 'text-yellow-400' : index === 1 ? 'text-slate-300' : index === 2 ? 'text-amber-600' : 'text-slate-500'}`}>
                                    {index + 1}{index === 0 ? 'st' : index === 1 ? 'nd' : index === 2 ? 'rd' : 'th'}
                                </span>
                                <div className="w-2 h-2 rounded-full shadow-[0_0_5px_rgba(255,255,255,0.3)]" style={{backgroundColor: color}}></div>
                                <span className="text-white text-xs font-medium capitalize">{color} Player</span>
                            </div>
                            {index === 0 && <span className="text-[10px] bg-yellow-400/20 text-yellow-400 px-2 py-0.5 rounded-full font-bold uppercase tracking-tighter">Winner</span>}
                        </div>
                    ))}
                </div>
            )}
        </div>

        <div className="pt-3 sm:pt-4 border-t border-slate-700 w-full flex justify-center">
            <div className="flex flex-col items-center gap-3 sm:gap-4">
                <Dice 
                    value={gameState.last_rolled_value || 6} 
                    isRolling={isRolling} 
                    disabled={gameState.dice_value !== null}
                    onRoll={handleRollDice} 
                />
                {gameState.dice_value !== null && !isRolling && (
                    <span className="text-blue-400 font-bold animate-pulse text-[11px] sm:text-sm">
                        Select a token to move!
                    </span>
                )}
            </div>
        </div>
      </div>

      {/* Game Board Container */}
      <div className="w-full flex justify-center items-center px-2">
        <PhaserGameComponent gameState={gameState} onTokenClick={handleTokenClick} />
      </div>

      {/* Footer Credit */}
      <footer className="fixed bottom-2 sm:bottom-4 left-1/2 -translate-x-1/2 z-50 pointer-events-none animate-in fade-in duration-1000">
        <p className="text-slate-500 text-[8px] sm:text-[10px] md:text-xs font-medium tracking-[0.2em] uppercase opacity-60">
          Created & Developed by SOHAM DEY
        </p>
      </footer>
    </div>
  );
}

export default App;
