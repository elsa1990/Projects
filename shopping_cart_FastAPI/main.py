from fastapi import FastAPI
from shopping_cart import  models
from shopping_cart.database import engine
from shopping_cart.routers import shoppingcart, user, authentication

app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(authentication.router)
app.include_router(shoppingcart.router)
app.include_router(user.router)

# pipenv run uvicorn main:app --reload --port 8888