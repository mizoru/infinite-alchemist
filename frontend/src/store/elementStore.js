import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { elementsApi } from '../services/api';
import useSettingsStore from './settingsStore';

// Mock data for when the backend is not available
const MOCK_ELEMENTS = {
  en: [
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
  ],
  ru: [
    {
      id: 5,
      name: "Вода",
      emoji: "💧",
      description: "Прозрачная жидкость, необходимая для жизни.",
      is_basic: true,
      created_at: "2025-03-05T20:02:42",
      discovered_by: null
    },
    {
      id: 6,
      name: "Огонь",
      emoji: "🔥",
      description: "Быстрое окисление материала, производящее тепло и свет.",
      is_basic: true,
      created_at: "2025-03-05T20:02:42",
      discovered_by: null
    },
    {
      id: 7,
      name: "Земля",
      emoji: "🌍",
      description: "Твёрдая поверхность под нами и материал, из которого она состоит.",
      is_basic: true,
      created_at: "2025-03-05T20:02:42",
      discovered_by: null
    },
    {
      id: 8,
      name: "Воздух",
      emoji: "💨",
      description: "Невидимая смесь газов, окружающая планету.",
      is_basic: true,
      created_at: "2025-03-05T20:02:42",
      discovered_by: null
    }
  ]
};

// Helper to get current language
const getCurrentLanguage = () => {
  const state = useSettingsStore.getState();
  return state.language || 'en';
};

