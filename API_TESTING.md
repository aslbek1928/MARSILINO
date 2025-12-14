~# Discount App - Comprehensive API Documentation

**Base URL**: `https://marsilino.onrender.com`

---

## 🔑 Authentication Concepts

This API uses **JWT (JSON Web Token)** for authentication.
1.  **Login**: You send credentials (phone + OTP/Password/PIN) to an auth endpoint.
2.  **Receive Tokens**: You get a JSON response with `access` and `refresh` tokens.
3.  **Authenticate Requests**: For all protected endpoints, you must include the `access` token in the header.

**Header Format**:
```http
Authorization: Bearer <your_access_token>
```

### User Roles
1.  **Mobile User (Customer)**: End-users who use the app to get discounts. Authenticate via Phone + OTP.
2.  **Restaurant Admin**: Owners who manage restaurant settings. Authenticate via Phone + Password.
3.  **Cashier**: Employees who process transactions. Authenticate via Restaurant ID + Phone + PIN.

---

## 📱 Mobile User Flow
*For customers using the mobile app.*

### 1. Request OTP
Initiates the login process by sending an SMS code.
*   **Method**: `POST`
*   **URL**: `/api/auth/request-otp/`
*   **Body**:
    ```json
    {
      "phone_number": "+998901234567"
    }
    ```
*   **Response**: `200 OK` (Message saying OTP sent)

### 2. Verify OTP & Login
Validates the code and logs the user in.
*   **Method**: `POST`
*   **URL**: `/api/auth/verify-otp/`
*   **Body**:
    ```json
    {
      "phone_number": "+998901234567",
      "code": "123456"
    }
    ```
*   **Response**: `200 OK`
    ```json
    {
      "refresh": "eyJhbG...",
      "access": "eyJhbG...",
      "is_new_user": false
    }
    ```

### 3. Get My Profile
Fetch details of the currently logged-in user.
*   **Method**: `GET`
*   **URL**: `/api/me/`
*   **Header**: `Authorization: Bearer <access_token>`
*   **Response**: `200 OK`
    ```json
    {
      "id": "uuid...",
      "phone_number": "+998901234567",
      "full_name": "John Doe",
      "liked_restaurants": [1, 5]
    }
    ```

### 4. Update Profile
Update your name.
*   **Method**: `PATCH`
*   **URL**: `/api/me/`
*   **Header**: `Authorization: Bearer <access_token>`
*   **Body**:
    ```json
    {
      "full_name": "Jane User"
    }
    ```

### 5. Like/Unlike Restaurant
Add or remove a restaurant from favorites.
*   **Method**: `POST`
*   **URL**: `/api/me/liked-restaurants/<restaurant_id>/<action>/`
    *   Replace `<restaurant_id>` with the UUID of the restaurant.
    *   Replace `<action>` with `add` or `remove`.
*   **Header**: `Authorization: Bearer <access_token>`

### 6. View My Transactions
See history of purchases.
*   **Method**: `GET`
*   **URL**: `/api/me/transactions/`
*   **Header**: `Authorization: Bearer <access_token>`

---

## 🍽 Public Data
*No authentication required.*

### 1. List Restaurants
Get a list of all available restaurants.
*   **Method**: `GET`
*   **URL**: `/api/restaurants/`

### 2. Restaurant Details
Get full info (menu, social media, gallery) for a specific restaurant.
*   **Method**: `GET`
*   **URL**: `/api/restaurants/<restaurant_id>/`

---

## 💼 Restaurant Admin Panel
*For restaurant owners. Requires Admin authentication.*

### 1. Admin Login
*   **Method**: `POST`
*   **URL**: `/api/restaurant-admin/auth/login/`
*   **Body**:
    ```json
    {
      "phone_number": "+998991234567",
      "password": "your_secure_password"
    }
    ```
*   **Response**: Returns `access` token (Admin permissions).

### 2. Get Restaurant Settings
View your restaurant's configuration.
*   **Method**: `GET`
*   **URL**: `/api/restaurant-admin/restaurant/`
*   **Header**: `Authorization: Bearer <admin_access_token>`

### 3. Update Restaurant Settings
Update info like working hours or discount percentage.
*   **Method**: `PATCH`
*   **URL**: `/api/restaurant-admin/restaurant/`
*   **Header**: `Authorization: Bearer <admin_access_token>`
*   **Body** (partial updates allowed):
    ```json
    {
      "description": "New description...",
      "discount_percentage": "15.00"
    }
    ```

### 4. Upload Gallery Image
*   **Method**: `POST`
*   **URL**: `/api/restaurant-admin/restaurant/gallery/`
*   **Header**: `Authorization: Bearer <admin_access_token>`
*   **Body**: Form-data with key `image` (file).

### 5. List Cashiers
*   **Method**: `GET`
*   **URL**: `/api/restaurant-admin/cashiers/`
*   **Header**: `Authorization: Bearer <admin_access_token>`

### 6. Create Cashier
*   **Method**: `POST`
*   **URL**: `/api/restaurant-admin/cashiers/`
*   **Header**: `Authorization: Bearer <admin_access_token>`
*   **Body**:
    ```json
    {
      "name": "Cashier Alex",
      "phone_number": "+998900000001"
    }
    ```
*   **Response**: **IMPORTANT**: Returns the generated PIN code only once!

### 7. Regenerate Cashier PIN
If a cashier forgets their PIN.
*   **Method**: `POST`
*   **URL**: `/api/restaurant-admin/cashiers/<cashier_id>/regenerate-pin/`
*   **Header**: `Authorization: Bearer <admin_access_token>`

### 8. View Users (Analytics)
See list of customers who have visited the restaurant.
*   **Method**: `GET`
*   **URL**: `/api/restaurant-admin/users/`
*   **Header**: `Authorization: Bearer <admin_access_token>`

---

## 🏪 Cashier Flow
*For POS terminals.*

### 1. Cashier Login
*   **Method**: `POST`
*   **URL**: `/api/restaurants/cashier/auth/login/`
*   **Body**:
    ```json
    {
      "restaurant_id": "<your_restaurant_uuid>",
      "phone_number": "+998900000001",
      "pin_code": "1234"
    }
    ```
