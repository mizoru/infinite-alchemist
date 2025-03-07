import React, { useState, useRef, useEffect } from 'react';
import { useDrop } from 'react-dnd';
import { motion, AnimatePresence } from 'framer-motion';
import Element from '../elements/Element';
import useElementStore from '../../store/elementStore';
import useSettingsStore from '../../store/settingsStore';

const WorkbenchElement = ({ element, position, onDragEnd, onDrop, onDuplicate, onRemove, workbenchRef }) => {
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
    console.log('Drag ended with info:', info);
    
    // Make sure workbenchRef is defined and has a current value
    if (!workbenchRef || !workbenchRef.current) {
      console.error('workbenchRef is not defined or has no current value');
      return;
    }
    
    // Make sure the info object has a point property
    if (!info || !info.point) {
      console.error('Invalid drag info object:', info);
      return;
    }
    
    // Check if the element was dropped on another element
    // Get all elements on the workbench
    const workbenchElements = document.querySelectorAll('.workbench-element');
    let droppedOnElement = null;
    
    workbenchElements.forEach(el => {
      // Skip the current element
      if (!el.dataset || !el.dataset.workbenchId || el.dataset.workbenchId === element.workbenchId) {
        return;
      }
      
      // Check if the point is within this element's bounds
      const rect = el.getBoundingClientRect();
      if (
        info.point.x >= rect.left &&
        info.point.x <= rect.right &&
        info.point.y >= rect.top &&
        info.point.y <= rect.bottom
      ) {
        droppedOnElement = el.dataset.workbenchId;
      }
    });
    
    // If dropped on another element, trigger the combination
    if (droppedOnElement) {
      console.log('Dropped on element:', droppedOnElement);
      // Find the target element in the workbench elements
      const targetElement = document.querySelector(`[data-workbench-id="${droppedOnElement}"]`);
      if (targetElement && targetElement.dataset && targetElement.dataset.elementId) {
        // Create a mock item for the onDrop callback
        const mockItem = {
          id: element.id,
          workbenchId: element.workbenchId,
          isOnWorkbench: true
        };
        
        // Get the target element data
        const targetElementData = {
          id: parseInt(targetElement.dataset.elementId),
          workbenchId: droppedOnElement,
          isOnWorkbench: true
        };
        
        // Call the onDrop callback
        onDrop(targetElementData, mockItem);
        return;
      }
    }
    
    // If not dropped on another element, just update the position
    const newPosition = { 
      x: info.point.x - workbenchRef.current.getBoundingClientRect().left, 
      y: info.point.y - workbenchRef.current.getBoundingClientRect().top 
    };
    
    // Ensure the position is within the workbench bounds
    const workbenchRect = workbenchRef.current.getBoundingClientRect();
    newPosition.x = Math.max(0, Math.min(newPosition.x, workbenchRect.width));
    newPosition.y = Math.max(0, Math.min(newPosition.y, workbenchRect.height));
    
    console.log('New position calculated:', newPosition);
    setElementPosition(newPosition);
    onDragEnd(element.workbenchId, newPosition);
  };
  
  // Handle element duplication
  const handleDuplicate = () => {
    console.log('Duplicating element:', element);
    if (onDuplicate) {
      onDuplicate(element, elementPosition);
    }
  };
  
  return (
    <motion.div
      ref={ref}
      className={`absolute cursor-move workbench-element ${isOver ? 'ring-2 ring-green-500' : ''}`}
      data-workbench-id={element.workbenchId}
      data-element-id={element.id}
      style={{ 
        left: elementPosition.x, 
        top: elementPosition.y,
        zIndex: 1 
      }}
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      exit={{ scale: 0 }}
      drag={true}
      dragMomentum={false}
      onDragEnd={handleDragEnd}
      whileDrag={{ zIndex: 1000, scale: 1.05 }}
    >
      <Element 
        element={element} 
        size="large" 
        isOnWorkbench={true}
        onDuplicate={handleDuplicate}
      />
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
      // If the element is already on the workbench, don't add it again
      if (item.isOnWorkbench) {
        console.log('Element is already on workbench, not adding a copy');
        return { dropped: true };
      }
      
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
      
      console.log('Adjusted position:', adjustedPosition);
      
      // Update the element's position in the state
      setElementsOnWorkbench(prev => 
        prev.map(el => 
          el.workbenchId === workbenchId 
            ? { ...el, position: adjustedPosition } 
            : el
        )
      );
    } else {
      // If workbenchRef is not available, just update the position
      setElementsOnWorkbench(prev => 
        prev.map(el => 
          el.workbenchId === workbenchId 
            ? { ...el, position: newPosition } 
            : el
        )
      );
    }
  };
  
  // Duplicate an element on the workbench
  const duplicateElement = (element, position) => {
    console.log('Duplicating element:', element);
    
    // Create a slightly offset position for the duplicate
    const offsetPosition = {
      x: position.x + 20,
      y: position.y + 20
    };
    
    // Add a duplicate of the element to the workbench
    addElementToWorkbenchInternal(element, offsetPosition);
  };

  // Handle element combination
  const handleElementCombination = async (targetElement, droppedElement) => {
    console.log('Combining elements:', targetElement, 'and', droppedElement);
    
    // Make sure we have valid elements
    if (!targetElement || !droppedElement) {
      console.error('Invalid elements for combination');
      return;
    }
    
    // Make sure we have valid IDs
    if (!targetElement.id || !droppedElement.id) {
      console.error('Elements missing IDs for combination');
      return;
    }
    
    // If the dropped element is from the workbench, remove it
    if (droppedElement.isOnWorkbench && droppedElement.workbenchId) {
      console.log('Removing dropped element from workbench:', droppedElement.workbenchId);
      setElementsOnWorkbench(prev => 
        prev.filter(el => el.workbenchId !== droppedElement.workbenchId)
      );
    }
    
    // Don't combine if it's the same element instance
    if (targetElement.workbenchId && droppedElement.workbenchId && 
        targetElement.workbenchId === droppedElement.workbenchId) {
      console.log('Cannot combine an element with itself');
      return;
    }
    
    setIsLoading(true);
    try {
      // Call the API to combine elements
      const result = await combineElements(targetElement.id, droppedElement.id, playerName);
      
      console.log('Combination result:', result);
      
      // Get the position for the result
      // If targetElement has a position, use it
      // Otherwise, use a default position in the center of the workbench
      let resultPosition = { x: 0, y: 0 };
      
      if (targetElement.position) {
        resultPosition = targetElement.position;
      } else if (workbenchRef.current) {
        // If no position is available, place it in the center of the workbench
        const rect = workbenchRef.current.getBoundingClientRect();
        resultPosition = {
          x: rect.width / 2 - 50,  // Adjust for element width
          y: rect.height / 2 - 50  // Adjust for element height
        };
      }
      
      // Show the result
      setCombinationResult({
        ...result,
        position: resultPosition
      });
      
      // Set loading to false after getting the result
      setIsLoading(false);
      
      // Remove the target element
      setElementsOnWorkbench(prev => 
        prev.filter(el => el.workbenchId !== targetElement.workbenchId)
      );
      
      // Notify parent component of discovery
      if (onDiscovery && result.is_new_discovery) {
        onDiscovery(result);
      }
      
      // Clear the result after a delay and add the new element
      setTimeout(() => {
        // Add the result to the workbench
        if (result.result) {
          setElementsOnWorkbench(prev => [
            ...prev,
            { 
              ...result.result, 
              workbenchId: `${result.result.id}-${Date.now()}`,
              position: resultPosition 
            }
          ]);
        }
        
        setCombinationResult(null);
      }, 2000);
      
    } catch (error) {
      console.error('Error combining elements:', error);
      setIsLoading(false);
      
      // Show error message
      // TODO: Implement error toast or notification
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
    <div 
      ref={(node) => {
        workbenchRef.current = node;
        drop(node);
      }}
      className={`
        workbench relative rounded-xl overflow-hidden
        ${getWorkbenchStateClasses()}
        transition-colors duration-200
      `}
      style={{ 
        minHeight: '400px',
        height: '60vh'
      }}
    >
      {/* Elements on workbench */}
      <AnimatePresence>
        {elementsOnWorkbench.map((element) => (
          <WorkbenchElement
            key={element.workbenchId}
            element={element}
            position={element.position}
            workbenchRef={workbenchRef}
            onDragEnd={(id, newPosition) => updateElementPosition(id, newPosition)}
            onDrop={handleElementCombination}
            onDuplicate={duplicateElement}
          />
        ))}
      </AnimatePresence>

      {/* Combination result animation */}
      <AnimatePresence>
        {combinationResult && combinationResult.position && (
          <motion.div
            className="absolute z-10"
            style={{ 
              left: combinationResult.position.x, 
              top: combinationResult.position.y 
            }}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ 
              scale: [0, 1.2, 1], 
              opacity: 1 
            }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="relative">
              <Element 
                element={combinationResult.result} 
                size="large"
                className={`
                  ${combinationResult.is_new_discovery ? 'ring-2 ring-green-500' : ''}
                  ${combinationResult.is_first_discovery ? 'ring-2 ring-purple-500' : ''}
                `}
              />
              
              {combinationResult.is_new_discovery && (
                <motion.div
                  className="absolute -top-2 -right-2 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-full"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  New!
                </motion.div>
              )}
              
              {combinationResult.is_first_discovery && (
                <motion.div
                  className="absolute -top-2 -left-2 bg-purple-500 text-white text-xs font-bold px-2 py-1 rounded-full"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  First!
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading indicator */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            className="absolute inset-0 flex items-center justify-center bg-black/30 backdrop-blur-sm z-20"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="text-center">
              <motion.div
                className="inline-block w-12 h-12 border-4 border-accent border-t-transparent rounded-full"
                animate={{ rotate: 360 }}
                transition={{ 
                  duration: 1,
                  repeat: Infinity,
                  ease: "linear"
                }}
              />
              <p className="mt-4 text-white font-medium">Combining elements...</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty state */}
      {elementsOnWorkbench.length === 0 && !isLoading && !combinationResult && (
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <p className="text-textSecondary mb-2">Drag elements here to combine them</p>
            <p className="text-xs text-textSecondary opacity-70">
              Drag elements from the library or click on them to add to the workbench.
              <br />
              Right-click elements on the workbench to duplicate them.
              <br />
              Drag one element onto another to combine them.
            </p>
          </motion.div>
        </div>
      )}

      {/* Clear button */}
      {elementsOnWorkbench.length > 0 && (
        <motion.button
          className="absolute bottom-4 right-4 bg-red-500/80 hover:bg-red-500 text-white px-3 py-1 rounded-lg text-sm"
          onClick={clearWorkbench}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Clear
        </motion.button>
      )}
    </div>
  );
};

export default Workbench; 