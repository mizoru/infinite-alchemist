import React, { useState, useEffect } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import './App.css';
import Workbench from './components/workbench/Workbench';
import Library from './components/library/Library';
import Settings from './components/ui/Settings';
import DiscoveryNotification from './components/ui/DiscoveryNotification';
import StarsBackground from './components/ui/StarsBackground';
import useElementStore from './store/elementStore';
import useSettingsStore from './store/settingsStore';

function App() {
  const { t } = useTranslation();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [discoveryNotification, setDiscoveryNotification] = useState(null);
  const { fetchElements, addBasicElements } = useElementStore();
  const { playerName, darkMode, language } = useSettingsStore();

  // Fetch elements on mount
  useEffect(() => {
    console.log('Fetching elements...');
    fetchElements().then(() => {
      console.log('Elements fetched successfully');
      console.log('Current elements in store:', useElementStore.getState().elements);
    }).catch(error => {
      console.error('Error fetching elements:', error);
    });
  }, [fetchElements]);

  // Add basic elements to discovered elements if none exist
  useEffect(() => {
    const discoveredElements = useElementStore.getState().discoveredElements;
    console.log('Current discovered elements:', discoveredElements);
    if (discoveredElements.length === 0) {
      console.log('No discovered elements, adding basic elements...');
      addBasicElements();
      console.log('Basic elements added:', useElementStore.getState().discoveredElements);
    }
  }, [addBasicElements]);

  // Refetch elements when language changes
  useEffect(() => {
    fetchElements();
  }, [language, fetchElements]);

  // Handle new element discovery
  const handleDiscovery = (discovery) => {
    console.log('New discovery:', discovery);
    if (discovery && discovery.is_new_discovery) {
      setDiscoveryNotification(discovery);
    }
  };

  // Clear discovery notification
  const clearDiscoveryNotification = () => {
    setDiscoveryNotification(null);
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className={`min-h-screen ${darkMode ? 'bg-primary' : 'bg-gray-100'} ${darkMode ? 'text-text' : 'text-gray-900'} transition-colors duration-300`}>
        {/* Stars background */}
        {darkMode && <StarsBackground />}
        
        {/* Header */}
        <header className={`p-4 border-b ${darkMode ? 'border-accent' : 'border-gray-200'}`}>
          <div className="container mx-auto flex justify-between items-center">
            <h1 className="text-2xl font-bold">{t('app.title')}</h1>
            
            <div className="flex items-center gap-4">
              {playerName && (
                <div className="text-sm">
                  {t('ui.playingAs')}: <span className="font-bold">{playerName}</span>
                </div>
              )}
              
              <button 
                className={`btn ${darkMode ? 'bg-accent hover:bg-accent/80' : 'bg-blue-500 hover:bg-blue-600 text-white'}`}
                onClick={() => setIsSettingsOpen(true)}
              >
                {t('ui.settings')}
              </button>
            </div>
          </div>
        </header>
        
        {/* Main content */}
        <main className="container mx-auto p-4">
          <Workbench onDiscovery={handleDiscovery} />
          <Library />
        </main>
        
        {/* Footer */}
        <footer className={`p-4 border-t ${darkMode ? 'border-accent' : 'border-gray-200'} mt-8`}>
          <div className="container mx-auto text-center text-sm text-textSecondary">
            <p>Infinite Alchemist &copy; 2025</p>
            <p className="mt-1">Combine elements to discover the world!</p>
          </div>
        </footer>
        
        {/* Settings modal */}
        <AnimatePresence>
          {isSettingsOpen && (
            <Settings 
              isOpen={isSettingsOpen} 
              onClose={() => setIsSettingsOpen(false)} 
            />
          )}
        </AnimatePresence>

        {/* Discovery notification */}
        <DiscoveryNotification 
          discovery={discoveryNotification} 
          onClose={clearDiscoveryNotification} 
        />
      </div>
    </DndProvider>
  );
}

export default App;
