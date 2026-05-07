export class AudioManager {
    private isMuted: boolean = false;
    // In a real environment, we would load HTML5 Audio objects here:
    // private sounds = { roll: new Audio('/sounds/roll.mp3') }

    play(soundName: 'roll' | 'move' | 'capture' | 'win' | 'click') {
        if (this.isMuted) return;
        
        // Mocking the audio play. When assets are added to /public, 
        // this will play the actual files.
        console.log(`[Audio Manager] Playing sound: ${soundName}`);
        
        // Example logic for future implementation:
        // const audio = this.sounds[soundName];
        // if (audio) {
        //     audio.currentTime = 0;
        //     audio.play().catch(e => console.warn("Audio play blocked by browser", e));
        // }
    }

    toggleMute() {
        this.isMuted = !this.isMuted;
        return this.isMuted;
    }
}

export const audioManager = new AudioManager();
