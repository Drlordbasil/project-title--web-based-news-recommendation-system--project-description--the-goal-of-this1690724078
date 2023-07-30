import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
from flask import Flask, render_template, request

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class NewsArticle:
    def __init__(self, title, author, date, content):
        self.title = title
        self.author = author
        self.date = date
        self.content = content

    def preprocess_content(self):
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        tokens = word_tokenize(self.content.lower())
        tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalpha()]
        tokens = [token for token in tokens if token not in stop_words]
        self.content = ' '.join(tokens)


class NewsRecommendationSystem:
    def __init__(self, url):
        self.url = url
        self.news_articles = []
        self.user_profile = None
        self.conn = None

    def scrape_news_articles(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('article')
        for article in articles:
            title = article.find('h2').text.strip()
            author = article.find('span', class_='author').text.strip()
            date = article.find('time').text.strip()
            content = article.find('div', class_='content').text.strip()
            news_article = NewsArticle(title, author, date, content)
            news_article.preprocess_content()
            self.news_articles.append(news_article)

    def create_user_profile(self, categories):
        self.user_profile = {'preferred_categories': categories}

    def recommend_news_articles(self):
        tfidf_vectorizer = TfidfVectorizer()
        content = [article.content for article in self.news_articles]
        tfidf_matrix = tfidf_vectorizer.fit_transform(content)
        user_profile_text = ' '.join(self.user_profile['preferred_categories'])
        user_profile_vector = tfidf_vectorizer.transform([user_profile_text])
        similarities = cosine_similarity(user_profile_vector, tfidf_matrix)
        similarities = similarities.flatten()
        articles_scores = [(article, score) for article, score in zip(self.news_articles, similarities)]
        articles_scores.sort(key=lambda x: x[1], reverse=True)
        return articles_scores


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('news_recommendations.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                preferred_categories TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                date TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def insert_user(self, name, preferred_categories):
        self.cursor.execute('INSERT INTO users (name, preferred_categories) VALUES (?, ?)', (name, preferred_categories))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_article(self, title, author, date, content):
        self.cursor.execute('INSERT INTO articles (title, author, date, content) VALUES (?, ?, ?, ?)',
                            (title, author, date, content))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()


app = Flask(__name__)
recommendation_system = NewsRecommendationSystem('https://www.example.com/news')
database = Database()


@app.route('/')
def index():
    users = database.get_users()
    return render_template('index.html', users=users)


@app.route('/recommendations', methods=['POST'])
def recommendations():
    user_name = request.form['user_name']
    user_categories = request.form.getlist('categories')
    user_id = database.insert_user(user_name, ','.join(user_categories))
    users = database.get_users()
    recommendation_system.create_user_profile(user_categories)
    recommended_articles = recommendation_system.recommend_news_articles()
    return render_template('recommendations.html', users=users, recommended_articles=recommended_articles)


if __name__ == '__main__':
    recommendation_system.scrape_news_articles()
    app.run(debug=True)