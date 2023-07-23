# Telegram Bot for Movies Recommendation

The Telegram bot is a movie recommendation bot that suggests movies or TV series based on the user's current mood. The bot utilizes the Telegram API and interacts with the user using commands and inline keyboard buttons. It also communicates with The Movie Database (TMDb) API to retrieve information about movies and genres.

## Key Features:

1. **Commands Handling:** The bot responds to specific commands, such as `/start`, `/help`, `/contact`, and `/mood`. `/start` greets the user, `/help` provides information on how to use the bot, `/contact` displays the bot owner's contact details, and `/mood` allows the user to choose their current mood to get movie recommendations accordingly.

2. **Mood Selection:** When the user sends or presses `/mood`, the bot presents a menu keyboard with various mood options. Each mood corresponds to a movie genre, and the user can choose their mood by clicking on the respective button.

3. **Genre-based Movie Recommendations:** After the user selects a mood, the bot makes a request to TMDb to retrieve a list of movies related to the chosen genre. It sorts the movies by popularity and selects a random movie from the top 15 results.

4. **Movie Information:** The bot fetches movie details, including title, poster, description, rating, and story. It sends the movie poster as a photo to the user, followed by the movie details as a caption.

5. **Security Considerations:** The bot uses environment variables stored in a `.env` file to protect sensitive data such as the TMDb API key and bot token. The `.env` file is excluded from version control to prevent accidental exposure.

## Required Libraries:

- `requests`: To make HTTP requests to the TMDb API.
- `random`: For generating random movie selections.
- `telebot`: A library for interacting with the Telegram Bot API.
- `decouple`: For working with environment variables.
- `os`: For handling file operations.
- `from telebot import types`: To use inline keyboards for mood selection.

## How it Works:

The bot starts by handling various commands, such as `/start`, `/help`, and `/contact`. When the user sends or presses `/mood`, the bot displays a menu with mood options, where each mood corresponds to a movie genre. The user can choose a mood, and the bot fetches movie recommendations from TMDb based on the selected genre. It then selects a random movie from the top 15 results and sends the movie poster as a photo to the user. The movie details, including title, description, rating, and story, are sent as a caption with the photo.

The bot securely manages sensitive data, such as API keys and tokens, using environment variables stored in the `.env` file. This file is excluded from version control to prevent accidental exposure of sensitive information.
