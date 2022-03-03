// const lerp = (start, end, t) => {
//   return [start[0] * t + end[0] * (1 - t), start[1] * t + end[1] * (1 - t)];
// };

// const getUnitVectorFromStartToEnd = (start, end) => {
//   direction = [end[0]-start[0], end[1]-start[1]]
//   mag = Math.sqrt(direction[0]**2 + direction[1]**2)
//   return direction.map(x=>x/mag);
// }

// // distance between two vectors
// const vecDistance = (a, b) => {
//   return Math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2);
// }

class Particle {
  constructor({ geometry, properties, type, velocityScale, yoffset, perlinOffset}) {
    // initialize positions
    this.start = new Victor(
      geometry.coordinates[0][0],
      geometry.coordinates[0][1]
    );
    this.end = new Victor(
      geometry.coordinates[1][0],
      geometry.coordinates[1][1] - yoffset
    );
    this.position = debug?this.end:this.start;
    this.velocityScale = velocityScale*(0.8+Math.random()*.4) // was previously multiplied on a unit vector...
    this.velocity = new Victor(0, 0); // this.velocity = getUnitVectorFromStartToEnd(this.start, this.end).map(x=> x*velocityScale);

    // Initialize other stuff
    this.properties = properties;
    this.type = type;
    this.seaLevel = 24.0;
    this.departureTime = null;
    this.homeSeaLevel =
      this.properties.flood_2020_500.flood_polygon_aggregate_metadata.max_static_bfe;
    this.seekThreshold = 40.55 + Math.random()*0.05;
    this.state = debug?"CORAL":"HOME"; // home, fall, coral
    this.perlinOffset = perlinOffset;
  }

  // convert yourself back to a geojson feature element
  toFeature() {
    return {
      geometry: {
        coordinates: [this.position.x, this.position.y],
        type: "Point",
      },
      properties: {...this.properties, state: this.state},
      type: "Feature",
    };
  }

  setSeaLevel(level) {
    this.seaLevel = level;
  }

  applyForce(vec){
    this.velocity.add(vec);
    if(this.velocity.x > this.velocityScale){
      this.velocity.x = this.velocityScale;
    }
    if(this.velocity.y > this.velocityScale){
      this.velocity.y = this.velocityScale
    }
  }

  computeFirstForce(){
    // todo - push off in a direction 
    let dirVec = new Victor(Math.random()*2-1, Math.random());
    return dirVec.normalize().multiplyScalar(this.velocityScale);
  }

  computeWaterResistanceForce(){
    return this.velocity.clone().multiplyScalar(-1).multiplyScalar(0.3);
  }

  computeGravityForce(){
    // todo - gravity
    return(new Victor(0,-1).normalize().multiplyScalar(this.velocityScale*0.35));
    //return new Victor(noise.perlin2(this.position.x, this.position.y), -this.velocityScale).normalize().multiplyScalar(this.velocityScale);
  }

  computePerlinForce(){
    return(new Victor(noise.perlin2(this.position.x+this.perlinOffset, this.position.y+this.perlinOffset),0).normalize().multiplyScalar(this.velocityScale*.06));
  }

  computeSeekForce(){
    // todo - seek
    let targetVel = this.end.clone().subtract(this.position).normalize().multiplyScalar(this.velocityScale); // fast in direction of thing...
    return targetVel.subtract(this.velocity);
  }

  doHomeUpdate(){ // update to run when you are in "Home" state
    if (this.homeSeaLevel >= this.seaLevel) {
      if (!this.departureTime) {
        this.departureTime =
          this.homeSeaLevel == 0
            ? Math.random(0, 1) * 600 + 60 
            : Math.random(0, 1) * 360 + 60;
      } else if (this.departureTime <= 1) {
        this.applyForce(this.computeFirstForce()); // start falling! 
        this.state = "FALL";
      } else {
        this.departureTime -= 1;
      }
    }
  }

  doFallUpdate(){ // update to run when in "Fall" state
    this.applyForce(this.computeGravityForce());
    this.applyForce(this.computePerlinForce());
    this.applyForce(this.computeWaterResistanceForce());
    this.position.add(this.velocity); // update position
    if (this.position.y < this.seekThreshold ){
      this.state = "SEEK";
    }
    if (this.position.distance(this.end) < 0.0005) {
      this.state = "CORAL";
    }
  }

  doSeekUpdate(){
    this.applyForce(this.computeSeekForce());
    this.applyForce(this.computeWaterResistanceForce());
    this.position.add(this.velocity); // update position
    if (this.position.distance(this.end) < 0.0005) {
      this.state = "CORAL";
    }
  }

  // figure out my next frame position and
  // update position variables
  update() {
    if (this.state == "HOME") {
      this.doHomeUpdate();
    } else if (this.state == "FALL") {
      this.doFallUpdate();
    } else if (this.state == "SEEK"){
      this.doSeekUpdate();
    } else if (this.state == "CORAL") {
      // don't move
    } else {
      throw "Got Unexpected State Value";
    }
  }
}
