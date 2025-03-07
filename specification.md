### **"Infinite Alchemist" Game Specification**

#### **Core Gameplay Mechanics**
1. **Truly Infinite Combinations**: 
   - The game will begin with 4 basic elements (e.g., Fire, Water, Earth, Air).
   - Players will drag one element onto another to attempt a combination.
   - The game will query a database for any existing recipe of the combination. If it exists, the result is shown immediately.
   - If no recipe exists, the game will query the LLM to determine if a new element is created and what it is. The result is stored in the database for future reference.
   - The first discovery of a new element will reward the player with a special animation or message, creating a sense of accomplishment.

2. **LLM-Driven Combinations**:
   - The LLM will determine the outcome of a combination query based on internal logic and coherence (combinations should "make sense").
   - Players will receive a loading/waiting animation while the game queries the LLM.
   - Upon a successful result, the combination is stored in the database, making it available to all players from that point forward.

---

#### **LLM Integration and Model Independence**
- **LLM Queries**: Each new recipe is determined by querying the LLM. Once a combination is discovered, it is permanently stored in the database to avoid re-querying the LLM for the same combination.
- **Model Independence**: The backend is designed to be adaptable to any language model, allowing flexibility to switch models (e.g., GPT, fine-tuned models) without major code changes.

---

#### **Backend and Frameworks**
- **Python Backend**: Python will be used for the backend due to its robust ML capabilities and strong support for database interactions.
- **Backend Framework**:
   - **FastAPI**: Lightweight, asynchronous, and ideal for real-time game queries. It will handle API requests for LLM queries, game data storage, and retrieval.
- **Database**:
   - **SQLite**: Chosen for its simplicity and suitability for the game's early stages. It will store:
     - **Recipe data**: Discovered combinations.
     - **Player data**: Which elements the player has discovered.
     - **First discovery info**: Information about who first discovered specific combinations.
   - In the future, a cloud-based solution could replace SQLite for scalability.

---

#### **UI/UX Design**
1. **Workbench ("Crafting Area")**:
   - **Type**: Free-form, drag-and-drop interface where players can freely arrange elements for experimentation.
   - **Interactions**:
     - **Left-click** to drag elements from the Library to the Workbench.
     - **Right-click** to duplicate an element for quicker combination testing.
     - **No visual clues** for potential combinations to maintain the discovery aspect.
     - **Elements stay where they are placed** on the workbench until moved or removed.
     - **Combination occurs** only when one element is dropped directly on top of another.
     - **No limit** to the number of elements that can be placed on the workbench simultaneously.
   - **Design**: Clean, minimalistic interface with a subtle background pattern to keep focus on the elements.

2. **Library ("Discovered Elements")**:
   - Displays all discovered elements with draggable icons.
   - **Search** function for quickly locating elements.
   - **Sort options**:
     - Alphabetical order.
     - By time discovered (newest first or oldest first).

3. **Customization Menu**:
   - **Nickname input**: Players can enter a nickname, stored locally (no login required).
   - **Language selection**: 
     - Initial release will support English only.
     - Russian language support will be added in a subsequent update.
     - Language can be chosen at the start or via the settings menu.
   - **Game Mode**:
     - **Classic Mode**: Start with four basic elements.
     - **Custom Mode**: Start with a limited pool of similar elements (as a challenge).
   - **Future Expansion**: Options for more advanced customizations will be introduced later (e.g., changing game rules or altering recipe logic).

4. **Feedback Animation**:
   - Visual feedback (such as a glow or burst) when a new combination is discovered or when an action is performed successfully.
   

---

#### **Game Sessions and Custom Games**
- Each game session will be unique to the player:
   - The **starting elements** may vary based on game mode (Classic or Custom).
   - **Session storage**: Player-specific data (discovered elements, settings) will be stored locally using **LocalStorage**.
   - Multiple game sessions can be supported, with different profiles for custom game modes.
   - **Game modes**:
     - **Classic Mode**: Default starting elements.
     - **Custom Mode**: Start with specific sets of elements.

---

#### **State Management**
- **React Context API**: Will be used for managing the state of the game (discovered elements, active combinations, settings) across the application. It's lightweight and native to React, making it easy to integrate.
- **Future considerations**: If game complexity increases, you can migrate to Zustand or Redux for more advanced state management.

---

#### **Cloud and Storage**
- **LocalStorage**: Will be used to store session data, player preferences, discovered elements, and game state. This ensures continuity between sessions.
- **IndexedDB** may be considered for more complex data storage in the future (e.g., larger player data or session histories).
- **SQLite**: Initially for storing combinations, player discovery progress, and game data. The database will transition to a more scalable cloud-based solution as the game grows.

---

