import React from 'react';
import { useDrag } from 'react-dnd';
import { useTranslation } from 'react-i18next';

const Element = ({ element, onClick }) => {
  const { t } = useTranslation();
  
  // Translate basic element names
  const getElementName = (element) => {
    if (element.is_basic) {
      // Check if this is a basic element that needs translation
      const basicElements = ['Water', 'Fire', 'Earth', 'Air', 'Вода', 'Огонь', 'Земля', 'Воздух'];
      if (basicElements.includes(element.name)) {
        // Convert to lowercase key for translation
        const key = element.name.toLowerCase();
        return t(`elements.${key}`);
      }
    }
    return element.name;
  };
  
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'element',
    item: { ...element, isOnWorkbench: false },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
    end: (item, monitor) => {
      const dropResult = monitor.getDropResult();
      console.log('Element dropped:', item, 'Result:', dropResult);
    },
  }));
  
  return (
    <div
      ref={drag}
      className={`element ${isDragging ? 'dragging' : ''}`}
      onClick={() => onClick && onClick(element)}
    >
      <span className="element-emoji">{element.emoji}</span>
      <span className="element-name">{getElementName(element)}</span>
    </div>
  );
};

export default Element; 