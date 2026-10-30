"""
سیستم پیشنهاددهنده فیلم (نسخه بهبودیافته)
این کد بر اساس ساختار کلاسی اولیه بهبود یافته و برای موضوع پروژه (پیشنهاد فیلم) تنظیم شده است.
"""

import pandas as pd

class MovieRecommender:
    """یک سیستم پیشنهاددهنده ساده مبتنی بر محبوبیت و ژانرهای مورد علاقه کاربر."""

    def __init__(self, ratings_df, movies_df):
        """
        مقداردهی اولیه سیستم با داده‌های کاربران و فیلم‌ها
        ratings_df: دیتافریم شامل ستون‌های (userId, movieId, rating)
        movies_df: دیتافریم شامل ستون‌های (movieId, title, genres)
        """
        self.ratings = ratings_df
        self.movies = movies_df

    def get_popular_movies(self, top_k=5):
        """پیشنهاد پرطرفدارترین فیلم‌ها (برای حل مشکل کاربران جدید یا Cold Start)"""
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
        """پیشنهاد فیلم به یک کاربر خاص بر اساس سلیقه قبلی او"""
        # بررسی اینکه آیا کاربر جدید است یا خیر (Cold Start)
        if user_id not in self.ratings["userId"].values:
            return self.get_popular_movies(top_k)

        # پیدا کردن فیلم‌هایی که کاربر به آن‌ها امتیاز خوب (۴ یا ۵) داده است
        user_ratings = self.ratings[self.ratings["userId"] == user_id]
        liked_movies = user_ratings[user_ratings["rating"] >= 4]["movieId"]

        # استخراج ژانرهای مورد علاقه کاربر
        liked_genres = self.movies[self.movies["movieId"].isin(liked_movies)]["genres"].str.split("|")
        genre_counts = pd.Series([g for sublist in liked_genres for g in sublist]).value_counts()
        
        # اگر کاربر هیچ فیلمی را لایک نکرده بود، فیلم‌های محبوب را پیشنهاد بده
        if len(genre_counts) == 0:
            return self.get_popular_movies(top_k)

        favorite_genre = genre_counts.index[0]

        # پیدا کردن فیلم‌های جدید از ژانر مورد علاقه که کاربر هنوز ندیده است
        candidates = self.movies[
            self.movies["genres"].str.contains(favorite_genre, na=False)
            & ~self.movies["movieId"].isin(liked_movies)
        ]
        
        return candidates.head(top_k)

    @staticmethod
    def precision_at_k(recommended_ids, relevant_ids, k):
        """معیار ارزیابی: محاسبه دقت در K پیشنهاد اول"""
        rec_k = set(recommended_ids[:k])
        rel = set(relevant_ids)
        if k == 0:
            return 0.0
        return len(rec_k & rel) / k
