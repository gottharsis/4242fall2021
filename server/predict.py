import pickle
import sklearn
import numpy as np

MODEL_PATH = "./server/model/model.sav"
ENCODER_PATH = "./server/model/encoder.sav"

FEATURES = [
    "AK",
    "AL",
    "AR",
    "AS",
    "AZ",
    "CA",
    "CO",
    "CT",
    "DC",
    "DE",
    "FL",
    "FM",
    "GA",
    "GU",
    "HI",
    "IA",
    "ID",
    "IL",
    "IN",
    "KS",
    "KY",
    "LA",
    "MA",
    "MD",
    "ME",
    "MH",
    "MI",
    "MN",
    "MO",
    "MP",
    "MS",
    "MT",
    "NC",
    "ND",
    "NE",
    "NH",
    "NJ",
    "NM",
    "NV",
    "NY",
    "OH",
    "OK",
    "OR",
    "PA",
    "PR",
    "QM",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VA",
    "VI",
    "VT",
    "WA",
    "WI",
    "WV",
    "WY",
    "XB",
    "XL",
    "XV",
    "JANSSEN",
    "MODERNA",
    "PFIZER\\BIONTECH",
    "UNKNOWN MANUFACTURER",
    "F",
    "M",
    "U",
    # "has_med_history",
    # "has_allergies",
]


class ModelProvider:
    def __init__(self):
        self._model = None
        self._encoder = None

    def load_model(self):
        with open(MODEL_PATH, "rb") as f:
            self._model = pickle.load(f)
        return self._model


    def load_encoder(self):
        with open(ENCODER_PATH, "rb") as f:
            self._encoder = pickle.load(f)
        return self._encoder

    def get_model(self):
        if not self._model:
            self.load_model()
        return self._model

    def get_encoder(self):
        if not self._encoder:
            self.load_encoder()
        return self._encoder

provider = ModelProvider()

def process_request(data: dict):
    state = data["state"]
    sex = data["sex"]
    manufacturer = data["vaccineManufacturer"]

    inp = np.zeros(len(FEATURES))
    for j in (state, sex, manufacturer):
        inp[FEATURES.index(j)] = 1


    # history = data["medicalHistory"]
    # allergies = data["allergies"]

    # if history and history.lower() != "none":
    #     inp[-2] = 1
    # if allergies and allergies.lower() != 'none':
    #     inp[-1] = 1

    return inp


def predict_symptoms(data: dict):
    global provider
    model = provider.get_model()
    encoder = provider.get_encoder()

    inp = process_request(data).reshape(1, -1)
    result = model.predict(inp)

    result = result[result < len(encoder.classes_)]

    symptoms = encoder.inverse_transform(result.ravel())
    return list(symptoms.ravel())

    
if __name__ == '__main__':
    data = { "sex": "M", "state": "GA", "vaccineManufacturer": "PFIZER\\BIONTECH", "medicalHistory": "bumif", "allergies": "" }
    inp = process_request(data)
    print(inp)

    res = predict_symptoms(data)
    print("Predicted symptoms:")
    print(res)



