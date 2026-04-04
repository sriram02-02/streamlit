import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import os
import json
import pymysql
# st.set_page_config(
#     page_title="PhonePe Pulse Dashboard",
#     page_icon="D:\streamlit\env\Scripts\phonepe-icon.webp",
#     layout="wide"
# )
# st.title("PhonePe Pulse Analysis")
# st.sidebar.title("Phonepe Pulse Analysis")
# page=st.sidebar.radio("goto", ["Home", "Business case study"])
# st.markdown("""
# <style>

# .stApp {
#     background-color: #0E1117;
# }

# section[data-testid="stSidebar"] {
#     background-color: #5f259f;
# }

# h1 {
#     color:white;
# }

# </style>
# """, unsafe_allow_html=True)
# if page=="Home":
#     st.header("Welcome to the PhonePe Pulse Analysis Dashboard!")
#     st.write("This dashboard provides insights into the transaction data of PhonePe, a leading digital payments platform in India. Explore various aspects of the data, including transaction trends, user behavior, and regional analysis.")
# elif page=="Business case study":
#     option=st.selectbox("Select a business case study", ["Transaction Trends", "User Behavior Analysis", "Regional Analysis"])
    
def get_agg_insurance():
    path="pulse/data/aggregated/insurance/country/india/state/"
    agg_state=os.listdir(path)
    clm={"state":[],"year":[],"quarter":[],"insurance_type":[],"insured_count":[],"insured_amount":[]}
    if os.path.exists(path):
        agg_state=os.listdir(path)
        for s in agg_state:
            ps=path+s+"/"
            if os.path.exists(ps):
                agg_year=os.listdir(ps)
                for y in agg_year:
                    psy=ps+y+"/"
                    if os.path.exists(psy):
                        agg_quarter=os.listdir(psy)
                        for q in agg_quarter:
                            psyq=psy+q
                            if os.path.exists(psyq):
                                try:
                                    Data=open(psyq,"r")
                                    D=json.load(Data)
                                    if "transactionData" in D["data"]:
                                        for d in D["data"]["transactionData"]:
                                            Name=d["name"]
                                            Count=d["paymentInstruments"][0]["count"]
                                            Amount=d["paymentInstruments"][0]["amount"]
                                            clm["state"].append(s)
                                            clm["year"].append(y)
                                            clm["quarter"].append(int(q.strip(".json")))
                                            clm["insurance_type"].append(Name)
                                            clm["insured_count"].append(Count)
                                            clm["insured_amount"].append(Amount)
                                except Exception as e:
                                    st.error(f"Error processing file {psyq}: {e}")
    return pd.DataFrame(clm)
        
    
def get_agg_transaction():
    path="pulse/data/aggregated/transaction/country/india/state/"

    agg_state=os.listdir(path)
    clm={"state":[],"year":[],"quarter":[],"transaction_type":[],"transaction_count":[],"transaction_amount":[]}
    if os.path.exists(path):
        for s in agg_state:
            ps=path+s+"/"
            if os.path.exists(ps):
                agg_year=os.listdir(ps)
                for y in agg_year:
                    psy=ps+y+"/"
                    if os.path.exists(psy):
                        agg_quarter=os.listdir(psy)
                        for q in agg_quarter:
                            psyq=psy+q
                            if os.path.exists(psyq):
                                try:
                                    Data=open(psyq,"r")
                                    D=json.load(Data)
                                    for d in D["data"]["transactionData"]:
                                        Name=d["name"]
                                        Count=d["paymentInstruments"][0]["count"]
                                        Amount=d["paymentInstruments"][0]["amount"]
                                        clm["state"].append(s)
                                        clm["year"].append(y)
                                        clm["quarter"].append(int(q.strip(".json")))
                                        clm["transaction_type"].append(Name)
                                        clm["transaction_count"].append(Count)
                                        clm["transaction_amount"].append(Amount)
                                except Exception as e:
                                    st.error(f"Error processing file {psyq}: {e}")

    return pd.DataFrame(clm)
        

