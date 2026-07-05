# Farm Connect 🌱

A full-stack, direct-to-consumer farm marketplace that connects local farmers directly with buyers, eliminating middlemen markups and maximizing farmer profits.

## Tech Stack

- **Frontend**: React.js, React Router, Tailwind CSS, Lucide Icons, Axios.
- **Backend**: Node.js, Express.js, MongoDB (Mongoose), JSON Web Token (JWT) Authentication, BcryptJS.

---

## Features

1. **Farmer & Consumer Authentication**: Role-based registration and login, secured using JWT stored in LocalStorage.
2. **Product Directory**: Dynamic product grid with real-time text-search and category pill filtering.
3. **Transparent Farmer Info**: Every product listing details the source farm, address, contact number, and history.
4. **Shopping Cart**: Real-time quantity adjustments, automatic validation against remaining farmer stock.
5. **Direct Checkout**: Smooth shipping address input, phone confirmation, and Cash on Delivery order creation.
6. **Premium Farmer Dashboard**:
   - **Sales Stats**: Track total sales revenue, active listing counts, and pending order tallies.
   - **Listed Produce Management**: Create, update, or remove produce listings.
   - **Order Dispatch Tracker**: View buyer name, shipping address, items ordered, and update order status (Pending -> Processing -> Shipped -> Delivered).
7. **Consumer Order History**: Check order date, track status, and view delivery parameters.

---

## Folder Structure

```text
agri connect/
├── backend/                  # Express.js REST API
│   ├── config/               # DB connection configurations
│   ├── controllers/          # Request handlers
│   ├── middleware/           # JWT verification & error handling middlewares
│   ├── models/               # Mongoose schemas (User, Product, Order)
│   ├── routes/               # API endpoints mappings
│   ├── .env                  # Port & database credentials
│   └── server.js             # API server entry
│
└── frontend/                 # Vite + React Single Page App
    ├── public/               # Static assets
    ├── src/                  # React source files
    │   ├── components/       # Custom Navbar, Footer, and ProtectedRoute wrapper
    │   ├── context/          # AuthContext and CartContext state managers
    │   ├── pages/            # View components (Home, Shop, Cart, Dashboard, Profile, Orders)
    │   ├── services/         # Axios API clients with auto-interceptors
    │   ├── index.css         # Tailwind directives and custom animation classes
    │   └── main.jsx          # React app mounter
    ├── index.html            # Main HTML document
    └── tailwind.config.js    # Tailwind v3 design token configuration
```

---

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (Version 16 or higher)
- [MongoDB](https://www.mongodb.com/) (Local installation or MongoDB Atlas cluster connection URI)

### Setup Instructions

1. **Clone/Open the workspace** in your editor.

2. **Database Setup**:
   - Make sure your MongoDB service is running (locally on `mongodb://127.0.0.1:27017/farmconnect` or update the `MONGO_URI` in `backend/.env` with your MongoDB Atlas connection string).

3. **Run the Backend Server**:
   ```bash
   cd backend
   npm install
   npm run dev
   ```
   The backend server will run on [http://localhost:5000](http://localhost:5000).

4. **Run the Frontend Application**:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```
   The frontend dev server will launch at [http://localhost:3000](http://localhost:3000) (with active proxy configurations pointing `/api` to the backend server).

---

## Design System

The application uses an agricultural-inspired premium color palette:
- **Primary Color**: Forest Green (`#16a34a` to `#14532d`) for freshness and growth.
- **Secondary Color**: Warm Amber/Earth (`#f59e0b` to `#78350f`) for farm authenticity.
- **Aesthetics**: Fully responsive mobile-friendly layouts, sticky glassmorphic navigation header, soft shadows, hover-lift card motions, and smooth page entry transitions.
