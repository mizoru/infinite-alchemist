import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Create a store with persistence
const useSettingsStore = create(
  persist(
    (set) => ({
      // State
      playerName: '',
      language: 'en', // Default language is English
      gameMode: 'classic', // 'classic' or 'custom'
      darkMode: true, // Default to dark mode
      soundEnabled: true,
      
      // Actions
      setPlayerName: (name) => set({ playerName: name }),
      setLanguage: (language) => set({ language }),
      setGameMode: (mode) => set({ gameMode: mode }),
      toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
      toggleSound: () => set((state) => ({ soundEnabled: !state.soundEnabled })),
      
      // Reset settings to defaults
      resetSettings: () => set({
        playerName: '',
        language: 'en',
        gameMode: 'classic',
        darkMode: true,
        soundEnabled: true,
      }),
    }),
    {
      name: 'infinite-alchemist-settings',
    }
  )
);

export default useSettingsStore; 