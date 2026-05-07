import * as Phaser from 'phaser';

// Define the board mapping (Absolute 0-51 coordinates to grid x,y)
// Based on the second image: Red starts at Top-Left arm entrance (6, 1)
const pathCoords = [
    // Top arm (Red)
    {x:6,y:1}, {x:6,y:2}, {x:6,y:3}, {x:6,y:4}, {x:6,y:5}, 
    {x:5,y:6}, {x:4,y:6}, {x:3,y:6}, {x:2,y:6}, {x:1,y:6}, {x:0,y:6}, 
    {x:0,y:7}, 
    // Left arm (Blue)
    {x:0,y:8}, {x:1,y:8}, {x:2,y:8}, {x:3,y:8}, {x:4,y:8}, {x:5,y:8},
    {x:6,y:9}, {x:6,y:10}, {x:6,y:11}, {x:6,y:12}, {x:6,y:13}, {x:6,y:14},
    {x:7,y:14},
    // Bottom arm (Yellow)
    {x:8,y:14}, {x:8,y:13}, {x:8,y:12}, {x:8,y:11}, {x:8,y:10}, {x:8,y:9},
    {x:9,y:8}, {x:10,y:8}, {x:11,y:8}, {x:12,y:8}, {x:13,y:8}, {x:14,y:8},
    {x:14,y:7},
    // Right arm (Green)
    {x:14,y:6}, {x:13,y:6}, {x:12,y:6}, {x:11,y:6}, {x:10,y:6}, {x:9,y:6},
    {x:8,y:5}, {x:8,y:4}, {x:8,y:3}, {x:8,y:2}, {x:8,y:1}, {x:8,y:0},
    {x:7,y:0}, {x:6,y:0}
];

// Map colors to their start square index in pathCoords
const START_SQUARES_MAP = {
    red: 0,
    blue: 13,
    yellow: 26,
    green: 39
};

const homePaths: Record<string, {x:number, y:number}[]> = {
    red: [{x:7,y:1},{x:7,y:2},{x:7,y:3},{x:7,y:4},{x:7,y:5}],
    blue: [{x:1,y:7},{x:2,y:7},{x:3,y:7},{x:4,y:7},{x:5,y:7}],
    yellow: [{x:7,y:13},{x:7,y:12},{x:7,y:11},{x:7,y:10},{x:7,y:9}],
    green: [{x:13,y:7},{x:12,y:7},{x:11,y:7},{x:10,y:7},{x:9,y:7}]
};

const baseSpots: Record<string, {x:number, y:number}[]> = {
    red: [{x:1.5,y:1.5}, {x:3.5,y:1.5}, {x:1.5,y:3.5}, {x:3.5,y:3.5}],
    green: [{x:10.5,y:1.5}, {x:12.5,y:1.5}, {x:10.5,y:3.5}, {x:12.5,y:3.5}],
    yellow: [{x:10.5,y:10.5}, {x:12.5,y:10.5}, {x:10.5,y:12.5}, {x:12.5,y:12.5}],
    blue: [{x:1.5,y:10.5}, {x:3.5,y:10.5}, {x:1.5,y:12.5}, {x:3.5,y:12.5}]
};

// Stars (Safe Zones) indices in pathCoords
const STAR_INDICES = [1, 14, 27, 40];

export default class LudoBoardScene extends Phaser.Scene {
    private tokenSprites: Phaser.GameObjects.Arc[] = [];
    private cellSize: number = 40;

    constructor() {
        super('LudoBoardScene');
    }

