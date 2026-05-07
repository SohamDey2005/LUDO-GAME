import { useState, useEffect } from 'react';
import PhaserGameComponent from './components/PhaserGameComponent';
import Dice from './components/Dice';
import { createGame, rollDice, moveToken, GameState } from './services/api';
import { socketManager } from './services/socket';
import { audioManager } from './services/audio';

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [isRolling, setIsRolling] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [clientId] = useState<string>(Math.random().toString(36).substring(7));

  useEffect(() => {
    // Listen for real-time state updates
    socketManager.onUpdate((state) => {
        setGameState(state);
    });

    // Initialize game and connect to socket
    createGame().then(state => {
        setGameState(state);
        socketManager.connect(state.id, clientId);
    }).catch(e => setError(e.message));

    return () => {
        socketManager.disconnect();
    };
  }, [clientId]);

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

  if (!gameState) {
      return <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">Loading...</div>;
  }

  return (
    <div className="min-h-screen flex flex-col md:flex-row items-center justify-center gap-6 md:gap-12 p-4 sm:p-8 bg-gradient-to-br from-slate-900 to-slate-800 overflow-x-hidden">
      
      <div className="flex flex-col items-center gap-6 sm:gap-8 bg-slate-800/50 p-6 sm:p-8 rounded-3xl backdrop-blur-md border border-slate-700 shadow-2xl w-full max-w-sm md:max-w-xs lg:max-w-sm">
        <h1 className="text-3xl sm:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 tracking-tight">
            LUDO AI
        </h1>
        
        <div className="w-full space-y-4">
            <div className="bg-slate-700/50 p-4 rounded-xl border border-slate-600">
                <h3 className="text-slate-300 text-xs font-bold uppercase tracking-wider mb-2">Current Turn</h3>
                <div className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded-full shadow-[0_0_10px_rgba(255,255,255,0.5)]`} style={{backgroundColor: gameState.current_turn}}></div>
                    <span className="text-white font-medium capitalize">{gameState.current_turn} Player</span>
                </div>
            </div>

            {gameState.last_action && (
                <div className="bg-slate-800/80 p-3 rounded-lg text-sm text-slate-300 border border-slate-700">
                    {gameState.last_action}
                </div>
            )}
            
            {error && (
                <div className="bg-red-500/20 text-red-300 p-3 rounded-lg text-sm border border-red-500/50">
                    {error}
                </div>
            )}
            
            {gameState.winner && (
                <div className="bg-green-500/20 text-green-300 p-3 rounded-lg text-sm border border-green-500/50 font-bold">
                    Winner: {gameState.winner}!
                </div>
            )}
        </div>

        <div className="pt-4 border-t border-slate-700 w-full flex justify-center">
            <div className="flex flex-col items-center gap-4">
                <Dice 
                    value={gameState.dice_value || 6} 
                    isRolling={isRolling} 
                    disabled={gameState.dice_value !== null}
                    onRoll={handleRollDice} 
                />
                {gameState.dice_value !== null && !isRolling && (
                    <span className="text-blue-400 font-bold animate-pulse text-sm">
                        Select a token to move!
                    </span>
                )}
            </div>
        </div>
      </div>

      <PhaserGameComponent gameState={gameState} onTokenClick={handleTokenClick} />

      {/* Footer Credit */}
      <footer className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 pointer-events-none animate-in fade-in duration-1000">
        <p className="text-slate-500 text-[10px] sm:text-xs font-medium tracking-[0.2em] uppercase opacity-60">
          Created & Developed by SOHAM DEY
        </p>
      </footer>
    </div>
  );
}

export default App;
