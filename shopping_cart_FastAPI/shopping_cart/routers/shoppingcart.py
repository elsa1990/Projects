from typing import List
from fastapi import APIRouter, Depends, status
from shopping_cart import schemas, database, oauth2
from sqlalchemy.orm import Session
from shopping_cart.repository import shoppingcart

router = APIRouter(
    # prefix="/blog",
    tags=['Shopping Cart']
)

get_db = database.get_db

# get all product info
@router.get('/get_products_info', response_model=List[schemas.Getallproducts])
def all(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return shoppingcart.get_all_products(db)

# fuzzy search
@router.post('/fuzzy_search', response_model=List[schemas.Getallproducts])
def fuzzy_search(request: schemas.Fuzzy, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return shoppingcart.fuzzy(request, db)

# add to cart
@router.post('/cart', status_code=status.HTTP_201_CREATED, response_model=schemas.Showorders)
def create(request: schemas.Addtocart, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return shoppingcart.create(request, db)

# delete order
@router.delete('/delete_order/{id}', status_code=status.HTTP_404_NOT_FOUND)
def destroy(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return shoppingcart.destroy(id, db)


@router.patch('/cart/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id: int, request: schemas.Modify, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return shoppingcart.update(id, request.dict(), db)

# show order by id
@router.get('/show_orders/{id}', status_code=200, response_model=schemas.Showorders)
def show(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return shoppingcart.show(id, db)
