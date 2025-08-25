# Online Cinema

## Description
Online Cinema is a digital platform that allows users to browse, watch, and purchase movies online. It offers a convenient and personalized experience for users to explore a wide selection of films.

---

## Key Features

### User Authentication
- Registration with email confirmation.
- Account activation via email link.
- Password reset and change functionality.
- JWT-based authentication with access and refresh tokens.
- Different user roles with varying permissions (User, Moderator, Admin).

### Movies
- Browse movie catalog with search, filter, and sort options.
- View detailed movie descriptions.
- Rate movies, leave comments, like/dislike.
- Add movies to favorites.

### Shopping Cart
- Add movies to the cart before purchase.
- Remove movies or clear the cart.
- Prevent duplicate or repeated purchases.

### Orders
- Place orders for movies in the cart.
- View order history with status and details.
- Cancel orders before payment.

### Payments
- Make payments via Stripe.
- View payment history and status.
- Integration with payment webhooks for transaction validation.

---

## Technologies
- **Backend:** FastAPI
- **Database:** PostgreSQL (or SQLite for testing)
- **ORM:** SQLAlchemy 2.0+
- **Asynchronous tasks:** Celery + Redis
- **Authentication:** JWT tokens
- **Containerization:** Docker & Docker Compose
- **Dependency Management:** Poetry

---

## Setup
1. Clone the repository:
```bash
git clone <repository_url>
```
2. Install dependencies using Poetry:
```bash
poetry install
```
3. Run services with Docker Compose:
```bash
docker-compose up --build
```

## Testing

- Async tests are implemented with pytest and pytest-asyncio.

- Run tests:
```bash
pytest
```
## Notes

- Activation and password reset tokens are managed asynchronously.

- User roles determine access to different features in the system.

- The system is designed to be scalable and maintainable using Docker and Celery for background tasks.

---

## Author
**Name:** Nazarii  
**Telegram:** [@Carn1vor3](https://t.me/Carn1vor3)   
**GitHub:** [repository link](https://github.com/Carn1vor3/cinema_project_fastapi)

---