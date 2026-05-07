import React from 'react';
import { audioManager } from '../services/audio';

interface DiceProps {
    value: number;
    isRolling: boolean;
    onRoll: () => void;
}

const Dice: React.FC<DiceProps> = ({ value, isRolling, onRoll }) => {
    const handleRoll = () => {
        audioManager.play('roll');
        onRoll();
    };
    const renderDots = () => {
        const dots = [];
        // A simple dot mapping based on dice value
        const dotConfig: Record<number, number[]> = {
            1: [4],
            2: [0, 8],
            3: [0, 4, 8],
            4: [0, 2, 6, 8],
            5: [0, 2, 4, 6, 8],
            6: [0, 2, 3, 5, 6, 8]
        };

        const activeDots = dotConfig[value] || [];

        for (let i = 0; i < 9; i++) {
            if (activeDots.includes(i)) {
                dots.push(<div key={i} className="w-3 h-3 bg-slate-800 rounded-full" />);
            } else {
                dots.push(<div key={i} className="w-3 h-3" />);
            }
        }
        return dots;
    };

    return (
        <div className="flex flex-col items-center gap-4">
            <button 
                onClick={handleRoll}
                disabled={isRolling}
                className={`
                    relative w-20 h-20 bg-white rounded-2xl shadow-xl flex items-center justify-center
                    transition-all duration-300 ease-in-out border-b-4 border-slate-300
                    ${isRolling ? 'animate-bounce cursor-not-allowed scale-95 border-b-0 translate-y-1' : 'hover:-translate-y-1 hover:shadow-2xl cursor-pointer active:translate-y-1 active:border-b-0'}
                `}
            >
                <div className="grid grid-cols-3 grid-rows-3 gap-1 p-2 w-full h-full">
                    {renderDots()}
                </div>
            </button>
            <span className="text-slate-300 font-semibold uppercase tracking-wider text-sm">
                {isRolling ? 'Rolling...' : 'Roll Dice'}
            </span>
        </div>
    );
};

export default Dice;
