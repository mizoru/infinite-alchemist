import React from 'react';
import { motion } from 'framer-motion';
import useSettingsStore from '../../store/settingsStore';
import useElementStore from '../../store/elementStore';

const Settings = ({ isOpen, onClose }) => {
  const { 
    playerName, 
    language, 
    gameMode, 
    darkMode, 
    soundEnabled,
    setPlayerName,
    setLanguage,
    setGameMode,
    toggleDarkMode,
    toggleSound,
    resetSettings
  } = useSettingsStore();
  
  const { resetDiscoveredElements, addBasicElements } = useElementStore();
  
  // Handle game reset
  const handleResetGame = () => {
    if (window.confirm('Are you sure you want to reset your game? All your discovered elements will be lost.')) {
      resetDiscoveredElements();
      addBasicElements();
    }
  };
  
  // If not open, don't render
  if (!isOpen) return null;
  
  return (
    <motion.div
      className="fixed inset-0 bg-black/80 flex items-center justify-center z-50"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div 
        className="bg-secondary p-6 rounded-xl w-full max-w-md"
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-2xl font-bold mb-6">Settings</h2>
        
        <div className="space-y-6">
          {/* Player Name */}
          <div>
            <label className="block text-sm font-medium mb-2">Player Name</label>
            <input
              type="text"
              className="input w-full"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              placeholder="Enter your name"
            />
          </div>
          
          {/* Language */}
          <div>
            <label className="block text-sm font-medium mb-2">Language</label>
            <select
              className="input w-full"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="ru" disabled>Russian (Coming Soon)</option>
            </select>
          </div>
          
          {/* Game Mode */}
          <div>
            <label className="block text-sm font-medium mb-2">Game Mode</label>
            <select
              className="input w-full"
              value={gameMode}
              onChange={(e) => setGameMode(e.target.value)}
            >
              <option value="classic">Classic Mode</option>
              <option value="custom" disabled>Custom Mode (Coming Soon)</option>
            </select>
          </div>
          
          {/* Toggle Switches */}
          <div className="flex justify-between">
            <div className="flex items-center">
              <label className="mr-2">Dark Mode</label>
              <button
                className={`w-12 h-6 rounded-full p-1 transition-colors ${darkMode ? 'bg-blue-600' : 'bg-gray-400'}`}
                onClick={toggleDarkMode}
              >
                <div className={`w-4 h-4 rounded-full bg-white transition-transform ${darkMode ? 'translate-x-6' : ''}`} />
              </button>
            </div>
            
            <div className="flex items-center">
              <label className="mr-2">Sound</label>
              <button
                className={`w-12 h-6 rounded-full p-1 transition-colors ${soundEnabled ? 'bg-blue-600' : 'bg-gray-400'}`}
                onClick={toggleSound}
              >
                <div className={`w-4 h-4 rounded-full bg-white transition-transform ${soundEnabled ? 'translate-x-6' : ''}`} />
              </button>
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="flex justify-between pt-4 border-t border-accent">
            <button
              className="btn bg-red-600 hover:bg-red-700"
              onClick={handleResetGame}
            >
              Reset Game
            </button>
            
            <button
              className="btn"
              onClick={onClose}
            >
              Close
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Settings; 