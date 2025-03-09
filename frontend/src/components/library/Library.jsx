import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import Element from '../elements/Element';
import useElementStore from '../../store/elementStore';
import useSettingsStore from '../../store/settingsStore';

const Library = () => {
  const { t } = useTranslation();
  const { language, darkMode } = useSettingsStore();
  const { getDiscoveredElements } = useElementStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('alphabetical');
  const [activeFilter, setActiveFilter] = useState('all');
  const [filteredElements, setFilteredElements] = useState([]);

  // Define sort options with translations
  const SORT_OPTIONS = {
    alphabetical: { label: t('ui.sortByName'), fn: (a, b) => a.name.localeCompare(b.name) },
    newest: { label: t('ui.newestFirst'), fn: (a, b) => new Date(b.created_at) - new Date(a.created_at) },
    oldest: { label: t('ui.oldestFirst'), fn: (a, b) => new Date(a.created_at) - new Date(b.created_at) },
  };

  // Define filters with translations
  const FILTERS = {
    all: { label: t('ui.allElements'), fn: () => true },
    basic: { label: t('ui.basicElements'), fn: (el) => el.is_basic },
    discovered: { label: t('ui.discovered'), fn: (el) => !el.is_basic },
    recent: { label: t('ui.recentDiscoveries'), fn: (el) => el.is_new_discovery },
  };

  // Get discovered elements for current language
  const discoveredElements = getDiscoveredElements();
  
  // Filter and sort elements when search term, discovered elements, or language changes
  useEffect(() => {
    let filtered = [...discoveredElements];
    
    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(element => 
        element.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Apply category filter
    filtered = filtered.filter(FILTERS[activeFilter].fn);
    
    // Apply sorting
    filtered.sort(SORT_OPTIONS[sortBy].fn);
    
    setFilteredElements(filtered);
  }, [searchTerm, discoveredElements, sortBy, activeFilter, language]);

  // Handle element click (add to workbench)
  const handleElementClick = (element) => {
    console.log('Element clicked in library:', element);
    
    if (!element || !element.id) {
      console.error('Invalid element clicked:', element);
      return;
    }
    
    // Get the translated name for the element
    let displayName = element.name;
    
    // For basic elements, get the translated name
    if (element.is_basic === true || element.is_basic === 1) {
      const elementToKey = {
        'Water': 'water',
        'Fire': 'fire',
        'Earth': 'earth',
        'Air': 'air',
        'Вода': 'water',
        'Огонь': 'fire',
        'Земля': 'earth',
        'Воздух': 'air'
      };
      
      if (element.name in elementToKey) {
        displayName = t(`elements.${elementToKey[element.name]}`);
      }
    }
    
    // Create a complete element object to pass to the workbench
    const elementToAdd = {
      id: element.id,
      name: element.name,
      emoji: element.emoji,
      is_basic: element.is_basic,
      language: element.language,
      displayName: displayName
    };
    
    console.log('Dispatching add-to-workbench event with element:', elementToAdd);
    
    // Dispatch a custom event to add the element to the workbench
    const event = new CustomEvent('add-to-workbench', { 
      detail: {
        element: elementToAdd
      }
    });
    window.dispatchEvent(event);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex justify-between items-center mb-6">
        <motion.h2 
          className="text-xl font-bold"
          initial={{ x: -20 }}
          animate={{ x: 0 }}
        >
          {t('ui.library')}
        </motion.h2>
        <motion.div 
          className="text-sm text-textSecondary"
          initial={{ x: 20 }}
          animate={{ x: 0 }}
        >
          {discoveredElements.length} {t('ui.elementsDiscovered')}
        </motion.div>
      </div>
      
      <div className="space-y-4 mb-6">
        {/* Search and Sort */}
        <div className="flex gap-4">
          <input
            type="text"
            placeholder={t('ui.search')}
            className={`
              input flex-grow
              ${darkMode ? 'bg-secondary' : 'bg-white'}
              transition-colors duration-200
            `}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          
          <select
            className={`
              input min-w-[140px]
              ${darkMode ? 'bg-secondary' : 'bg-white'}
              transition-colors duration-200
            `}
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            {Object.entries(SORT_OPTIONS).map(([value, { label }]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {Object.entries(FILTERS).map(([value, { label }]) => (
            <button
              key={value}
              className={`
                px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap
                transition-colors duration-200
                ${activeFilter === value
                  ? (darkMode ? 'bg-accent text-white' : 'bg-blue-500 text-white')
                  : (darkMode ? 'bg-secondary/50 hover:bg-accent/50' : 'bg-gray-100 hover:bg-gray-200')
                }
              `}
              onClick={() => setActiveFilter(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
      
      <motion.div 
        className={`
          library rounded-xl p-6
          ${darkMode ? 'bg-secondary/50' : 'bg-white'}
          transition-colors duration-200
        `}
        initial={{ y: 20 }}
        animate={{ y: 0 }}
      >
        <AnimatePresence mode="popLayout">
          {filteredElements.length === 0 ? (
            <motion.div
              className="text-center text-textSecondary p-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {searchTerm ? t('messages.noResults') : t('messages.emptyLibrary')}
            </motion.div>
          ) : (
            <motion.div 
              className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {filteredElements.map((element, index) => (
                <motion.div
                  key={element.id}
                  layout
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ 
                    duration: 0.2,
                    delay: index * 0.03 
                  }}
                >
                  <Element 
                    element={element} 
                    onClick={handleElementClick}
                    isOnWorkbench={false}
                  />
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
};

export default Library; 