    create() {
        const graphics = this.add.graphics();
        const boardSize = Math.min(window.innerWidth, 600);
        this.cellSize = boardSize / 15;
        
        graphics.fillStyle(0xffffff, 1);
        graphics.fillRect(0, 0, boardSize, boardSize);

        const colors = { red: 0xff0000, green: 0x00ff00, yellow: 0xffff00, blue: 0x00bfff, white: 0xffffff };

        const drawBase = (x: number, y: number, color: number) => {
            graphics.fillStyle(color, 1);
            graphics.fillRect(x * this.cellSize, y * this.cellSize, 6 * this.cellSize, 6 * this.cellSize);
            graphics.fillStyle(colors.white, 1);
            graphics.fillRect((x + 1) * this.cellSize, (y + 1) * this.cellSize, 4 * this.cellSize, 4 * this.cellSize);
        };

        // Bases: Top-Left (Red), Top-Right (Green), Bottom-Right (Yellow), Bottom-Left (Blue)
        drawBase(0, 0, colors.red); 
        drawBase(9, 0, colors.green);
        drawBase(9, 9, colors.yellow); 
        drawBase(0, 9, colors.blue);

        // Draw Home Stretches
        ['red','green','yellow','blue'].forEach((col) => {
            graphics.fillStyle(colors[col as keyof typeof colors], 1);
            homePaths[col].forEach(p => {
                graphics.fillRect(p.x * this.cellSize, p.y * this.cellSize, this.cellSize, this.cellSize);
            });
        });

        // Center Triangle Design
        const cx = 7.5 * this.cellSize;
        const cy = 7.5 * this.cellSize;
        const mid = 1.5 * this.cellSize;
        
        graphics.fillStyle(colors.red, 1);
        graphics.fillTriangle(cx - mid, cy - mid, cx + mid, cy - mid, cx, cy);
        graphics.fillStyle(colors.green, 1);
        graphics.fillTriangle(cx + mid, cy - mid, cx + mid, cy + mid, cx, cy);
        graphics.fillStyle(colors.yellow, 1);
        graphics.fillTriangle(cx - mid, cy + mid, cx + mid, cy + mid, cx, cy);
        graphics.fillStyle(colors.blue, 1);
        graphics.fillTriangle(cx - mid, cy - mid, cx - mid, cy + mid, cx, cy);

        // Draw Stars on Safe Squares
        const starColors = [colors.red, colors.green, colors.yellow, colors.blue];
        STAR_INDICES.forEach((idx, i) => {
            const coord = pathCoords[idx];
            this.drawStar(coord.x * this.cellSize + this.cellSize/2, coord.y * this.cellSize + this.cellSize/2, 5, this.cellSize * 0.4, this.cellSize * 0.2, starColors[i]);
        });

        // Draw Arrows at Starts
        this.drawArrow(6.5 * this.cellSize, 0.5 * this.cellSize, colors.red, 'down');
        this.drawArrow(14.5 * this.cellSize, 6.5 * this.cellSize, colors.green, 'left');
        this.drawArrow(8.5 * this.cellSize, 14.5 * this.cellSize, colors.yellow, 'up');
        this.drawArrow(0.5 * this.cellSize, 8.5 * this.cellSize, colors.blue, 'right');

        // Grid
        graphics.lineStyle(1, 0x000000, 0.5);
        for(let i=0; i<=15; i++) {
            graphics.beginPath(); graphics.moveTo(0, i*this.cellSize); graphics.lineTo(boardSize, i*this.cellSize); graphics.strokePath();
            graphics.beginPath(); graphics.moveTo(i*this.cellSize, 0); graphics.lineTo(i*this.cellSize, boardSize); graphics.strokePath();
        }

        this.events.on('update-game-state', this.onUpdateGameState, this);
    }

    private drawStar(x: number, y: number, points: number, outerRadius: number, innerRadius: number, color: number) {
        const graphics = this.add.graphics();
        graphics.fillStyle(color, 1);
        graphics.lineStyle(1, 0x000000, 1);
        let rot = Math.PI / 2 * 3;
        let step = Math.PI / points;

        graphics.beginPath();
        graphics.moveTo(x, y - outerRadius);
        for (let i = 0; i < points; i++) {
            graphics.lineTo(x + Math.cos(rot) * outerRadius, y + Math.sin(rot) * outerRadius);
            rot += step;
            graphics.lineTo(x + Math.cos(rot) * innerRadius, y + Math.sin(rot) * innerRadius);
            rot += step;
        }
        graphics.lineTo(x, y - outerRadius);
        graphics.closePath();
        graphics.fillPath();
        graphics.strokePath();
    }

