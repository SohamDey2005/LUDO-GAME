export class SocketManager {
    private socket: WebSocket | null = null;
    private onStateUpdate: ((state: any) => void) | null = null;

    connect(gameId: string, clientId: string) {
        if (this.socket) {
            this.socket.close();
        }
        
        const wsUrl = `ws://localhost:8000/ws/game/${gameId}/${clientId}`;
        this.socket = new WebSocket(wsUrl);

        this.socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                if (message.type === 'STATE_UPDATE' && this.onStateUpdate) {
                    this.onStateUpdate(message.data);
                }
            } catch (e) {
                console.error("Error parsing websocket message", e);
            }
        };

        this.socket.onclose = () => {
            console.log("WebSocket disconnected.");
            // Reconnect logic could go here
        };
    }

    onUpdate(callback: (state: any) => void) {
        this.onStateUpdate = callback;
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
}

export const socketManager = new SocketManager();
