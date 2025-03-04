import { useState, useEffect } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { AnimatePresence } from 'framer-motion';
import Workbench from './components/workbench/Workbench';
import Library from './components/library/Library';
import Settings from './components/ui/Settings';
import useElementStore from './store/elementStore';
import useSettingsStore from './store/settingsStore';

function App() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const { fetchElements, addBasicElements } = useElementStore();
  const { playerName } = useSettingsStore();

  // Fetch elements on mount
  useEffect(() => {
    fetchElements();
  }, [fetchElements]);

  // Add basic elements to discovered elements if none exist
  useEffect(() => {
    const discoveredElements = useElementStore.getState().discoveredElements;
    if (discoveredElements.length === 0) {
      addBasicElements();
    }
  }, [addBasicElements]);

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="min-h-screen bg-primary text-text">
        {/* Stars background */}
        <div className="stars">
          {/* Stars would be added dynamically with JavaScript */}
        </div>
        
        {/* Header */}
        <header className="p-4 border-b border-accent">
          <div className="container mx-auto flex justify-between items-center">
            <h1 className="text-2xl font-bold">Infinite Alchemist</h1>
            
            <div className="flex items-center gap-4">
              {playerName && (
                <div className="text-sm">
                  Playing as: <span className="font-bold">{playerName}</span>
                </div>
              )}
              
              <button 
                className="btn"
                onClick={() => setIsSettingsOpen(true)}
              >
                Settings
              </button>
            </div>
          </div>
        </header>
        
        {/* Main content */}
        <main className="container mx-auto p-4">
          <Workbench />
          <Library />
        </main>
        
        {/* Footer */}
        <footer className="p-4 border-t border-accent mt-8">
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
      </div>
    </DndProvider>
  );
}

export default App;
