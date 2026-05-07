import React, { useEffect, useRef } from 'react';
import { createPhaserGame } from '../game/PhaserGame';
import { GameState } from '../services/api';

interface Props {
    gameState: GameState | null;
    onTokenClick: (tokenId: string) => void;
}

const PhaserGameComponent: React.FC<Props> = ({ gameState, onTokenClick }) => {
    const gameRef = useRef<Phaser.Game | null>(null);

    useEffect(() => {
        if (!gameRef.current) {
            gameRef.current = createPhaserGame();
            
            // Listen for token clicks from Phaser
            window.addEventListener('ludo-token-click', ((e: CustomEvent) => {
                onTokenClick(e.detail);
            }) as EventListener);
        }

        return () => {
            if (gameRef.current) {
                gameRef.current.destroy(true);
                gameRef.current = null;
            }
        };
    }, []);

    // Sync state to Phaser
    useEffect(() => {
        if (gameRef.current && gameState) {
            const scene = gameRef.current.scene.getScene('LudoBoardScene');
            if (scene) {
                scene.events.emit('update-game-state', gameState);
            }
        }
    }, [gameState]);

    return (
        <div className="w-full max-w-[600px] aspect-square rounded-xl overflow-hidden shadow-2xl border-4 border-slate-700 bg-white">
            <div id="phaser-container" className="w-full h-full" />
        </div>
    );
};

export default PhaserGameComponent;
