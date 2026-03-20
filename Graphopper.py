import requests
import urllib.parse
import json
from datetime import datetime

route_url = "https://graphhopper.com/api/1/route?"

# Ayn Lorebelle E. Cavan
# Mary Jasmin P. Ompad 
# John Carlo L. Borgueta
# Jade Mykel R. Ventic


def get_api_key_graphopper():
    with open("GRAPHOPPER_API_KEY.txt", "r") as file:
        return file.read().strip()


def get_api_key_openrouter():
    with open("OPENROUTER_API_KEY.txt", "r") as file:
        return file.read().strip()


# ✅ Export function
def export_response(content):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"route_summary_{timestamp}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"\nResponse exported to {filename}")
    except Exception as e:
        print(f"Error exporting response: {e}")


key = get_api_key_graphopper()
OPENROUTER_API_KEY = get_api_key_openrouter()
output = ""


def geocoding(location, key):

    while location == "":
        location = input("Enter the location again: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({
        "q": location,
        "limit": "1",
        "key": key
    })

    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code

    print("Geocoding API URL for " + location + ":\n" + url)

    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        if state and country:
            new_loc = f"{name}, {state}, {country}"
        elif state:
            new_loc = f"{name}, {country}"
        else:
            new_loc = name

        print("Geocoding API URL for " + new_loc +
              " (Location Type: " + value + ")\n" + url)
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        if json_status != 200:
            print("Geocode API status: " + str(json_status) +
                  "\nError message: " + json_data["message"])

    return json_status, lat, lng, new_loc


while True:
    output = ""  # reset every loop

    print("\n" + "="*50)
    print("{:^50}".format("GRAPHHOPPER VEHICLE PROFILES"))
    print("="*50)

    print("\nAvailable Options:\n")
    print("  [1] car")
    print("  [2] bike")
    print("  [3] foot")

    print("\n" + "-"*50)
    print("Type the name or number of your choice")
    print("-"*50 + "\n")

    profile = ["car", "bike", "foot"]
    vehicle = input("Enter vehicle: ")

    if vehicle in ["quit", "q"]:
        break
    elif vehicle not in profile:
        vehicle = "car"
        print("No valid vehicle profile was entered. Using the car profile.")

    loc1 = input("Starting Location: ")
    if loc1 in ["quit", "q"]:
        break
    orig = geocoding(loc1, key)

    loc2 = input("Destination: ")
    if loc2 in ["quit", "q"]:
        break
    dest = geocoding(loc2, key)

    print("=================================================")

    if orig[0] == 200 and dest[0] == 200:
        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])

        paths_url = route_url + urllib.parse.urlencode({
            "key": key,
            "vehicle": vehicle
        }) + op + dp

        paths_status = requests.get(paths_url).status_code
        paths_data = requests.get(paths_url).json()

        output += "Routing API Status: " + str(paths_status) + "\n"
        output += "Routing API URL:\n" + paths_url + "\n"
        output += "=================================================\n"
        output += f"Directions from {orig[3]} to {dest[3]} by {vehicle}\n"
        output += "=================================================\n"

        if paths_status == 200:
            miles = (paths_data["paths"][0]["distance"]) / 1000 / 1.61
            km = (paths_data["paths"][0]["distance"]) / 1000

            sec = int(paths_data["paths"][0]["time"] / 1000 % 60)
            min = int(paths_data["paths"][0]["time"] / 1000 / 60 % 60)
            hr = int(paths_data["paths"][0]["time"] / 1000 / 60 / 60)

            output += f"Distance Traveled: {miles:.1f} miles / {km:.1f} km\n"
            output += f"Trip Duration: {hr:02d}:{min:02d}:{sec:02d}\n"
            output += "=================================================\n"

            for each in paths_data["paths"][0]["instructions"]:
                path = each["text"]
                distance = each["distance"]

                output += f"{path} ({distance/1000:.1f} km / {distance/1000/1.61:.1f} miles)\n"

            output += "=============================================\n"
        else:
            output += "Error message: " + paths_data["message"] + "\n"

    # ✅ AI SUMMARY
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + OPENROUTER_API_KEY
        },
        data=json.dumps({
            "model": "openai/gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": output + ". Summarize the output, explain in simple terms, and provide insights on the results. Keep the output smaller and no asterisks or equal signs."
                }
            ]
        })
    )

    ai_response = response.json()["choices"][0]["message"]["content"]

    print("\n--- AI Summary ---\n")
    print(ai_response)

    # ✅ MENU-BASED EXPORT CHOICE
    print("\nWhat would you like to do next?")
    print("[1] Export response to text file")
    print("[2] Continue without saving")

    choice = input("Enter choice: ")

    if choice == "1":
        export_response(ai_response)
    elif choice == "2":
        print("Continuing without saving...")
    else:
        print("Invalid choice. Skipping export.")