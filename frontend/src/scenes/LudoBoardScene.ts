import * as Phaser from 'phaser';

// ─── Board coordinate maps ────────────────────────────────────────────────────
// 52-square perimeter path (absolute positions 0–51, clockwise)
const pathCoords = [
    // Red quadrant (0-12)
    {x:1,y:6}, {x:2,y:6}, {x:3,y:6}, {x:4,y:6}, {x:5,y:6},
    {x:6,y:5}, {x:6,y:4}, {x:6,y:3}, {x:6,y:2}, {x:6,y:1}, {x:6,y:0},
    {x:7,y:0}, {x:8,y:0},
    // Green quadrant (13-25)
    {x:8,y:1}, {x:8,y:2}, {x:8,y:3}, {x:8,y:4}, {x:8,y:5},
    {x:9,y:6}, {x:10,y:6}, {x:11,y:6}, {x:12,y:6}, {x:13,y:6}, {x:14,y:6},
    {x:14,y:7}, {x:14,y:8},
    // Yellow quadrant (26-38)
    {x:13,y:8}, {x:12,y:8}, {x:11,y:8}, {x:10,y:8}, {x:9,y:8},
    {x:8,y:9}, {x:8,y:10}, {x:8,y:11}, {x:8,y:12}, {x:8,y:13}, {x:8,y:14},
    {x:7,y:14}, {x:6,y:14},
    // Blue quadrant (39-51)
    {x:6,y:13}, {x:6,y:12}, {x:6,y:11}, {x:6,y:10}, {x:6,y:9},
    {x:5,y:8}, {x:4,y:8}, {x:3,y:8}, {x:2,y:8}, {x:1,y:8}, {x:0,y:8},
    {x:0,y:7}
];

// Home-column paths (logical positions 51-55 → home column index 0-4)
const homePaths: Record<string, {x:number, y:number}[]> = {
    red:    [{x:1,y:7},{x:2,y:7},{x:3,y:7},{x:4,y:7},{x:5,y:7}],
    green:  [{x:7,y:1},{x:7,y:2},{x:7,y:3},{x:7,y:4},{x:7,y:5}],
    yellow: [{x:13,y:7},{x:12,y:7},{x:11,y:7},{x:10,y:7},{x:9,y:7}],
    blue:   [{x:7,y:13},{x:7,y:12},{x:7,y:11},{x:7,y:10},{x:7,y:9}],
};

// Base spots for each color (4 circles in the home zone)
const baseSpots: Record<string, {x:number, y:number}[]> = {
    red:    [{x:1.5,y:1.5},{x:3.5,y:1.5},{x:1.5,y:3.5},{x:3.5,y:3.5}],
    green:  [{x:10.5,y:1.5},{x:12.5,y:1.5},{x:10.5,y:3.5},{x:12.5,y:3.5}],
    yellow: [{x:10.5,y:10.5},{x:12.5,y:10.5},{x:10.5,y:12.5},{x:12.5,y:12.5}],
    blue:   [{x:1.5,y:10.5},{x:3.5,y:10.5},{x:1.5,y:12.5},{x:3.5,y:12.5}],
};

// Color offset for absolute position calculation (mirrors Python backend)
const COLOR_OFFSETS: Record<string, number> = {
    red: 0, green: 13, yellow: 26, blue: 39
};

// Official safe zones (absolute positions 0-51)
const SAFE_ZONES = new Set([0, 8, 13, 21, 26, 34, 39, 47]);

const COLOR_HEX: Record<string, number> = {
    red: 0xff4136, green: 0x2ecc40, yellow: 0xffdc00, blue: 0x0074d9
};

// ─────────────────────────────────────────────────────────────────────────────

export default class LudoBoardScene extends Phaser.Scene {
    private tokenSprites: Phaser.GameObjects.Arc[] = [];
    private highlightRings: Phaser.GameObjects.Arc[] = [];
    private cellSize: number = 40;

    constructor() { super('LudoBoardScene'); }

    create() {
        const boardSize = 600;
        this.cellSize = boardSize / 15;
        this._drawBoard(boardSize);
        this.events.on('update-game-state', this.onUpdateGameState, this);
    }

    // ── Board drawing ──────────────────────────────────────────────────────────

