import './App.css';
import Map from "react-map-gl";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import React from "react";
import { useState, useEffect } from 'react';

function App() {

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
    getData("coral_test.geojson", setData);
  }, []);

  const INITIAL_VIEW_STATE = {
    longitude: -74,
    latitude: 40.7,
    zoom: 11,
    maxZoom: 16,
    pitch: 0,
    bearing: 0
  };

  const mapboxToken = process.env.REACT_APP_MAPBOX_ACCESS_TOKEN;
  const mapStyle = "mapbox://styles/jfoss117/ckzr8kmjs002314lelqt0w83j";
  const layers = [
    new ScatterplotLayer({
      id: "scatter-plot",
      data: data,
      radiusScale: 80,
      radiusMinPixels: 0.25,
      getPosition: (d) => {
        return d.geometry.coordinates[1];
      },
      getRadius: 0.7,
      getFillColor: [0, 0, 20, 80],
    }),
  ];

  return (
    <div className="Map">
    <DeckGL
      layers={layers}
      initialViewState={INITIAL_VIEW_STATE}
      controller={true}
    >
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
