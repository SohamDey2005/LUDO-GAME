import * as Phaser from 'phaser';

// Define the board mapping (Absolute 0-51 coordinates to grid x,y)
// Standard Ludo Path Coordinates (15x15 grid, starting from top-left going clockwise)
// Red start is at absolute 0, which is grid (1, 6)
const pathCoords = [
    // Red Start & Path to Green
    {x:1,y:6}, {x:2,y:6}, {x:3,y:6}, {x:4,y:6}, {x:5,y:6}, // 0-4
    {x:6,y:5}, {x:6,y:4}, {x:6,y:3}, {x:6,y:2}, {x:6,y:1}, {x:6,y:0}, // 5-10
    {x:7,y:0}, {x:8,y:0}, // 11-12
    // Green Start & Path to Yellow
    {x:8,y:1}, {x:8,y:2}, {x:8,y:3}, {x:8,y:4}, {x:8,y:5}, // 13-17
    {x:9,y:6}, {x:10,y:6}, {x:11,y:6}, {x:12,y:6}, {x:13,y:6}, {x:14,y:6}, // 18-23
    {x:14,y:7}, {x:14,y:8}, // 24-25
    // Yellow Start & Path to Blue
    {x:13,y:8}, {x:12,y:8}, {x:11,y:8}, {x:10,y:8}, {x:9,y:8}, // 26-30
    {x:8,y:9}, {x:8,y:10}, {x:8,y:11}, {x:8,y:12}, {x:8,y:13}, {x:8,y:14}, // 31-36
    {x:7,y:14}, {x:6,y:14}, // 37-38
    // Blue Start & Path to Red
    {x:6,y:13}, {x:6,y:12}, {x:6,y:11}, {x:6,y:10}, {x:6,y:9}, // 39-43
    {x:5,y:8}, {x:4,y:8}, {x:3,y:8}, {x:2,y:8}, {x:1,y:8}, {x:0,y:8}, // 44-49
    {x:0,y:7} // 50-51
];

// Home paths
const homePaths: Record<string, {x:number, y:number}[]> = {
    red: [{x:1,y:7},{x:2,y:7},{x:3,y:7},{x:4,y:7},{x:5,y:7}], // 51-55
    green: [{x:7,y:1},{x:7,y:2},{x:7,y:3},{x:7,y:4},{x:7,y:5}],
    yellow: [{x:13,y:7},{x:12,y:7},{x:11,y:7},{x:10,y:7},{x:9,y:7}],
    blue: [{x:7,y:13},{x:7,y:12},{x:7,y:11},{x:7,y:10},{x:7,y:9}]
};

const baseSpots: Record<string, {x:number, y:number}[]> = {
    red: [{x:1.5,y:1.5}, {x:3.5,y:1.5}, {x:1.5,y:3.5}, {x:3.5,y:3.5}],
    green: [{x:10.5,y:1.5}, {x:12.5,y:1.5}, {x:10.5,y:3.5}, {x:12.5,y:3.5}],
    yellow: [{x:10.5,y:10.5}, {x:12.5,y:10.5}, {x:10.5,y:12.5}, {x:12.5,y:12.5}],
    blue: [{x:1.5,y:10.5}, {x:3.5,y:10.5}, {x:1.5,y:12.5}, {x:3.5,y:12.5}]
};

export default class LudoBoardScene extends Phaser.Scene {
    private tokenSprites: Phaser.GameObjects.Arc[] = [];
    private cellSize: number = 40;

    constructor() {
        super('LudoBoardScene');
    }

