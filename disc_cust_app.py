import streamlit as st
import pandas as pd
import numpy as np

# Function to generate dummy data and save it to CSV files
def generate_dummy_data():
    # Owner Data
    df_owner = pd.DataFrame({
        'owner_id': range(1, 101),
        'age_bracket': np.random.choice(['18-24', '25-34', '35-44', '45-54', '55+'], size=100),
        'has_kids': np.random.choice([True, False], size=100),
        'family_status': np.random.choice(['Single', 'Married', 'Divorced', 'Widowed'], size=100)
    })
    df_owner.to_csv("owner.csv", index=False)

    # House Data
    df_house = pd.DataFrame({
        'house_id': range(1, 101),
        'owner_id': np.random.randint(1, 101, size=100),
        'neighborhood_demographics': np.random.choice(['Urban', 'Suburban', 'Rural'], size=100),
        'house_age_bracket': np.random.choice(['0-10 years', '11-20 years', '21+ years'], size=100),
        'house_size_sqft': np.random.randint(500, 5000, size=100)
    })
    df_house.to_csv("house.csv", index=False)

    # Advertisement Ratings Data
    df_ad_ratings = pd.DataFrame({
        'ad_id': np.random.randint(1, 21, size=200),
        'visit_id': np.random.randint(1, 101, size=200),
        'rating': np.random.randint(1, 6, size=200)
    })
    df_ad_ratings.to_csv("ad_ratings.csv", index=False)

    # Service Visit Data
    df_service_visit = pd.DataFrame({
        'visit_id': range(1, 101),
        'house_id': np.random.randint(1, 101, size=100)
    })
    df_service_visit.to_csv("service_visit.csv", index=False)

    # Advertisement Data
    df_advertisement = pd.DataFrame({
        "ad_id": range(1, 21),
        "category": np.random.choice(["Food", "Electronics"], size=20),
        "ad_offer_value_prop": np.random.choice(["cost_savings", "convenience", "premium_quality"], size=20),
        "ad_offer_tone": np.random.choice(["casual", "formal", "humorous"], size=20)
    })
    df_advertisement.to_csv("advertisement.csv", index=False)

# Generate dummy data if not already present
generate_dummy_data()

# Streamlit app code starts here

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    """Loads all CSV files and returns them as a dictionary of dataframes."""
    ry:
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

df_owner = data["owner"]
df_house = data["house"]
df_ad_ratings = data["ad_ratings"]
df_service_visit = data["service_visit"]
df_advertisement = data["advertisement"]

st.title("Market Size Estimator")
st.write(
   "Use the dropdowns below to define the new business's target profile and estimate their potential customer base in our network."
)
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
   st.header("Business Profile")
   ad_category = st.selectbox(
       "1. What is the business's main category?",
       options=["Any"] + list(df_advertisement['category'].unique())
   )

   ad_offer_value_prop = st.multiselect(
       "2. What value proposition does the business offer?",
       options=list(df_advertisement['ad_offer_value_prop'].unique())
   )
   
   ad_tone = st.multiselect(
       "3. Ad Tone",
       options=list(df_advertisement['ad_offer_tone'].unique())
   )

with col2:
   st.header("Target Customer Demographics")
   age_bracket = st.multiselect(
       "4. Which age bracket is the target customer?",
       options=list(df_owner['age_bracket'].unique())
   )

   has_kids_option = ["Any", True, False]
   has_kids_display_options = ["Any", "Yes", "No"]
   
   has_kids_index_selected_by_default_in_UI_component_to_render_first_time_around_as_any_filter_at_startup_and_empty_list_is_sent_to_streamlit_app=data.get('has_kids').apply(lambda x: x == True).any()
