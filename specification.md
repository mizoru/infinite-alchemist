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
   - **Design**: Clean, minimalistic interface with a subtle background pattern to keep focus on the elements.

2. **Library ("Discovered Elements")**:
   - Displays all discovered elements with draggable icons.
   - **Search** function for quickly locating elements.
   - **Sort options**:
     - Alphabetical order.
     - By time discovered (newest first or oldest first).

3. **Customization Menu**:
   - **Nickname input**: Players can enter a nickname, stored locally (no login required).
   - **Language selection**: Choose interface language at the start or via the settings menu.
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
