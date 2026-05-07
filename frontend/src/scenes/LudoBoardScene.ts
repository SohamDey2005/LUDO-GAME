import * as Phaser from 'phaser';

// Define the board mapping (Absolute 0-51 coordinates to grid x,y)
// 0 is Green's starting square (1, 6)
const pathCoords = [
    // Green Arm to Top
    {x:1,y:6}, {x:2,y:6}, {x:3,y:6}, {x:4,y:6}, {x:5,y:6}, 
    {x:6,y:5}, {x:6,y:4}, {x:6,y:3}, {x:6,y:2}, {x:6,y:1}, {x:6,y:0}, 
    {x:7,y:0}, {x:8,y:0}, 
    // Top to Blue Arm
    {x:8,y:1}, {x:8,y:2}, {x:8,y:3}, {x:8,y:4}, {x:8,y:5}, 
    {x:9,y:6}, {x:10,y:6}, {x:11,y:6}, {x:12,y:6}, {x:13,y:6}, {x:14,y:6}, 
    {x:14,y:7}, {x:14,y:8}, 
    // Blue Arm to Bottom
    {x:13,y:8}, {x:12,y:8}, {x:11,y:8}, {x:10,y:8}, {x:9,y:8}, 
    {x:8,y:9}, {x:8,y:10}, {x:8,y:11}, {x:8,y:12}, {x:8,y:13}, {x:8,y:14}, 
    {x:7,y:14}, {x:6,y:14}, 
    // Bottom to Green Arm
    {x:6,y:13}, {x:6,y:12}, {x:6,y:11}, {x:6,y:10}, {x:6,y:9}, 
    {x:5,y:8}, {x:4,y:8}, {x:3,y:8}, {x:2,y:8}, {x:1,y:8}, {x:0,y:8}, 
    {x:0,y:7}, {x:0,y:6} // 51 squares
];

// Re-map start squares to match the visual order
const START_SQUARES_MAP = {
    green: 0,
    yellow: 13,
    blue: 26,
    red: 39
};

const homePaths: Record<string, {x:number, y:number}[]> = {
    green: [{x:1,y:7},{x:2,y:7},{x:3,y:7},{x:4,y:7},{x:5,y:7}], 
    yellow: [{x:7,y:1},{x:7,y:2},{x:7,y:3},{x:7,y:4},{x:7,y:5}],
    blue: [{x:13,y:7},{x:12,y:7},{x:11,y:7},{x:10,y:7},{x:9,y:7}],
    red: [{x:7,y:13},{x:7,y:12},{x:7,y:11},{x:7,y:10},{x:7,y:9}]
};

const baseSpots: Record<string, {x:number, y:number}[]> = {
    green: [{x:1.5,y:1.5}, {x:3.5,y:1.5}, {x:1.5,y:3.5}, {x:3.5,y:3.5}],
    yellow: [{x:10.5,y:1.5}, {x:12.5,y:1.5}, {x:10.5,y:3.5}, {x:12.5,y:3.5}],
    blue: [{x:10.5,y:10.5}, {x:12.5,y:10.5}, {x:10.5,y:12.5}, {x:12.5,y:12.5}],
    red: [{x:1.5,y:10.5}, {x:3.5,y:10.5}, {x:1.5,y:12.5}, {x:3.5,y:12.5}]
};

const SAFE_ZONE_INDICES = [0, 8, 13, 21, 26, 34, 39, 47];

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

        const colors = { red: 0xff4136, green: 0x2ecc40, yellow: 0xffdc00, blue: 0x0074d9, safe: 0xdddddd };

        const drawBase = (x: number, y: number, color: number) => {
            graphics.fillStyle(color, 1);
            graphics.fillRect(x * this.cellSize, y * this.cellSize, 6 * this.cellSize, 6 * this.cellSize);
            graphics.fillStyle(0xffffff, 1);
            graphics.fillRoundedRect((x + 0.5) * this.cellSize, (y + 0.5) * this.cellSize, 5 * this.cellSize, 5 * this.cellSize, 10);
        };

        drawBase(0, 0, colors.green); drawBase(9, 0, colors.yellow);
        drawBase(9, 9, colors.blue); drawBase(0, 9, colors.red);

        // Draw Home Stretch Paths
        ['red','green','yellow','blue'].forEach((col) => {
            graphics.fillStyle(colors[col as keyof typeof colors], 1);
            homePaths[col].forEach(p => {
                graphics.fillRect(p.x * this.cellSize, p.y * this.cellSize, this.cellSize, this.cellSize);
            });
        });

        // Draw Center Triangle Colors
        const cx = 7.5 * this.cellSize;
        const cy = 7.5 * this.cellSize;
        const mid = 1.5 * this.cellSize;
        
        // Red Triangle
        graphics.fillStyle(colors.red, 1);
        graphics.fillTriangle(cx - mid, cy + mid, cx + mid, cy + mid, cx, cy);
        // Green Triangle
        graphics.fillStyle(colors.green, 1);
        graphics.fillTriangle(cx - mid, cy - mid, cx - mid, cy + mid, cx, cy);
        // Yellow Triangle
        graphics.fillStyle(colors.yellow, 1);
        graphics.fillTriangle(cx - mid, cy - mid, cx + mid, cy - mid, cx, cy);
        // Blue Triangle
        graphics.fillStyle(colors.blue, 1);
        graphics.fillTriangle(cx + mid, cy - mid, cx + mid, cy + mid, cx, cy);

        // Draw Safe Zones (Stars)
        SAFE_ZONE_INDICES.forEach(idx => {
            const coord = pathCoords[idx];
            this.drawStar(coord.x * this.cellSize + this.cellSize/2, coord.y * this.cellSize + this.cellSize/2, 5, this.cellSize * 0.4, this.cellSize * 0.2);
        });

        // Grid
        graphics.lineStyle(1, 0x000000, 0.3);
        for(let i=0; i<=15; i++) {
            graphics.beginPath(); graphics.moveTo(0, i*this.cellSize); graphics.lineTo(boardSize, i*this.cellSize); graphics.strokePath();
            graphics.beginPath(); graphics.moveTo(i*this.cellSize, 0); graphics.lineTo(i*this.cellSize, boardSize); graphics.strokePath();
        }

        this.events.on('update-game-state', this.onUpdateGameState, this);
    }

    private drawStar(x: number, y: number, points: number, outerRadius: number, innerRadius: number) {
        const graphics = this.add.graphics();
        graphics.fillStyle(0x000000, 0.2);
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
    }

    private onUpdateGameState(gameState: any) {
        this.tokenSprites.forEach(t => t.destroy());
        this.tokenSprites = [];

        const colorsMap: Record<string, number> = { red: 0xff4136, green: 0x2ecc40, yellow: 0xffdc00, blue: 0x0074d9 };
        const cellGroups: Record<string, any[]> = {};

        Object.values(gameState.players).forEach((player: any) => {
            player.tokens.forEach((token: any, index: number) => {
                let cellId = "";
                let baseCoords = {x:0, y:0};

                if (token.status === 'base') {
                    cellId = `base_${player.color}_${index}`;
                    baseCoords = baseSpots[player.color][index];
                } else if (token.status === 'active') {
                    if (token.position <= 50) {
                        const offset = START_SQUARES_MAP[player.color as keyof typeof START_SQUARES_MAP] || 0;
                        const absPos = (token.position + offset) % 52;
                        cellId = `path_${absPos}`;
                        baseCoords = pathCoords[absPos];
                    } else {
                        cellId = `home_${player.color}_${token.position - 51}`;
                        baseCoords = homePaths[player.color][token.position - 51];
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
