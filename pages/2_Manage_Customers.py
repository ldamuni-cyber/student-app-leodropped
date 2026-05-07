import streamlit as st
import re
from db import get_connection

st.set_page_config(page_title="Customers | leodropped", page_icon="🧢", layout="centered")
st.title("👤 Manage Customers")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^\d{10}$")

with st.expander("Add New Customer", expanded=False):
    with st.form("add_customer"):
        c1, c2 = st.columns(2)
        first_name = c1.text_input("First Name *")
        last_name = c2.text_input("Last Name *")
        c3, c4 = st.columns(2)
        email = c3.text_input("Email *")
        phone = c4.text_input("Phone (10 digits, optional)")
        submitted = st.form_submit_button("Add Customer")
        if submitted:
            errors = []
            if not first_name.strip(): errors.append("First name is required.")
            if not last_name.strip(): errors.append("Last name is required.")
            if not email.strip(): errors.append("Email is required.")
            elif not EMAIL_REGEX.match(email.strip()): errors.append("Email must be valid (e.g. name@example.com).")
            if phone.strip() and not PHONE_REGEX.match(phone.strip()): errors.append("Phone must be exactly 10 digits.")
            if errors:
                for e in errors: st.error(e)
            else:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO customers (first_name, last_name, email, phone) VALUES (%s, %s, %s, %s);",
                        (first_name.strip(), last_name.strip(), email.strip().lower(), phone.strip() or None)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"Customer added: {first_name} {last_name}")
                    st.rerun()
                except Exception as e:
                    if "unique" in str(e).lower(): st.error("That email is already registered.")
                    else: st.error(f"Error: {e}")

st.subheader("All Customers")
search = st.text_input("Search by name or email")

try:
    conn = get_connection()
    cur = conn.cursor()
    if search.strip():
        cur.execute(
            "SELECT id, first_name, last_name, email, phone FROM customers WHERE first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s ORDER BY last_name;",
            (f"%{search}%", f"%{search}%", f"%{search}%")
        )
    else:
        cur.execute("SELECT id, first_name, last_name, email, phone FROM customers ORDER BY last_name;")
    customers = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error: {e}")
    customers = []

if not customers:
    st.info("No customers found.")
else:
    for cust in customers:
        cid, fn, ln, em, ph = cust
        c1, c2, c3, c4, c5 = st.columns([2, 2, 3, 1, 1])
        c1.write(f"{fn} {ln}")
        c2.write(ph or "-")
        c3.write(em)
        if c4.button("Edit", key=f"ec_{cid}"):
            st.session_state["editing_customer"] = cid
        if c5.button("Delete", key=f"dc_{cid}"):
            st.session_state["confirm_del_customer"] = cid

    editing_id = st.session_state.get("editing_customer")
    if editing_id:
        cust_data = next((c for c in customers if c[0] == editing_id), None)
        if cust_data:
            st.divider()
            st.subheader(f"Edit Customer #{editing_id}")
            with st.form("edit_customer"):
                c1, c2 = st.columns(2)
                new_fn = c1.text_input("First Name *", value=cust_data[1])
                new_ln = c2.text_input("Last Name *", value=cust_data[2])
                c3, c4 = st.columns(2)
                new_email = c3.text_input("Email *", value=cust_data[3])
                new_phone = c4.text_input("Phone", value=cust_data[4] or "")
                s, ca = st.columns(2)
                save = s.form_submit_button("Save Changes")
                cancel = ca.form_submit_button("Cancel")
                if save:
                    errors = []
                    if not new_fn.strip(): errors.append("First name required.")
                    if not new_ln.strip(): errors.append("Last name required.")
                    if not new_email.strip(): errors.append("Email required.")
                    elif not EMAIL_REGEX.match(new_email.strip()): errors.append("Invalid email.")
                    if new_phone.strip() and not PHONE_REGEX.match(new_phone.strip()): errors.append("Phone must be 10 digits.")
                    if errors:
                        for e in errors: st.error(e)
                    else:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute(
                                "UPDATE customers SET first_name=%s, last_name=%s, email=%s, phone=%s WHERE id=%s;",
                                (new_fn.strip(), new_ln.strip(), new_email.strip().lower(), new_phone.strip() or None, editing_id)
                            )
                            conn.commit()
                            cur.close()
                            conn.close()
                            del st.session_state["editing_customer"]
                            st.success("Customer updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                if cancel:
                    del st.session_state["editing_customer"]
                    st.rerun()

    confirm_id = st.session_state.get("confirm_del_customer")
    if confirm_id:
        cust_data = next((c for c in customers if c[0] == confirm_id), None)
        if cust_data:
            st.divider()
            st.warning(f"Delete {cust_data[1]} {cust_data[2]}? This will also delete their orders.")
            c1, c2 = st.columns(2)
            if c1.button("Yes, Delete", key="yes_c"):
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM customers WHERE id=%s;", (confirm_id,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    del st.session_state["confirm_del_customer"]
                    st.success("Customer deleted.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            if c2.button("Cancel", key="no_c"):
                del st.session_state["confirm_del_customer"]
                st.rerun()
