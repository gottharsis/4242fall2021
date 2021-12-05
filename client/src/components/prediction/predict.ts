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

export async function predictSymptoms(
  demographics: IDemographics
): Promise<string[]> {
  try {
      const response = await axios.post('/predict-symptoms', demographics)
      return response.data.symptoms
  }
  catch(e) {
      return []
  }
}
