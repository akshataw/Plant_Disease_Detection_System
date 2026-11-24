import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import App from "../App.jsx";
import ResultCard from "../components/ResultCard.jsx";
import { AuthProvider } from "../context/AuthContext.jsx";

describe("App", () => {
  it("redirects anonymous users to the login page", async () => {
    localStorage.clear();
    render(
      <MemoryRouter initialEntries={["/"]}>
        <AuthProvider><App /></AuthProvider>
      </MemoryRouter>
    );
    expect(await screen.findByRole("heading", { name: "Log in" })).toBeInTheDocument();
  });
});

describe("ResultCard", () => {
  const result = {
    disease_name: "Tomato — Late blight",
    confidence: 0.42,
    low_confidence: true,
    is_healthy: false,
    model_version: "plant_disease_v1",
    top_k: [
      { label: "Tomato___Late_blight", name: "Tomato — Late blight", confidence: 0.42 },
      { label: "Tomato___healthy", name: "Tomato — Healthy", confidence: 0.3 },
    ],
    details: {
      pathogen: "Phytophthora infestans", description: "desc",
      symptoms: ["Dark lesions"], causes: ["Wet weather"], prevention: ["Spacing"], treatment: ["Fungicide"],
    },
  };

  it("shows disease details, alternatives and a low-confidence warning", () => {
    render(<ResultCard result={result} />);
    expect(screen.getByRole("heading", { name: "Tomato — Late blight" })).toBeInTheDocument();
    expect(screen.getByText("Fungicide")).toBeInTheDocument();
    expect(screen.getByText("Tomato — Healthy")).toBeInTheDocument();
    expect(screen.getByText(/not very confident/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Confidence 42%")).toBeInTheDocument();
  });
});
