from pymongo import MongoClient
import os
import pandas as pd

MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["apple_db"]
apple_collection = db["apple_data"]

# Get the absolute path of the static folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "static", "TDInventory.xlsx")
IMAGE_FOLDER = os.path.join(BASE_DIR, "static", "FruitPictures", "Heritage")  # Fetch from 'Heritage'

def find_image_for_accession(accession_number, cultivar_name):
    """Find an image where the filename contains both the cultivar name and the accession number."""
    if not isinstance(accession_number, str):
        accession_number = str(accession_number)  # Convert to string if it's a number
    
    if not isinstance(cultivar_name, str):
        cultivar_name = str(cultivar_name)  # Convert to string if it's a number or NaN
    else:
        cultivar_name = cultivar_name.replace(" ", "_")  # Normalize name to match file naming
    
    for file in os.listdir(IMAGE_FOLDER):
        if accession_number in file and cultivar_name in file:  # ✅ Match filenames containing both
            return file  # Return the first matching file
    return None  # No matching file found

def initialize_db():
    """Ensure MongoDB has apple data from Excel, and store only records with images from 'Heritage' folder."""
    if not os.path.exists(EXCEL_FILE):
        print(f"Excel file not found at: {EXCEL_FILE}. Skipping database initialization.")
        return
    
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="Malus")  # Ensure correct sheet name
        df.fillna("", inplace=True)  # Replace NaN values with an empty string
        data = df.to_dict(orient="records")  # Convert DataFrame to list of dictionaries

        filtered_data = []  # Store only entries with images

        for item in data:
            accession_number = item.get("ACCESSION", "")
            cultivar_name = item.get("CULTIVAR NAME", "")

            image_filename = find_image_for_accession(accession_number, cultivar_name)  # Find correct image
            
            if image_filename:  # ✅ Only add if an image exists
                item["image_url"] = f"/static/FruitPictures/Heritage/{image_filename}"  # URL for serving images
                filtered_data.append(item)  # Store only if image exists
        
        if filtered_data:  # ✅ Only insert if there is valid data
            apple_collection.delete_many({})  # Clear existing data
            apple_collection.insert_many(filtered_data)
            print("Apple data with images successfully loaded into MongoDB.")
        else:
            print("No apple data with images found. Skipping insertion.")

    except Exception as e:
        print(f"Error loading Excel file: {str(e)}")

# Initialize database on startup
initialize_db()
