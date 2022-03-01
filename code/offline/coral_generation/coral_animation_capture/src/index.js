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
      // center: { lng: -73.96635127723289, lat: 40.663827839766896 },
      center: { lng: -73.95130677740997, lat: 40.63110961057512 },
      zoom: 9.89886394624119,
      container: "container", // HTML container id
      style: style, // style URL
      //preserveDrawingBuffer: true,
      attributionControl: false,
    });

    // Final bounds are 
    //_ne: Dl {lng: -73.62394892456157, lat: 40.92304979628307}
    //_sw: Dl {lng: -74.30875362990382, lat: 40.4035944815125}

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

async function main(
  path_to_coral_data = "data/coral_progressive_test.geojson",
  path_to_sea_level_data = "data/sea_level_rise_2020s_500.geojson",
  path_to_static_data = "data/coral_progressive_static.geojson"
) {
  let coralData;
  let staticData;
  let seaLevelData;

  await fetch(path_to_coral_data)
    .then((res) => res.json())
    .then((d) => {
      coralData = d;
    });

  await fetch(path_to_static_data)
    .then((res) => res.json())
    .then((d) => {
      staticData = d;
    });

  await fetch(path_to_sea_level_data)
    .then((res) => res.json())
    .then((d) => {
      seaLevelData = d;
    });

  mapboxMap = initializeMapBox({
    token:
      "pk.eyJ1IjoiamZvc3MxMTciLCJhIjoiY2t6dXJsYncyN2gyZzJ4cHJkMm4yZ2tqNyJ9.BFDHjB7Y9clXwIv5bKJrdA",
    //style: "mapbox://styles/jfoss117/ckzr8kmjs002314lelqt0w83j",
    style: "mapbox://styles/jfoss117/cl08edlw5000k14mgbvcr5u47?fresh=true",
  });

  args = {
    coralData: coralData,
    seaLevelData: seaLevelData,
    staticData: staticData,
    mapBoxMap: mapboxMap,
    animationLen: 5, // in seconds
    fps: 60,
    colorInformation: county_level_jeff_current_color_information,
    floodCutpoints: [24.0, 17.0, 15.0, 14.0, 13.0, 12.0, 11.0, 10.0, 0.0],
    pRaiseFloodLevel: 1 / 120,
  };

  mapboxMap.on("load", () => {
    initializeCanvasCapture("coral_video"); // start canvas capture runnning
    manager = new AnimationManager(args);
    //render();
  });
}

main();