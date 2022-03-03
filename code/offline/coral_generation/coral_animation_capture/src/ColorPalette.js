// Mapbox expressions for making the dots different colors 
let county_level_jeff_original = {
  water_color: "#929fb0",
  color_expression: [
    "match",
    ["get", "county"],
    "Queens County",
    "#ffc9c1",
    "Bronx County",
    "#fc8b78",
    "New York County",
    "#ff7162",
    "Richmond County",
    "#434152",
    "Kings County",
    "#79647f",
    "#ccc"]
  
  };

let county_level_jeff_current_color_information = {
  water_color: "#3a414b",
  color_expression: [
    "match",
    ["get", "county"],
    "Queens County",
    "#FA5C5C",
    "Bronx County",
    "#F7C4BC",
    "New York County",
    "#ff7162",
    "Richmond County",
    "#1E1E2F",
    "Kings County",
    "#70538C",
    "#ccc",
  ],
  color_expression_desaturated_alt: [
    "match",
    ["get", "county"],
    "Queens County",
    "#EE7A7A",
    "Bronx County",
    "#F3CCC6",
    "New York County",
    "#F28A7F",
    "Richmond County",
    "#575566",
    "Kings County",
    "#7E6085",
    "#ccc",
  ],
  color_expression_desaturated: "grey",
  radius_info: {
    radius_large: 2.1,
    radius_small: 1.9,
  },
  coral_opacity: 1,
  static_opacity: 0.7,
};

let county_level_evan_proposal = [
  "match",
  ["get", "county"],
  "Queens County",
  "#4538A5",
  "Bronx County",
  "#C1466D",
  "New York County",
  "#FF7162",
  "Richmond County",
  "#FFCC3F",
  "Kings County",
  "#FF8D46",
  "#ccc",
];

let race_level_expression = [
  "match",
  ["get", "race"],
  "White_alone",
  "#ffc9c1",
  "Hispanic_or_Latino_(Any_Race)",
  "#fc8b78",
  "Black_or_African_American_alone",
  "#ff7162",
  "Asian_alone",
  "#434152",
  "Some_other_race_alone",
  "#79647f",
  /* other */ "#ccc",
];

// TODO: Poverty information
// 2.00 and over': 4139,
//          '.50 to .99': 591,
//          '1.00 to 1.24': 293,
//          '1.25 to 1.49': 246,
//          'Under .50': 489,
//          '1.85 to 1.99': 118,
//          '1.50 to 1.84': 362})