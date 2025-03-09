import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Element from '../elements/Element';

/**
 * Component to display a notification when a new element is discovered
 */
const DiscoveryNotification = ({ discovery, onClose, autoCloseDelay = 5000 }) => {
  // Auto close after delay
  useEffect(() => {
    if (discovery) {
      const timer = setTimeout(() => {
        onClose();
      }, autoCloseDelay);
      
      return () => clearTimeout(timer);
    }
  }, [discovery, onClose, autoCloseDelay]);

  if (!discovery) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed bottom-4 right-4 bg-secondary p-4 rounded-lg shadow-lg border border-accent z-50 max-w-sm"
        initial={{ opacity: 0, y: 50, scale: 0.9 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 20, scale: 0.9 }}
        transition={{ type: 'spring', damping: 20 }}
      >
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-bold text-green-400">New Discovery!</h3>
          <button 
            className="text-textSecondary hover:text-text"
            onClick={onClose}
          >
            ✕
          </button>
        </div>
        
        <div className="mb-3">
          <Element element={discovery.result} />
        </div>
        
        <div className="mt-4 text-xs text-textSecondary">
          {discovery.first_discoverer && (
            <p>First discovered by: {discovery.first_discoverer}</p>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default DiscoveryNotification; 