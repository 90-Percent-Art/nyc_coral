import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';

ReactDOM.render(
  <React.StrictMode>
    <App coral_url = "/coral_tests/coral_latest.geojson" />
  </React.StrictMode>,
  document.getElementById('root')
);
