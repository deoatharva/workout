import streamlit as st
import pymongo
from datetime import datetime, timedelta

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["workout_tracker"]
collection = db["daily_workouts"]

# Initialize workout data
start_date = datetime(2025, 1, 1)
today = datetime(2025, 1, 3)  # Assume today is January 3, 2025
day_difference = (today - start_date).days + 1
initial_reps = 20

# Function to calculate workout plan for a given day
def get_workout_plan(day):
    reps = initial_reps + (day - 1) * 5
    return {
        "pushups": reps,
        "situps": reps,
        "squats": reps,
    }

# Fetch or initialize today's workout data
def fetch_today_workout():
    today_str = today.strftime("%Y-%m-%d")
    workout = collection.find_one({"date": today_str})
    if not workout:
        workout_plan = get_workout_plan(day_difference)
        workout = {
            "date": today_str,
            "pushups": workout_plan["pushups"],
            "situps": workout_plan["situps"],
            "squats": workout_plan["squats"],
            "done": False,
        }
        collection.insert_one(workout)
    return workout

# Calculate monthly and yearly status
def calculate_status():
    all_workouts = list(collection.find())
    completed_days = sum(1 for w in all_workouts if w["done"])
    missed_days = sum(1 for w in all_workouts if not w["done"])
    return completed_days, missed_days

# Streamlit UI
st.title("Daily Workout Tracker")

workout = fetch_today_workout()
st.header(f"Today's Workout: {today.strftime('%B %d, %Y')}")

st.write(f"- Pushups: {workout['pushups']}")
st.write(f"- Situps: {workout['situps']}")
st.write(f"- Squats: {workout['squats']}")

# Checkbox to mark workout as done
if st.checkbox("Mark as Done", value=workout["done"]):
    if not workout["done"]:
        collection.update_one(
            {"date": workout["date"]}, {"$set": {"done": True}}
        )
        st.success("Workout marked as done!")
    else:
        st.info("Workout already marked as done.")

# Monthly and yearly status
if today.day == 31 or today.month != (today + timedelta(days=1)).month:
    st.subheader("Monthly Status")
    completed_days, missed_days = calculate_status()
    st.write(f"Days Completed: {completed_days}")
    st.write(f"Days Missed: {missed_days}")

if today.month == 12 and today.day == 31:
    st.subheader("Yearly Status")
    completed_days, missed_days = calculate_status()
    st.write(f"Days Completed: {completed_days}")
    st.write(f"Days Missed: {missed_days}")
