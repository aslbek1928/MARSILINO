# Discount App - Complete Documentation

## Project Overview

**Discount App** is a backend system for a restaurant discount loyalty program. It enables:
- **Mobile users** to discover restaurants, earn discounts, and track transactions
- **Restaurant admins** to manage their restaurant, cashiers, and view customer analytics
- **Cashiers** to process transactions at POS terminals

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND CLIENTS                         │
├─────────────────┬─────────────────────┬─────────────────────────┤
│   Mobile App    │  Restaurant Admin   │    POS Terminal         │
│   (Customer)    │     (Web Panel)     │     (Cashier)           │
└────────┬────────┴──────────┬──────────┴───────────┬─────────────┘
         │                   │                      │
         │ OTP Auth          │ Password Auth        │ PIN Auth
         ▼                   ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DJANGO REST API                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  accounts   │  │ restaurants │  │     transactions        │  │
│  │  (Auth)     │  │ (Data+RAP)  │  │     (Payments)          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    └─────────────────┘
```

---

## User Roles & Authentication

### 1. Mobile User (Customer)
- **Auth Method**: Phone number + OTP (One-Time Password)
- **Flow**:
  1. User enters phone number → `POST /api/auth/request-otp/`
  2. System sends 6-digit OTP (via Telegram, logged to console in dev)
  3. User enters OTP → `POST /api/auth/verify-otp/`
  4. System returns JWT tokens + `is_new_user` flag
  5. **If `is_new_user: true`**: Frontend prompts for name → `PATCH /api/me/` with `full_name`
  6. **If `is_new_user: false`**: User is logged in immediately (no name prompt)
- **Capabilities**: View restaurants, manage profile, view transaction history, like restaurants

```
┌─────────────────────────────────────────────────────────────┐
│                    MOBILE USER LOGIN FLOW                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   [Enter Phone] ──► [Request OTP] ──► [Enter OTP Code]      │
│                                              │              │
│                                              ▼              │
│                                    ┌─────────────────┐      │
│                                    │  Verify OTP     │      │
│                                    │  Returns:       │      │
│                                    │  - JWT tokens   │      │
│                                    │  - is_new_user  │      │
│                                    └────────┬────────┘      │
│                                             │               │
│                          ┌──────────────────┴────────┐      │
│                          ▼                           ▼      │
│                   is_new_user: true          is_new_user: false
│                          │                           │      │
│                          ▼                           ▼      │
│                 [Enter Full Name]              [Go to Home]  │
│                          │                                  │
│                          ▼                                  │
│                 PATCH /api/me/                              │
│                 {full_name: "..."}                          │
│                          │                                  │
│                          ▼                                  │
│                    [Go to Home]                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```


### 2. Restaurant Admin
- **Auth Method**: Phone number + Password
- **Flow**:
  1. Admin enters phone + password
  2. System validates credentials and checks `RestaurantAdmin` link
  3. Returns JWT tokens + restaurant info
- **Capabilities**: Full control over their restaurant settings, cashiers, and customer analytics

### 3. Cashier
- **Auth Method**: Restaurant ID + Phone + 4-digit PIN
- **Flow**:
  1. Cashier selects restaurant and enters phone + PIN
  2. System validates PIN hash
  3. Returns JWT with `role: 'cashier'` claim
- **Capabilities**: Process transactions at POS (future feature)

---

## Data Models

### `CustomUser` (accounts)
The main user model for all human users.
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| phone_number | String | Unique login identifier |
| full_name | String | Display name |
| liked_restaurants | M2M | Restaurants the user has favorited |
| is_staff | Boolean | Can access Django admin |
| is_active | Boolean | Account status |

### `PhoneOTP` (accounts)
Manages OTP codes for mobile authentication.
| Field | Type | Description |
|-------|------|-------------|
| phone_number | String | Target phone |
| code | String | 6-digit OTP |
| expires_at | DateTime | Validity window (5 min) |
| is_verified | Boolean | Marks OTP as used |
| attempt_count | Int | Failed attempts (max 3) |

### `RestaurantAdmin` (accounts)
Links a user to a restaurant for admin access.
| Field | Type | Description |
|-------|------|-------------|
| user | FK → CustomUser | The admin user |
| restaurant | FK → Restaurant | The managed restaurant |

### `Restaurant` (restaurants)
Core restaurant entity.
| Field | Type | Description |
|-------|------|-------------|
| name | String | Restaurant name |
| logo | Image | Logo file |
| description | Text | About text |
| hashtags | String | Comma-separated tags |
| working_hours | Text | Operating hours |
| contact_information | Text | Phone, email, etc. |
| social_media | JSON | Instagram, Telegram links |
| menu | JSON | Menu data structure |
| location_text | Text | Address |
| discount_percentage | Decimal | Loyalty discount % |

### `Cashier` (restaurants)
Restaurant employees who process transactions.
| Field | Type | Description |
|-------|------|-------------|
| restaurant | FK → Restaurant | Employer |
| name | String | Cashier name |
| phone_number | String | Login identifier |
| pin_code | String | Hashed 4-digit PIN |
| is_active | Boolean | Can login |

### `Transaction` (transactions)
Records of customer purchases.
| Field | Type | Description |
|-------|------|-------------|
| user | FK → CustomUser | Customer |
| restaurant | FK → Restaurant | Where purchase occurred |
| cashier | FK → Cashier | Who processed it |
| sum_before_discount | Decimal | Original amount |
| discount_percentage | Decimal | Applied discount % |
| sum_after_discount | Decimal | Final amount paid |
| discount_amount_uzs | Decimal | Savings in UZS |

---

## API Endpoints

### Public Endpoints (No Auth)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/auth/request-otp/` | POST | Request OTP for phone login |
| `POST /api/auth/verify-otp/` | POST | Verify OTP → get JWT tokens |
| `GET /api/restaurants/` | GET | List all restaurants (basic info) |
| `GET /api/restaurants/{id}/` | GET | Restaurant detail (full info) |
| `POST /api/restaurants/cashier/auth/login/` | POST | Cashier PIN login |
| `GET /api/docs/` | GET | Swagger API documentation |