def get_agg_user():
    path="pulse/data/aggregated/user/country/india/state/"

    combined_data={
    "state":[],
    "year":[],
    "quarter":[],
    "Registered_users":[],
    "app_opens":[],
    "brand":[],
    "count":[],
    "percentage":[]
    }

    if os.path.exists(path):
        agg_state=os.listdir(path)
        for s in agg_state:
            ps=path+s+"/"
            if os.path.exists(ps):
                agg_year=os.listdir(ps)
                for y in agg_year:
                    psy=ps+y+"/"
                    if os.path.exists(psy):
                        agg_quarter=os.listdir(psy)
                        for q in agg_quarter:
                            psyq=psy+q
                            if os.path.exists(psyq):
                                try:
                                    with open(psyq,"r") as f:
                                        D=json.load(f)
                                    aggregated = D.get("data", {}).get("aggregated", {})
                                    devices = D.get("data", {}).get("usersByDevice") or []
                                    reg_users = aggregated.get("registeredUsers")
                                    app_opens = aggregated.get("appOpens")
                                    if devices:
                                        for d in devices:
                                            combined_data["state"].append(s)
                                            combined_data["year"].append(y)
                                            combined_data["quarter"].append(int(q.strip(".json")))
                                            combined_data["Registered_users"].append(reg_users)
                                            combined_data["app_opens"].append(app_opens)
                                            combined_data["brand"].append(d.get("brand"))
                                            combined_data["count"].append(d.get("count"))
                                            combined_data["percentage"].append(d.get("percentage"))
                                    else:
                                        combined_data["state"].append(s)
                                        combined_data["year"].append(y)
                                        combined_data["quarter"].append(int(q.strip(".json")))
                                        combined_data["Registered_users"].append(reg_users)
                                        combined_data["app_opens"].append(app_opens)
                                        combined_data["brand"].append(None)
                                        combined_data["count"].append(None)
                                        combined_data["percentage"].append(None)

                                except Exception as e:
                                    st.error(f"Error processing file {psyq}: {e}")

    return pd.DataFrame(combined_data)
        

def get_map_insurance():
    path="pulse/data/map/insurance/hover/country/india/state/"
    map_state=os.listdir(path)
    insurance_data={"state":[],"year":[],"quarter":[],"insurance_type":[],"insured_count":[],"insured_amount":[]}
    if os.path.exists(path):
        for s in map_state:
            ps=path+s+"/"
            if os.path.exists(ps):
                map_year=os.listdir(ps)
                for y in map_year:
                    psy=ps+y+"/"
                    if os.path.exists(psy):
                        map_quarter=os.listdir(psy)
                        for q in map_quarter:
                            psyq=psy+q
                            if os.path.exists(psyq):
                                try:
                                    Data=open(psyq,"r")
                                    D=json.load(Data)
                                    hover_data = D.get("data", {}).get("hoverDataList")
                                    if hover_data:
                                        for state_data in hover_data:
                                            state_name = state_data.get("name","").title()
                                            for metric in state_data.get("metric", []):
                                                Name=metric["type"]
                                                Count=metric["count"]
                                                Amount=metric["amount"]
                                                insurance_data["state"].append(s)
                                                insurance_data["year"].append(y)
                                                insurance_data["quarter"].append(int(q.strip(".json")))
                                                insurance_data["insurance_type"].append(Name)
                                                insurance_data["insured_count"].append(Count)
                                                insurance_data["insured_amount"].append(Amount)
                                except Exception as e:
                                    st.error(f"Error processing file {psyq}: {e}")
    return pd.DataFrame(insurance_data)
        
    
def get_map_transaction():
    path="pulse/data/map/transaction/hover/country/india/state/"
    map_state=os.listdir(path)

    transaction_data={
        "state":[],
        "year":[],
        "quarter":[],
        "district":[],
        "transaction_type":[],
        "transaction_count":[],
        "transaction_amount":[]
    }

    if os.path.exists(path):
        for s in map_state:
            ps=path+s+"/"
            if os.path.exists(ps):
                map_year=os.listdir(ps)
                for y in map_year:
                    psy=ps+y+"/"
                    if os.path.exists(psy):
                        map_quarter=os.listdir(psy)
                        for q in map_quarter:
                            psyq=psy+q
                            if os.path.exists(psyq):
                                try:
                                    with open(psyq,"r") as f:
                                        D=json.load(f)

                                    hover_data = D.get("data", {}).get("hoverDataList")

                                    if hover_data:
                                        for state_data in hover_data:

                                            Name = state_data.get("name", "")
                                            metrics = state_data.get("metric", [])

                                            if metrics:
                                                for m in metrics:  # safer than [0]

                                                    transaction_data["state"].append(s)
                                                    transaction_data["year"].append(y)
                                                    transaction_data["quarter"].append(int(q.strip(".json")))
                                                    transaction_data["district"].append(Name)
                                                    transaction_data["transaction_type"].append(m.get("type"))
                                                    transaction_data["transaction_count"].append(m.get("count"))
                                                    transaction_data["transaction_amount"].append(m.get("amount"))

                                except Exception as e:
                                    st.error(f"Error processing file {psyq}: {e}")

    return pd.DataFrame(transaction_data)
        
    

    
def get_map_user():
    path="pulse/data/map/user/hover/country/india/state/"
    map_state=os.listdir(path)

    user_map_data={
        "state":[],
        "year":[],
        "quarter":[],
        "Registered_users":[],
        "app_opens":[]
    }

    if os.path.exists(path):
        for s in map_state:
            ps=path+s+"/"
            if os.path.exists(ps):
                map_year=os.listdir(ps)
                for y in map_year:
                    psy=ps+y+"/"
                    if os.path.exists(psy):
                        map_quarter=os.listdir(psy)
                        for q in map_quarter:
                            psyq=psy+q
                            if os.path.exists(psyq):
                                try:
                                    with open(psyq,"r") as Data:
                                            D=json.load(Data)

                                    hover_data = D.get("data", {}).get("hoverData")

                                    if hover_data:
                                        for district, state_data in hover_data.items():

                                            user_map_data["state"].append(s)
                                            user_map_data["year"].append(y)
                                            user_map_data["quarter"].append(int(q.strip(".json")))
                                            user_map_data["Registered_users"].append(state_data.get("registeredUsers", 0))
                                            user_map_data["app_opens"].append(state_data.get("appOpens", 0))

                                except Exception as e:
                                    st.error(f"Error processing file {psyq}: {e}")

    return pd.DataFrame(user_map_data)
        
    

