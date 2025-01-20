export type Driver = {
  driver_id: Number,
  driver_name: String
}

export type Vehicle = {
  vehicle_id: Number,
  vehicle_license_plate: String
}

export type Track = {
  track_id: Number,
  track_file_name: String,
  track_driver_id: Number,
  track_vehicle_id: Number
}

export type Point = {
  point_id: Number,
  point_track_id: Number,
  point_lat: Number,
  point_lon: Number,
  point_ele: Number
}

export type ApiStore = {
  drivers: Driver[],
  vehicles: Vehicle[]
}

export type DisplayedTrack = {
  track: Track,
  points: Point[]
}

export type MapStore = {
  displayedTracks: DisplayedTrack[]
}
