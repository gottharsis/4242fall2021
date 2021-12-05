import { Formik, FormikProps } from "formik";
import React from "react";
import { Button, Container, Form } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import {
  initialValues,
  MANUFACTURERS,
  STATES,
  predictSymptoms,
  IDemographics,
} from "./predict";

function PForm({
  values,
  errors,
  touched,
  handleChange,
  handleBlur,
  handleSubmit,
  isSubmitting,
}: FormikProps<IDemographics>) {
  return (
    <Form>
      <Form.Group>
        <Form.Label> Age </Form.Label>
        <Form.Control
          type="numeric"
          name="age"
          onChange={handleChange}
          onBlur={handleBlur}
          value={values.age}
        ></Form.Control>
      </Form.Group>
    </Form>
  );
}

export default function PredictionForm() {
  const navigate = useNavigate();
  const onSubmit = async (
    values: IDemographics,
    { setSubmitting }: { setSubmitting: any }
  ) => {
    const result = await predictSymptoms(values);
    setSubmitting(false);
    console.log(result);
    navigate("/results", { state: { symptoms: result } });
  };

  return (
    <Formik initialValues={initialValues} onSubmit={onSubmit}>
      {({
        values,
        errors,
        touched,
        handleChange,
        handleBlur,
        handleSubmit,
        isSubmitting,
      }) => (
        <>
          <Container>
            <h1>Symptom Prediction</h1>
            <p>Enter your data below to predict your likely symptoms.</p>
            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3">
                <Form.Label> Age </Form.Label>
                <Form.Control
                  type="numeric"
                  name="age"
                  onChange={handleChange}
                  onBlur={handleBlur}
                  value={values.age}
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Sex</Form.Label>
                <Form.Select
                  name="sex"
                  value={values.sex}
                  onChange={handleChange}
                  onBlur={handleBlur}
                >
                  <option value="M"> Male </option>
                  <option value="F"> Female </option>
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label> State </Form.Label>
                <Form.Select
                  name="state"
                  value={values.state}
                  onChange={handleChange}
                  onBlur={handleBlur}
                >
                  {STATES.map((state) => (
                    <option key={state} value={state}>
                      {state}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label> Vaccine Manufacturer </Form.Label>
                <Form.Select
                  name="vaccineManufacturer"
                  onChange={handleChange}
                  onBlur={handleBlur}
                  value={values.vaccineManufacturer}
                >
                  {MANUFACTURERS.map((i) => (
                    <option value={i} key={i}>
                      {i}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label> Medical History </Form.Label>
                <Form.Control
                  name="medicalHistory"
                  onChange={handleChange}
                  onBlur={handleBlur}
                  value={values.medicalHistory}
                  as="textarea"
                  rows={3}
                ></Form.Control>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label> Allergies </Form.Label>
                <Form.Control
                  name="allergies"
                  onChange={handleChange}
                  onBlur={handleBlur}
                  value={values.allergies}
                  as="textarea"
                  rows={3}
                ></Form.Control>
              </Form.Group>
              <Button type="submit" disabled={isSubmitting}>
                {(isSubmitting && "Submitting...") || "Submit"}
              </Button>
            </Form>
          </Container>
        </>
      )}
    </Formik>
  );
}
