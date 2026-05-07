export interface Token {
    id: string;
    color: string;
    position: number;
    status: 'base' | 'active' | 'finished';
}

export interface Player {
    id: string;
    name: string;
    color: string;
    player_type: 'human' | 'ai';
    tokens: Token[];
}

export interface GameState {
    id: string;
    players: Record<string, Player>;
    current_turn: string;
    status: 'waiting' | 'in_progress' | 'finished';
    dice_value: number | null;
    last_rolled_value: number;
    consecutive_sixes: number;
    winner: string | null;
    last_action: string | null;
    turn_order: string[];
}

const API_BASE = 'https://ludo-backend-175911647281.us-central1.run.app/api/game';

export const createGame = async (): Promise<GameState> => {
    const res = await fetch(`${API_BASE}/create`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to create game');
    return res.json();
};

export const getGame = async (gameId: string): Promise<GameState> => {
    const res = await fetch(`${API_BASE}/${gameId}`);
    if (!res.ok) throw new Error('Failed to get game');
    return res.json();
};

export const rollDice = async (gameId: string): Promise<GameState> => {
    const res = await fetch(`${API_BASE}/${gameId}/roll`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to roll dice');
    return res.json();
};

export const moveToken = async (gameId: string, playerId: string, tokenId: string): Promise<GameState> => {
    const res = await fetch(`${API_BASE}/${gameId}/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_id: playerId, token_id: tokenId })
    });
    if (!res.ok) throw new Error('Failed to move token');
    return res.json();
};
