# Infinite Alchemist - Backend

This is the backend for the Infinite Alchemist game, a creative element combination game powered by LLMs.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables by copying `.env.example` to `.env` and filling in the required values:
```bash
cp .env.example .env
```

5. Initialize the database:
```bash
python -m app.db.init_db
```

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

### API Usage

When using the API, always specify the language parameter:

```
POST /api/elements/combine
{
    "element1_id": 1,
    "element2_id": 2,
    "player_name": "player123",
    "lang": "en"  // or "ru" for Russian
}
```

## LLM Service

The LLM service is responsible for handling element combinations using a language model. It supports both OpenAI and Hugging Face models, with Hugging Face being the default.

### Environment Variables

The following environment variables are used by the LLM service:

- `LLM_PROVIDER`: The LLM provider to use (default: "huggingface")
- `OPENAI_API_KEY`: The OpenAI API key (required if using OpenAI)
- `LLM_API_KEY`: The Hugging Face API key (required if using Hugging Face)
- `LLM_MODEL`: The Hugging Face model name (default: "lightblue/suzume-llama-3-8B-multilingual")
- `REDIS_URL`: The Redis URL for caching (optional)

## Using the Prompt Tester

The prompt tester is a tool for testing different prompts with the LLM service. It helps you find the most effective prompt for element combinations.

### Running the Prompt Tester

To run the prompt tester:

```bash
python -m app.scripts.test_prompts
```

This will test all available prompts with a set of predefined element combinations and print the results.

### How the Prompt Tester Works

1. The prompt tester loads all available prompts from the `app/prompts` directory.
2. It tests each prompt with a set of predefined element combinations.
3. It evaluates the results based on success rate, errors, and invalid JSON responses.
4. It prints the results and saves detailed results to a JSON file.


### Adding Test Cases

You can add custom test cases to the prompt tester by modifying the `test_cases` list in the `PromptTester` class:

```python
self.test_cases = [
    # Basic combinations
    ("Water", "Fire", "Steam"),
    ("Earth", "Fire", "Lava"),
    ("Water", "Earth", "Mud"),
    ("Fire", "Air", "Smoke"),
    
    # More complex combinations
    ("Gold", "Silver", "Alloy"),
    ("Tree", "Axe", "Wood"),
    ("Flour", "Water", "Dough"),
    ("Dough", "Fire", "Bread"),
    
    # Abstract combinations
    ("Knowledge", "Power", "Wisdom"),
    ("Time", "Money", "Efficiency"),
    
    # Nonsensical combinations that should be handled gracefully
    ("Nonsense", "Gibberish", None),
    ("12345", "67890", None),
    ("", "", None),
]
```

Each test case is a tuple of `(element1, element2, expected_result)`. If `expected_result` is `None`, the combination is expected to be invalid.

## Running Tests

To test the LLM service with refusals:

```bash
python -m app.scripts.test_refusals
```

To test the game API with a mock LLM service:

```bash
python -m app.scripts.test_game_api
``` 