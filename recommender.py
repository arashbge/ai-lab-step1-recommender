"""
سیستم پیشنهاددهنده فیلم با قابلیت به‌روزرسانی محیط (چالش کثیفی مجدد / تغییر در طول زمان)
ایده برگرفته از تمرین کلاسی (ربات جاروبرقی) و توسعه‌یافته برای پروژه پیشنهاد فیلم.
"""

import pandas as pd

class MovieRecommender:
    """سیستم پیشنهاددهنده ساده با قابلیت تطبیق با تغییرات محیط (سلیقه کاربر و فیلم‌های جدید)"""

    def __init__(self, ratings_df, movies_df):
        self.ratings = ratings_df
        self.movies = movies_df

    def get_popular_movies(self, top_k=5):
        """پیشنهاد پرطرفدارترین فیلم‌ها (برای حل مشکل Cold Start)"""
        if self.ratings.empty:
            return self.movies.head(top_k)
            
        popular_movies = (
            self.ratings.groupby("movieId")["rating"]
            .mean()
            .sort_values(ascending=False)
            .head(top_k)
            .index
        )
        return self.movies[self.movies["movieId"].isin(popular_movies)]

    def recommend_for_user(self, user_id, top_k=5):
        """پیشنهاد فیلم به کاربر بر اساس سلیقه فعلی او"""
        if user_id not in self.ratings["userId"].values:
            return self.get_popular_movies(top_k)

        user_ratings = self.ratings[self.ratings["userId"] == user_id]
        liked_movies = user_ratings[user_ratings["rating"] >= 4]["movieId"]

        liked_genres = self.movies[self.movies["movieId"].isin(liked_movies)]["genres"].str.split("|")
        genre_counts = pd.Series([g for sublist in liked_genres for g in sublist]).value_counts()
        
        if len(genre_counts) == 0:
            return self.get_popular_movies(top_k)

        favorite_genre = genre_counts.index[0]

        candidates = self.movies[
            self.movies["genres"].str.contains(favorite_genre, na=False)
            & ~self.movies["movieId"].isin(liked_movies)
        ]
        return candidates.head(top_k)

    # ---------------------------------------------------------
    # بخش جدید: پیاده‌سازی چالش «کثیفی مجدد محیط» (تغییر در طول زمان)
    # ---------------------------------------------------------
    def simulate_time_passing(self, user_id, new_rating_movie_id, new_rating_value):
        """
        شبیه‌سازی گذر زمان: کاربر یک فیلم جدید می‌بیند و به آن امتیاز می‌دهد.
        این کار باعث می‌شود سلیقه کاربر تغییر کند (محیط کثیف/تغییر یافته شود).
        """
        new_row = pd.DataFrame({
            'userId': [user_id], 
            'movieId': [new_rating_movie_id], 
            'rating': [new_rating_value]
        })
        # به‌روزرسانی دیتابیس امتیازها (تغییر محیط)
        self.ratings = pd.concat([self.ratings, new_row], ignore_index=True)
        print(f"محیط تغییر کرد: کاربر {user_id} به فیلم {new_rating_movie_id} امتیاز {new_rating_value} داد.")
        
        # حالا سیستم باید پیشنهادهای جدید بده
        return self.recommend_for_user(user_id)

    def add_new_movie(self, movie_id, title, genres):
        """
        شبیه‌سازی اضافه شدن فیلم جدید به کاتالوگ (تغییر محیط)
        """
        new_movie = pd.DataFrame({
            'movieId': [movie_id], 
            'title': [title], 
            'genres': [genres]
        })
        self.movies = pd.concat([self.movies, new_movie], ignore_index=True)
        print(f"محیط تغییر کرد: فیلم جدید '{title}' به سیستم اضافه شد.")
