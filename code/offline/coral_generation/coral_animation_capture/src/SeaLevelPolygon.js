class SeaLevelPolygon {
  constructor({ type, geometry, properties }) {
    this.type = type;
    this.geometry = geometry;
    this.properties = properties;
    this.static_bfe = parseInt(properties.static_bfe);
    this.isFlooded = false;
    this.currentOpacity = 0;

    this.maxOpacity = 0.7; // flooded 
    this.transitionTime = 0.5; 
    this.opacityIncrement = this.maxOpacity/(this.transitionTime*60);
  }

  toFeature() {
    return {
      type: this.type,
      geometry: this.geometry,
      properties: { ...this.properties, currentOpacity: this.currentOpacity },
    };
  }

  setSeaLevel(level) {
    this.seaLevel = level;
  }

  update() {
    if(this.seaLevel <= this.static_bfe && this.currentOpacity<this.maxOpacity){
        this.currentOpacity+=this.opacityIncrement;
    }
  }
}