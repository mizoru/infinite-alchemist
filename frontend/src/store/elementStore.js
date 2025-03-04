import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { elementsApi } from '../services/api';

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
          set({ elements: data.elements, isLoading: false });
        } catch (error) {
          set({ error: error.message, isLoading: false });
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
          set({ error: error.message, isLoading: false });
          throw error;
        }
      },
      
      // Reset discovered elements (for new game)
      resetDiscoveredElements: () => {
        set({ discoveredElements: [] });
      },
      
      // Add basic elements to discovered elements
      addBasicElements: () => {
        const basicElements = get().elements.filter(el => el.is_basic === 1);
        set({ discoveredElements: basicElements });
      },
    }),
    {
      name: 'infinite-alchemist-storage',
      partialize: (state) => ({ discoveredElements: state.discoveredElements }),
    }
  )
);

export default useElementStore; 