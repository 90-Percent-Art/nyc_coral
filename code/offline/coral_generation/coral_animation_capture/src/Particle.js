const lerp = (start, end, t) => {
  return [start[0] * t + end[0] * (1 - t), start[1] * t + end[1] * (1 - t)];
};

const getUnitVectorFromStartToEnd = (start, end) => {
  direction = [end[0]-start[0], end[1]-start[1]]
  mag = Math.sqrt(direction[0]**2 + direction[1]**2)
  return direction.map(x=>x/mag);
}

// distance between two vectors
const vecDistance = (a, b) => {
  return Math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2);
}

class Particle {
  constructor({ geometry, properties, type, velocityScale, yoffset}) {
    this.start = geometry.coordinates[0];
    this.end = [
      geometry.coordinates[1][0],
      geometry.coordinates[1][1] - yoffset,
    ];
    this.velocity = getUnitVectorFromStartToEnd(this.start, this.end).map(x=> x*velocityScale);
    this.position = this.start; // what is going to update.
    this.properties = properties;
    this.type = type;
    this.seaLevel = 24.0;
    this.departureTime = null;
    this.homeSeaLevel = this.properties.flood_2020_500.flood_polygon_aggregate_metadata.max_static_bfe;
    this.state = "HOME"; // home, fall, coral
  }

  // convert yourself back to a geojson feature element
  toFeature() {
    return {
      geometry: {
        coordinates: this.position,
        type: "Point",
      },
      properties: {...this.properties, state: this.state},
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

        if(!this.departureTime){
          this.departureTime = Math.random(0,1)*360+60; // choose a departure time. 
        }else if(this.departureTime <= 1){
          this.state = "FALL";
        }else{
          this.departureTime-=1;
        }
      }

    } else if (this.state == "FALL") {
      
      this.position = [
        this.position[0] + this.velocity[0],
        this.position[1] + this.velocity[1],
      ];

      if(vecDistance(this.position, this.end) < 0.0005){
        this.state = "CORAL";
      }

    } else if (this.state == "CORAL") {
      // don't move
    } else {
      throw "Got Unexpected State Value";
    }
  }
}
