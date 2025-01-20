import { Driver, Point, Track, Vehicle } from "src/types/types";
import { apiStore } from "stores/apiStore";

class ApiService {
  async uploadTrack(file: File) {
    const fileContent = await file.text();
    const response = await fetch("http://127.0.0.1:5000/track", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        "file_name": file.name,
        "file_content": fileContent
      })
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }
  }

  async getAllDrivers(): Promise<Driver[]> {
    const response = await fetch("http://127.0.0.1:5000/driver");

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return await response.json();
  }

  async getDriver(driverId: Number): Promise<Driver> {
    const response = await fetch(`http://127.0.0.1:5000/driver/${driverId}`);

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return await response.json();
  }

  async getAllVehicles(): Promise<Vehicle[]> {
    const response = await fetch("http://127.0.0.1:5000/vehicle");

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return await response.json();
  }

  async getVehicle(vehicleId: Number): Promise<Vehicle> {
    const response = await fetch(`http://127.0.0.1:5000/vehicle/${vehicleId}`);

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return await response.json();
  }

  async getAllTracks(): Promise<Track[]> {
    const response = await fetch("http://127.0.0.1:5000/track");

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return await response.json();
  }

  async getTracks(driverId: Number, vehicleId: Number): Promise<Track[]> {
    const response = await fetch(`http://127.0.0.1:5000/track/${driverId}/${vehicleId}`);

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return await response.json();
  }

  async getPoints(trackId: Number): Promise<Point[]> {
    const response = await fetch(`http://127.0.0.1:5000/point/${trackId}`);

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return await response.json();
  }

  async loadData() {
    const drivers = await this.getAllDrivers();
    const vehicles = await this.getAllVehicles();

    for (const driver of drivers) {
      // if the driver has not been loaded from api yet, add
      if (!apiStore.state.drivers.find(d => d.driver_id == driver.driver_id)) {
        apiStore.state.drivers.push(driver);
      }
    }

    for (const vehicle of vehicles) {
      // if the vehicle has not been loaded from api yet, add
      if (!apiStore.state.vehicles.find(v => v.vehicle_id == vehicle.vehicle_id)) {
        apiStore.state.vehicles.push(vehicle);
      }
    }
  }
}

export const apiService = new ApiService();
