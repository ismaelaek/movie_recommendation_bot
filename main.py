import requests
import random
import telebot 
from telebot import types
from decouple import config
import os

# the following variables are stored in a ".env " file 
api_key = config('api_key')
bot_username = config('bot_username')
bot_token = config('bot_token')
email = config('email')
owner_name = config('owner_name')
GitHub = config('GitHub')

# get all availables genres and store thme in a variable later 
def get_all_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}"
    response = requests.get(url)
    data = response.json()
    genres = {genre['name'] : genre['id'] for genre in data['genres']}
    return genres

all_genres = get_all_genres()
# set a mood for each genre 
# it's much easier to make only one dictionnary
moods = [
    {"Excited": "Action"},
    {"Thrilled": "Adventure"},
    {"Enchanting": "Animation"},
    {"Hilarious": "Comedy"},
    {"Intrigued": "Crime"},
    {"Enlightened": "Documentary"},
    {"Thoughtful": "Drama"},
    {"Joyful": "Family"},
    {"Imaginative": "Fantasy"},
    {"Fascinated": "History"},
    {"Scared": "Horror"},
    {"Melodious": "Music"},
    {"Curious": "Mystery"},
    {"Romantic": "Romance"},
    {"Wondrous": "Science Fiction"},
    {"Entertained": "TV Movie"},
    {"Intense": "Thriller"},
    {"Heroic": "War"},
    {"Adventurous": "Western"}
]

###############
# handle commands 

bot = telebot.TeleBot(bot_token)
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome to Movie Recommaneder bot \n\n /help for help ")

@bot.message_handler(commands=['help'])
def start(message):
    help_content = "send or press /mood to choose your current mood \nsend or press /contact to contact the owner"
    bot.send_message(message.chat.id, help_content)

@bot.message_handler(commands=['contact'])
def handle_contact(message):
    info = f"""
        Owner Name  -  {owner_name}
        Email       -  {email} 
        GitHub Profile       -  {GitHub} 
    """
    bot.send_message(chat_id=message.chat.id, text=info)

@bot.message_handler(commands=['mood'])
def Choose_Mode(message):
    # Create a menu keyboard
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    
    # Add buttons for each mood
    for mood in moods:
        Current_Mood = list(mood.keys())[0]
        Selected_Genre = mood[Current_Mood]
        button = types.InlineKeyboardButton(text=Current_Mood, callback_data=Selected_Genre)
        keyboard.add(button)
    
    # Send the menu message
    bot.send_message(chat_id=message.chat.id, text="Choose your mood :", reply_markup=keyboard)

# Handle button clicks
@bot.callback_query_handler(func=lambda call: True)
def button_click(call):
    
    Selected_Genre = call.data.strip()
    bot.send_message(chat_id=call.message.chat.id, text=f"we have chosen {Selected_Genre} movies/series for your current mood !")
    
    # get id of selectedd genre 
    Genre_id = all_genres.get(Selected_Genre)
    
    # make a request to TMDb to return movies depends on chosen mood
    if Genre_id:
        response = requests.get(f'https://api.themoviedb.org/3/discover/movie', params={
            'api_key': {api_key},
            'with_genres': {Genre_id},
            'sort_by': 'popularity.desc',
            'page': 1
        }).json()
        movies = response['results']
        sorted_movies = sorted(movies, key=lambda x: x['popularity'], reverse=True)
        
        # make a list of top 15 movie and choose a randam one 
        top_movies = sorted_movies[:15]
        random_movie = random.choice(top_movies)
        
        # extarcting selected movie's info
        title = random_movie['title']
        poster_path = random_movie['poster_path']
        description = random_movie['overview']
        rating = random_movie['vote_average']
        story = random_movie['tagline'] if 'tagline' in random_movie else 'N/A'
        imgurl='https://image.tmdb.org/t/p/original' + poster_path
        
        # I have a problem sending photo by url so I had to make the program download the poster and send it then delete it 
        photo_data = requests.get(imgurl)
        photo_filename = 'photo.jpg'
        with open(photo_filename, 'wb') as photo_file:
            photo_file.write(photo_data.content)

        with open(photo_filename, 'rb') as photo_file:
            bot.send_photo(chat_id=call.message.chat.id, photo=photo_file)

        # Delete the downloaded photo file
        os.remove(photo_filename)
        
        caption=f'{title}\n\nRating: {rating}\n\nDescription: {description}\n\nStory: {story}'
        bot.send_message(chat_id=call.message.chat.id, text=caption)

# start the bot 
bot.polling()
