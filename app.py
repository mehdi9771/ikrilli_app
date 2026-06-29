import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Set up mobile screen frameworks
st.set_page_config(page_title="Ikrilli", page_icon="🚗", layout="centered")

# Custom CSS theme injector for smartphones
st.markdown("""
    <style>
    .stApp { background-color: #111216; color: #FFFFFF; }
    .car-card { background-color: #1F232C; padding: 16px; border-radius: 12px; margin-bottom: 12px; border-left: 5px solid #FF4B4B; }
    .badge-card { background-color: #1F232C; padding: 16px; border-radius: 12px; margin-bottom: 12px; border-left: 5px solid #00E676; }
    .green-badge { background-color: #00E676; color: #000000; padding: 3px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; }
    .ins-label { background-color: #FFA000; color: #000000; padding: 3px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; }
    </style>
""", unsafe_allow_html=True)

CARS_FILE = "ikrilli_cars.csv"
CHATS_FILE = "ikrilli_chats.csv"

# Initialize raw storage structures
if not os.path.exists(CARS_FILE):
    pd.DataFrame(columns=['Agency_Name', 'Phone', 'Wilaya', 'Car_Name', 'Price_DA', 'Requires_Insurance', 'Insurance_Amount', 'Total_Trips', 'Rating']).to_csv(CARS_FILE, index=False)
if not os.path.exists(CHATS_FILE):
    pd.DataFrame(columns=['Sender', 'Receiver', 'Timestamp', 'Message', 'Is_Read']).to_csv(CHATS_FILE, index=False)

# Access Session Control Panel Setup
st.sidebar.title("🔑 Ikrilli Profile")
role = st.sidebar.radio("Identify Account Mode:", ["Customer", "Agency Renter"])
username = st.sidebar.text_input("Enter Profile Name:", "")

if 'role' not in st.session_state: st.session_state.role = "Customer"
if 'user' not in st.session_state: st.session_state.user = ""
st.session_state.role = role
st.session_state.user = username

# Global Live Notification Banner
if st.session_state.user:
    df_n = pd.read_csv(CHATS_FILE)
    unr = df_n[(df_n['Receiver'] == st.session_state.user) & (df_n['Is_Read'] == False)]
    if not unr.empty:
        st.toast(f"🔔 Notification: You have {len(unr)} new message(s) waiting in your inbox!", icon="💬")

# MODE A: CUSTOMER SHOPPING EXPERIENCE 
if st.session_state.role == "Customer":
    st.title("🚗 Search Rental Vehicles")
    
    col1, col2 = st.columns(2)
    with col1: query = st.text_input("🔍 Type keywords (e.g. Golf, Mercedes):", "")
    with col2: loc = st.selectbox("📍 Select City:", ["All 58 Wilayas", "Algiers", "Oran", "Constantine", "Sétif"])
    
    no_ins = st.checkbox("⚡ Show cars with NO insurance deposit required")
    
    df_cars = pd.read_csv(CARS_FILE)
    if df_cars.empty:
        st.info("No cars listed yet. Toggle to 'Agency Renter' above to post!")
    else:
        if query: df_cars = df_cars[df_cars['Car_Name'].str.contains(query, case=False, na=False)]
        if loc != "All 58 Wilayas": df_cars = df_cars[df_cars['Wilaya'] == loc]
        if no_ins: df_cars = df_cars[df_cars['Requires_Insurance'] == False]
        
        for idx, row in df_cars.iterrows():
            is_green = int(row['Total_Trips']) > 50 and float(row['Rating']) > 4.7
            box_class = "badge-card" if is_green else "car-card"
            
            st.markdown(f"""
            <div class="{box_class}">
                <h3>🚗 {row['Car_Name']}</h3>
                <p><b>🏢 Agency:</b> {row['Agency_Name']} (📍 {row['Wilaya']}) | <b>💰 Price:</b> {row['Price_DA']:,} DA/Day</p>
                <p>⭐ Rating: {row['Rating']} ({row['Total_Trips']} rentals completed)</p>
            </div>
            """, unsafe_allow_html=True)
            
            t1, t2 = st.columns(2)
            with t1:
                if is_green: st.markdown('<span class="green-badge">🟢 Green Car - High Customer Trust</span>', unsafe_allow_html=True)
            with t2:
                if row['Requires_Insurance']: st.markdown(f'<span class="ins-label">⚠️ Deposit Req: {row["Insurance_Amount"]:,} DA</span>', unsafe_allow_html=True)
                else: st.markdown('<span class="green-badge">🛡️ Zero Upfront Insurance</span>', unsafe_allow_html=True)
            
            if st.button(f"✉️ Place Order Request ({row['Agency_Name']})", key=f"bk_{idx}"):
                if not st.session_state.user:
                    st.error("⚠️ Set your Profile Name in the sidebar first to access text messaging!")
                else:
                    df_ch = pd.read_csv(CHATS_FILE)
                    new_msg = pd.DataFrame([{'Sender': st.session_state.user, 'Receiver': row['Agency_Name'], 'Timestamp': datetime.now().strftime("%M:%S"), 'Message': f"Salâm! I am requesting to rent your {row['Car_Name']} listing. Let's arrange pickup.", 'Is_Read': False}])
                    pd.concat([df_ch, new_msg], ignore_index=True).to_csv(CHATS_FILE, index=False)
                    st.success("Booking request initialized! Communicate in the inbox panel at the bottom of the page.")

