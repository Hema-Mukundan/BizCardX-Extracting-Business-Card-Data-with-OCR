#Loading important libraries
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import cv2
import pandas as pd
import numpy as np
import sqlite3
import time

# Connect to a database (or create a new one if it doesn't exist)
conn = sqlite3.connect('bizcard_database.db')
cursor = conn.cursor()

#Create a table
cursor.execute('''CREATE TABLE IF NOT EXISTS card_details
              (Id INTEGER PRIMARY KEY,
              Cardholder_Name TEXT,
              Designation TEXT,
              Address VARCHAR,
              Pincode INTEGER,
              Mobile INTEGER,
              email VARCHAR,
              Website VARCHAR,
              Company_Name VARCHAR)
        ''')
conn.commit()

#Setting Streamlit page
with st.sidebar:
    selected =option_menu(
        menu_title=None,
        options= [ "Home", "BizCard_Data"],
        icons=["house","credit-card"],
        default_index=0
    )
if selected == "Home":
    st.title (":orange[BizCardX: Extracting Business Card Data with OCR]")
    st.write('<style>p {  font-style: normal;  font-size: 25px;</style>', unsafe_allow_html=True)

    # Using HTML and CSS to style the text
    st.markdown("""<div style="text-align: justify; text-justify: inter-word; font-size: 25px;">
            The project aims at developing a Streamlit application that allows users to upload an image of a 
            <span style="color: blue;">business card</span> and extract relevant information using <span style="color: blue;">easyOCR</span>. The extracted information includes 
            <span style="color: blue;">Cardholder Name, Designation, Address, Pincode, Mobile number, email, website URL and Company's name</span>. 
            This information should then be displayed in the application's <span  style="color: blue;">graphical user interface (GUI)</span>. 
            The application should allow users to save the extracted information into the database</span>. 
            The database should be able to store multiple entries, each with its own extracted information.</div>""", unsafe_allow_html=True)  
    st.write('')
    st.write('')
    st.markdown("**:orange[Technologies used]: :blue[OCR, Streamlit GUI, SQL, Python]**")

if selected == "BizCard_Data":
    st.header (":orange[Extracting Business Card Data with OCR]")
    data = ['Insert Card_Data', 'View Card_Data', 'Update Card_Data', 'Delete Card_Data']
    st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    choose_option = st.radio("Select An Option", data)

    if choose_option == 'Insert Card_Data':
        file_upload = st.file_uploader(":blue[Please Upload Business Card to process:]",type=["jpg", "jpeg", "png", "tiff", "tif", "gif"])
        
        if file_upload != None:
            image = cv2.imdecode(np.fromstring(file_upload.read(), np.uint8), 1)
            with st.spinner('In progress...'):
                time.sleep(3)
            st.image(image, caption='Uploaded Successfully', use_column_width=True)

            reader = easyocr.Reader(['en'])
            if st.button('Upload to Database'):
                biz_card = reader.readtext(image, detail=0)
                text = "\n".join(biz_card)
            
            # st.success("Data Inserted")
                insert_data = "INSERT INTO card_details (Cardholder_Name, Designation, Address, Pincode, Mobile, email, Website, Company_Name) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?)"
                values = (biz_card[0], biz_card[1], biz_card[2], biz_card[3], biz_card[4], biz_card[5], biz_card[6], biz_card[7])
                    
                cursor.execute(insert_data, values)
                conn.commit()
                    
                st.success("Data Inserted into the Database successfully")            
        else:
            st.write("No Business Card uploaded!")
        
    if choose_option == 'View Card_Data':
        cursor.execute("SELECT * FROM card_details")
        result = cursor.fetchall()
        df = pd.DataFrame(result,
                        columns=['Id', 'Cardholder_Name', 'Designation', 'Address', 'Pincode', 'Mobile', 'email', 'Website', 'Company_Name'])
        st.write(df)
    
    if choose_option == 'Update Card_Data':
        try:
            cursor.execute("SELECT Id, Cardholder_Name FROM card_details")
            result = cursor.fetchall()
            business_cards = {}

            for row in result:
                business_cards[row[1]] = row[0]
            select_card_name = st.selectbox("Select Card To Edit", list(business_cards.keys()))

            cursor.execute("SELECT * FROM card_details WHERE Cardholder_Name=?", (select_card_name,))
            result = cursor.fetchone()

            Cardholder_Name = st.text_input("Cardholder_Name", result[1])
            Designation = st.text_input("Designation", result[2])
            Address = st.text_input("Address", result[3])
            Pincode = st.text_input("Pincode", result[4])
            Mobile = st.text_input("Mobile", result[5])
            email = st.text_input("Email", result[6])
            Website = st.text_input("Website", result[7])
            Company_Name = st.text_input("Company_Name", result[8])
        
            if st.button("Update"):
                cursor.execute(
                    "UPDATE card_details SET Cardholder_Name=?, Designation=?, Address=?, Pincode=?, Mobile=?, email=?, Website=?, Company_Name=? WHERE Cardholder_Name=?",
                    (Cardholder_Name, Designation, Address, Pincode, Mobile, email, Website, Company_Name, select_card_name))
                conn.commit()
                st.success("Card Data Updated")
        except Exception as e:
            st.error(f"Error: {e}")

    if choose_option == 'Delete Card_Data':
        try:
            cursor.execute("SELECT Id, Cardholder_Name FROM card_details")
            result = cursor.fetchall()
            business_cards = {}

            for row in result:
                business_cards[row[1]] = row[0]
            select_card_name = st.selectbox("Select Card To Delete", list(business_cards.keys()))

            if st.button("Delete Card"):
                cursor.execute("DELETE FROM card_details WHERE Cardholder_Name=?", (select_card_name,))
                conn.commit()
                st.success("Card Data Deleted")
        except Exception as e:
            st.error(f"Error: {e}")
