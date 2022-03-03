// This script will load the data, set everything up, and kick off the animation
let manager;
let fnum=0; // how many frames

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
      // center: { lng: -73.95130677740997, lat: 40.63110961057512 }, <- WHAT WAS USED FOR ALL THE MAIN RENDERS with offset .15 and 
      center: { lng: -73.96246278102689, lat: 40.63460678257843 },
      zoom: 10.201089607663054, // with particle offset .13
      container: "container", // HTML container id
      style: style, // style URL
      preserveDrawingBuffer: true,
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
        console.log("Recorded Frame", fnum)
        fnum++;
    }
    if (fnum > 15000) {
      console.log("Finished recording");
      manager.setDone();
      CanvasCapture.stopRecord();
    }
    requestAnimationFrame(render);
}

// # Good corals to run 
// # coral_progressive_generic
// # coral_progressive_many_interval2
// # coral_progressive_generic_highshock - DRAWN
// # coral_progressive_few_interval
// coral_progressive_few_interval3 -- funny two curving toward one another (next?)
// coral_progressive_few_interval4 - fine normal 
// coral_progressive_few_interval6 - DRAWINGn - was run on dark theme
// coral_progressive_random_intervals2 -- good number of intervals with some spacing
// coral_progressive_random_intervals3 - handful of tall guyz
async function main(
  path_to_coral_data = "data/coral_progressive_few_interval4.geojson", // this one has been run dark theme
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
    // style: "mapbox://styles/jfoss117/cl08edlw5000k14mgbvcr5u47?fresh=true",
    style: "mapbox://styles/jfoss117/cl0aa6i4k001r16qhjyqbf8eh?fresh=true",
  });

  debug = true;

  args = {
    coralData: coralData,
    seaLevelData: seaLevelData,
    staticData: staticData,
    mapBoxMap: mapboxMap,
    animationLen: 5, // in seconds
    fps: 60,
    colorInformation: county_level_jeff_dark_theme_color_information,
    floodCutpoints: [24.0, 17.0, 15.0, 14.0, 13.0, 12.0, 11.0, 10.0, 0.0],
    pRaiseFloodLevel: 1 / 480, // 1/120
    perlinOffset: 5.5,
    debug: debug,
  };

  mapboxMap.on("load", () => {
    initializeCanvasCapture("coral_video"); // start canvas capture runnning
    manager = new AnimationManager(args);
    if (!debug) {
      render();
    }
  });
}

main();