    private drawArrow(x: number, y: number, color: number, direction: string) {
        const graphics = this.add.graphics();
        graphics.fillStyle(color, 1);
        graphics.lineStyle(1, 0x000000, 1);
        
        const size = this.cellSize * 0.4;
        graphics.save();
        graphics.translate(x, y);
        if (direction === 'down') graphics.rotate(0);
        if (direction === 'left') graphics.rotate(Math.PI / 2);
        if (direction === 'up') graphics.rotate(Math.PI);
        if (direction === 'right') graphics.rotate(-Math.PI / 2);

        graphics.beginPath();
        graphics.moveTo(-size/2, -size);
        graphics.lineTo(size/2, -size);
        graphics.lineTo(size/2, 0);
        graphics.lineTo(size, 0);
        graphics.lineTo(0, size);
        graphics.lineTo(-size, 0);
        graphics.lineTo(-size/2, 0);
        graphics.closePath();
        graphics.fillPath();
        graphics.strokePath();
        graphics.restore();
    }

    private onUpdateGameState(gameState: any) {
        this.tokenSprites.forEach(t => t.destroy());
        this.tokenSprites = [];

        const colorsMap: Record<string, number> = { red: 0xff0000, green: 0x00ff00, yellow: 0xffff00, blue: 0x00bfff };
        const cellGroups: Record<string, any[]> = {};

        Object.values(gameState.players).forEach((player: any) => {
            player.tokens.forEach((token: any, index: number) => {
                let cellId = "";
                let baseCoords = {x:0, y:0};

                if (token.status === 'base') {
                    cellId = `base_${player.color}_${index}`;
                    baseCoords = baseSpots[player.color][index];
                } else if (token.status === 'active') {
                    if (token.position <= 51) {
                        const offset = START_SQUARES_MAP[player.color as keyof typeof START_SQUARES_MAP] || 0;
                        const absPos = (token.position + offset) % 52;
                        cellId = `path_${absPos}`;
                        baseCoords = pathCoords[absPos];
                    } else {
                        cellId = `home_${player.color}_${token.position - 52}`;
                        baseCoords = homePaths[player.color][token.position - 52];
                    }
                } else {
                    cellId = `finish_${player.color}`;
                    baseCoords = {x: 7.5, y: 7.5};
                }

                if (!cellGroups[cellId]) cellGroups[cellId] = [];
                cellGroups[cellId].push({ token, player, baseCoords });
            });
        });

        Object.entries(cellGroups).forEach(([cellId, group]) => {
            group.forEach((item, i) => {
                const { token, player, baseCoords } = item;
                const colorCode = colorsMap[player.color];
                
                let offsetX = 0;
                let offsetY = 0;
                if (group.length > 1 && !cellId.startsWith('base')) {
                    const angle = (i / group.length) * Math.PI * 2;
                    const radius = this.cellSize * 0.2;
                    offsetX = Math.cos(angle) * radius;
                    offsetY = Math.sin(angle) * radius;
                }

                const sprite = this.add.circle(
                    baseCoords.x * this.cellSize + this.cellSize/2 + offsetX, 
                    baseCoords.y * this.cellSize + this.cellSize/2 + offsetY, 
                    this.cellSize * (group.length > 1 ? 0.25 : 0.35),
                    colorCode
                );
                
                sprite.setStrokeStyle(2, 0xffffff);
                sprite.setScale(0);
                sprite.setInteractive(new Phaser.Geom.Circle(0, 0, this.cellSize * 0.35), Phaser.Geom.Circle.Contains);
                
                this.tweens.add({
                    targets: sprite,
                    scale: 1,
                    duration: 300,
                    ease: 'Back.easeOut'
                });
                
                sprite.on('pointerdown', () => {
                    window.dispatchEvent(new CustomEvent('ludo-token-click', { detail: token.id }));
                });
                
                sprite.on('pointerover', () => {
                    sprite.setStrokeStyle(4, 0xffffff);
                    document.body.style.cursor = 'pointer';
                });
                sprite.on('pointerout', () => {
                    sprite.setStrokeStyle(2, 0xffffff);
                    document.body.style.cursor = 'default';
                });
                
                this.tokenSprites.push(sprite);
            });
        });
    }
}
