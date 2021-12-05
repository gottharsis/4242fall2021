import random

potential_symptoms = [
    "Fever",
    "Chills",
    "Headache",
    "Pain at Injection Site",
    "Tiredness",
    "Nausea",
    "Swelling",
    "Muscle Pain",
    "Swollen Lymph Nodes",
    "Joint Pain"
]

def predict_symptoms(_):
    k = random.randint(1, len(potential_symptoms) - 2)  
    symptoms = random.sample(potential_symptoms, k)
    return symptoms


