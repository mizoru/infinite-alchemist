import React, { useState, useRef, useEffect } from 'react';
import { useDrop } from 'react-dnd';
import { motion, AnimatePresence } from 'framer-motion';
import Element from '../elements/Element';
import useElementStore from '../../store/elementStore';
import useSettingsStore from '../../store/settingsStore';

const WorkbenchElement = ({ element, position, onDragEnd, onDrop }) => {
  const ref = useRef(null);
  const [elementPosition, setElementPosition] = useState(position);
  
  // Update position when the prop changes
  useEffect(() => {
    setElementPosition(position);
  }, [position]);
  
  // Set up drop functionality for this element
  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'element',
    drop: (item, monitor) => {
      // Only process if we're dropping onto this element (not the workbench)
      if (monitor.didDrop() || !ref.current) {
        return;
      }
      
      // Get the dropped element
      const droppedElement = item;
      
      // Call the onDrop callback with both elements
      onDrop(element, droppedElement);
    },
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  }));
  
  // Set up the drag ref
  drop(ref);
  
  // Handle drag end
  const handleDragEnd = (event, info) => {
    const newPosition = { x: elementPosition.x + info.offset.x, y: elementPosition.y + info.offset.y };
    setElementPosition(newPosition);
    onDragEnd(element.workbenchId, newPosition);
  };
  
  return (
    <motion.div
      ref={ref}
      className={`absolute cursor-move ${isOver ? 'ring-2 ring-green-500' : ''}`}
      style={{ 
        left: elementPosition.x, 
        top: elementPosition.y,
        zIndex: 1 
      }}
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      exit={{ scale: 0 }}
      drag
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragElastic={0.1}
      dragMomentum={false}
      onDragEnd={handleDragEnd}
      whileDrag={{ zIndex: 1000, scale: 1.05 }}
    >
      <Element element={element} size="large" />
    </motion.div>
  );
};

