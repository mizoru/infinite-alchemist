# Infinite Alchemist AKA Бесконченый алхимик

A customizable element combination game inspired by Infinite Craft, with support for multiple languages and LLM integration.

## Overview

Infinite Alchemist is a game where players combine elements to discover new ones. Starting with basic elements like Water, Fire, Earth, and Air, players can create thousands of unique combinations. The game uses a Large Language Model (LLM) to generate new elements based on the combinations.

## Features

- **Element Combination**: Drag and drop elements to combine them and discover new ones
- **Persistent Library**: Keep track of all your discovered elements
- **Customization**: Change your nickname, language, and game mode
- **Responsive Design**: Play on desktop or mobile devices
- **Dark Mode**: Easy on the eyes with a beautiful dark theme
- **Internationalization**: Support for multiple languages (English, with Russian coming soon)

## Tech Stack

### Backend
- Python 3.10+
- FastAPI
- SQLite
- SQLAlchemy
- Langchain

### Frontend
- React 18
- JavaScript
- Vite
- React DnD (Drag and Drop)
- Framer Motion (Animations)
- Tailwind CSS
- Zustand (State Management)
- i18next (Internationalization)

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- OpenAI API key

### Backend Setup
1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file with your LLM API key.

6. Initialize the database:
   ```
   python -m app.db.init_db
   ```

7. Start the backend server:
   ```
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:5173`

## Project Structure

```
infinite-alchemist/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── store/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── tailwind.config.js
├── README.md
└── TODO.md
```

## Acknowledgments

- Inspired by [Infinite Craft](https://neal.fun/infinite-craft/)
