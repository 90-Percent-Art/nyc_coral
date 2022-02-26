import './App.css';
import Map from "react-map-gl";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer, SolidPolygonLayer } from "@deck.gl/layers";
import React from "react";
import { useState, useEffect } from 'react';

function getRandom(min, max) {
  return Math.random() * (max - min) + min;
}

function App({coral_url}) {
  const [data, setData] = useState([]);
  const [floodLevel, setFloodLevel] = useState(0); // nobody is flooded here
  const [floodPolygons, setFloodPolygons] = useState([]);

  let floodLevels = [24.0,17.0, 15.0, 14.0,13.0,12.0,11.0,10.0,0.0];

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
    getData(coral_url, setData); // get the coral data
    getData("sea_level_rise_2020s_500.geojson", setFloodPolygons); // get the flood polygons
    console.log(floodPolygons);
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
    zoom: 10.033299478365162,
  };

  const pointIsFlooded = (point) => {
    return (
      point.properties.flood_2020_500.flood_polygon_aggregate_metadata
        .max_static_bfe >= floodLevels[floodLevel]
    );
  }

  const mapboxToken = process.env.REACT_APP_MAPBOX_ACCESS_TOKEN;
  const mapStyle = "mapbox://styles/jfoss117/ckzr8kmjs002314lelqt0w83j";
  const layers = [
    new ScatterplotLayer({
      id: "scatter-plot",
      data: data,
      radiusScale: 80,
      radiusMinPixels: 0.01,
      getPosition: (d) => {
        if (pointIsFlooded(d)) {
          let pt = d.geometry.coordinates[1];
          return [pt[0], pt[1]-0.1]; // 1 means coral, 0 means home.
        } else{
          return d.geometry.coordinates[0];
        }
      },
      getRadius: 1,
      getFillColor: (d) => [255, 100 * getRandom(0.5, 1.6), 80, 200],
      updateTriggers:{
        getPosition: [floodLevel]
      }, 
      transitions:{
        getPosition:{
          duration: 500,
        }
      }
    }),
    new SolidPolygonLayer({
      id: "polygon-layer",
      data: floodPolygons,
      filled: true,
      stroked: true,
      visible: true,
      lineWidthMinPixels: 1,
      getPolygon: (d) => d.geometry.coordinates[0],
      getFillColor: (d) => {
        if (parseInt(d.properties.static_bfe) >= floodLevels[floodLevel]) {
          return [146, 184, 221, 125];
        } else {
          return [146, 184, 221, 0];
        }
      }, 
      updateTriggers: {
        getFillColor: [floodLevel]
      }, 
      transitions:{
        getFillColor:{
          duration: 1000,
        }
      }
    }),
  ];

  return (
    <>
      <div className='Container'>
      <div className={"Buttons"}>
        <button
          onClick={() => {
            setFloodLevel((prev) => prev>7?0:prev + 1);
            console.log(floodLevel);
          }}
        >
          FloodLevel
        </button>
      </div>
      <div className={"MyMap"}>
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
      </div>
    </>
  );
}

export default App;
