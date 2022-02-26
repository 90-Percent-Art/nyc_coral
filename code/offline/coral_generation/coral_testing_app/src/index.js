import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';

ReactDOM.render(
  <React.StrictMode>
    <App coral_url = "coral_progressive_test.geojson" />
  </React.StrictMode>,
  document.getElementById('root')
);
