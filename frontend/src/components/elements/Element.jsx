import React, { useRef } from 'react';
import { useDrag } from 'react-dnd';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

const Element = ({ element, onClick, onDuplicate, size = 'medium', className = '', isOnWorkbench = false }) => {
  const { t } = useTranslation();
  const elementRef = useRef(null);
  
  // Handle null element
  if (!element) {
    console.warn('Element component received null element');
    return null;
  }
  
  // Translate basic element names
  const getElementName = (element) => {
    if (!element) return 'Unknown';
    
    if (element.is_basic === true || element.is_basic === 1) {
      // Check if this is a basic element that needs translation
      // Map of element names to translation keys
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
      
      // If the element name is in our map, use the corresponding key for translation
      if (element.name in elementToKey) {
        return t(`elements.${elementToKey[element.name]}`);
      }
    }
    return element.name;
  };
  
  // Set up drag functionality with React DnD
  // Only enable React DnD dragging when not on the workbench
  // When on the workbench, we use Framer Motion's drag instead
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'element',
    item: () => {
      const displayName = getElementName(element);
      console.log('Starting drag for element:', element, 'with displayName:', displayName);
      return { 
        id: element.id, 
        name: element.name,
        displayName: displayName, // Add translated name for display
        emoji: element.emoji,
        is_basic: element.is_basic,
        language: element.language,
        workbenchId: element.workbenchId,
        isOnWorkbench: isOnWorkbench
      };
    },
    canDrag: !isOnWorkbench, // Disable React DnD dragging when on workbench
    end: (item, monitor) => {
      const dropResult = monitor.getDropResult();
      if (item && dropResult) {
        console.log('Element dropped:', item, 'Result:', dropResult);
      }
    },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }), [isOnWorkbench, element.id, element.workbenchId, element.name, element.emoji, element.is_basic]);

  // Size classes
  const sizeClasses = {
    small: 'text-xs py-1 px-2',
    medium: 'text-sm py-2 px-3',
    large: 'text-base py-3 px-4',
  };

  // Get emoji or default
  const emoji = element.emoji || '🔮';

  // Element type classes
  const getTypeClasses = () => {
    if (element.is_basic === true || element.is_basic === 1) {
      return 'border-blue-500/30 bg-blue-500/10';
    }
    if (element.is_new_discovery) {
      return 'border-green-500/30 bg-green-500/10';
    }
    return 'border-accent/30 bg-secondary/80';
  };

  // Handle click
  const handleClick = () => {
    console.log('Element clicked:', element);
    if (onClick) onClick(element);
  };
  
  // Handle right click (context menu)
  const handleContextMenu = (e) => {
    e.preventDefault(); // Prevent default context menu
    console.log('Element right-clicked:', element);
    if (onDuplicate) onDuplicate(element);
  };

  // Connect the drag ref to the element ref
  // Only apply the drag ref if not on workbench
  if (!isOnWorkbench) {
    drag(elementRef);
  }

  return (
    <motion.div
      ref={elementRef}
      className={`
        element-card backdrop-blur-sm rounded-lg border 
        flex items-center ${isOnWorkbench ? 'cursor-move' : 'cursor-grab'} select-none 
        shadow-md hover:shadow-lg
        ${sizeClasses[size]}
        ${getTypeClasses()}
        ${className}
        ${isDragging ? 'ring-2 ring-accent ring-opacity-50' : ''}
      `}
      onClick={handleClick}
      onContextMenu={handleContextMenu}
      whileHover={{ 
        scale: 1.05, 
        boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
        transition: { duration: 0.2 }
      }}
      whileTap={{ scale: 0.95 }}
      style={{ 
        opacity: isDragging ? 0.7 : 1,
      }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        type: 'spring',
        stiffness: 500,
        damping: 30
      }}
    >
      <div className="relative">
        <span className="element-emoji mr-2 text-lg filter drop-shadow-md">{emoji}</span>
        {isDragging && (
          <motion.div
            className="absolute inset-0 bg-white opacity-20"
            initial={{ scale: 0 }}
            animate={{ scale: 1.2 }}
            transition={{ repeat: Infinity, duration: 1 }}
          />
        )}
      </div>
      <span className="element-name font-medium">{getElementName(element)}</span>
      {(element.is_basic === true || element.is_basic === 1) && (
        <span className="ml-2 text-xs bg-blue-500/30 text-blue-200 px-1 rounded">{t('ui.basic')}</span>
      )}
      {element.is_new_discovery && (
        <span className="ml-2 text-xs bg-green-500/30 text-green-200 px-1 rounded">{t('ui.new')}</span>
      )}
    </motion.div>
  );
};

export default Element; 