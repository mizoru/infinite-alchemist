import React from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import useSettingsStore from '../../store/settingsStore';
import useElementStore from '../../store/elementStore';

const Settings = ({ isOpen, onClose }) => {
  const { t, i18n } = useTranslation();
  
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
  
  // Handle language change
  const handleLanguageChange = (e) => {
    const newLang = e.target.value;
    setLanguage(newLang);
    i18n.changeLanguage(newLang);
  };
  
  // Handle game reset
  const handleResetGame = () => {
    if (window.confirm(t('ui.resetConfirm'))) {
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
        <h2 className="text-2xl font-bold mb-6">{t('ui.settings')}</h2>
        
        <div className="space-y-6">
          {/* Player Name */}
          <div>
            <label className="block text-sm font-medium mb-2">{t('ui.playerName')}</label>
            <input
              type="text"
              className="input w-full"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              placeholder={t('ui.enterName')}
            />
          </div>
          
          {/* Language */}
          <div>
            <label className="block text-sm font-medium mb-2">{t('ui.language')}</label>
            <select
              className="input w-full"
              value={language}
              onChange={handleLanguageChange}
            >
              <option value="en">{t('languages.en')}</option>
              <option value="ru">{t('languages.ru')}</option>
            </select>
          </div>
          
          {/* Game Mode */}
          <div>
            <label className="block text-sm font-medium mb-2">{t('ui.gameMode')}</label>
            <select
              className="input w-full"
              value={gameMode}
              onChange={(e) => setGameMode(e.target.value)}
            >
              <option value="classic">{t('gameModes.classic')}</option>
              <option value="custom" disabled>{t('gameModes.custom')} ({t('ui.comingSoon')})</option>
            </select>
          </div>
          
          {/* Toggle Switches */}
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{t('ui.darkMode')}</span>
              <button 
                className={`w-12 h-6 rounded-full p-1 transition-colors ${darkMode ? 'bg-primary' : 'bg-gray-300'}`}
                onClick={toggleDarkMode}
              >
                <div className={`w-4 h-4 rounded-full bg-white transform transition-transform ${darkMode ? 'translate-x-6' : ''}`} />
              </button>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{t('ui.sound')}</span>
              <button 
                className={`w-12 h-6 rounded-full p-1 transition-colors ${soundEnabled ? 'bg-primary' : 'bg-gray-300'}`}
                onClick={toggleSound}
              >
                <div className={`w-4 h-4 rounded-full bg-white transform transition-transform ${soundEnabled ? 'translate-x-6' : ''}`} />
              </button>
            </div>
          </div>
          
          {/* Reset Game Button */}
          <div className="pt-4">
            <button 
              className="btn btn-danger w-full"
              onClick={handleResetGame}
            >
              {t('ui.reset')}
            </button>
          </div>
          
          {/* Close Button */}
          <div className="pt-2">
            <button 
              className="btn btn-secondary w-full"
              onClick={onClose}
            >
              {t('ui.close')}
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Settings; 