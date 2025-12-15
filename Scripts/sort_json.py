import json

# Example JSON content (replace with your file reading logic)
with open("C:/Users/Angus/Angus_Stuff/Programming/AudioRecording/addedjson.json", "r") as json_file:
    data = json.load(json_file)

# Sort the data by the "Time Delta" key
sorted_data = sorted(data, key=lambda x: int(x["Time"]))

# Save to a JSON file
with open("sorted_output.json", "w") as json_file:
    json.dump(sorted_data, json_file, indent=4)