    private _drawBoard(boardSize: number) {
        const g = this.add.graphics();

        // White background
        g.fillStyle(0xffffff, 1);
        g.fillRect(0, 0, boardSize, boardSize);

        // Colored bases
        const drawBase = (bx: number, by: number, col: number) => {
            g.fillStyle(col, 1);
            g.fillRect(bx * this.cellSize, by * this.cellSize, 6 * this.cellSize, 6 * this.cellSize);
            g.fillStyle(0xffffff, 1);
            g.fillRect((bx+1)*this.cellSize, (by+1)*this.cellSize, 4*this.cellSize, 4*this.cellSize);
            [{sx:bx+1.5,sy:by+1.5},{sx:bx+3.5,sy:by+1.5},{sx:bx+1.5,sy:by+3.5},{sx:bx+3.5,sy:by+3.5}]
                .forEach(s => {
                    g.fillStyle(col, 1);
                    g.fillCircle((s.sx+0.5)*this.cellSize, (s.sy+0.5)*this.cellSize, this.cellSize*0.6);
                });
        };
        drawBase(0, 0, COLOR_HEX.red);
        drawBase(9, 0, COLOR_HEX.green);
        drawBase(9, 9, COLOR_HEX.yellow);
        drawBase(0, 9, COLOR_HEX.blue);

        // Home columns
        Object.entries(homePaths).forEach(([col, path]) => {
            g.fillStyle(COLOR_HEX[col], 1);
            path.forEach(p => g.fillRect(p.x*this.cellSize, p.y*this.cellSize, this.cellSize, this.cellSize));
        });

        // Safe zone star markers
        SAFE_ZONES.forEach(absPos => {
            if (absPos < pathCoords.length) {
                const p = pathCoords[absPos];
                g.fillStyle(0xaaaaaa, 0.5);
                g.fillStar((p.x+0.5)*this.cellSize, (p.y+0.5)*this.cellSize, 5, this.cellSize*0.2, this.cellSize*0.4);
            }
        });

        // Center finishing zone
        g.fillStyle(0x111111, 0.7);
        g.fillRect(6*this.cellSize, 6*this.cellSize, 3*this.cellSize, 3*this.cellSize);

        // Grid lines
        g.lineStyle(1, 0x000000, 0.2);
        for (let i = 0; i <= 15; i++) {
            g.beginPath(); g.moveTo(0, i*this.cellSize); g.lineTo(boardSize, i*this.cellSize); g.strokePath();
            g.beginPath(); g.moveTo(i*this.cellSize, 0); g.lineTo(i*this.cellSize, boardSize); g.strokePath();
        }
    }

    // ── State rendering ────────────────────────────────────────────────────────

    private onUpdateGameState(gameState: any) {
        // Destroy all old sprites and highlight rings
        this.tokenSprites.forEach(t => t.destroy());
        this.highlightRings.forEach(r => r.destroy());
        this.tokenSprites = [];
        this.highlightRings = [];

        const validIds: Set<string> = new Set(gameState.valid_move_ids || []);

        Object.values(gameState.players).forEach((player: any) => {
            const colorCode = COLOR_HEX[player.color];
            const offset = COLOR_OFFSETS[player.color] ?? 0;

            player.tokens.forEach((token: any, index: number) => {
                const coords = this._resolveCoords(token, player.color, offset, index);
                if (!coords) return;

                const cx = coords.x * this.cellSize + this.cellSize / 2;
                const cy = coords.y * this.cellSize + this.cellSize / 2;
                const r  = this.cellSize * 0.35;

                // ── Valid-move highlight ring (pulsing glow) ────────────────
                if (validIds.has(token.id) && token.status !== 'finished') {
                    const ring = this.add.circle(cx, cy, r + 6, 0xffffff, 0);
                    ring.setStrokeStyle(3, 0xffffff);
                    this.tweens.add({
                        targets: ring,
                        alpha: { from: 1, to: 0.1 },
                        yoyo: true,
                        repeat: -1,
                        duration: 500,
                        ease: 'Sine.easeInOut',
                    });
                    this.highlightRings.push(ring);
                }

                // ── Token circle ───────────────────────────────────────────
                const sprite = this.add.circle(cx, cy, r, colorCode);
                sprite.setStrokeStyle(2, 0xffffff);
                sprite.setScale(0);
                sprite.setInteractive(
                    new Phaser.Geom.Circle(0, 0, r),
                    Phaser.Geom.Circle.Contains
                );

                this.tweens.add({
                    targets: sprite, scale: 1, duration: 280, ease: 'Back.easeOut'
                });

                sprite.on('pointerdown', () => {
                    window.dispatchEvent(new CustomEvent('ludo-token-click', { detail: token.id }));
                });
                sprite.on('pointerover', () => {
                    sprite.setStrokeStyle(4, 0xffff00);
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

    private _resolveCoords(
        token: any, color: string, offset: number, index: number
    ): { x: number; y: number } | null {
        if (token.status === 'base') {
            return baseSpots[color]?.[index] ?? null;
        }
        if (token.status === 'active') {
            if (token.position <= 50) {
                const absPos = (token.position + offset) % 52;
                return pathCoords[absPos] ?? null;
            }
            if (token.position >= 51 && token.position <= 55) {
                return homePaths[color]?.[token.position - 51] ?? null;
            }
        }
        if (token.status === 'finished') {
            return { x: 7.5, y: 7.5 };
        }
        return null;
    }
}
