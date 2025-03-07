import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { elementsApi } from '../services/api';

// Mock data for when the backend is not available
const MOCK_ELEMENTS = [
  {
    id: 1,
    name: "Water",
    emoji: "💧",
    description: "A clear, colorless liquid essential for life.",
    is_basic: true,
    created_at: "2025-03-05T20:02:42",
    discovered_by: null
  },
  {
    id: 2,
    name: "Fire",
    emoji: "🔥",
    description: "The rapid oxidation of material producing heat and light.",
    is_basic: true,
    created_at: "2025-03-05T20:02:42",
    discovered_by: null
  },
  {
    id: 3,
    name: "Earth",
    emoji: "🌍",
    description: "The solid ground beneath us and the material that forms it.",
    is_basic: true,
    created_at: "2025-03-05T20:02:42",
    discovered_by: null
  },
  {
    id: 4,
    name: "Air",
    emoji: "💨",
    description: "The invisible mixture of gases that surrounds the planet.",
    is_basic: true,
    created_at: "2025-03-05T20:02:42",
    discovered_by: null
  }
];

// Create a store with persistence
const useElementStore = create(
  persist(
    (set, get) => ({
      // State
      elements: [],
      discoveredElements: [],
      isLoading: false,
      error: null,
      
      // Actions
      fetchElements: async () => {
        set({ isLoading: true, error: null });
        try {
          const data = await elementsApi.getElements();
          console.log('Fetched elements:', data.elements);
          set({ elements: data.elements, isLoading: false });
          
          // If no discovered elements, add basic elements
          const { discoveredElements } = get();
          if (discoveredElements.length === 0) {
            const basicElements = data.elements.filter(el => el.is_basic === true || el.is_basic === 1);
            console.log('Adding basic elements to discovered:', basicElements);
            set({ discoveredElements: basicElements });
          }
        } catch (error) {
          console.error('Error fetching elements:', error);
          
          // Use mock data if the backend is not available
          console.log('Using mock data instead');
          set({ 
            elements: MOCK_ELEMENTS, 
            isLoading: false,
            error: `Backend not available: ${error.message}`
          });
          
          // If no discovered elements, add basic mock elements
          const { discoveredElements } = get();
          if (discoveredElements.length === 0) {
            set({ discoveredElements: MOCK_ELEMENTS });
          }
        }
      },
      
      combineElements: async (element1Id, element2Id, playerName) => {
        set({ isLoading: true, error: null });
        try {
          const result = await elementsApi.combineElements(element1Id, element2Id, playerName);
          
          // Update elements list if it's a new discovery
          if (result.is_new_discovery) {
            const elements = [...get().elements];
            elements.push(result.result);
            set({ elements });
          }
          
          // Add to discovered elements if not already there
          const discoveredElements = [...get().discoveredElements];
          const alreadyDiscovered = discoveredElements.some(el => el.id === result.result.id);
          
          if (!alreadyDiscovered) {
            discoveredElements.push(result.result);
            set({ discoveredElements });
          }
          
          set({ isLoading: false });
          return result;
        } catch (error) {
          console.error('Error combining elements:', error);
          
          // Mock combination result if the backend is not available
          const mockResult = {
            element1_id: element1Id,
            element2_id: element2Id,
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
            is_first_discovery: true
          };
          
          // Add the mock result to the elements and discovered elements
          const elements = [...get().elements];
          elements.push(mockResult.result);
          
          const discoveredElements = [...get().discoveredElements];
          discoveredElements.push(mockResult.result);
          
          set({ 
            elements, 
            discoveredElements,
            isLoading: false,
            error: `Backend not available: ${error.message}`
          });
          
          return mockResult;
        }
      },
      
      // Reset discovered elements (for new game)
      resetDiscoveredElements: () => {
        set({ discoveredElements: [] });
      },
      
      // Add basic elements to discovered elements
      addBasicElements: () => {
        const elements = get().elements;
        console.log('All elements:', elements);
        const basicElements = elements.filter(el => el.is_basic === true || el.is_basic === 1);
        console.log('Basic elements:', basicElements);
        if (basicElements.length > 0) {
          set({ discoveredElements: basicElements });
        } else {
          console.warn('No basic elements found in the store');
          // Use mock data if no basic elements are found
          set({ discoveredElements: MOCK_ELEMENTS });
        }
      },
      
      // Get element by ID
      getElementById: (id) => {
        const element = get().elements.find(el => el.id === id);
        if (!element) {
          console.warn(`Element with ID ${id} not found in the store`);
          // Return mock element if not found
          return MOCK_ELEMENTS.find(el => el.id === id);
        }
        return element;
      },
    }),
    {
      name: 'infinite-alchemist-storage',
      partialize: (state) => ({ discoveredElements: state.discoveredElements }),
    }
  )
);

export default useElementStore; 