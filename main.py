import requests
import random
import telebot
from telebot import types
from decouple import config
from googletrans import Translator
import time

# Load environment variables
api_key = config("API_KEY")
bot_token = config("BOT_TOKEN")
bot = telebot.TeleBot(bot_token)
email = config('EMAIL')
owner_name = config('OWNER_NAME')
github = config('GITHUB')


# Retry decorator for robust error handling
def retry_on_exception(func):
    def wrapper(*args, **kwargs):
        retries = 5
        while retries > 0:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                retries -= 1
                print(f"Network error: {e}. Retrying... {retries} retries left.")
                time.sleep(2)  # Wait before retrying
            except Exception as e:
                print(f"Unexpected error: {e}. Exiting.")
                break
        return None

    return wrapper


# Function to fetch all genres with retry logic
@retry_on_exception
def get_all_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return {genre["name"]: genre["id"] for genre in data["genres"]}


# Handle commands
@bot.message_handler(commands=["start"])
def start(message):
    start_message = """
🎥 **Welcome to the Ultimate Movie Recommender Bot!** 🎬  
Your personal guide to discovering amazing movies tailored to your mood! 🌟  

✨ **Available Commands:**  
- /start - Get started with the bot
- /mood - Choose your current mood for personalized recommendations  
- /contact - Get in touch with the bot's creator  

💡 **Exciting News:**  
🔗 **Free direct links to watch movies are coming soon!** Stay tuned for this awesome feature. 🎉  

🎭 **Let the movie magic begin!**  
    """
    bot.send_message(message.chat.id, start_message, parse_mode="Markdown")


@bot.message_handler(commands=["mood"])
def choose_mood(message):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    moods = {
        "🎢 Excited": "Adventure",
        "🚀 Thrilled": "Science Fiction",
        "🪄 Enchanting": "Fantasy",
        "😂 Hilarious": "Comedy",
        "🕵️ Intrigued": "Mystery",
        "📚 Enlightened": "Documentary",
        "🤔 Thoughtful": "Drama",
        "👨‍👩‍👧 Joyful": "Family",
        "🎨 Imaginative": "Animation",
        "🏰 Fascinated": "History",
        "😨 Scared": "Comedy",
        "🎵 Melodious": "Music",
        "🔍 Curious": "Documentary",
        "❤️ Romantic": "Romance",
        "🌌 Wondrous": "Fantasy",
        "🔥 Entertained": "Action",
        "🌟 Intense": "Drama",
        "🛡️ Heroic": "War",
        "🏜️ Adventurous": "Western",
        "😢 Sad": "Comedy",
    }

    buttons = [types.InlineKeyboardButton(text=mood, callback_data=genre) for mood, genre in moods.items()]
    keyboard.add(*buttons)

    bot.send_message(
        message.chat.id,
        "🎭 Choose your current mood:",
        reply_markup=keyboard,
    )


# Contact command
@bot.message_handler(commands=['contact'])
def contact_info(message):
    bot.send_message(
        message.chat.id,
        f"👤 **Owner Information:**\n\n"
        f"👨‍💻 Name: `{owner_name}`\n"
        f"📧 Email: `{email}`\n"
        f"🔗 GitHub: [View Profile]({github})\n\n"
        f"☕ **Enjoying the bot?**\n"
        f"Show your support by buying me a coffee! Your support helps me keep improving this bot and building more cool projects. Every coffee counts! \n"
        f"[Buy Me a Coffee](https://buymeacoffee.com/ismail_aek)\n",
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: True)
@retry_on_exception
def handle_callback(call):
    genre = call.data
    bot.send_message(call.message.chat.id, f"You selected {genre}. Fetching recommendations...")

    genre_id = get_all_genres().get(genre, None)
    if not genre_id:
        bot.send_message(call.message.chat.id, "Sorry, no movies found for this genre.")
        return

    # Fetch movies for the genre
    url = f"https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "with_genres": genre_id,
        "sort_by": "popularity.desc",
        "page": 1,
    }
    response = requests.get(url, params=params).json()
    movies = response.get("results", [])
    if not movies:
        bot.send_message(call.message.chat.id, "No popular movies found in this genre. Try another mood!")
        return

    # Select a random movie and send the details
    random_movie = random.choice(movies)
    movie_id = random_movie["id"]
    title = random_movie["title"]
    overview = random_movie["overview"]
    rating = random_movie["vote_average"]
    poster_path = random_movie["poster_path"]
    img_url = f"https://image.tmdb.org/t/p/original{poster_path}"

    translator = Translator()
    arabic_overview = translator.translate(overview, src='en', dest='ar').text

    # Fetch trailer from TMDb
    trailer_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}"
    trailer_response = requests.get(trailer_url).json()
    trailer_key = None
    for video in trailer_response.get("results", []):
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            trailer_key = video["key"]
            break

    # Construct caption
    caption = (
        f"🎥 **{title}**\n\n"
        f"⭐️ Rating: `{rating}`\n\n"
        f"📝 Overview:\n{overview}\n\n"
        f"🇲🇦 Arabic:\n{arabic_overview}\n\n"
        f"📖 More Details: [View details](https://www.themoviedb.org/movie/{movie_id})\n\n"
    )

    # Create an inline keyboard with a "Watch Trailer" button (if available)
    keyboard = types.InlineKeyboardMarkup()
    if trailer_key:
        youtube_link = f"https://www.youtube.com/watch?v={trailer_key}"
        keyboard.add(types.InlineKeyboardButton("🎥 Watch Trailer", url=youtube_link))
    else:
        caption += "🚫 Trailer not available.\n\n"

    bot.send_photo(call.message.chat.id, img_url, caption=caption, parse_mode="Markdown", reply_markup=keyboard)


# Start polling with error handling
while True:
    try:
        print("Bot is running...")
        bot.polling(non_stop=True)
    except requests.exceptions.ReadTimeout:
        print("Timeout error. Retrying...")
        time.sleep(5)
    except Exception as e:
        print(f"Unexpected error: {e}. Retrying in 5 seconds...")
        time.sleep(5)
