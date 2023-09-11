The Python script can be optimized in the following ways:

1. Import only the necessary functions and modules from nltk instead of importing the entire nltk module.
  ```python
   from nltk.corpus import stopwords, wordnet
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    ```

2. Use list comprehensions instead of for loops to preprocess the content in the NewsArticle class .
  ```python

   def preprocess_content(self):
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        tokens = word_tokenize(self.content.lower())
        tokens = [lemmatizer.lemmatize(token)
                  for token in tokens if token.isalpha()]
        tokens = [token for token in tokens if token not in stop_words]
        self.content = ' '.join(tokens)
    ```

3. Use a dictionary comprehension instead of a for loop to create the user profile in the NewsRecommendationSystem class .
  ```python

   def create_user_profile(self, categories):
        self.user_profile = {'preferred_categories': categories}
    ```

4. Use a generator expression instead of a list comprehension when calculating the TF-IDF matrix in the recommend_news_articles() method.
  ```python
   content = (article.content for article in self.news_articles)
    tfidf_matrix = tfidf_vectorizer.fit_transform(content)
    ```

5. Use a lambda function instead of a lambda expression in the articles_scores.sort() method call.
  ```python
   articles_scores.sort(key=lambda x: x[1], reverse=True)
    ```

6. Move the database connection and creation to a separate method that is called before running the Flask app.
  ```python

   def connect_to_database():
        recommendation_system.scrape_news_articles()
        app.run(debug=True)

    if __name__ == '__main__':
        database.create_tables()
        connect_to_database()
    ```

Note: These optimizations are specific to the provided code snippet and may not apply to other parts of the codebase. Additional optimizations may be possible depending on the specific requirements and context of the code.