# MODE B: AGENCY UPLOAD INTERFACE
elif st.session_state.role == "Agency Renter":
    st.title("💼 Agency Fleet Hub")
    st.subheader("Flat Listing Rule: 15,000 DA monthly for all your cars")
    
    with st.form("upload_form"):
        model = st.text_input("Car Brand & Model Details (e.g. Golf 8 R-Line, Mercedes C200):")
        price = st.number_input("Daily Rental Fee (DA):", min_value=1000, value=7000)
        req_ins = st.checkbox("Toggle Upfront Security Deposit Requirement")
        ins_val = st.number_input("Insurance Value (DA):", min_value=0, value=0)
        
        if st.form_submit_button("Publish Vehicle Listing"):
            if not st.session_state.user: st.error("⚠️ Configure your Agency Name in the sidebar panel first!")
            elif model:
                df = pd.read_csv(CARS_FILE)
                new_row = pd.DataFrame([{'Agency_Name': st.session_state.user, 'Phone': "0555123456", 'Wilaya': "Algiers", 'Car_Name': model, 'Price_DA': price, 'Requires_Insurance': req_ins, 'Insurance_Amount': ins_val if req_ins else 0, 'Total_Trips': 0, 'Rating': 5.0}])
                pd.concat([df, new_row], ignore_index=True).to_csv(CARS_FILE, index=False)
                st.success(f"Success! '{model}' is now live on the index list.")

# SECURE COMMUNICATIONS HUB LAYER
st.markdown("---")
st.title("💬 Secure Messaging Center")

if not st.session_state.user:
    st.warning("Please specify an active profile name inside the sidebar configuration to check your inbox logs.")
else:
    df_m = pd.read_csv(CHATS_FILE)
    threads = pd.Series(list(df_m[df_m['Sender'] == st.session_state.user]['Receiver']) + list(df_m[df_m['Receiver'] == st.session_state.user]['Sender'])).dropna().unique()
    
    if len(threads) == 0:
        st.info("Your message exchange ledger history is currently clear.")
    else:
        chat_partner = st.selectbox("Open Active Thread Conversation:", threads)
        if chat_partner:
            df_m.loc[(df_m['Sender'] == chat_partner) & (df_m['Receiver'] == st.session_state.user), 'Is_Read'] = True
            df_m.to_csv(CHATS_FILE, index=False)
            
            log_df = df_m[((df_m['Sender'] == st.session_state.user) & (df_m['Receiver'] == chat_partner)) | ((df_m['Sender'] == chat_partner) & (df_m['Receiver'] == st.session_state.user))]
            
            for _, msg in log_df.iterrows():
                side = "right" if msg['Sender'] == st.session_state.user else "left"
                bubble = "#0076FF" if msg['Sender'] == st.session_state.user else "#2C2F38"
                st.markdown(f'<div style="text-align: {side}; margin-bottom: 5px;"><span style="background-color: {bubble}; padding: 8px 12px; border-radius: 12px; display: inline-block; color: white;"><b>{msg["Sender"]}:</b> {msg["Message"]}</span></div>', unsafe_allow_html=True)
                
            with st.form("send_reply", clear_on_submit=True):
                txt = st.text_input("Write response message:")
                if st.form_submit_button("Send") and txt:
                    df_wr = pd.read_csv(CHATS_FILE)
                    new_r = pd.DataFrame([{'Sender': st.session_state.user, 'Receiver': chat_partner, 'Timestamp': datetime.now().strftime("%M:%S"), 'Message': txt, 'Is_Read': False}])
                    pd.concat([df_wr, new_r], ignore_index=True).to_csv(CHATS_FILE, index=False)
                    st.rerun()