const Workbench = ({ onDiscovery }) => {
  const [elementsOnWorkbench, setElementsOnWorkbench] = useState([]);
  const [combinationResult, setCombinationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const { combineElements } = useElementStore();
  const { playerName, darkMode } = useSettingsStore();
  const workbenchRef = useRef(null);

  // Set up drop functionality for the workbench
  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'element',
    drop: (item, monitor) => {
      // Get drop position relative to the workbench
      const workbenchRect = workbenchRef.current.getBoundingClientRect();
      const dropPosition = monitor.getClientOffset();
      
      // Calculate position within the workbench
      const x = dropPosition.x - workbenchRect.left;
      const y = dropPosition.y - workbenchRect.top;
      
      console.log('Dropped at position:', { x, y });
      console.log('Item dropped:', item);
      
      // Add element to workbench at this position
      addElementToWorkbench(item, { x, y });
      
      return { dropped: true };
    },
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  }));

  // Listen for custom events from the Library component
  useEffect(() => {
    const handleAddToWorkbench = (event) => {
      const { element } = event.detail;
      console.log('Custom event received:', element);
      
      // Calculate center position of workbench
      if (workbenchRef.current) {
        const rect = workbenchRef.current.getBoundingClientRect();
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        // Add element to center of workbench
        addElementToWorkbench({ id: element.id, name: element.name }, { 
          x: centerX - 50, // Offset by half element width
          y: centerY - 30  // Offset by half element height
        });
      }
    };
    
    // Add event listener
    window.addEventListener('add-to-workbench', handleAddToWorkbench);
    
    // Clean up
    return () => {
      window.removeEventListener('add-to-workbench', handleAddToWorkbench);
    };
  }, []);

  // Add element to workbench at a specific position
  const addElementToWorkbench = (item, position) => {
    // Find the element in the store
    const element = useElementStore.getState().getElementById(item.id);
    
    if (!element) {
      console.error('Element not found:', item);
      // Try to fetch elements if they're not loaded yet
      useElementStore.getState().fetchElements().then(() => {
        // Try again after fetching
        const refetchedElement = useElementStore.getState().getElementById(item.id);
        if (refetchedElement) {
          console.log('Element found after fetching:', refetchedElement);
          addElementToWorkbenchInternal(refetchedElement, position);
        } else {
          console.error('Element still not found after fetching:', item);
          // Create a mock element if it's still not found
          const mockElement = {
            id: item.id,
            name: item.name || `Element ${item.id}`,
            emoji: "❓",
            description: "This element couldn't be loaded from the backend.",
            is_basic: false,
            created_at: new Date().toISOString(),
            discovered_by: null
          };
          console.log('Using mock element instead:', mockElement);
          addElementToWorkbenchInternal(mockElement, position);
        }
      }).catch(error => {
        console.error('Error fetching elements:', error);
        // Create a mock element if there's an error
        const mockElement = {
          id: item.id,
          name: item.name || `Element ${item.id}`,
          emoji: "❓",
          description: "This element couldn't be loaded from the backend.",
          is_basic: false,
          created_at: new Date().toISOString(),
          discovered_by: null
        };
        console.log('Using mock element instead:', mockElement);
        addElementToWorkbenchInternal(mockElement, position);
      });
      return;
    }
    
    addElementToWorkbenchInternal(element, position);
  };
  
  // Internal function to add element to workbench
  const addElementToWorkbenchInternal = (element, position) => {
    console.log('Adding element to workbench:', element, 'at position:', position);
    
    // Add element to workbench with position
    setElementsOnWorkbench(prev => [
      ...prev, 
      { 
        ...element, 
        workbenchId: `${element.id}-${Date.now()}`, // Unique ID for this instance
        position 
      }
    ]);
  };

  // Update element position when dragged
  const updateElementPosition = (workbenchId, newPosition) => {
    console.log('Updating position for element:', workbenchId, 'to:', newPosition);
    
    // Make sure the position is within the workbench boundaries
    if (workbenchRef.current) {
      const rect = workbenchRef.current.getBoundingClientRect();
      
      // Adjust position if needed to keep element within bounds
      const adjustedPosition = {
        x: Math.max(0, Math.min(newPosition.x, rect.width - 100)),
        y: Math.max(0, Math.min(newPosition.y, rect.height - 100))
      };
      
      setElementsOnWorkbench(
        elementsOnWorkbench.map(el => 
          el.workbenchId === workbenchId 
            ? { ...el, position: adjustedPosition } 
            : el
        )
      );
    } else {
      // If workbenchRef is not available, just update the position
      setElementsOnWorkbench(
        elementsOnWorkbench.map(el => 
          el.workbenchId === workbenchId 
            ? { ...el, position: newPosition } 
            : el
        )
      );
    }
  };

  // Handle element combination
  const handleElementCombination = async (targetElement, droppedElement) => {
    // Don't combine if it's the same element instance
    if (targetElement.workbenchId === droppedElement.workbenchId) {
      return;
    }
    
    console.log('Combining elements:', targetElement, 'and', droppedElement);
    
    setIsLoading(true);
    try {
      // Call the API to combine elements
      const result = await combineElements(targetElement.id, droppedElement.id, playerName);
      
      console.log('Combination result:', result);
      
      // Show the result
      setCombinationResult({
        ...result,
        position: targetElement.position // Show result at the target element's position
      });
      
      // Remove the combined elements
      setElementsOnWorkbench(
        elementsOnWorkbench.filter(el => 
          el.workbenchId !== targetElement.workbenchId && 
          el.workbenchId !== droppedElement.workbenchId
        )
      );
      
      // Notify parent component about the discovery
      if (onDiscovery && typeof onDiscovery === 'function') {
        onDiscovery(result);
      }
      
      // Clear the result after a delay
      setTimeout(() => {
        // Add the result to the workbench
        if (result.result) {
          setElementsOnWorkbench(prev => [
            ...prev.filter(el => 
              el.workbenchId !== targetElement.workbenchId && 
              el.workbenchId !== droppedElement.workbenchId
            ),
            { 
              ...result.result, 
              workbenchId: `${result.result.id}-${Date.now()}`,
              position: targetElement.position 
            }
          ]);
        }
        
        setCombinationResult(null);
      }, 2000);
    } catch (error) {
      console.error('Error combining elements:', error);
      
      // Create a mock result if there's an error
      const mockResult = {
        element1_id: targetElement.id,
        element2_id: droppedElement.id,
        result_id: 999,
        result: {
          id: 999,
          name: "Mock Result",
          emoji: "✨",
          description: "This is a mock result because the backend is not available.",
          is_basic: false,
          created_at: new Date().toISOString(),
          discovered_by: null
        },
        is_new_discovery: true,
        is_first_discovery: true,
        position: targetElement.position
      };
      
      // Show the mock result
      setCombinationResult(mockResult);
      
      // Remove the combined elements
      setElementsOnWorkbench(
        elementsOnWorkbench.filter(el => 
          el.workbenchId !== targetElement.workbenchId && 
          el.workbenchId !== droppedElement.workbenchId
        )
      );
      
      // Clear the result after a delay
      setTimeout(() => {
        // Add the mock result to the workbench
        setElementsOnWorkbench(prev => [
          ...prev.filter(el => 
            el.workbenchId !== targetElement.workbenchId && 
            el.workbenchId !== droppedElement.workbenchId
          ),
          { 
            ...mockResult.result, 
            workbenchId: `${mockResult.result.id}-${Date.now()}`,
            position: targetElement.position 
          }
        ]);
        
        setCombinationResult(null);
      }, 2000);
    } finally {
      setIsLoading(false);
    }
  };

  // Clear workbench
  const clearWorkbench = () => {
    setElementsOnWorkbench([]);
    setCombinationResult(null);
  };

  // Get workbench state classes
  const getWorkbenchStateClasses = () => {
    if (isOver) {
      return 'bg-accent/30 border-accent';
    }
    return 'bg-secondary/20 border-accent/30';
  };

  return (
    <div className="mb-8">
      <motion.h2 
        className="text-xl font-bold mb-4"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        Workbench
      </motion.h2>
      
      <motion.div 
        ref={(node) => {
          drop(node);
          workbenchRef.current = node;
        }}
        className={`
          workbench border-2 rounded-xl p-6 min-h-[400px] relative
          transition-colors duration-300 ease-in-out
          ${getWorkbenchStateClasses()}
        `}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        {isLoading ? (
          <motion.div 
            className="absolute inset-0 flex items-center justify-center backdrop-blur-sm z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div 
              className="w-16 h-16 border-4 border-accent rounded-full border-t-transparent"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            />
          </motion.div>
        ) : null}
        
        {/* Elements on workbench */}
        <AnimatePresence>
          {elementsOnWorkbench.map((element) => (
            <WorkbenchElement
              key={element.workbenchId}
              element={element}
              position={element.position}
              onDragEnd={(id, newPosition) => updateElementPosition(id, newPosition)}
              onDrop={handleElementCombination}
            />
          ))}
        </AnimatePresence>
        
        {/* Combination result animation */}
        {combinationResult && (
          <motion.div 
            className="absolute z-50"
            style={{ 
              left: combinationResult.position.x, 
              top: combinationResult.position.y 
            }}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1.2, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ 
              type: "spring",
              stiffness: 500,
              damping: 30
            }}
          >
            <Element 
              element={combinationResult.result} 
              size="large"
              className={combinationResult.is_new_discovery ? 'ring-4 ring-green-500/30' : ''}
            />
          </motion.div>
        )}
        
        {/* Empty state */}
        {elementsOnWorkbench.length === 0 && !combinationResult && (
          <motion.div 
            className="text-center text-textSecondary p-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <p className="text-lg mb-2">Drag elements here to combine them</p>
            <p className="text-sm opacity-75">
              Drop elements anywhere on the workbench and drag them around
            </p>
          </motion.div>
        )}
        
        {/* Clear button */}
        {elementsOnWorkbench.length > 0 && (
          <motion.div
            className="absolute bottom-4 right-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <button 
              className={`
                btn px-6 py-2
                ${darkMode ? 'bg-red-500/20 hover:bg-red-500/30' : 'bg-red-500 hover:bg-red-600'}
              `}
              onClick={clearWorkbench}
            >
              Clear Workbench
            </button>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default Workbench; 