// Create a store with persistence
const useElementStore = create(
  persist(
    (set, get) => ({
      // State
      elements: {
        en: [],
        ru: []
      },
      discoveredElements: {
        en: [],
        ru: []
      },
      isLoading: false,
      error: null,
      
      // Actions
      fetchElements: async () => {
        const lang = getCurrentLanguage();
        set({ isLoading: true, error: null });
        
        try {
          const data = await elementsApi.getElements();
          console.log('Fetched elements:', data.elements);
          
          // Update elements for current language
          set(state => ({
            elements: {
              ...state.elements,
              [lang]: data.elements
            },
            isLoading: false
          }));
          
          // If no discovered elements for current language, add basic elements
          const { discoveredElements } = get();
          if (!discoveredElements[lang] || discoveredElements[lang].length === 0) {
            get().addBasicElements();
          }
        } catch (error) {
          console.error('Error fetching elements:', error);
          
          // Use mock data if the backend is not available
          console.log('Using mock data instead');
          const mockElements = MOCK_ELEMENTS[lang] || MOCK_ELEMENTS.en;
          
          set(state => ({ 
            elements: {
              ...state.elements,
              [lang]: mockElements
            },
            isLoading: false,
            error: `Backend not available: ${error.message}`
          }));
          
          // If no discovered elements for current language, add basic mock elements
          const { discoveredElements } = get();
          if (!discoveredElements[lang] || discoveredElements[lang].length === 0) {
            set(state => ({
              discoveredElements: {
                ...state.discoveredElements,
                [lang]: mockElements
              }
            }));
          }
        }
      },
      
      // Add basic elements to discovered elements
      addBasicElements: () => {
        const lang = getCurrentLanguage();
        console.log(`Adding basic elements for language: ${lang}`);
        
        // Get elements for current language
        const elements = get().elements[lang] || [];
        
        // Filter basic elements based on language
        let basicElements = [];
        
        if (elements.length > 0) {
          // Filter elements from the backend
          basicElements = elements.filter(el => {
            const isBasic = el.is_basic === true || el.is_basic === 1;
            const matchesLanguage = lang === 'en' 
              ? ['Water', 'Fire', 'Earth', 'Air'].includes(el.name)
              : ['Вода', 'Огонь', 'Земля', 'Воздух'].includes(el.name);
            
            return isBasic && matchesLanguage;
          });
          
          console.log('Filtered basic elements:', basicElements);
          
          // If no basic elements found for the current language, use mock data
          if (basicElements.length === 0) {
            console.log(`No basic elements found for ${lang}, using mock data`);
            basicElements = MOCK_ELEMENTS[lang] || MOCK_ELEMENTS.en;
          }
        } else {
          // Use mock data if no elements from backend
          console.log('No elements from backend, using mock data');
          basicElements = MOCK_ELEMENTS[lang] || MOCK_ELEMENTS.en;
        }
        
        // Add basic elements to discovered elements for current language
        set(state => {
          const currentDiscovered = state.discoveredElements[lang] || [];
          return {
            discoveredElements: {
              ...state.discoveredElements,
              [lang]: [
                ...currentDiscovered.filter(el => !el.is_basic),
                ...basicElements
              ]
            }
          };
        });
      },
      
      // Add a new element to discovered elements
      addDiscoveredElement: (element) => {
        const lang = getCurrentLanguage();
        
        set(state => {
          const currentDiscovered = state.discoveredElements[lang] || [];
          
          // Check if element already exists
          const exists = currentDiscovered.some(el => el.id === element.id);
          if (exists) {
            return state;
          }
          
          return {
            discoveredElements: {
              ...state.discoveredElements,
              [lang]: [...currentDiscovered, element]
            }
          };
        });
      },
      
      // Reset discovered elements
      resetDiscoveredElements: () => {
        const lang = getCurrentLanguage();
        
        set(state => ({
          discoveredElements: {
            ...state.discoveredElements,
            [lang]: []
          }
        }));
      },
      
      // Get discovered elements for current language
      getDiscoveredElements: () => {
        const lang = getCurrentLanguage();
        return get().discoveredElements[lang] || [];
      },
      
      // Combine two elements
      combineElements: async (element1Id, element2Id, playerName = null) => {
        set({ isLoading: true, error: null });
        try {
          const result = await elementsApi.combineElements(element1Id, element2Id, playerName);
          console.log('Combination result:', result);
          
          // Check if there was an error in the combination
          if (result.error) {
            set({ 
              isLoading: false, 
              error: result.error 
            });
            return result;
          }
          
          // Add the result to discovered elements
          if (result.result) {
            get().addDiscoveredElement(result.result);
          }
          
          set({ isLoading: false });
          return result;
        } catch (error) {
          console.error('Error combining elements:', error);
          set({ isLoading: false, error: `Error combining elements: ${error.message}` });
          
          // Return a mock result for offline mode
          const lang = getCurrentLanguage();
          return {
            element1_id: element1Id,
            element2_id: element2Id,
            result_id: null,
            result: null,
            is_new_discovery: false,
            is_first_discovery: false,
            error: "Failed to connect to the server. Please try again later."
          };
        }
      },
      
      // Get element by ID
      getElementById: (id) => {
        const lang = getCurrentLanguage();
        const elements = get().elements[lang] || [];
        
        const element = elements.find(el => el.id === id);
        if (!element) {
          console.warn(`Element with ID ${id} not found in the store for language ${lang}`);
          
          // Try to fetch the element from the API
          get().fetchElementById(id);
          
          // Return mock element if not found
          const mockElements = MOCK_ELEMENTS[lang] || MOCK_ELEMENTS.en;
          return mockElements.find(el => el.id === id) || mockElements[0];
        }
        return element;
      },
      
      // Fetch a specific element by ID
      fetchElementById: async (id) => {
        const lang = getCurrentLanguage();
        
        try {
          const element = await elementsApi.getElement(id);
          
          set(state => {
            const currentElements = state.elements[lang] || [];
            return {
              elements: {
                ...state.elements,
                [lang]: [...currentElements.filter(el => el.id !== id), element]
              }
            };
          });
          
          return element;
        } catch (error) {
          console.error(`Error fetching element with ID ${id}:`, error);
          return null;
        }
      }
    }),
    {
      name: 'infinite-alchemist-storage',
      partialize: (state) => ({ discoveredElements: state.discoveredElements }),
    }
  )
);

export default useElementStore; 