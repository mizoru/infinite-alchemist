import React, { useState } from 'react';
import { useDrop } from 'react-dnd';
import { motion, AnimatePresence } from 'framer-motion';
import Element from '../elements/Element';
import useElementStore from '../../store/elementStore';
import useSettingsStore from '../../store/settingsStore';

const Workbench = () => {
  const [elementsOnWorkbench, setElementsOnWorkbench] = useState([]);
  const [combinationResult, setCombinationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const { combineElements } = useElementStore();
  const { playerName } = useSettingsStore();

  // Set up drop functionality
  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'element',
    drop: (item) => addElementToWorkbench(item),
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  }));

  // Add element to workbench
  const addElementToWorkbench = (item) => {
    // Find the element in the store
    const element = useElementStore.getState().elements.find(e => e.id === item.id);
    
    // Add element to workbench
    if (elementsOnWorkbench.length < 2) {
      setElementsOnWorkbench([...elementsOnWorkbench, element]);
    }
    
    // If we now have 2 elements, try to combine them
    if (elementsOnWorkbench.length === 1) {
      setTimeout(() => {
        combineElementsOnWorkbench([...elementsOnWorkbench, element]);
      }, 500);
    }
  };

  // Combine elements on workbench
  const combineElementsOnWorkbench = async (elements) => {
    if (elements.length !== 2) return;
    
    setIsLoading(true);
    try {
      const result = await combineElements(elements[0].id, elements[1].id, playerName);
      setCombinationResult(result);
      
      // Clear workbench after a delay
      setTimeout(() => {
        setElementsOnWorkbench([]);
        setCombinationResult(null);
      }, 3000);
    } catch (error) {
      console.error('Error combining elements:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Clear workbench
  const clearWorkbench = () => {
    setElementsOnWorkbench([]);
    setCombinationResult(null);
  };

  return (
    <div className="mb-8">
      <h2 className="text-xl font-bold mb-4">Workbench</h2>
      <div 
        ref={drop} 
        className={`workbench ${isOver ? 'bg-accent/20' : ''}`}
      >
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
          </div>
        ) : (
          <>
            <div className="flex gap-4 mb-4">
              <AnimatePresence>
                {elementsOnWorkbench.map((element, index) => (
                  <motion.div
                    key={`${element.id}-${index}`}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                  >
                    <Element element={element} />
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
            
            {combinationResult && (
              <div className="mt-8">
                <h3 className="text-lg font-semibold mb-2">Result:</h3>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <Element element={combinationResult.result} />
                  {combinationResult.is_new_discovery && (
                    <div className="mt-2 text-green-400 font-bold">
                      New Discovery!
                    </div>
                  )}
                </motion.div>
              </div>
            )}
            
            {elementsOnWorkbench.length > 0 && (
              <button 
                className="btn mt-4"
                onClick={clearWorkbench}
              >
                Clear Workbench
              </button>
            )}
            
            {elementsOnWorkbench.length === 0 && !combinationResult && (
              <div className="text-center text-textSecondary p-8">
                Drag elements here to combine them
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Workbench; 