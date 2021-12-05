import { default as axios } from "axios";
export interface IDemographics {
  age: number;
  sex: "M" | "F";
  vaccineManufacturer: string;
  medicalHistory: string;
  allergies: string;
  state: string;
}

export const MANUFACTURERS = [
  "PFIZER\\BIONTECH",
  "MODERNA",
  "UNKNOWN MANUFACTURER",
  "JANSSEN",
];

export const STATES = [
  "AL",
  "AK",
  "AZ",
  "AR",
  "CA",
  "CO",
  "CT",
  "DE",
  "FL",
  "GA",
  "HI",
  "ID",
  "IL",
  "IN",
  "IA",
  "KS",
  "KY",
  "LA",
  "ME",
  "MD",
  "MA",
  "MI",
  "MN",
  "MS",
  "MO",
  "MT",
  "NE",
  "NV",
  "NH",
  "NJ",
  "NM",
  "NY",
  "NC",
  "ND",
  "OH",
  "OK",
  "OR",
  "PA",
  "RI",
  "SC",
  "SD",
  "TN",
  "TX",
  "UT",
  "VT",
  "VA",
  "WA",
  "WV",
  "WI",
  "WY",
];

export const initialValues: IDemographics = {
  age: 18,
  sex: "M",
  vaccineManufacturer: MANUFACTURERS[0],
  medicalHistory: "",
  allergies: "",
  state: STATES[0],
};

export async function predictSymptoms(
  demographics: IDemographics
): Promise<string[]> {
  try {
    const response = await axios.post("/predict-symptoms", demographics);
    return response.data.symptoms;
  } catch (e) {
    return [];
  }
}
