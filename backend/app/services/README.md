# LLM Service for Infinite Alchemist

This directory contains the services used by the Infinite Alchemist game, including the LLM service for element combinations.

## LLM Service

The `llm_service.py` file contains the `LLMService` class, which is responsible for handling element combinations using a language model. The service supports both OpenAI and Hugging Face models, with Hugging Face being the default.

### Features

- Support for both OpenAI and Hugging Face models
- Robust prompt template with rules for valid and invalid combinations
- JSON response handling with clear formats for both valid and invalid combinations
- Caching mechanism using Redis and in-memory caching
- Proper handling of refusals for nonsensical combinations

### Environment Variables

The following environment variables are used by the LLM service:

- `LLM_PROVIDER`: The LLM provider to use (default: "huggingface")
- `OPENAI_API_KEY`: The OpenAI API key (required if using OpenAI)
- `OPENAI_MODEL_NAME`: The OpenAI model name (default: "gpt-3.5-turbo")
- `HUGGINGFACE_ENDPOINT_URL`: The Hugging Face endpoint URL (required if using Hugging Face)
- `HUGGINGFACE_API_TOKEN`: The Hugging Face API token (optional)
- `LLM_TEMPERATURE`: The temperature parameter for the LLM (default: 0.7)
- `LLM_MAX_NEW_TOKENS`: The maximum number of new tokens for the LLM (default: 512)
- `REDIS_URL`: The Redis URL for caching (optional)

### Response Format

The LLM service returns responses in the following format:

For valid combinations:
```json
{
  "valid": true,
  "result": "New Element Name",
  "emoji": "🔥"
}
```

For invalid combinations:
```json
{
  "valid": false,
  "reason": "Brief explanation of why this combination is impossible"
}
```

## Testing

The following test scripts are available for testing the LLM service:

- `test_refusals.py`: Tests the LLM's ability to refuse nonsensical combinations
- `test_game_api.py`: Tests the game API with a mock LLM service

To run the tests, use the following commands:

```bash
python -m app.scripts.test_refusals
python -m app.scripts.test_game_api
```

## Rules for Valid Combinations

The LLM service uses the following rules to determine if a combination is valid:

1. Elements can ONLY be combined if they have a logical relationship.
2. Physical elements (like Water, Fire, Earth) can be combined with other physical elements.
3. Abstract concepts (like Love, Democracy, Philosophy) CANNOT be combined with physical elements.
4. Elements from completely different domains with no connection CANNOT be combined.
5. Combinations that violate the laws of physics or common sense are NOT allowed. 