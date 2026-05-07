import * as Phaser from 'phaser';
import LudoBoardScene from '../scenes/LudoBoardScene';

const config: Phaser.Types.Core.GameConfig = {
    type: Phaser.AUTO,
    parent: 'phaser-container',
    width: 600,
    height: 600,
    backgroundColor: '#1e293b', // slate-800
    scene: [LudoBoardScene],
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
        parent: 'phaser-container',
        width: 600,
        height: 600
    }
};

export const createPhaserGame = () => {
    return new Phaser.Game(config);
};
