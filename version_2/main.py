from fastapi import FastAPI
from database import Base, engine
from routes.users import router as user_router
from routes.movies import router as movie_router
from routes.favorites import router as favorite_router

# Инициализация приложения
app = FastAPI()

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Подключение маршрутов
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(movie_router, prefix="/movies", tags=["Movies"])
app.include_router(favorite_router, prefix="/favorites", tags=["Favorites"])

# Точка входа
@app.get("/")
def root():
    return {"message": "Welcome to the Movie API"}