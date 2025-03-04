import React from 'react';
import { useDrag } from 'react-dnd';
import { motion } from 'framer-motion';

const Element = ({ element, onClick }) => {
  // Set up drag functionality
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'element',
    item: { id: element.id, name: element.name },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }));

  return (
    <motion.div
      ref={drag}
      className="element-card"
      onClick={() => onClick && onClick(element)}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      style={{ opacity: isDragging ? 0.5 : 1 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <span className="element-emoji">{element.emoji}</span>
      <span className="element-name">{element.name}</span>
    </motion.div>
  );
};

export default Element; 