"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { bind, play, setEnabled, type SoundName } from "cuelume";

const STORAGE_KEY = "interface-sounds";

type SoundContextValue = {
  enabled: boolean;
  ready: boolean;
  playSound: (sound: SoundName) => void;
  toggleSound: () => void;
};

const SoundContext = createContext<SoundContextValue | null>(null);

export function CuelumeSoundProvider({ children, defaultEnabled = true }: { children: ReactNode; defaultEnabled?: boolean }) {
  const [enabled, setSoundEnabled] = useState(defaultEnabled);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let next = defaultEnabled;
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored === "on" || stored === "off") next = stored === "on";
    } catch {
      // Keep a session-only preference when storage is unavailable.
    }
    setSoundEnabled(next);
    setEnabled(next);
    bind();
    setReady(true);
  }, [defaultEnabled]);

  const playSound = useCallback((sound: SoundName) => {
    play(sound);
  }, []);

  const toggleSound = useCallback(() => {
    setSoundEnabled((current) => {
      const next = !current;
      if (next) {
        setEnabled(true);
        play("toggle");
      } else {
        play("droplet");
        setEnabled(false);
      }
      try {
        window.localStorage.setItem(STORAGE_KEY, next ? "on" : "off");
      } catch {
        // The toggle still works for this session.
      }
      return next;
    });
  }, []);

  const value = useMemo(() => ({ enabled, ready, playSound, toggleSound }), [enabled, ready, playSound, toggleSound]);
  return <SoundContext.Provider value={value}>{children}</SoundContext.Provider>;
}

export function useInterfaceSounds() {
  const value = useContext(SoundContext);
  if (!value) throw new Error("useInterfaceSounds must be used inside CuelumeSoundProvider");
  return value;
}

export function SoundToggle({ className = "" }: { className?: string }) {
  const { enabled, ready, toggleSound } = useInterfaceSounds();
  return (
    <button
      type="button"
      className={className}
      onClick={toggleSound}
      aria-label={enabled ? "Turn interface sounds off" : "Turn interface sounds on"}
      aria-pressed={enabled}
      disabled={!ready}
    >
      <span aria-hidden="true">{enabled ? "🔊" : "🔇"}</span>
      <span>{enabled ? "Sound on" : "Sound off"}</span>
    </button>
  );
}
