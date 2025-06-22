// frontend/__tests__/HealthCheckScreen.test.tsx
import React from "react";
import { render, waitFor, screen } from "@testing-library/react-native";
import HealthCheckScreen from "../src/screens/HealthCheckScreen";

// Mock the global fetch function
global.fetch = jest.fn();

describe("HealthCheckScreen", () => {
  beforeEach(() => {
    // Reset fetch mock for each test
    (global.fetch as jest.Mock).mockClear();
  });

  it("displays loading state initially", () => {
    (global.fetch as jest.Mock).mockImplementationOnce(
      () => new Promise(() => {})
    ); // Keep promise pending
    render(<HealthCheckScreen />);
    expect(screen.getByText("Loading Health Status...")).toBeTruthy();
  });

  it("displays the status message on successful fetch", async () => {
    const mockHealthData = {
      status: "Backend is super healthy!",
      timestamp: new Date().toISOString(),
    };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockHealthData,
    });

    render(<HealthCheckScreen />);

    await waitFor(() => {
      expect(screen.getByText(`Status: ${mockHealthData.status}`)).toBeTruthy();
    });
    expect(screen.queryByText("Error fetching status")).toBeNull();
  });

  it("displays an error message on failed fetch (network error)", async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(
      new Error("Network request failed")
    );

    render(<HealthCheckScreen />);

    await waitFor(() => {
      expect(
        screen.getByText("Error fetching status: Network request failed")
      ).toBeTruthy();
    });
    expect(screen.queryByText("Status:")).toBeNull();
  });

  it("displays an error message on failed fetch (HTTP error)", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ message: "Internal Server Error" }), // Optional: mock error response body
    });

    render(<HealthCheckScreen />);

    await waitFor(() => {
      expect(
        screen.getByText("Error fetching status: HTTP error! status: 500")
      ).toBeTruthy();
    });
    expect(screen.queryByText("Status:")).toBeNull();
  });
});
