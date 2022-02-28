class AnimationManager {

  constructor({ coralData, seaLevelData, mapBoxMap, floodCutpoints, animationLen, fps}) {
    this.coralData = coralData;
    this.seaLevelData = seaLevelData;
    this.mapBoxMap = mapBoxMap;
    this.animationLen = animationLen;
    this.fps = fps;
    this.floodCutpoints = floodCutpoints;
    this.currentFloodLevel = 0; // start at zero
    this.particleList = this.coralData.features.map((x) => new Particle(x));
    this.seaLevelPolygonList = this.seaLevelData.features.map(x => new SeaLevelPolygon(x));
    this.initializeMapBoxLayers();
  }

  // initializes the mapboxpoint layer
  initializeMapBoxLayers() {
    
    // The point source
    this.mapBoxMap.addSource("point", {
      type: "geojson",
      data: this.getCurrentParticleData(),
    });
    this.mapBoxMap.addLayer({
      id: "point",
      source: "point",
      type: "circle",
      paint: {
        "circle-radius": 1.9,
        "circle-color": "darkblue",
      },
    });

    // The sea level source
    this.mapBoxMap.addSource("sealevel", {
      type: "geojson",
      data: this.getCurrentSeaLevelData(),
    });
    this.mapBoxMap.addLayer({
      id: "sealevel",
      type: "fill",
      source: "sealevel", // reference the data source
      paint: {
        "fill-color": "#92b8dd", // blue color fill
        "fill-opacity": ["get", "currentOpacity"]
      },
    });

  }

  getCurrentSeaLevelData(){
      return {
        type: "FeatureCollection",
        features: this.seaLevelPolygonList.map(x=>x.toFeature()),
      };
  }

  getCurrentParticleData() {
    return {
      type: "FeatureCollection",
      features: this.particleList.map((x) => x.toFeature()),
    };
  }

  update() {
    
    // possibly raise the flood level
    if(Math.random() < 1/60){
      if(this.currentFloodLevel < this.floodCutpoints.length){
        this.currentFloodLevel += 1;
        console.log(this.currentFloodLevel)
      }
    }

    // update all the particles. 
    this.particleList.forEach((x) => {
      x.setSeaLevel(this.floodCutpoints[this.currentFloodLevel])
      x.update();
    });

    this.seaLevelPolygonList.forEach((x) => {
        x.setSeaLevel(this.floodCutpoints[this.currentFloodLevel]);
        x.update();
    });
}

  draw() {
    this.mapBoxMap.getSource("point").setData(this.getCurrentParticleData());
    this.mapBoxMap.getSource("sealevel").setData(this.getCurrentSeaLevelData());
  }

  updateDraw() {
    this.update();
    this.draw();
  }
}