---

### Mobile User Endpoints (JWT Required)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/me/` | GET | Get current user's profile |
| `PATCH /api/me/` | PATCH | Update profile (full_name) |
| `POST /api/me/liked-restaurants/{id}/add/` | POST | Add restaurant to favorites |
| `POST /api/me/liked-restaurants/{id}/remove/` | POST | Remove from favorites |
| `GET /api/me/transactions/` | GET | User's transaction history (paginated) |

---

### Restaurant Admin Endpoints (JWT + IsRestaurantAdmin)

#### Users Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/restaurant-admin/users/` | GET | List customers with transaction stats |
| `GET /api/restaurant-admin/users/export/` | GET | Export to Excel (.xlsx) |

**User Stats Returned**:
- `total_transactions` - Number of visits
- `total_spent_before_discount` - Gross spending
- `total_discount_amount` - Total savings given
- `total_spent_after_discount` - Net revenue
- `last_transaction_date` - Most recent visit

**Filters**:
- `date_from`, `date_to` - Transaction date range
- `min_spent`, `max_spent` - Spending range
- `min_transactions`, `max_transactions` - Visit count range
- `search` - Phone or name search

#### Cashier Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/restaurant-admin/cashiers/` | GET | List all cashiers |
| `POST /api/restaurant-admin/cashiers/` | POST | Create cashier (returns PIN once) |
| `PATCH /api/restaurant-admin/cashiers/{id}/` | PATCH | Update cashier info |
| `POST /api/restaurant-admin/cashiers/{id}/regenerate-pin/` | POST | Generate new PIN |

#### Restaurant Settings
| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/restaurant-admin/restaurant/` | GET | Get restaurant settings |
| `PATCH /api/restaurant-admin/restaurant/` | PATCH | Update settings |
| `POST /api/restaurant-admin/restaurant/gallery/` | POST | Upload gallery image |

---

## Security Features

### Rate Limiting (OTP)
- 1 minute cooldown between OTP requests
- Maximum 5 OTPs per hour per phone number
- Returns HTTP 429 when exceeded

### PIN Security (Cashiers)
- PINs stored using Django's password hashing (bcrypt)
- Never returned after initial creation
- Regenerate creates new PIN, invalidates old

### JWT Tokens
- Access token: 1 day lifetime
- Refresh token: 30 days lifetime
- Bearer token in Authorization header

---

## Testing

```bash
# Run all auth tests
./venv/bin/python manage.py test accounts.tests

# Tests include:
# - OTP request/verify flows
# - Admin authentication
# - Cashier PIN authentication  
# - Permission enforcement
```

**16 tests total**, covering:
- OTP creation, verification, expiration, reuse prevention
- Admin login, data isolation
- Cashier PIN validation, inactive rejection
- Permission checks for all user types

---

## Running the Project

```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
./venv/bin/python manage.py runserver

# Access points:
# - API: http://127.0.0.1:8000/api/
# - Admin: http://127.0.0.1:8000/admin/
# - Docs: http://127.0.0.1:8000/api/docs/
```
