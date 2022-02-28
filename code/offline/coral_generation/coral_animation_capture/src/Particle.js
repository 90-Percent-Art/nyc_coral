const lerp = (start, end, t) => {
  return [start[0] * t + end[0] * (1 - t), start[1] * t + end[1] * (1 - t)];
};

class Particle {
  constructor({ geometry, properties, type }) {
    this.start = geometry.coordinates[0];
    this.end = geometry.coordinates[1];
    this.position = this.start; // what is going to update.
    this.properties = properties;
    this.type = type;
    this.seaLevel = 24.0;
    this.homeSeaLevel =
      this.properties.flood_2020_500.flood_polygon_aggregate_metadata.max_static_bfe;
    this.state = "HOME"; // home, fall, coral
  }

  // convert yourself back to a geojson feature element
  toFeature() {
    return {
      geometry: {
        coordinates: this.position,
        type: "Point",
      },
      properties: this.properties,
      type: "Feature",
    };
  }

  setSeaLevel(level) {
    this.seaLevel = level;
  }

  // figure out my next frame position and
  // update position variables
  update() {
    if (this.state == "HOME") {
      if (this.homeSeaLevel >= this.seaLevel) {
        this.state = "FALL";
      }
    } else if (this.state == "FALL") {
      this.position = [this.position[0], this.position[1] - 0.001*Math.random()];
    } else if (this.state == "CORAL") {
      // don't move
    } else {
      throw "Got Unexpected State Value";
    }
  }
}
