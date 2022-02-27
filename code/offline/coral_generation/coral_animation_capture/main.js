mapboxgl.accessToken = "";

let mapBoxMap = new mapboxgl.Map({
  altitude: 1.5,
  bearing: 0,
  height: 1107,
  center: [-74.01063177933962, 40.75813025358964],
  zoom: 10.033299478365162,
  container: "container", // HTML container id
  style: "mapbox://styles/jfoss117/ckzr8kmjs002314lelqt0w83j", // style URL
  preserveDrawingBuffer: true,
});

// t is zero to one
const lerp = (start, end, t) => {
  return [start[0] * t + end[0] * (1 - t), start[1] * t + end[1] * (1 - t)];
};

let baseData;
// t is between 0 and 1
const getCurrentData = (t, data) => {
  return {
    type: "FeatureCollection",
    features: data.features.map((x) => ({
      geometry: {
        type: "Point",
        coordinates: lerp(
          x.geometry.coordinates[0],
          x.geometry.coordinates[1],
          t
        ),
      },
      properties: x.properties,
    })),
  };
};

mapBoxMap.on("load", async () => {
  // fetch data and add it as a source
  await fetch("coral_progressive_test.geojson")
    .then((res) => res.json())
    .then((data) => {
      console.log(data);
      baseData = data;
      mapBoxMap.addSource("point", {
        type: "geojson",
        data: getCurrentData(1, data),
      });
      mapBoxMap.addLayer({
        id: "point",
        source: "point",
        type: "circle",
        paint: {
          "circle-radius": 1.4,
          "circle-color": "red",
        },
      });
    });

  CanvasCapture.init(
    document.getElementsByTagName("canvas")[0],
    { showRecDot: true } // Options are optional, more info below.
  );

  CanvasCapture.bindKeyToVideoRecord("v", {
    format: CanvasCapture.WEBM, // Options are optional, more info below.
    name: "myVideo",
    fps: 60,
  });

  // MAIN RENDER LOOP
  let currT = 1;
  let animationLen = 5; // seconds
  let fps = 60; // fps
  let increment = 1 / (animationLen * fps);

  function render() {
    if (currT - increment >= -increment * 120) {
      currT -= increment;
    } else {
      currT = 1;
    }

    // Update the map
    mapBoxMap
      .getSource("point")
      .setData(getCurrentData(currT < 0 ? 0 : currT, baseData));

    if (CanvasCapture.isRecording()) {
      CanvasCapture.recordFrame();
    }
    requestAnimationFrame(render);
  }

  render();
});