#### **Future Expansion and Customization**
- The game will be highly customizable in the future:
  - Players will eventually be able to create **custom elements**, modify recipes, or influence the rules of combination logic.
  - **Game Mode Customization**: Expand on game modes to offer more challenges, restrictions, or sandbox modes.
  
---

### **Final Specification Overview**

#### **Backend**:
- **Python** + **FastAPI** for handling API requests and database interactions.
- **SQLite** for initial database management, storing player data and recipes.
  
#### **Frontend**:
- **React** with **React Context API** for state management.
- **Framer Motion** for animations.
- **React DnD** for drag-and-drop functionality in the crafting area.
- **Tailwind CSS** for minimalistic and clean design.

#### **LLM Integration**:
- Query LLM for new combinations only when no pre-existing recipe exists in the database.
- Store LLM responses in the database for future reuse.

# Infinite Alchemist UI Specification

## Overall Layout
- Dark theme with black background (#000000) and white/gray text
- Stars or dots scattered across the background creating a space-like effect
- Main game area occupies the central space
- Fixed header at top
- Sidebar menu on the right
- Control icons at bottom

## Header (Top)
- Game title "Infinite Alchemist" positioned in top-right corner

## Main Game Area (Center)
- Interactive space showing element combinations
- Elements displayed as rounded rectangular buttons
- Each element button contains:
  - An emoji/icon on the left
  - Element name in white text
  - Dark, semi-transparent background
- Elements connected by thin white lines
- Elements can be dragged and dropped to combine

## Sidebar (Right)
- Fixed width panel containing all discovered elements
- Organized in a grid of element buttons
- Each button shows:
  - Element emoji/icon
  - Element name
  - Consistent styling with main game elements
- Categories include:
  - Basic elements (Water, Fire, Wind, Earth)
  - Natural phenomena (Rainbow, Storm, Rain)
  - Geographical features (Mountain, Lake, Ocean)
  - Living things (Fish, Dragon)
  - Locations (Hawaii, California, America)
  - And many more derived elements

## Bottom Control Bar
- Left side:
  - Reset button
- Right side:
  - Dark/Light mode toggle
  - Sound toggle
  - Volume control
  - Trash bin icon for deleting elements

## Search Function
- Search bar at bottom
- Shows total number of discoverable items (648 shown in screenshot)
- Placeholder text: "Search (648) items..."

## Additional Features
- "Discoveries" toggle button
- "Sort by time" option
- Dark/light mode functionality

## Element Button Styling
- Rounded corners (approximately 4-8px radius)
- Padding around text and icon
- Semi-transparent dark background
- Icon on left, text on right
- Hover effects (likely a subtle highlight)

## Typography
- Clean, sans-serif font family
- White text on dark backgrounds
- Consistent text size hierarchy:
  - Larger for header elements
  - Medium for element names
  - Smaller for UI controls and search

## Interactive Elements
- Draggable elements
- Clickable buttons
- Hover states on interactive elements
- Clear visual feedback for combinations

## Color Scheme
- Primary background: Black
- Text: White
- UI elements: Semi-transparent white/gray
- Interactive elements: Various colors for different element types
- Accent colors: Used sparingly for special elements or states

### **Implementation Plan**

#### **Phase 1: Initial Setup**
1. **Backend Setup**:
   - Set up a Python environment.
   - Install FastAPI and SQLite.
   - Create initial database schema for storing recipes and player data.

2. **Frontend Setup**:
   - Set up a React project.
   - Install necessary libraries: React Context API, Framer Motion, React DnD, Tailwind CSS.

3. **LLM Integration**:
   - Set up API endpoints in FastAPI for querying the LLM.
   - Implement logic to store and retrieve combinations from the database.

#### **Phase 2: Core Features Development**
1. **Core Gameplay Mechanics**:
   - Implement drag-and-drop functionality for combining elements.
   - Develop the logic for querying the database and LLM for new combinations.
   - Implement feedback animations for new discoveries.

2. **UI/UX Design**:
   - Design the Workbench and Library interfaces.
   - Implement the customization menu and feedback animations.

3. **State Management**:
   - Use React Context API to manage game state.
   - Implement LocalStorage for session persistence.

#### **Phase 3: Testing and Refinement**
1. **Testing**:
   - Conduct unit tests for backend API endpoints.
   - Perform integration tests for frontend and backend interactions.
   - User testing for UI/UX feedback.

2. **Refinement**:
   - Optimize database queries and LLM interactions.
   - Refine UI/UX based on user feedback.
   - Ensure smooth drag-and-drop functionality and animations.

#### **Phase 4: Deployment and Future Expansion**
1. **Deployment**:
   - Deploy the backend using a suitable hosting service.
   - Deploy the frontend using a static site hosting service.
   - Ensure database is properly configured for initial launch.

2. **Future Expansion**:
   - Plan for transitioning to a cloud-based database solution.
   - Implement more advanced customization options and game modes.
   - Continuously update the game based on player feedback and new feature requests.

### **Technology Stack and Library Versions**

#### **Backend**
- **Python**: 3.10+
- **FastAPI**: 0.104.0
- **Uvicorn**: 0.23.2 (ASGI server)
- **SQLite**: 3.42.0
- **SQLAlchemy**: 2.0.23 (ORM)
- **Pydantic**: 2.4.2 (data validation)
- **Python-dotenv**: 1.0.0 (environment variables)
- **Langchain**: 0.0.335 (for LLM abstraction)
- HF API

#### **Frontend**
- **Node.js**: 18.18.0+
- **React**: 18.2.0
- **Vite**: 4.5.0 (build tool)
- **React Router**: 6.18.0
- **React DnD**: 16.0.1 (drag and drop)
- **Framer Motion**: 10.16.4 (animations)
- **Tailwind CSS**: 3.3.5
- **Axios**: 1.6.0 (HTTP client)
- **Zustand**: 4.4.6 (state management)
- **i18next**: 23.6.0 (internationalization)
- **React-i18next**: 13.3.1 (React bindings for i18next)
- **Jest**: 29.7.0 (testing)
- **React Testing Library**: 14.1.0 (component testing)

# Backend Architecture Specification

## Overview

## Core Components

### 1. API Layer

The API layer serves as the interface between the frontend and the backend services. It is implemented using FastAPI, providing a RESTful API with the following characteristics:

- **OpenAPI Documentation**: Auto-generated API documentation
- **Request Validation**: Using Pydantic models
- **Authentication**: JWT-based authentication for future user accounts
- **CORS Support**: Configured for frontend access
- **Rate Limiting**: To prevent abuse of LLM services

#### Exposed Endpoints

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/elements` | GET | Get all elements with pagination | - | List of elements |
| `/api/elements/{element_id}` | GET | Get element by ID | - | Element details |
| `/api/elements/combine` | POST | Combine two elements | `{element1_id, element2_id, player_name}` | Combination result |
| `/api/elements/basic` | GET | Get all basic elements | - | List of basic elements |
| `/api/players/{player_name}` | GET | Get player profile | - | Player details |
| `/api/players/{player_name}/elements` | GET | Get elements discovered by player | - | List of elements |
| `/api/players/{player_name}/stats` | GET | Get player statistics | - | Player stats |
| `/api/discoveries` | GET | Get recent discoveries | - | List of discoveries |
| `/api/discoveries/{player_name}` | GET | Get discoveries by player | - | List of discoveries |
| `/api/settings` | GET | Get game settings | - | Game settings |

### 2. Service Layer

The service layer contains the business logic of the application, separated into distinct services with specific responsibilities:

#### LLM Service

The LLM Service is responsible for generating new elements through combinations. It is designed to be model-agnostic, supporting multiple LLM providers.

**Key Features:**
- **Provider Abstraction**: Common interface for different LLM providers
- **Prompt Management**: Templates for element generation in multiple languages
- **Response Parsing**: Extracting structured data from LLM responses
- **Caching**: Storing previous responses to reduce API calls
- **Fallback Mechanisms**: Handling service outages or rate limits

**Supported Providers:**
- OpenAI (GPT models)
- Hugging Face (Various models)
- Local models (future support)

#### Element Service

The Element Service manages the game's elements, their properties, and relationships.

**Key Features:**
- **Element CRUD**: Create, read, update, and delete elements
- **Element Relationships**: Managing parent-child relationships between elements
- **Element Search**: Finding elements by name, properties, or relationships
- **Element Validation**: Ensuring element data integrity

#### Combination Service

The Combination Service handles the logic of combining elements and determining the results.

**Key Features:**
- **Combination Processing**: Handling element combination requests
- **Result Determination**: Using the LLM service to generate new elements
- **Combination History**: Tracking previous combinations
- **Combination Rules**: Applying game rules to combinations

#### Player Service

The Player Service manages player data, progress, and statistics.

**Key Features:**
- **Player Profiles**: Managing player information
- **Progress Tracking**: Recording discovered elements
- **Statistics**: Calculating and updating player statistics
- **Settings Management**: Handling player preferences

#### Cache Service

The Cache Service provides caching capabilities to improve performance and reduce LLM API calls.

**Key Features:**
- **Response Caching**: Storing LLM responses
- **Cache Invalidation**: Managing cache lifecycle
- **Distributed Caching**: Supporting Redis for scalability
- **Cache Statistics**: Monitoring cache performance

### 3. Data Layer

The data layer is responsible for data persistence and retrieval, using SQLAlchemy as the ORM with SQLite as the database.

#### Database Schema

**Elements Table**
```
elements
├── id (PK)
├── name (Unique)
├── emoji
├── is_basic (Boolean)
├── created_at (DateTime)
└── created_by (String, nullable)
```

**Element Combinations Table**
```
element_combinations
├── element1_id (PK, FK -> elements.id)
├── element2_id (PK, FK -> elements.id)
├── result_id (PK, FK -> elements.id)
├── created_at (DateTime)
└── discovered_by (String, nullable)
```

**Player Elements Table**
```
player_elements
├── player_name (PK)
├── element_id (PK, FK -> elements.id)
└── unlocked_at (DateTime)
```

**Player Stats Table**
```
player_stats
├── id (PK)
├── player_name (Unique)
├── elements_discovered (Integer)
├── elements_unlocked (Integer)
├── combinations_tried (Integer)
├── successful_combinations (Integer)
├── failed_combinations (Integer)
├── last_active (DateTime)
└── created_at (DateTime)
```

**Discovery History Table**
```
discovery_history
├── id (PK)
├── element_id (FK -> elements.id)
├── player_name (String)
├── discovered_at (DateTime)
└── is_first_discovery (Boolean)
```

#### Data Access Layer

The data access layer provides an abstraction over the database operations:

- **Repositories**: Classes that handle database operations for specific entities
- **Unit of Work**: Managing transaction boundaries
- **Query Objects**: Encapsulating complex queries
- **Data Mappers**: Converting between database models and domain objects

### 4. Core Layer

The core layer contains application-wide utilities and configurations:

- **Configuration Management**: Loading and validating configuration
- **Logging**: Centralized logging setup
- **Error Handling**: Global exception handling
- **Security**: Authentication and authorization utilities
- **Internationalization**: Language support utilities

## Cross-Cutting Concerns

### Caching Strategy

The caching strategy is designed to minimize LLM API calls and improve response times:

1. **LLM Response Caching**:
   - Cache key: Combination of element IDs and language
   - Cache duration: Indefinite (permanent recipes)
   - Cache backend: Redis (primary), in-memory (fallback)

2. **Element Data Caching**:
   - Cache key: Element ID or name
   - Cache duration: Short-term (minutes)
   - Cache backend: In-memory

3. **Player Data Caching**:
   - Cache key: Player name
   - Cache duration: Medium-term (hours)
   - Cache backend: Redis

### Error Handling

The error handling strategy ensures robust operation and meaningful feedback:

1. **API Errors**:
   - Standardized error responses with HTTP status codes
   - Detailed error messages for debugging
   - Client-friendly error messages for production

2. **LLM Service Errors**:
   - Retry mechanism for transient errors
   - Fallback to alternative providers
   - Graceful degradation when services are unavailable

3. **Database Errors**:
   - Transaction rollback on failure
   - Connection retry for transient errors
   - Data validation before persistence

### Internationalization

The internationalization strategy supports multiple languages:

1. **LLM Prompts**:
   - Language-specific prompt templates
   - Cultural context awareness
   - Consistent terminology across languages

2. **API Responses**:
   - Language parameter for text-based responses
   - Consistent data structure across languages
   - Default language fallback

3. **Error Messages**:
   - Translated error messages
   - Language-specific validation messages
   - Cultural sensitivity in messaging

## Data Flow

### Element Combination Flow

1. **Frontend Request**:
   - User combines two elements
   - Frontend sends element IDs and player name to `/api/elements/combine`

2. **API Layer**:
   - Validates request data
   - Passes data to Combination Service

3. **Combination Service**:
   - Checks if combination exists in database
   - If exists, returns cached result
   - If not, requests new combination from LLM Service

4. **LLM Service**:
   - Checks cache for previous identical request
   - If cached, returns cached response
   - If not cached:
     - Retrieves element details
     - Constructs prompt with element information
     - Sends prompt to LLM provider
     - Parses response to extract new element
     - Caches response for future requests

5. **Combination Service (continued)**:
   - Creates new element in database if needed
   - Records combination in database
   - Updates player statistics
   - Records discovery history

6. **API Layer (response)**:
   - Formats response with combination result
   - Includes flags for new discovery and first discovery
   - Returns response to frontend

### Player Progress Flow

1. **Frontend Request**:
   - Frontend requests player elements from `/api/players/{player_name}/elements`

2. **API Layer**:
   - Validates player name
   - Passes request to Player Service

3. **Player Service**:
   - Retrieves player profile
   - If player doesn't exist, creates new profile
   - Retrieves player's discovered elements

4. **API Layer (response)**:
   - Formats response with player elements
   - Returns response to frontend

## Future Expansion

The architecture is designed to support future expansion:

1. **User Authentication**:
   - JWT-based authentication
   - User registration and login
   - Social authentication

2. **Multiplayer Features**:
   - Real-time updates via WebSockets
   - Collaborative discovery
   - Leaderboards and achievements

3. **Advanced Game Modes**:
   - Custom starting elements
   - Challenge modes
   - Time-limited modes
