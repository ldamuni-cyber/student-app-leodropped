# 🧢 LEODROPPED

A hat business tracker built to manage orders and inventory for **leodropped**, a small business that sells stock hats in various styles, colors, and sizes. This app makes it easy to track what hats are in stock, who the customers are, and the status of every order — all in one place.

## Live App

**[Click here to open leodropped](https://student-app-leodropped-3wqbfawebuq3y549wazlza.streamlit.app/)**

---

## ERD

*(Add erd.png here after exporting from dbdiagram.io)*

---

## Table Descriptions

- **hats** — Stores all hat products with style, color, size, price, and current stock quantity.
- **customers** — Stores customer contact info including name, email, and phone number.
- **orders** — Stores each order with a reference to the customer, order status, and payment status.
- **order_items** — Junction table linking orders to hats. One order can include many hats and one hat can appear in many orders (many-to-many relationship).
- **hat_sizes** — Lookup table for hat sizes that drives the size dropdown in the inventory form.
- **order_statuses** — Lookup table for order statuses (Pending, Shipped, Delivered, Cancelled).
- **payment_statuses** — Lookup table for payment statuses (Unpaid, Paid, Refunded).

---

## How to Run Locally

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.streamlit/secrets.toml` file with your database connection:
4. Run the app: `streamlit run Home.py`

---

## Pages

- **Home** — Dashboard with live metrics for hat products, customers, total orders, and pending orders
- **Manage Inventory** — Add, edit, and delete hats with search by style or color
- **Manage Customers** — Add, edit, and delete customers with search by name or email
- **Manage Orders** — Create orders, filter by status, and edit or delete existing orders
