import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

// Create stars for the background
const createStars = () => {
  const starsContainer = document.createElement('div');
  starsContainer.className = 'stars';
  
  // Create 100 stars with random positions
  for (let i = 0; i < 100; i++) {
    const star = document.createElement('div');
    star.className = 'star';
    star.style.top = `${Math.random() * 100}%`;
    star.style.left = `${Math.random() * 100}%`;
    star.style.opacity = Math.random() * 0.7 + 0.3;
    star.style.width = `${Math.random() * 2 + 1}px`;
    star.style.height = star.style.width;
    
    // Add a subtle animation with random duration
    star.style.animation = `pulse ${Math.random() * 3 + 2}s infinite alternate`;
    
    starsContainer.appendChild(star);
  }
  
  document.body.appendChild(starsContainer);
};

// Create stars when the DOM is loaded
document.addEventListener('DOMContentLoaded', createStars);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
