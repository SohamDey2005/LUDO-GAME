import * as Phaser from 'phaser';
import LudoBoardScene from '../scenes/LudoBoardScene';

const config: Phaser.Types.Core.GameConfig = {
    type: Phaser.AUTO,
    parent: 'phaser-container',
    width: '100%',
    height: '100%',
    backgroundColor: '#1e293b', 
    scene: [LudoBoardScene],
    scale: {
        mode: Phaser.Scale.RESIZE,
        autoCenter: Phaser.Scale.CENTER_BOTH,
    }
};

export const createPhaserGame = () => {
    return new Phaser.Game(config);
};
