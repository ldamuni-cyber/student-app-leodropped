import streamlit as st
from db import get_connection, get_order_statuses, get_payment_statuses

st.set_page_config(page_title="Orders | leodropped", page_icon="🧢", layout="centered")
st.title("📦 Manage Orders")

ORDER_STATUSES = get_order_statuses()
PAYMENT_STATUSES = get_payment_statuses()

def load_customers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, first_name || ' ' || last_name FROM customers ORDER BY last_name;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {name: cid for cid, name in rows}

def load_hats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, style || ' - ' || color || ' (' || size || ')' FROM hats WHERE quantity_in_stock > 0 ORDER BY style;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {label: hid for hid, label in rows}

with st.expander("Create New Order", expanded=False):
    customers = load_customers()
    hats = load_hats()
    if not customers:
        st.warning("Add a customer first.")
    elif not hats:
        st.warning("Add hats with stock first.")
    else:
        with st.form("create_order"):
            selected_customer = st.selectbox("Customer *", list(customers.keys()))
            c1, c2 = st.columns(2)
            status = c1.selectbox("Order Status *", ORDER_STATUSES)
            payment_status = c2.selectbox("Payment Status *", PAYMENT_STATUSES)
            notes = st.text_area("Notes (optional)")
            st.markdown("**Add a Hat to this Order**")
            selected_hat = st.selectbox("Hat *", list(hats.keys()))
            quantity = st.number_input("Quantity *", min_value=1, step=1, value=1)
            submitted = st.form_submit_button("Create Order")
            if submitted:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    customer_id = customers[selected_customer]
                    hat_id = hats[selected_hat]
                    cur.execute("SELECT price, quantity_in_stock FROM hats WHERE id=%s;", (hat_id,))
                    hat_info = cur.fetchone()
                    unit_price = hat_info[0]
                    stock = hat_info[1]
                    if quantity > stock:
                        st.error(f"Not enough stock. Only {stock} available.")
                    else:
                        cur.execute("INSERT INTO orders (customer_id, status, payment_status, notes) VALUES (%s, %s, %s, %s) RETURNING id;", (customer_id, status, payment_status, notes.strip() or None))
                        order_id = cur.fetchone()[0]
                        cur.execute("INSERT INTO order_items (order_id, hat_id, quantity, unit_price) VALUES (%s, %s, %s, %s);", (order_id, hat_id, quantity, unit_price))
                        cur.execute("UPDATE hats SET quantity_in_stock = quantity_in_stock - %s WHERE id=%s;", (quantity, hat_id))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"Order #{order_id} created!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

st.subheader("All Orders")
filter_status = st.selectbox("Filter by status", ["All"] + ORDER_STATUSES)

try:
    conn = get_connection()
    cur = conn.cursor()
    if filter_status != "All":
        cur.execute("SELECT o.id, c.first_name || ' ' || c.last_name, o.order_date, o.status, o.payment_status FROM orders o JOIN customers c ON c.id = o.customer_id WHERE o.status = %s ORDER BY o.order_date DESC;", (filter_status,))
    else:
        cur.execute("SELECT o.id, c.first_name || ' ' || c.last_name, o.order_date, o.status, o.payment_status FROM orders o JOIN customers c ON c.id = o.customer_id ORDER BY o.order_date DESC;")
    orders = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error: {e}")
    orders = []

if not orders:
    st.info("No orders found.")
else:
    for order in orders:
        oid, cname, odate, ostatus, opay = order
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2, 2, 1.5, 1.5, 1, 1])
        c1.write(f"#{oid}")
        c2.write(cname)
        c3.write(odate.strftime("%b %d, %Y") if odate else "-")
        c4.write(ostatus)
        c5.write(opay)
        if c6.button("Edit", key=f"eo_{oid}"):
            st.session_state["editing_order"] = oid
        if c7.button("Delete", key=f"do_{oid}"):
            st.session_state["confirm_del_order"] = oid

    editing_id = st.session_state.get("editing_order")
    if editing_id:
        order_data = next((o for o in orders if o[0] == editing_id), None)
        if order_data:
            st.divider()
            st.subheader(f"Edit Order #{editing_id}")
            with st.form("edit_order"):
                c1, c2 = st.columns(2)
                new_status = c1.selectbox("Status *", ORDER_STATUSES, index=ORDER_STATUSES.index(order_data[3]))
                new_payment = c2.selectbox("Payment Status *", PAYMENT_STATUSES, index=PAYMENT_STATUSES.index(order_data[4]))
                new_notes = st.text_area("Notes")
                s, ca = st.columns(2)
                save = s.form_submit_button("Save Changes")
                cancel = ca.form_submit_button("Cancel")
                if save:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("UPDATE orders SET status=%s, payment_status=%s, notes=%s WHERE id=%s;", (new_status, new_payment, new_notes.strip() or None, editing_id))
                        conn.commit()
                        cur.close()
                        conn.close()
                        del st.session_state["editing_order"]
                        st.success("Order updated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                if cancel:
                    del st.session_state["editing_order"]
                    st.rerun()

    confirm_id = st.session_state.get("confirm_del_order")
    if confirm_id:
        order_data = next((o for o in orders if o[0] == confirm_id), None)
        if order_data:
            st.divider()
            st.warning(f"Delete Order #{confirm_id} for {order_data[1]}? This cannot be undone.")
            c1, c2 = st.columns(2)
            if c1.button("Yes, Delete", key="yes_o"):
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM orders WHERE id=%s;", (confirm_id,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    del st.session_state["confirm_del_order"]
                    st.success("Order deleted.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            if c2.button("Cancel", key="no_o"):
                del st.session_state["confirm_del_order"]
                st.rerun()
