from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

# Инициализация базы данных
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Определение моделей базы данных
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)


class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)


class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    user = relationship("User")
    movie = relationship("Movie")


# Создание таблиц
Base.metadata.create_all(bind=engine)

# Инициализация FastAPI
app = FastAPI()


# Dependency для сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD для пользователей
@app.post("/users/")
def create_user(name: str, email: str, db: Session = Depends(get_db)):
    user = User(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.put("/users/{user_id}")
def update_user(user_id: int, name: str, email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = name
    user.email = email
    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


# CRUD для фильмов
@app.post("/movies/")
def create_movie(title: str, description: str, db: Session = Depends(get_db)):
    movie = Movie(title=title, description=description)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, title: str, description: str, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    movie.title = title
    movie.description = description
    db.commit()
    db.refresh(movie)
    return movie


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie)
    db.commit()
    return {"message": "Movie deleted"}


# Работа с избранным
@app.post("/favorites/")
def add_to_favorites(user_id: int, movie_id: int, db: Session = Depends(get_db)):
    favorite = Favorite(user_id=user_id, movie_id=movie_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


@app.delete("/favorites/")
def remove_from_favorites(user_id: int, movie_id: int, db: Session = Depends(get_db)):
    favorite = db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.movie_id == movie_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(favorite)
    db.commit()
    return {"message": "Favorite deleted"}


@app.get("/favorites/{user_id}")
def get_favorites(user_id: int, db: Session = Depends(get_db)):
    favorites = db.query(Favorite).filter(Favorite.user_id == user_id).all()
    return [{"movie_id": fav.movie_id, "movie_title": fav.movie.title} for fav in favorites]
