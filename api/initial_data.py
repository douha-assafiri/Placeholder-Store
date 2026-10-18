from sqlalchemy.orm import Session

from helpers import logger
from models import Place

SAMPLE_PLACES = [
    {"name": "Studio Wireless Headphones", "category": "Electronics", "price": 149, "old_price": 199, "rating": 4.8, "tag": "Bestseller", "quantity": 18,
     "image_path": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=900&q=85",
     "description": "Immersive sound, soft ear cushions and an all-day battery for your everyday soundtrack."},
    {"name": "Nordic Analog Watch", "category": "Accessories", "price": 189, "rating": 4.9, "tag": "New", "quantity": 12,
     "image_path": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=900&q=85",
     "description": "A refined, minimalist watch designed to complement every outfit."},
    {"name": "Everyday Runner Sneakers", "category": "Fashion", "price": 109, "old_price": 139, "rating": 4.7, "tag": "Sale", "quantity": 25,
     "image_path": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=900&q=85",
     "description": "Lightweight comfort and effortless style for wherever the day takes you."},
    {"name": "Mirrorless Travel Camera", "category": "Electronics", "price": 649, "rating": 4.9, "quantity": 8,
     "image_path": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=900&q=85",
     "description": "Capture life beautifully with a compact, capable everyday camera."},
    {"name": "Classic Canvas Backpack", "category": "Accessories", "price": 79, "rating": 4.6, "quantity": 30,
     "image_path": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=900&q=85",
     "description": "Smart storage, comfortable straps and a timeless look for daily adventures."},
    {"name": "Minimal Desk Lamp", "category": "Home & Living", "price": 89, "rating": 4.8, "tag": "Popular", "quantity": 16,
     "image_path": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=900&q=85",
     "description": "Warm, focused light in a clean design that fits any workspace."},
    {"name": "Retro Sunglasses", "category": "Fashion", "price": 59, "rating": 4.5, "quantity": 21,
     "image_path": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=900&q=85",
     "description": "A classic silhouette made for sunny days and weekend escapes."},
    {"name": "Portable Bluetooth Speaker", "category": "Electronics", "price": 119, "old_price": 149, "rating": 4.7, "tag": "Sale", "quantity": 14,
     "image_path": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=900&q=85",
     "description": "Big sound in a small package. Take your favourite playlists anywhere."},
]


# Only adds what's missing
def add_initial_data(db: Session):
    if db.query(Place).first() is None:
        db.add_all(Place(stock=place["quantity"] > 0, **place) for place in SAMPLE_PLACES)
        logger.info(f"Added {len(SAMPLE_PLACES)} sample places")
    db.commit()