def get_top_insurance():
    path="pulse/data/top/insurance/country/india/state/"
    top_state=os.listdir(path)
    top_insurance_data={"state":[],"year":[],"quarter":[],"district":[],"insurance_type":[],"insured_count":[],"insured_amount":[]}
    if os.path.exists(path):
        for s in top_state:
            ps=path+s+"/"
            if os.path.exists(ps):
                top_year=os.listdir(ps)
                for y in top_year:
                    psy=ps+y+"/"
                    if os.path.exists(psy):
                        top_quarter=os.listdir(psy)
                        for q in top_quarter:
                            psyq=psy+q
                            if os.path.exists(psyq):
                                try:
                                    Data=open(psyq,"r")
                                    D=json.load(Data)
                                    top_data = D.get("data", {}).get("districts", [])
                                    for entry in top_data:

                                        Name=entry["entityName"]
                                        Type=entry["metric"]["type"]
                                        Count=entry["metric"]["count"]
                                        Amount=entry["metric"]["amount"]
                                        top_insurance_data["state"].append(s)
                                        top_insurance_data["year"].append(y)
                                        top_insurance_data["quarter"].append(int(q.strip(".json")))
                                        top_insurance_data["district"].append(Name)
                                        top_insurance_data["insurance_type"].append(Type)
                                        top_insurance_data["insured_count"].append(Count)
                                        top_insurance_data["insured_amount"].append(Amount)
                                except Exception as e:
                                    st.error(f"Error processing file {psyq}: {e}")
    return pd.DataFrame(top_insurance_data)
        
    
def get_top_transaction():
    path="pulse/data/top/transaction/country/india/state/"
    top_state=os.listdir(path)
    top_transaction_data={"state":[],"year":[],"quarter":[],"district":[],"transaction_type":[],"transaction_count":[],"transaction_amount":[]} 
    if os.path.exists(path):
        for s in top_state:
            ps=path+s+"/"
            if os.path.exists(ps):
                top_year=os.listdir(ps)
                for y in top_year:
                    psy=ps+y+"/"
                    if os.path.exists(psy):
                        top_quarter=os.listdir(psy)
                        for q in top_quarter:
                            psyq=psy+q
                            if os.path.exists(psyq):
                                try:
                                    Data=open(psyq,"r")
                                    D=json.load(Data)
                                    top_data = D.get("data", {}).get("districts", [])
                                    for entry in top_data:
                                        Name=entry["entityName"]
                                        Type=entry["metric"]["type"]
                                        Count=entry["metric"]["count"]
                                        Amount=entry["metric"]["amount"]
                                        top_transaction_data["state"].append(s)
                                        top_transaction_data["year"].append(y)
                                        top_transaction_data["quarter"].append(int(q.strip(".json")))
                                        top_transaction_data["district"].append(Name)
                                        top_transaction_data["transaction_type"].append(Type)
                                        top_transaction_data["transaction_count"].append(Count)
                                        top_transaction_data["transaction_amount"].append(Amount)
                                except Exception as e:
                                    st.error(f"Error processing file {psyq}: {e}")
    return pd.DataFrame(top_transaction_data)
        
    
def get_top_user():
    path="pulse/data/top/user/country/india/state/"
    top_state=os.listdir(path)
    top_user_data={"state":[],"year":[],"quarter":[],"district":[],"Registered_users":[]}
    if os.path.exists(path):
        for s in top_state:
            ps=path+s+"/"
            if os.path.exists(ps):
                top_year=os.listdir(ps)
                for y in top_year:
                    psy=ps+y+"/"
                    if os.path.exists(psy):
                        top_quarter=os.listdir(psy)
                        for q in top_quarter:
                            psyq=psy+q
                            if os.path.exists(psyq):
                                try:
                                    Data=open(psyq,"r")
                                    D=json.load(Data)
                                    top_data = D.get("data", {}).get("districts", [])
                                    for entry in top_data:

                                        Name=entry["name"]
                                        Registered_users=entry["registeredUsers"]
                                        top_user_data["state"].append(s)
                                        top_user_data["year"].append(y)
                                        top_user_data["quarter"].append(int(q.strip(".json")))
                                        top_user_data["district"].append(Name)
                                        top_user_data["Registered_users"].append(Registered_users)
                                except Exception as e:
                                    st.error(f"Error processing file {psyq}: {e}")
    return pd.DataFrame(top_user_data)
        
    
                        




