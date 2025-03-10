# Infinite Alchemist AKA Бесконченый алхимик

A customizable element combination game inspired by Infinite Craft, with support for multiple languages and LLM integration.

![image](https://github.com/user-attachments/assets/5e44c101-f0d7-4a50-b1b6-c657a8699fbe)
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

## Key Components

### Element Store

The Element Store is a central state management system built with Zustand that handles all element-related data in the application. It's responsible for:

1. **Storing Elements**: Maintains a list of all elements and discovered elements
2. **Fetching Elements**: Communicates with the backend API to retrieve elements
3. **Combining Elements**: Handles the logic for combining elements and updating the state
4. **Error Handling**: Provides fallback mechanisms when the backend is unavailable
5. **Persistence**: Saves the user's discovered elements to localStorage

The Element Store provides methods like:
- `fetchElements()`: Loads elements from the backend
- `combineElements()`: Combines two elements to create a new one
- `getElementById()`: Retrieves a specific element by ID
- `addBasicElements()`: Adds the basic elements to the discovered elements list

This centralized approach ensures consistent state management across the application and simplifies the component logic.

### Workbench Component

The Workbench is the main interactive area where users can:
- Place elements by dragging from the Library or clicking on them
- Move elements around freely
- Combine elements by dropping one on top of another

It uses React DnD for drag and drop functionality and Framer Motion for animations.

### Library Component

The Library displays all discovered elements and allows users to:
- Search for specific elements
- Sort elements by different criteria
- Filter elements by category
- Drag elements to the Workbench or click to add them

## Internationalization Architecture

Infinite Alchemist supports multiple languages with completely separate element trees for each language:

### Key Features

- **Language-Specific Elements**: Each language has its own set of elements with unique IDs.
- **Independent Crafting Trees**: Element combinations are language-specific, allowing for culturally relevant combinations.
- **Basic Elements**: Each language starts with the same four basic elements (Water, Fire, Earth, Air) but with localized names.
- **LLM Integration**: The LLM generates language-specific combinations based on the selected language.

### Database Structure

The database is designed to support language-specific elements:

```
elements
├── id (PK)
├── name (String)
├── emoji (String)
├── is_basic (Boolean)
├── language (String) - "en", "ru", etc.
├── created_at (DateTime)
└── created_by (String, nullable)
```

Element combinations are also language-specific:

```
element_combinations
├── element1_id (PK, FK -> elements.id)
├── element2_id (PK, FK -> elements.id)
├── result_id (FK -> elements.id)
├── language (PK, String) - "en", "ru", etc.
├── created_at (DateTime)
└── discovered_by (String, nullable)
```

### Frontend Implementation

The frontend stores elements separately for each language and sends the current language to the backend when combining elements. The UI is fully translated using i18next.

## Acknowledgments

- Inspired by [Infinite Craft](https://neal.fun/infinite-craft/)
