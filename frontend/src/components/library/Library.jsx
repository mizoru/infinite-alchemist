import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Element from '../elements/Element';
import useElementStore from '../../store/elementStore';

const Library = () => {
  const { discoveredElements } = useElementStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('alphabetical'); // 'alphabetical', 'newest', 'oldest'
  const [filteredElements, setFilteredElements] = useState([]);

  // Filter and sort elements when discoveredElements, searchTerm, or sortBy changes
  useEffect(() => {
    let filtered = [...discoveredElements];
    
    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(element => 
        element.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Apply sorting
    switch (sortBy) {
      case 'alphabetical':
        filtered.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'newest':
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        break;
      case 'oldest':
        filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        break;
      default:
        break;
    }
    
    setFilteredElements(filtered);
  }, [discoveredElements, searchTerm, sortBy]);

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Library</h2>
        <div className="text-sm text-textSecondary">
          {discoveredElements.length} elements discovered
        </div>
      </div>
      
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          placeholder={`Search (${discoveredElements.length}) items...`}
          className="input flex-grow"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        
        <select
          className="input bg-secondary"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="alphabetical">Sort by name</option>
          <option value="newest">Newest first</option>
          <option value="oldest">Oldest first</option>
        </select>
      </div>
      
      <div className="library">
        {filteredElements.length === 0 ? (
          <div className="text-center text-textSecondary p-8">
            {searchTerm ? 'No elements match your search' : 'No elements discovered yet'}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {filteredElements.map((element) => (
              <motion.div
                key={element.id}
                layout
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <Element element={element} />
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Library; 