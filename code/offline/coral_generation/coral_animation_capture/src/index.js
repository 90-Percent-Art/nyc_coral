// This script will load the data, set everything up, and kick off the animation
let manager;

const initializeCanvasCapture = (outputName) => {
    CanvasCapture.init(document.getElementsByTagName("canvas")[0], {
      showRecDot: true,
    });

    CanvasCapture.bindKeyToVideoRecord("v", {
      format: CanvasCapture.WEBM,
      name: outputName,
      fps: 60,
    });
}

const initializeMapBox = ({token, style}) => {
    mapboxgl.accessToken = token;
    newMap = new mapboxgl.Map({
      altitude: 1.5,
      bearing: 0,
      height: 1107,
      center: {lng: -73.97113612185217, lat: 40.62869926050584},
      zoom: 9.910809184890859,
      container: "container", // HTML container id
      style: style, // style URL
      preserveDrawingBuffer: true,
      attributionControl: false,
    });

//_ne: Dl {lng: -73.57670111388728, lat: 40.92738252600151}
//_sw: Dl {lng: -74.3655711298158, lat: 40.3286741000577}

    newMap.addControl(new mapboxgl.AttributionControl(), "top-left");

    return newMap;

}

// the main render loop
function render(){
    manager.updateDraw();
    if (CanvasCapture.isRecording()) {
        CanvasCapture.recordFrame();
        console.log("Recorded Frame")
    }
    requestAnimationFrame(render);
}

async function main(path_to_coral_data = "data/coral_progressive_test.geojson", path_to_sea_level_data = "data/sea_level_rise_2020s_500.geojson"){

    let coralData;
    let seaLevelData;

    await fetch(path_to_coral_data)
    .then((res) => res.json())
    .then((d) => {
        coralData = d;
    });

    await fetch(path_to_sea_level_data)
      .then((res) => res.json())
      .then((d) => {
        seaLevelData = d;
      });

    mapboxMap = initializeMapBox({
      token:
        "pk.eyJ1IjoiamZvc3MxMTciLCJhIjoiY2t6dXJsYncyN2gyZzJ4cHJkMm4yZ2tqNyJ9.BFDHjB7Y9clXwIv5bKJrdA",
      style: "mapbox://styles/jfoss117/ckzr8kmjs002314lelqt0w83j",
    });

    args = {
      coralData: coralData,
      seaLevelData: seaLevelData,
      mapBoxMap: mapboxMap,
      animationLen: 5, // in seconds
      fps: 60,
      floodCutpoints: [24.0, 17.0, 15.0, 14.0, 13.0, 12.0, 11.0, 10.0, 0.0]
    };

    mapboxMap.on("load", () => {
      initializeCanvasCapture("coral_video"); // start canvas capture runnning
      manager = new AnimationManager(args);
      render();
    });

}

main();