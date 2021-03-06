class AnimationManager {
  constructor({
    coralData,
    staticData,
    seaLevelData,
    mapBoxMap,
    floodCutpoints,
    pRaiseFloodLevel,
    animationLen,
    fps,
    colorInformation,
    perlinOffset,
    debug,
  }) {
    this.coralData = coralData;
    this.staticData = staticData;    
    this.seaLevelData = seaLevelData; 
    this.mapBoxMap = mapBoxMap;
    this.animationLen = animationLen;
    this.fps = fps;
    this.colorInformation = colorInformation;
    this.floodCutpoints = floodCutpoints;
    this.pRaiseFloodLevel = pRaiseFloodLevel;
    this.debug = debug;
    this.currentFloodLevel = 0; // start at zero
    this.isDone=false;
    this.particleList = this.coralData.features.map(
      (x) => new Particle({ ...x, yoffset: 0.13, velocityScale:0.000125, perlinOffset:perlinOffset, debug:debug})
    );
    this.seaLevelPolygonList = this.seaLevelData.features.map(
      (x) => new SeaLevelPolygon({...x, debug:debug})
    );
    this.initializeMapBoxLayers();
    this.timeSinceLastFloodRaise = 0;
  }

  // initializes the mapboxpoint layer
  initializeMapBoxLayers() {
    // The Animated point source
    this.mapBoxMap.addSource("point", {
      type: "geojson",
      data: this.getCurrentParticleData(),
    });
    this.mapBoxMap.addLayer({
      id: "point",
      source: "point",
      type: "circle",
      paint: {
        "circle-radius": [
          "match",
          ["get", "state"],
          "HOME",
          this.colorInformation.radius_info.radius_small,
          "FALL",
          this.colorInformation.radius_info.radius_large,
          "CORAL",
          this.colorInformation.radius_info.radius_large,
          this.colorInformation.radius_info.radius_large,
        ],
        "circle-color": [
          "match",
          ["get", "state"],
          "HOME",
          this.colorInformation.color_expression_desaturated,
          "FALL",
          this.colorInformation.color_expression,
          "CORAL",
          this.colorInformation.color_expression,
          this.colorInformation.color_expression,
        ], //this.dotColorExpression,
        "circle-opacity": [
          "match",
          ["get", "state"],
          "HOME",
          this.colorInformation.static_opacity,
          "FALL",
          this.colorInformation.coral_opacity,
          "CORAL",
          this.colorInformation.coral_opacity,
          this.colorInformation.coral_opacity,
        ],
      },
    });

    // The STATIC source 
    this.mapBoxMap.addSource("static", {
      type: "geojson",
      data: {
        type: "FeatureCollection",
        features: this.staticData.features.map(x=>{
          return {
            type: "Feature",
            geometry: {
              type: "Point",
              coordinates: x.geometry.coordinates
            },
            properties: x.properties
          }
        })
      },
    });

    this.mapBoxMap.addLayer(
      {
        id: "static",
        source: "static",
        type: "circle",
        paint: {
          "circle-radius": this.colorInformation.radius_info.radius_small,
          "circle-color": this.colorInformation.color_expression_desaturated,
          "circle-opacity": this.colorInformation.static_opacity,
        },
      },
      "point"
    );

    // The sea level source
    this.mapBoxMap.addSource("sealevel", {
      type: "geojson",
      data: this.getCurrentSeaLevelData(),
    });
    this.mapBoxMap.addLayer(
      {
        id: "sealevel",
        type: "fill",
        source: "sealevel", // reference the data source
        paint: {
          "fill-color": this.colorInformation.water_color, // blue color fill
          "fill-opacity": ["get", "currentOpacity"],
          "fill-outline-color": "rgba(58, 65, 75, 0.5)", // hack for no border...
        },
      },
      "point"
    );
  }

  getCurrentSeaLevelData() {
    return {
      type: "FeatureCollection",
      features: this.seaLevelPolygonList.map((x) => x.toFeature()),
    };
  }

  getCurrentParticleData() {
    return {
      type: "FeatureCollection",
      features: this.particleList.map((x) => x.toFeature()),
    };
  }

  setDone(){
    this.isDone=true;
  }

  update() {
    // possibly raise the flood level
    if (this.timeSinceLastFloodRaise > 600 || (Math.random() < this.pRaiseFloodLevel) && this.timeSinceLastFloodRaise > 180) {
      if (this.currentFloodLevel < this.floodCutpoints.length - 1) {
        this.currentFloodLevel += 1;
        console.log(this.currentFloodLevel);
      }
      this.timeSinceLastFloodRaise = 0;
    } else{
      this.timeSinceLastFloodRaise+=1;
    }

    // update all the particles.
    this.particleList.forEach((x) => {
      x.setSeaLevel(this.floodCutpoints[this.currentFloodLevel]);
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
    if(!this.isDone){
      this.update();
      this.draw();
    }else{

    }
  }
}