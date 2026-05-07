import React, { useState, useEffect } from 'react';
import { audioManager } from '../services/audio';

interface DiceProps {
    value: number;
    isRolling: boolean;
    disabled?: boolean;
    onRoll: () => void;
}

const Dice: React.FC<DiceProps> = ({ value, isRolling, disabled, onRoll }) => {
    const [displayValue, setDisplayValue] = useState(value);

    // Animation effect: tumble the dots while isRolling is true
    useEffect(() => {
        let interval: any;
        if (isRolling) {
            interval = setInterval(() => {
                setDisplayValue(Math.floor(Math.random() * 6) + 1);
            }, 80);
        } else {
            setDisplayValue(value);
        }
        return () => clearInterval(interval);
    }, [isRolling, value]);

    const handleRoll = () => {
        audioManager.play('roll');
        onRoll();
    };

    const renderDots = (val: number) => {
        const dots = [];
        const dotConfig: Record<number, number[]> = {
            1: [4],
            2: [0, 8],
            3: [0, 4, 8],
            4: [0, 2, 6, 8],
            5: [0, 2, 4, 6, 8],
            6: [0, 2, 3, 5, 6, 8]
        };

        const activeDots = dotConfig[val] || [];

        for (let i = 0; i < 9; i++) {
            if (activeDots.includes(i)) {
                dots.push(<div key={i} className="w-2.5 h-2.5 sm:w-3 sm:h-3 bg-slate-800 rounded-full shadow-inner" />);
            } else {
                dots.push(<div key={i} className="w-2.5 h-2.5 sm:w-3 sm:h-3" />);
            }
        }
        return dots;
    };

    return (
        <div className="flex flex-col items-center gap-3">
            <button 
                onClick={handleRoll}
                disabled={isRolling || disabled}
                className={`
                    relative w-16 h-16 sm:w-20 sm:h-20 bg-white rounded-2xl shadow-xl flex items-center justify-center
                    transition-all duration-200 ease-in-out border-b-4 border-slate-300
                    ${isRolling ? 'animate-[shake_0.2s_infinite] cursor-not-allowed border-b-0 translate-y-1' : (disabled ? 'opacity-50 cursor-not-allowed grayscale-[0.5]' : 'hover:-translate-y-1 hover:shadow-2xl cursor-pointer active:translate-y-1 active:border-b-0')}
                `}
            >
                <div className="grid grid-cols-3 grid-rows-3 gap-1 p-2 w-full h-full">
                    {renderDots(displayValue)}
                </div>
            </button>
            <span className="text-slate-400 font-bold uppercase tracking-[0.2em] text-[10px] sm:text-xs">
                {isRolling ? 'Rolling...' : (disabled ? 'Dice Locked' : 'Roll Dice')}
            </span>
        </div>
    );
};

export default Dice;
