import './App.css';
import Map from "react-map-gl";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import React from "react";
import { useState, useEffect } from 'react';

function getRandom(min, max) {
  return Math.random() * (max - min) + min;
}

function App({coral_url}) {

  const [data, setData] = useState([]);
  
  const getData = (url, callback) => {
    fetch(url, {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    })
      .then((response) => response.json())
      .then((myJSON) => {
        callback(myJSON.features);
      });
  };
  useEffect(() => {
    getData(coral_url, setData);
  }, []);

  const INITIAL_VIEW_STATE = {
    altitude: 1.5,
    bearing: 0,
    height: 1107,
    latitude: 40.75813025358964,
    longitude: -74.01063177933962,
    maxPitch: 60,
    maxZoom: 16,
    minPitch: 0,
    minZoom: 0,
    pitch: 0,
    width: 1065,
    zoom: 10.033299478365162

  };

  const mapboxToken = process.env.REACT_APP_MAPBOX_ACCESS_TOKEN;
  const mapStyle = "mapbox://styles/jfoss117/ckzr8kmjs002314lelqt0w83j";
  const layers = [
    new ScatterplotLayer({
      id: "scatter-plot",
      data: data,
      radiusScale: 80,
      radiusMinPixels: 0.01,
      getPosition: (d) => {
        return d.geometry.coordinates[1];
      },
      getRadius: 1,
      getFillColor: d => [255, 100 * getRandom(0.5, 1.6), 80, 200],
    }),
  ];

  return (
    <div className="Map">
    <DeckGL
      layers={layers}
      initialViewState={INITIAL_VIEW_STATE}
      controller={true}>
      <Map
        reuseMaps={true}
        mapboxApiAccessToken={mapboxToken}
        mapStyle={mapStyle}
        preventStyleDiffing={true}
      />
    </DeckGL>
    </div>
  );
}

export default App;
