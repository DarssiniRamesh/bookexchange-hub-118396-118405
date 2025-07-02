# BookSwap Backend API Route & Data Contract Summary

This document summarizes the core REST API endpoints, their parameters, and their request/response formats for the **Book Exchange Hub backend**. These endpoints support user authentication, book management, swaps, purchases, and the user dashboard.

## Authentication (`/auth`)

- **POST `/auth/signup`**
  - Description: Create a new user account.
  - Request: `{ "username": str, "email": email, "password": str (min 6) }`
  - Response: User object (id, username, email, is_active, created_at)
  - Errors: `409` Email or username already in use.

- **POST `/auth/token`**
  - Description: Obtain a JWT bearer token by logging in.
  - Request: `application/x-www-form-urlencoded` with `username=<email>`, `password=<password>`
  - Response: `{ "access_token": str, "token_type": "bearer" }`
  - Errors: `401` Invalid credentials.

- **GET `/auth/me`**
  - Description: Get current user’s info (JWT required).
  - Response: User object
  - Auth: Requires bearer token.

## Book Management (`/books`)

- **POST `/books/`**
  - Description: Add a new book (user-owned).
  - Auth: Required.
  - Request: `{ title, author, description?, image_url?, category?, is_for_sale?, price? }`
  - Response: Book object.

- **GET `/books/`**
  - Description: List all books in marketplace.
  - Query Params:
    - `category` (str, optional)
    - `search` (str, optional; title/author search)
    - `for_sale` (bool, optional)
  - Response: `[Book, ...]`

- **GET `/books/{book_id}`**
  - Description: Get details for a specific book.

- **PUT `/books/{book_id}`**
  - Description: Update book info (owner only).
  - Auth: Required.
  - Request: BookUpdate object.

- **DELETE `/books/{book_id}`**
  - Description: Delete a book (owner only).
  - Auth: Required.
  - Status: `204 No Content` on success.

## Swap Requests (`/swaps`)

- **POST `/swaps/`**
  - Description: Request to swap (send request to owner for their book).
  - Auth: Required.
  - Request: `{ book_id, owner_id }`
  - Response: SwapRequest object.

- **GET `/swaps/`**
  - Description: List all swap requests (admin endpoint).

- **GET `/swaps/my`**
  - Description: List all swaps initiated by current user.
  - Auth: Required.

- **GET `/swaps/received`**
  - Description: List all swap requests received by current user (as owner).
  - Auth: Required.

- **PUT `/swaps/{swap_id}/status`**
  - Description: Accept/reject/cancel a swap. Only owner can accept/reject; only requester can cancel.
  - Auth: Required.
  - Request: `{ status: "pending"|"accepted"|"rejected"|"cancelled" }`
  - Response: SwapRequest object.

## Purchases (`/purchases`)

- **POST `/purchases/`**
  - Description: Initiate a book purchase (Stripe integration stub).
  - Auth: Required.
  - Request: `{ book_id, amount }`
  - Response: Purchase object (status set to completed immediately for demo).

- **GET `/purchases/my`**
  - Description: List all purchases made by current user.
  - Auth: Required.

## Dashboard/User History (`/dashboard`)

- **GET `/dashboard/`**
  - Description: Return *all* books, swaps, and purchases for the current user.
  - Auth: Required.
  - Response: `{ books: [...], swaps: [...], purchases: [...] }`

---

## Data Model Summaries

### User

```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@email.com",
  "is_active": true,
  "created_at": "2024-06-09T12:00:00"
}
```

### Book

```json
{
  "id": 7,
  "title": "Example Book",
  "author": "Writer",
  "description": "Desc",
  "image_url": "...",
  "category": "Fiction",
  "owner_id": 1,
  "is_available": true,
  "is_for_sale": false,
  "price": null
}
```

### SwapRequest

```json
{
  "id": 3,
  "book_id": 7,
  "requester_id": 2,
  "book_owner_id": 1,
  "status": "pending",
  "created_at": "2024-06-09T12:15:00",
  "updated_at": "2024-06-09T12:15:00"
}
```

### Purchase

```json
{
  "id": 2,
  "buyer_id": 2,
  "book_id": 7,
  "status": "completed",
  "stripe_payment_intent_id": "stubbed-intent-id",
  "amount": 12.99,
  "purchased_at": "2024-06-09T12:30:00"
}
```

### UserHistory

```json
{
  "books": [/* BookOut objects */],
  "swaps": [/* SwapRequestOut objects */],
  "purchases": [/* PurchaseOut objects */]
}
```

---

## General Notes

- Most endpoints (except `/auth/token`, `/auth/signup`, `/books` get/list, `/books/{id}` get) require a JWT Bearer token.
- Unauthorized or invalid access will result in `401` or `403`.
- Book updates and deletions are restricted to the user who owns them. Swap state changes are permissioned as per role (owner/requester).

---

## Enum Values

- Swap Status: `"pending"`, `"accepted"`, `"rejected"`, `"cancelled"`
- Purchase Status: `"pending"`, `"completed"`, `"failed"`

---

For request/response schema details, refer to the OpenAPI and FastAPI interactive docs, or see below.

