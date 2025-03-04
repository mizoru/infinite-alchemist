import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints for elements
export const elementsApi = {
  // Get all elements
  getElements: async (skip = 0, limit = 100) => {
    try {
      const response = await api.get(`/elements?skip=${skip}&limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching elements:', error);
      throw error;
    }
  },

  // Get a specific element by ID
  getElement: async (id) => {
    try {
      const response = await api.get(`/elements/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching element with ID ${id}:`, error);
      throw error;
    }
  },

  // Create a new element
  createElement: async (elementData) => {
    try {
      const response = await api.post('/elements', elementData);
      return response.data;
    } catch (error) {
      console.error('Error creating element:', error);
      throw error;
    }
  },

  // Combine two elements
  combineElements: async (element1Id, element2Id, playerName = null) => {
    try {
      const response = await api.post('/elements/combine', {
        element1_id: element1Id,
        element2_id: element2Id,
        player_name: playerName,
      });
      return response.data;
    } catch (error) {
      console.error('Error combining elements:', error);
      throw error;
    }
  },
};

export default api; 