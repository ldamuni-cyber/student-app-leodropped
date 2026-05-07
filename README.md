# 🧢 LEODROPPED — Hat Business Order & Inventory Tracker

A Streamlit web application for managing orders and inventory for **leodropped**, a hat business that sells stock hats in various styles, colors, and sizes.

## Live App

🔗 [https://student-app-leodropped-3wqbfawebuq3y549wazlza.streamlit.app/](https://student-app-leodropped-3wqbfawebuq3y549wazlza.streamlit.app/)

---

## Tables

**hats** — stores all hat products with style, color, size, price, and current stock quantity.

**customers** — stores customer contact info (name, email, phone).

**orders** — stores each customer order with status (Pending/Shipped/Delivered/Cancelled) and payment status (Unpaid/Paid/Refunded).

**order_items** — junction table linking orders to hats. One order can include multiple hats, and one hat can appear in many orders (many-to-many).

**hat_sizes** — lookup table for hat sizes (drives the size dropdown).

**order_statuses** — lookup table for order statuses (drives the status dropdown).

**payment_statuses** — lookup table for payment statuses (drives the payment dropdown).

---

## How to Run Locally

1. Clone the repo:
