import React, { useState, useEffect } from 'react';

const FRUITS = ['🍎', '🥑', '🍓', '🍋', '🫐', '🍑', '🥕', '🍌', '🍍', '🍇', '🍄', '🥦', '🍉'];

// Master persistent AudioContext instance
let masterAudioCtx = null;
let cachedPopBuffer = null;

const getMasterContext = () => {
  if (!masterAudioCtx && typeof window !== 'undefined') {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (AudioCtx) {
      masterAudioCtx = new AudioCtx();
    }
  }
  if (masterAudioCtx && masterAudioCtx.state === 'suspended') {
    masterAudioCtx.resume().catch(() => {});
  }
  return masterAudioCtx;
};

// Pre-synthesize and decode a deep, rich, punchy pop sound waveform in RAM memory
const getPopBuffer = (ctx) => {
  if (cachedPopBuffer) return cachedPopBuffer;

  const sampleRate = ctx.sampleRate || 44100;
  const duration = 0.1; // 100ms
  const numFrames = Math.floor(sampleRate * duration);
  const buffer = ctx.createBuffer(1, numFrames, sampleRate);
  const data = buffer.getChannelData(0);

  for (let i = 0; i < numFrames; i++) {
    const t = i / sampleRate;

    // Pitch sweep starting at 750Hz jumping up to 1500Hz then rapidly dropping to 250Hz
    let freq = 750;
    if (t < 0.02) {
      freq = 750 + (1500 - 750) * (t / 0.02);
    } else {
      freq = 1500 * Math.exp(-(t - 0.02) * 35) + 200;
    }

    const phase = 2 * Math.PI * freq * t;

    // Sharp attack & full-bodied exponential decay
    let env = 1.0;
    if (t < 0.002) {
      env = t / 0.002;
    } else {
      env = Math.exp(-(t - 0.002) * 28);
    }

    // Mix sine wave with warm triangle harmonic for a crisp, punchy pop body
    const sineSample = Math.sin(phase);
    const triSample = (2 / Math.PI) * Math.asin(Math.sin(phase));
    data[i] = (sineSample * 0.65 + triSample * 0.35) * env * 0.95;
  }

  cachedPopBuffer = buffer;
  return cachedPopBuffer;
};

// Play instant zero-latency pop sound directly from memory buffer
const playInstantPopSound = () => {
  try {
    const ctx = getMasterContext();
    if (!ctx) return;

    const buffer = getPopBuffer(ctx);
    const source = ctx.createBufferSource();
    const gain = ctx.createGain();

    source.buffer = buffer;
    // Pleasant, consistent click pop volume level (0.45)
    gain.gain.setValueAtTime(0.45, ctx.currentTime);

    source.connect(gain);
    gain.connect(ctx.destination);

    // Instant zero-delay execution
    source.start(0);
  } catch {
    // Autoplay fallback
  }
};

export default function FruitBurstOverlay() {
  const [bursts, setBursts] = useState([]);

  useEffect(() => {
    // Pre-initialize master audio context on first user pointerdown/touchstart
    const unlockAudio = () => {
      getMasterContext();
    };
    window.addEventListener('pointerdown', unlockAudio, { passive: true });
    window.addEventListener('touchstart', unlockAudio, { passive: true });

    const handlePointerDown = (e) => {
      // Play pop sound IMMEDIATELY on touch/press down (zero latency!)
      playInstantPopSound();

      const clickX = e.clientX || (e.touches && e.touches[0] ? e.touches[0].clientX : 0);
      const clickY = e.clientY || (e.touches && e.touches[0] ? e.touches[0].clientY : 0);

      if (!clickX && !clickY) return;

      const newParticles = Array.from({ length: 7 }).map((_, i) => {
        const angle = (i / 7) * 2 * Math.PI + (Math.random() * 0.5 - 0.25);
        const distance = 45 + Math.random() * 55;
        const dx = Math.cos(angle) * distance;
        const dy = Math.sin(angle) * distance - 35;

        return {
          id: `${Date.now()}-${i}-${Math.random()}`,
          fruit: FRUITS[Math.floor(Math.random() * FRUITS.length)],
          x: clickX,
          y: clickY,
          dx,
          dy,
          rotate: (Math.random() - 0.5) * 80
        };
      });

      setBursts((prev) => [...prev, ...newParticles]);

      setTimeout(() => {
        setBursts((prev) => prev.filter((p) => !newParticles.includes(p)));
      }, 850);
    };

    window.addEventListener('pointerdown', handlePointerDown);

    return () => {
      window.removeEventListener('pointerdown', unlockAudio);
      window.removeEventListener('touchstart', unlockAudio);
      window.removeEventListener('pointerdown', handlePointerDown);
    };
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {bursts.map((particle) => (
        <span
          key={particle.id}
          className="absolute text-2xl animate-fruit-burst select-none pointer-events-none"
          style={{
            left: `${particle.x}px`,
            top: `${particle.y}px`,
            '--dx': `${particle.dx}px`,
            '--dy': `${particle.dy}px`,
            '--rot': `${particle.rotate}deg`,
          }}
        >
          {particle.fruit}
        </span>
      ))}
    </div>
  );
}