    create() {
        const graphics = this.add.graphics();
        const boardSize = 600;
        this.cellSize = boardSize / 15;
        
        // Draw background
        graphics.fillStyle(0xffffff, 1);
        graphics.fillRect(0, 0, boardSize, boardSize);

        const colors = { red: 0xff4136, green: 0x2ecc40, yellow: 0xffdc00, blue: 0x0074d9, safe: 0xdddddd };

        // Draw Bases
        const drawBase = (x: number, y: number, color: number) => {
            graphics.fillStyle(color, 1);
            graphics.fillRect(x * this.cellSize, y * this.cellSize, 6 * this.cellSize, 6 * this.cellSize);
            graphics.fillStyle(0xffffff, 1);
            graphics.fillRect((x + 1) * this.cellSize, (y + 1) * this.cellSize, 4 * this.cellSize, 4 * this.cellSize);
            // Spots
            const spots = [{sx: x + 1.5, sy: y + 1.5}, {sx: x + 3.5, sy: y + 1.5}, {sx: x + 1.5, sy: y + 3.5}, {sx: x + 3.5, sy: y + 3.5}];
            spots.forEach(spot => {
                graphics.fillStyle(color, 1);
                graphics.fillCircle((spot.sx + 0.5) * this.cellSize, (spot.sy + 0.5) * this.cellSize, this.cellSize * 0.6);
            });
        };

        drawBase(0, 0, colors.red); drawBase(9, 0, colors.green);
        drawBase(9, 9, colors.yellow); drawBase(0, 9, colors.blue);

        // Draw Home Stretch & Center Triangle (omitted repetitive code for brevity, same as before)
        // ... drawing homes ...
        ['red','green','yellow','blue'].forEach((col) => {
            graphics.fillStyle(colors[col as keyof typeof colors], 1);
            homePaths[col].forEach(p => {
                graphics.fillRect(p.x * this.cellSize, p.y * this.cellSize, this.cellSize, this.cellSize);
            });
        });

        // Center Triangle (Simplification: just draw a center box for now)
        graphics.fillStyle(0x000000, 0.5);
        graphics.fillRect(6*this.cellSize, 6*this.cellSize, 3*this.cellSize, 3*this.cellSize);

        // Grid
        graphics.lineStyle(1, 0x000000, 0.3);
        for(let i=0; i<=15; i++) {
            graphics.beginPath(); graphics.moveTo(0, i*this.cellSize); graphics.lineTo(boardSize, i*this.cellSize); graphics.strokePath();
            graphics.beginPath(); graphics.moveTo(i*this.cellSize, 0); graphics.lineTo(i*this.cellSize, boardSize); graphics.strokePath();
        }

        // Listen for game state updates from React
        this.events.on('update-game-state', this.onUpdateGameState, this);
    }

    private onUpdateGameState(gameState: any) {
        // Clear existing tokens
        this.tokenSprites.forEach(t => t.destroy());
        this.tokenSprites = [];

        const colorsMap: Record<string, number> = { red: 0xff4136, green: 0x2ecc40, yellow: 0xffdc00, blue: 0x0074d9 };

        // Render tokens based on state
        Object.values(gameState.players).forEach((player: any) => {
            const colorCode = colorsMap[player.color];
            
            player.tokens.forEach((token: any, index: number) => {
                let coords = {x: 0, y: 0};
                
                if (token.status === 'base') {
                    coords = baseSpots[player.color][index];
                } else if (token.status === 'active') {
                    if (token.position <= 50) {
                        // Main path
                        const offset = { red: 0, green: 13, yellow: 26, blue: 39 }[player.color as string] || 0;
                        const absPos = (token.position + offset) % 52;
                        coords = pathCoords[absPos];
                    } else if (token.position >= 51 && token.position <= 55) {
                        // Home path
                        coords = homePaths[player.color][token.position - 51];
                    }
                } else if (token.status === 'finished') {
                    // Center
                    coords = {x: 7.5, y: 7.5}; 
                }

                if (coords) {
                    const sprite = this.add.circle(
                        coords.x * this.cellSize + this.cellSize/2, 
                        coords.y * this.cellSize + this.cellSize/2, 
                        this.cellSize * 0.35, // Start with full radius for hitbox
                        colorCode
                    );
                    sprite.setStrokeStyle(2, 0xffffff);
                    sprite.setScale(0); // Start at scale 0 for animation
                    sprite.setInteractive(new Phaser.Geom.Circle(0, 0, this.cellSize * 0.35), Phaser.Geom.Circle.Contains);
                    
                    // Entry animation (Scale Tween instead of Radius)
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
                }
            });
        });
    }
}
