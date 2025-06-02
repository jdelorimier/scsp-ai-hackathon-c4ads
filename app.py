import streamlit as st
import pandas as pd

# Mock function to simulate querying a backend or model
def run_query(user_input):
    # Replace this with your real query logic
    if user_input.strip().lower() == "cats":
        return {
            "results": [
                {"title": "Cat 1", "image_url": "https://i.ebayimg.com/images/g/7cIAAOSwFHZnMA8N/s-l225.jpg"},
                {"title": "Cat 2", "image_url": "https://i.ebayimg.com/images/g/7cIAAOSwFHZnMA8N/s-l225.jpg"},
            ]
        }
    else:
        return {"results": []}
    
# --- Mock analysis function ---
def run_analysis(results):
    # Replace with real analysis logic
    st.subheader("Analysis Results")
    st.write(f"Running analysis on {len(results)} items...")
    for r in results:
        st.markdown(f"✅ Processed: **{r['title']}**")

# Streamlit UI
st.title("Image Search App")

# Step 1: User input
user_input = st.text_input("Enter your query:")

# Only run query if user submitted something
if user_input:
    response = run_query(user_input)

    results = response.get("results", [])
    
    if results:
        st.write(f"Found {len(results)} results:")

        # Display table with title and image preview
        for item in results:
            cols = st.columns([1, 3])
            cols[0].write(f"**{item['title']}**")
            cols[1].image(item['image_url'], width=150)
            
        # --- Run Analysis Button ---
        if st.button("Run analysis"):
            run_analysis(results)
    else:
        st.warning("No results found.")