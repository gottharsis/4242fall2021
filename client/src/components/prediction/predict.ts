import { default as axios } from "axios";
export interface IDemographics {
  age: number;
  sex: "M" | "F";
  vaccineManufacturer: string;
  medicalHistory: string;
  allergies: string;
}

export const MANUFACTURERS = ["PFIZER\\BIONTECH", "MODERNA", "UNKNOWN MANUFACTURER", "JANSSEN"];

export const initialValues: IDemographics = {
  age: 18,
  sex: "M",
  vaccineManufacturer: "Pfizer",
  medicalHistory: "",
  allergies: "",
};

export function predictSymptoms(
  demographics: IDemographics
): Promise<string[]> {
  return new Promise<string[]>((resolve) =>
    setTimeout(() => resolve(["symptom1", "testsymptom2"]), 500)
  );
  // try {
  //     const response = await axios.post('/predict-symptoms', symptoms)
  //     return response.data
  // }
  // catch(e) {
  //     return []
  // }
}
