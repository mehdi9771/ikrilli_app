import streamlit as pd_st
import pandas as pd
from datetime import datetime
import os

# Set up mobile-responsive screen settings
pd_st.set_page_config(page_title="Ikrilli - Car Rental", page_icon="🚗", layout="centered")

# Custom CSS styling to optimize visual layout for smartphones
pd_st.markdown("""
    <style>
    .stApp { background-color: #111216; color: #FFFFFF; }
    .car-card { background-color: #1F232C; padding: 18px; border-radius: 12px; margin-bottom: 15px; border-left: 5px solid #FF4B4B; }
    .badge-card { background-color: #1F232C; padding: 18px; border-radius: 12px; margin-bottom: 15px; border-left: 5px solid #00E676; }
    .green-badge { background-color: #00E676; color: #000000; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    .insurance-label { background-color: #FFA000; color: #000000; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    .free-label { background-color: #2196F3; color: #FFFFFF; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATABASE AND CORE FILE STORAGE INITIALIZATION
# ---------------------------------------------------------
CARS_FILE = "ikrilli_cars.csv"
CHATS_FILE = "ikrilli_chats.csv"

def init_databases():
    if not os.path.exists(CARS_FILE):
        df_cars = pd.DataFrame(columns=[
            'Agency_Name', 'Phone', 'Wilaya', 'Car_Name', 
            'Price_DA', 'Requires_Insurance', 'Insurance_Amount', 
            'Total_Trips', 'Rating'
        ])
        df_cars.to_csv(CARS_FILE, index=False)
        
    if not os.path.exists(CHATS_FILE):
        df_chats = pd.DataFrame(columns=['Sender', 'Receiver', 'Timestamp', 'Message', 'Is_Read'])
        df_chats.to_csv(CHATS_FILE, index=False)

init_databases()

# ---------------------------------------------------------
# GLOBAL APP STATE NAVIGATION
# ---------------------------------------------------------
if 'user_role' not in pd_st.session_state:
    pd_st.session_state.user_role = "Customer"
if 'username' not in pd_st.session_state:
    pd_st.session_state.username = ""

# Sidebar Control Panel Navigation Header
pd_st.sidebar.title("🔑 Ikrilli Access Control")
role_selection = pd_st.sidebar.radio("Select Your Account Profile:", ["Customer", "Agency Renter"])

# Account Name Input Field to Route Custom Real-time Messages Correctly
username_input = pd_st.sidebar.text_input("Enter Your Profile/Agency Name:", pd_st.session_state.username)
if username_input:
    pd_st.session_state.username = username_input
pd_st.session_state.user_role = role_selection

# ---------------------------------------------------------
# REAL-TIME LIVE NOTIFICATION BANNERS
# ---------------------------------------------------------
if pd_st.session_state.username:
    df_chats_notify = pd.read_csv(CHATS_FILE)
    unread_alerts = df_chats_notify[
        (df_chats_notify['Receiver'] == pd_st.session_state.username) & 
        (df_chats_notify['Is_Read'] == False)
    ]
    if not unread_alerts.empty:
        pd_st.toast(f"🔔 Notification: You have {len(unread_alerts)} new message(s) waiting for you!", icon="💬")

# ---------------------------------------------------------
# INTERFACE VIEW 1: CUSTOMER DISCOVERY AND BOOKING PORTAL
# ---------------------------------------------------------
if pd_st.session_state.user_role == "Customer":
    pd_st.title("🚗 Find Your Next Rental")
    pd_st.subheader("Instant smart search engine across Algeria")
    
    # Visual Search Interface Bars
    col_search, col_wilaya = pd_st.columns(2)
    with col_search:
        search_keyword = pd_st.text_input("🔍 Type car name keywords (e.g., Golf, Mercedes, Clio):", "")
    with col_wilaya:
        wilaya_filter = pd_st.selectbox("📍 Select Wilaya:", ["All 58 Wilayas", "Algiers", "Oran", "Constantine", "Sétif", "Annaba"])
        
    hide_insurance = pd_st.checkbox("⚡ Show cars with NO insurance deposit required")
    
    # Load and process the live vehicle marketplace rows
    df_cars = pd.read_csv(CARS_FILE)
    
    if df_cars.empty:
        pd_st.info("No cars listed on the app yet. Switch to Agency Renter mode to submit cars!")
    else:
        # Apply Search Engine Filtering
        if search_keyword:
            df_cars = df_cars[df_cars['Car_Name'].str.contains(search_keyword, case=False, na=False)]
        if wilaya_filter != "All 58 Wilayas":
            df_cars = df_cars[df_cars['Wilaya'] == wilaya_filter]
        if hide_insurance:
            df_cars = df_cars[df_cars['Requires_Insurance'] == False]
            
        pd_st.write(f"Showing {len(df_cars)} available configurations matching your rules:")
        
        # Display the car catalog dynamically to the browser interface
        for index, row in df_cars.iterrows():
            # Check conditions to apply the custom "Green Car Badge"
            has_green_badge = int(row['Total_Trips']) > 50 and float(row['Rating']) > 4.7
            card_style = "badge-card" if has_green_badge else "car-card"
            
            with pd_st.container():
                pd_st.markdown(f"""
                <div class="{card_style}">
                    <h3>🚗 {row['Car_Name']}</h3>
                    <p><b>🏢 Agency:</b> {row['Agency_Name']} (📍 {row['Wilaya']})</p>
                    <p><b>💰 Daily Fee:</b> <span style="font-size:20px; color:#FF4B4B; font-weight:bold;">{row['Price_DA']:,} DA</span></p>
                    <p>⭐ Rating: {row['Rating']} ({row['Total_Trips']} bookings completed)</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Append conditional visual indicator tags inline
                col_tag1, col_tag2 = pd_st.columns(2)
                with col_tag1:
                    if has_green_badge:
                        pd_st.markdown('<span class="green-badge">🟢 Green Car - Most Trusted</span>', unsafe_allow_html=True)
                    else:
                        pd_st.markdown('<span class="free-label">Standard Listing</span>', unsafe_allow_html=True)
                with col_tag2:
                    if row['Requires_Insurance']:
                        pd_st.markdown(f'<span class="insurance-label">⚠️ Insurance req: {row["Insurance_Amount"]:,} DA</span>', unsafe_allow_html=True)
                    else:
                        pd_st.markdown('<span class="green-badge">🛡️ No Insurance Deposit</span>', unsafe_allow_html=True)
                
                # Action Booking Controls
                if pd_st.button(f"✉️ Message & Rent from {row['Agency_Name']}", key=f"rent_{index}"):
                    if not pd_st.session_state.username:
                        pd_st.error("⚠️ Please enter your Profile Name in the left sidebar first to start chatting!")
                    else:
                        # Append a default greeting transaction to kickstart communication logs
                        df_chats = pd.read_csv(CHATS_FILE)
                        new_chat = pd.DataFrame([{
                            'Sender': pd_st.session_state.username,
                            'Receiver': row['Agency_Name'],
                            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'Message': f"Salâm! I am interested in renting your {row['Car_Name']} listed for {row['Price_DA']:,} DA. Is it available?",
                            'Is_Read': False
                        }])
                        df_chats = pd.concat([df_chats, new_chat], ignore_index=True)
                        df_chats.to_csv(CHATS_FILE, index=False)
                        pd_st.success(f"Order request sent! Go to the messaging hub panel below to speak with {row['Agency_Name']}.")

# ---------------------------------------------------------
# INTERFACE VIEW 2: AGENCY LISTINGS & INVENTORY MANAGEMENT
# ---------------------------------------------------------
elif pd_st.session_state.user_role == "Agency Renter":
    pd_st.title("💼 Agency Owner Portal")
    pd_st.subheader("Manage your vehicles and monthly listing status")
    pd_st.info("💡 Flat Listing Rules: Your subscription covers ALL your active cars for a flat fee of 15,000 DA monthly.")
    
    # Add a new car configuration form
    with pd_st.form("add_car_form"):
        pd_st.write("### ➕ Upload New Vehicle Fleet Data")
        car_model = pd_st.text_input("Car Brand & Model Name (e.g., Golf 8 R-Line, Mercedes C200):")
        daily_rate = pd_st.number_input("Daily Rental Fee Price (DZD/DA):", min_value=1000, max_value=200000, value=6000, step=500)
        
        ins_checkbox = pd_st.checkbox("Require upfront security insurance cash deposit from buyer?")
        ins_amount = pd_st.number_input("If yes, enter explicit insurance deposit amount (DZD):", min_value=0, max_value=100000, value=0, step=1000)
        
        submit_btn = pd_st.form_submit_button("Publish Vehicle Active On App")
        
        if submit_btn:
            if not pd_st.session_state.username:
                pd_st.error("⚠️ Set your Agency Name in the sidebar before publishing!")
            elif not car_model:
                pd_st.error("⚠️ Vehicle name field cannot be sent blank.")
            else:
                # Append newly input dataset directly to database storage CSV file
                df_cars_load = pd.read_csv(CARS_FILE)
                new_car_row = pd.DataFrame([{
                    'Agency_Name': pd_st.session_state.username,
                    'Phone': "0555123456",  
                    'Wilaya': "Algiers",     
                    'Car_Name': car_model,
                    'Price_DA': daily_rate,
                    'Requires_Insurance': ins_checkbox,
                    'Insurance_Amount': ins_amount if ins_checkbox else 0,
                    'Total_Trips': 0,        
                    'Rating': 5.0            
                }])
Use code with caution.df_cars_load = pd.concat([df_cars_load, new_car_row], ignore_index=True)df_cars_load.to_csv(CARS_FILE, index=False)pd_st.success(f"Success! '{car_model}' has been successfully added to your inventory catalog.")# View active store items belonging to logged agency profilepd_st.write("### 📋 Your Current Displayed Fleet Inventory")df_my_cars = pd.read_csv(CARS_FILE)if not df_my_cars.empty and pd_st.session_state.username:df_my_cars = df_my_cars[df_my_cars['Agency_Name'] == pd_st.session_state.username]if df_my_cars.empty:pd_st.write("No cars uploaded yet under this current agency title profile.")else:pd_st.dataframe(df_my_cars[['Car_Name', 'Price_DA', 'Requires_Insurance', 'Insurance_Amount', 'Total_Trips', 'Rating']], use_container_width=True)else:pd_st.write("Enter your profile name on the sidebar menu panel to access listed records.")---------------------------------------------------------THE PERSISTENT IN-APP MESSAGING INTERFACE FEED HUB---------------------------------------------------------pd_st.markdown("---")pd_st.title("💬 Ikrilli Communications Hub")if not pd_st.session_state.username:pd_st.warning("Please configure your profile account name inside the left sidebar to unlock your inbox logs.")else:df_messages = pd.read_csv(CHATS_FILE)# Isolate unique conversation partners linked to your account profileall_partners = pd.Series(list(df_messages[df_messages['Sender'] == pd_st.session_state.username]['Receiver']) +list(df_messages[df_messages['Receiver'] == pd_st.session_state.username]['Sender'])).dropna().unique()if len(all_partners) == 0:pd_st.info("Your chat history is currently clear.")else:# Choose chat window view dropdown select boxactive_chat_partner = pd_st.selectbox("Select an active thread profile history:", all_partners)if active_chat_partner:# Mark incoming items inside this conversation chain read instantlydf_messages.loc[(df_messages['Sender'] == active_chat_partner) & (df_messages['Receiver'] == pd_st.session_state.username), 'Is_Read'] = Truedf_messages.to_csv(CHATS_FILE, index=False)# Fetch message thread block rows sequentiallythread_df = df_messages[((df_messages['Sender'] == pd_st.session_state.username) & (df_messages['Receiver'] == active_chat_partner)) |((df_messages['Sender'] == active_chat_partner) & (df_messages['Receiver'] == pd_st.session_state.username))].sort_values(by='Timestamp')# Display text fields visually like messaging bubblesfor _, msg_row in thread_df.iterrows():align_style = "right" if msg_row['Sender'] == pd_st.session_state.username else "left"color_bubble = "#0076FF" if msg_row['Sender'] == pd_st.session_state.username else "#2C2F38"pd_st.markdown(f"""{msg_row['Sender']}: {msg_row['Message']}{msg_row['Timestamp']}""", unsafe_allow_html=True)# Reply action entry input box interface form sectionwith pd_st.form("chat_reply_form", clear_on_submit=True):reply_text = pd_st.text_input("Type your response message box:")send_reply = pd_st.form_submit_button("Send Response Text")if send_reply and reply_text:df_chats_save = pd.read_csv(CHATS_FILE)new_reply_row = pd.DataFrame([{'Sender': pd_st.session_state.username,'Receiver': active_chat_partner,'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),'Message': reply_text,'Is_Read': False}])df_chats_save = pd.concat([df_chats_save, new_reply_row], ignore_index=True)df_chats_save.to_csv(CHATS_FILE, index=False)pd_st.rerun()
