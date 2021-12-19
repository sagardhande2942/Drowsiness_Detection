import pandas as pd
import numpy as np

df = pd.read_csv("start.csv")

weights = []

dict = {"User is drowsy": 5, "User is distracted Looking Right": 1, "User is distracted Looking Left": 1, "No face detected": 0,
"User is Speaking or talking on phone please focus on road" : 1}

for i in df['Message']:
    i = i.strip()
    print(i)
    if i == "User is drowsy":
        weights.append(dict[i])
    elif i == "User is distracted Looking Right":
        weights.append(dict[i])
    elif i == "User is distracted Looking Left":
        weights.append(dict[i])
    elif i == "No face detected":
        weights.append(dict[i])
    elif i == "User is Speaking or talking on phone please focus on road":
        weights.append(dict[i])
    else:
        weights.append("")

print(weights)
df['Weights'] = weights

check = False
index = 0
global_timestamp = ""

for i in df['Message']: 
    print(index)
    i = i.strip()
    if i == "User is drowsy":
        if check:
            print(global_timestamp)
            print(df.iloc[index]['Timestamp'][:-2])
            if global_timestamp == df.iloc[index]['Timestamp'][:-2].strip():
                df = df.drop(df.index[index]) 
                index -= 1
        check = True
        global_timestamp = df.iloc[index]['Timestamp']
        global_timestamp = global_timestamp[:-2].strip()
    else:
        check = False
    index += 1

print(df)
# df.set_index("Sr No.")
df.to_csv("start.csv", index=False)