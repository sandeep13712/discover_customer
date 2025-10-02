import streamlit as st
import pandas as pd
import numpy as np

# Set the page configuration for a wider layout
st.set_page_config(layout="wide")

# --- 1. Load and Cache the data ---
@st.cache_data
def load_data():
    """Loads all CSV files and returns them as a dictionary of dataframes."""
    try:
        df_owner = pd.read_csv("owner.csv")
        df_house = pd.read_csv("house.csv")
        df_ad_ratings = pd.read_csv("ad_ratings.csv")
        df_service_visit = pd.read_csv("service_visit.csv")
        df_advertisement = pd.read_csv("advertisement.csv")
        return {
            "owner": df_owner,
            "house": df_house,
            "ad_ratings": df_ad_ratings,
            "service_visit": df_service_visit,
            "advertisement": df_advertisement,
        }
    except FileNotFoundError:
        st.error("Please run the data generation script first to create the CSV files.")
        return None

data = load_data()
if data is None:
    st.stop()

# Assign dataframes for easier access
df_owner = data["owner"]
df_house = data["house"]
df_ad_ratings = data["ad_ratings"]
df_service_visit = data["service_visit"]
df_advertisement = data["advertisement"]

# --- 2. Build the app layout ---
st.title("Market Size Estimator for New Businesses")
st.write("Use the dropdowns below to define the new business's target profile and estimate their potential customer base in our network.")
st.markdown("---")

# Use columns for a better layout
col1, col2, col3 = st.columns(3)

with col1:
    st.header("Business Profile")
    # Question 1: What type of business is it?
    ad_category = st.selectbox(
        "1. What is the business's main category?",
        options=['Any'] + list(df_advertisement['category'].unique()),
        help="Select the category that best fits the business's offering."
    )

    # Question 2: Who is your ideal customer? (Inferred target attributes)
    ad_offer_value_prop = st.multiselect(
        "2. What value proposition does the business offer?",
        options=list(df_advertisement['ad_offer_value_prop'].unique()),
        default=[],
        help="Select any that apply. E.g., 'cost_savings', 'convenience'."
    )
    
    # Question 3: Ad Tone
    ad_headline_tone = st.multiselect(
        "3. What is the ad's intended tone?",
        options=list(df_advertisement['ad_headline_tone'].unique()),
        default=[],
        help="Select the tone that fits the ad content."
    )

with col2:
    st.header("Target Customer Demographics")
    # Age Bracket
    age_bracket = st.multiselect(
        "4. Which age bracket is the target customer?",
        options=list(df_owner['age_bracket'].unique()),
        default=[],
        help="Select the target age group for the business."
    )

    # Has Kids
    has_kids = st.selectbox(
        "5. Are the target customers families with kids?",
        options=['Any', 'Yes', 'No'],
        help="Filter for households with or without children."
    )

    # Family Status
    family_status = st.multiselect(
        "6. What is the target family status?",
        options=list(df_owner['family_status'].unique()),
        default=[],
        help="Filter by family composition."
    )

with col3:
    st.header("Target Home & Location")
    # Neighborhood Demographics
    neighborhood_demographics = st.multiselect(
        "7. Which neighborhood type is the target?",
        options=list(df_house['neighborhood_demographics'].unique()),
        default=[],
        help="Filter by general neighborhood type."
    )
    
    # House Age Bracket
    house_age_bracket = st.multiselect(
        "8. What is the age bracket of the target homes?",
        options=list(df_house['house_age_bracket'].unique()),
        default=[],
        help="Filter by the age of the houses."
    )

    # House Size
    min_sqft, max_sqft = int(df_house['house_size_sqft'].min()), int(df_house['house_size_sqft'].max())
    house_size_sqft = st.slider(
        "9. What is the size range of the target homes (sqft)?",
        min_value=min_sqft, max_value=max_sqft, value=(min_sqft, max_sqft)
    )

st.markdown("---")

# --- 3. Calculation and display logic ---
if st.button("Calculate Market Size"):
    st.subheader("Results")
    
    # Start with all owners and progressively filter
    filtered_owners = df_owner.copy()
    
    # Filter owners based on demographic criteria
    if age_bracket:
        filtered_owners = filtered_owners[filtered_owners['age_bracket'].isin(age_bracket)]
    if has_kids == 'Yes':
        filtered_owners = filtered_owners[filtered_owners['has_kids'] == True]
    elif has_kids == 'No':
        filtered_owners = filtered_owners[filtered_owners['has_kids'] == False]
    if family_status:
        filtered_owners = filtered_owners[filtered_owners['family_status'].isin(family_status)]
    
    # Filter houses based on property criteria
    filtered_houses = df_house[
        (df_house['house_size_sqft'] >= house_size_sqft[0]) & 
        (df_house['house_size_sqft'] <= house_size_sqft[1])
    ]
    if neighborhood_demographics:
        filtered_houses = filtered_houses[filtered_houses['neighborhood_demographics'].isin(neighborhood_demographics)]
    if house_age_bracket:
        filtered_houses = filtered_houses[filtered_houses['house_age_bracket'].isin(house_age_bracket)]

    # Get the owners who live in the filtered houses
    owners_in_filtered_houses = filtered_houses['owner_id'].unique()
    filtered_owners = filtered_owners[filtered_owners['owner_id'].isin(owners_in_filtered_houses)]
    
    # Filter for owners who showed positive engagement with similar ad content
    positive_ratings_owners = set()
    if ad_category != 'Any':
        # Find ads with matching category
        matching_ads = df_advertisement[df_advertisement['category'] == ad_category]['ad_id']
        # Find ratings for these ads
        relevant_ratings = df_ad_ratings[df_ad_ratings['ad_id'].isin(matching_ads)]
        # Filter for positive ratings (4 or 5 stars)
        positive_ratings = relevant_ratings[relevant_ratings['rating'] >= 4]
        
        # Get the owners who made these positive ratings
        relevant_visits = df_service_visit[df_service_visit['visit_id'].isin(positive_ratings['visit_id'])]
        owners_from_positive_ratings = df_house[df_house['house_id'].isin(relevant_visits['house_id'])]['owner_id']
        positive_ratings_owners.update(owners_from_positive_ratings.unique())
    
    # If a category was selected, further filter the owners to only include those who have previously engaged positively
    if ad_category != 'Any':
        filtered_owners = filtered_owners[filtered_owners['owner_id'].isin(positive_ratings_owners)]

    # Final count
    market_size = filtered_owners['owner_id'].nunique()
    
    if market_size > 0:
        st.success(f"**Potential Customer Base Size: {market_size} homeowners**")
    else:
        st.warning("No customers matched your criteria. Try broadening your selection.")
        
    st.info(f"Based on the analysis of {df_owner['owner_id'].nunique()} homeowners in our database.")
    
    st.markdown("---")
    st.caption("Disclaimer: This is an estimation based on historical data and selected criteria.")

