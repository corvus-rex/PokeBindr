# PokeBindr

Digital Pokémon card binders for collectors.

## What & How

A web app to create, edit, and share digital Pokémon card binders. Search cards from a bundled dataset, drag them into a 4×4 grid page layout, organize across multiple pages, and share a read-only public link.

**Backend** (FastAPI + MongoDB):
```
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env 
uvicorn app.main:app --reload
```

**Frontend** (Vue 3 + TypeScript):
```
cd frontend
npm install
cp .env.example .env  # VITE_API_BASE_URL defaults to localhost:8000
npm run dev
```

The card dataset is auto-seeded into MongoDB on first startup.

## Who & What For

Built for Pokémon TCG collectors who want to present their collection visually, like a photo album for cards. The one job: let you build a binder, put cards in it, and share it.

## Why This Problem

As someone who collects Trading Cards, I know the hassle of having to take pictures of your physical binders just to share that you have specific cards in your collection. Collecting is inherently social, people want to show what they've put together and easilly share it with other people.

## What's Already Out There

Dex, Pokecollector, and various spreadsheet templates let you track what you own. However, the user has to trudge through layers of irrelevant features which prevents them from showcasing their binder or decks in under five minutes.

## In Scope / Out of Scope

**In scope**: Auth (JWT register/login), binder CRUD, card search, drag-to-organize, multi-page editor, public read-only sharing.

**Out of scope deliberately**: Trading, pricing, comments, likes, notifications, OAuth, email verification, password reset, admin panels, card price tracking, undo/redo, advanced filtering, multi-select.

## Assumptions

The card catalog is static, seeded once from a bundled JSON file and treated as read-only. The card catalog is updated once a new set is released (approximately every 3 months). Public URLs are unlisted (no auth required to view, no discoverability beyond the recent list).

## Three Questions for Real Users

1. What do you value the most out of your collection?
2. How often do you play the actual card game instead of just collecting? How often do you share a decklist with other players?
3. What's the first thing you'd want to share? A single binder link, or a profile page with all your binders?

## How I'd Know It's Working

A collector registers, creates a binder, searches for 10+ cards from memory, arranges them across 2+ pages, shares the public link, and the recipient can view all cards without logging in. If that journey takes under 2 minutes and feels like going through a real binder, it's working.

## What's Next

Allow advanced filtering (filter by Pokemon type, rarity, evolution stage, sets, etc). Ability to share profile, not just binders. Toggle for deck-building rules (rotating set legalities, card limits and duplication rules). The ability to show physical scan of their cards as proof of ownership. Integration with card grading APIs (PSA, TAG, etc). List cards to trade.