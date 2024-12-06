import requests
import random
import telebot 
from telebot import types
from decouple import config
from googletrans import Translator
import os

translator = Translator()

# the following variables are stored in a ".env " file 
api_key = config('API_KEY')
bot_username = config('BOT_USERNAME')
bot_token = config('BOT_TOKEN')
email = config('EMAIL')
owner_name = config('OWNER_NAME')
GitHub = config('GITHUB')

# get all available genres and store them in a variable later
def get_all_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}"
    response = requests.get(url)
    data = response.json()
    genres = {genre['name'] : genre['id'] for genre in data['genres']}
    return genres

all_genres = get_all_genres()
# set a mood for each genre 
# it's much easier to make only one dictionary
moods = [
    {"Excited": "Adventure"},
    {"Thrilled": "Science Fiction"},
    {"Enchanting": "Fantasy"},
    {"Hilarious": "Comedy"},
    {"Intrigued": "Mystery"},
    {"Enlightened": "Documentary"},
    {"Thoughtful": "Drama"},
    {"Joyful": "Family"},
    {"Imaginative": "Animation"},
    {"Fascinated": "History"},
    {"Scared": "Comedy"},
    {"Melodious": "Music"},
    {"Curious": "Documentary"},
    {"Romantic": "Romance"},
    {"Wondrous": "Fantasy"},
    {"Entertained": "Action"},
    {"Intense": "Drama"},
    {"Heroic": "War"},
    {"Adventurous": "Western"},
    {"Sad": "Comedy"}
]

###############
# handle commands 

bot = telebot.TeleBot(bot_token)
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome to Movie Recommender bot \n\n /help for help ")

@bot.message_handler(commands=['help'])
def start(message):
    help_content = "send or press /mood to choose your current mood \nsend or press /contact to contact the owner"
    bot.send_message(message.chat.id, help_content)

@bot.message_handler(commands=['contact'])
def handle_contact(message):
    info = f"""
Name: {owner_name}
Email: {email} 
GitHub: {GitHub} 
    """
    bot.send_message(chat_id=message.chat.id, text=info)

@bot.message_handler(commands=['mood'])
def choose_mood(message):
    # Create a menu keyboard
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    
    # Add buttons for each mood
    for mood in moods:
        current_mood = list(mood.keys())[0]
        selected_genre = mood[current_mood]
        button = types.InlineKeyboardButton(text=current_mood, callback_data=selected_genre)
        keyboard.add(button)
    
    # Send the menu message
    bot.send_message(chat_id=message.chat.id, text="Choose your mood :", reply_markup=keyboard)

# Handle button clicks
@bot.callback_query_handler(func=lambda call: True)
def button_click(call):
    
    selected_genre = call.data.strip()
    bot.send_message(chat_id=call.message.chat.id, text=f"we have chosen {selected_genre} movies/series for your current mood !")
    
    # get id of selected genre
    genre_id = all_genres.get(selected_genre)
    
    # make a request to TMDb to return movies depends on chosen mood
    if genre_id:
        response = requests.get(f'https://api.themoviedb.org/3/discover/movie', params={
            'api_key': {api_key},
            'with_genres': {genre_id},
            'sort_by': 'popularity.desc',
            'page': 1
        }).json()
        movies = response['results']
        sorted_movies = sorted(movies, key=lambda x: x['popularity'], reverse=True)
        
        # make a list of top 20 movie and choose a random one
        top_movies = sorted_movies[:20]
        print(top_movies)
        random_movie = random.choice(top_movies)

        # extracting selected movie's info
        title = random_movie['title']
        poster_path = random_movie['poster_path']
        overview = random_movie['overview']
        arabic_overview = translator.translate(overview, src='en', dest='ar')
        rating = random_movie['vote_average']
        img_url='https://image.tmdb.org/t/p/original' + poster_path
        
        # I have a problem sending photo by url, so I had to make the program download the poster and send it then delete it
        photo_data = requests.get(img_url)
        photo_filename = 'photo.jpg'
        with open(photo_filename, 'wb') as photo_file:
            photo_file.write(photo_data.content)

        with open(photo_filename, 'rb') as photo_file:
            bot.send_photo(chat_id=call.message.chat.id, photo=photo_file)

        # Delete the downloaded photo file
        os.remove(photo_filename)
        
        caption=f' **{title}** \n\nRating: {rating}\n\nOverview: {overview}\n\nبالعربية: {arabic_overview.text}'
        bot.send_message(chat_id=call.message.chat.id, text=caption)

# start the bot 
bot.polling()
