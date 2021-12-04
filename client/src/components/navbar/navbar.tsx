import React from "react";
import { Container, Nav, Navbar } from "react-bootstrap";
import { Link } from "react-router-dom";

export default function NavigationBar() {
  return (
    <>
      <Navbar bg="dark" expand="md" variant="dark">
        <Container>
          <Navbar.Brand href="/">
            {" "}
            COVID-19 Vaccine Side Effects{" "}
          </Navbar.Brand>
          <Navbar.Text>
            <Link to="/predict"> Symptom Prediction </Link>
          </Navbar.Text>
        </Container>
      </Navbar>
    </>
  );
}
