/**
 * Carbon Storytelling Utilities
 * 
 * Converts abstract carbon metrics into relatable real-world equivalences.
 * Uses established conversion factors and contextual narratives.
 * 
 * Design principles:
 * - Accuracy: Based on verified conversion factors
 * - Relatability: Uses familiar reference points
 * - Enterprise-grade: Professional tone, no gamification
 * - Flexibility: Works with any carbon value (kg CO2e)
 */

/**
 * Conversion factors based on industry standards
 * Sources: EPA, IPCC, Carbon Trust, Columbia University
 */
const CONVERSION_FACTORS = {
  // Car miles: EPA estimates average passenger vehicle emits 4.6 kg CO2e/gallon
  // ~25 mpg average => 0.184 kg CO2e/mile (using 4.6 kg per gallon)
  carMilesPerKg: 1 / 0.184,
  
  // Trees: Average mature tree absorbs ~21 kg CO2e/year (varies 10-48 depending on species)
  // Using conservative mid-range estimate
  treesPerKg: 1 / 21,
  
  // Flight distance: Commercial flight emits ~0.0257 kg CO2e/km (short-haul)
  // Using short-haul average; long-haul more efficient per km
  flightKmPerKg: 1 / 0.0257,
  
  // LED bulb usage: LED 10W bulb emits ~0.01 kg CO2e per hour of operation
  // Based on typical grid carbon intensity (0.4 kg CO2/kWh in US, lower globally)
  ledHoursPerKg: 1 / 0.01,
  
  // Additional useful conversions
  gHomeEquivalent: 1 / (10500 * 0.0004), // Average US home ~10,500 kWh/year at ~0.4 kg CO2/kWh
  passengersOnFlightHoursPerKg: 1 / (0.0257 * 400), // Shared across 400 passengers
};

/**
 * Calculate car miles equivalent
 * Represents distance a typical car would drive to emit same CO2
 * 
 * @param {number} carbonKg - CO2 equivalent in kg
 * @returns {number} - Approximate miles
 */
export function calculateCarMiles(carbonKg) {
  return carbonKg * CONVERSION_FACTORS.carMilesPerKg;
}

/**
 * Calculate trees needed for annual offset
 * Represents how many mature trees would be needed to absorb CO2 over a year
 * 
 * @param {number} carbonKg - CO2 equivalent in kg
 * @returns {number} - Number of trees
 */
export function calculateTreesNeeded(carbonKg) {
  return carbonKg * CONVERSION_FACTORS.treesPerKg;
}

/**
 * Calculate flight distance equivalent
 * Represents distance a round-trip flight would be with same carbon footprint
 * 
 * @param {number} carbonKg - CO2 equivalent in kg
 * @returns {number} - Approximate flight distance in km
 */
export function calculateFlightDistance(carbonKg) {
  return carbonKg * CONVERSION_FACTORS.flightKmPerKg;
}

/**
 * Calculate LED bulb hours equivalent
 * Represents hours a LED light could run with equivalent energy
 * 
 * @param {number} carbonKg - CO2 equivalent in kg
 * @returns {number} - Approximate hours
 */
export function calculateLedHours(carbonKg) {
  return carbonKg * CONVERSION_FACTORS.ledHoursPerKg;
}

/**
 * Format car miles for display
 * Returns human-readable equivalent like "250 miles of daily driving"
 * 
 * @param {number} carbonKg - CO2 equivalent in kg
 * @returns {Object} - { value: number, distance: string, description: string }
 */
export function formatCarMilesStory(carbonKg) {
  const miles = calculateCarMiles(carbonKg);
  
  let distance = '';
  let description = '';
  
  if (miles < 10) {
    distance = `${miles.toFixed(1)} miles`;
    description = 'a quick trip across town';
  } else if (miles < 100) {
    distance = `${miles.toFixed(0)} miles`;
    description = 'a day trip by car';
  } else if (miles < 500) {
    distance = `${miles.toFixed(0)} miles`;
    description = 'a long weekend road trip';
  } else if (miles < 2000) {
    distance = `${miles.toFixed(0)} miles`;
    description = 'a cross-country drive';
  } else {
    distance = `${(miles / 1000).toFixed(1)}k miles`;
    description = `${Math.round(miles / 1000)} times across the US`;
  }
  
  return {
    value: miles,
    distance,
    description
  };
}

/**
 * Format trees needed for display
 * Returns contextual narrative about offsetting
 * 
 * @param {number} carbonKg - CO2 equivalent in kg
 * @returns {Object} - { value: number, count: string, description: string, symbol: string }
 */
export function formatTreesStory(carbonKg) {
  const trees = calculateTreesNeeded(carbonKg);
  
  let count = '';
  let description = '';
  let symbol = '🌱'; // seedling
  
  if (trees < 0.5) {
    count = 'less than 1 tree';
    description = 'minimal offset needed';
  } else if (trees < 1) {
    count = `${trees.toFixed(2)} trees`;
    description = 'fraction of a mature tree';
  } else if (trees < 5) {
    count = `${Math.round(trees)} trees`;
    description = 'a small garden plot';
    symbol = '🌲';
  } else if (trees < 25) {
    count = `${Math.round(trees)} trees`;
    description = 'a neighborhood park';
    symbol = '🌳';
  } else if (trees < 100) {
    count = `${Math.round(trees)} trees`;
    description = 'a small forest';
    symbol = '🌲';
  } else {
    count = `${Math.round(trees)} trees`;
    description = `a medium-sized woodland`;
    symbol = '🌲';
  }
  
  return {
    value: trees,
    count,
    description,
    symbol
  };
}

/**
 * Format flight distance for display
 * Returns contextual narrative about travel distance
 * 
 * @param {number} carbonKg - CO2 equivalent in kg
 * @returns {Object} - { value: number, distance: string, route: string, description: string }
 */
export function formatFlightStory(carbonKg) {
  const km = calculateFlightDistance(carbonKg);
  const miles = km * 0.621371;
  
  let distance = '';
  let route = '';
  let description = '';
  
  if (km < 500) {
    distance = `${km.toFixed(0)} km`;
    route = 'regional flight';
    description = 'like a short hop between nearby cities';
  } else if (km < 2000) {
    distance = `${km.toFixed(0)} km`;
    route = 'medium-distance flight';
    description = `like flying from coast to nearby coast`;
  } else if (km < 5000) {
    distance = `${km.toFixed(0)} km`;
    route = 'long-haul flight';
    description = 'like a transatlantic crossing';
  } else if (km < 10000) {
    distance = `${km.toFixed(0)} km`;
    route = 'intercontinental flight';
    description = 'like flying halfway around the world';
  } else {
    distance = `${(km / 1000).toFixed(1)}k km`;
    route = 'multiple world tours';
    description = `equivalent to ${Math.round(km / 40000)} times around Earth`;
  }
  
  return {
    value: km,
    distance,
    route,
    description,
    miles: miles.toFixed(0)
  };
}

/**
 * Format LED bulb hours for display
 * Returns contextual narrative about energy equivalence
 * 
 * @param {number} carbonKg - CO2 equivalent in kg
 * @returns {Object} - { value: number, hours: string, days: string, description: string }
 */
export function formatLedStory(carbonKg) {
  const hours = calculateLedHours(carbonKg);
  const days = hours / 24;
  const years = days / 365;
  
  let timeframe = '';
  let description = '';
  
  if (hours < 100) {
    timeframe = `${hours.toFixed(1)} hours`;
    description = 'a few nights of lighting';
  } else if (hours < 1000) {
    timeframe = `${(hours / 24).toFixed(1)} days`;
    description = 'continuous LED lighting for a few days';
  } else if (hours < 8760) { // ~1 year
    timeframe = `${(hours / 24).toFixed(0)} days`;
    description = `a few months of continuous LED use`;
  } else if (hours < 87600) {
    timeframe = `${(hours / 8760).toFixed(1)} years`;
    description = 'years of continuous LED operation';
  } else {
    timeframe = `${(hours / 8760).toFixed(0)} years`;
    description = `${Math.round(hours / 8760)} decades of LED lighting`;
  }
  
  return {
    value: hours,
    hours: timeframe,
    days: (days).toFixed(1),
    description
  };
}

/**
 * Generate a contextual narrative message based on carbon amount
 * Professional tone, no gimmicks
 * 
 * @param {number} carbonKg - Annual CO2 equivalent in kg
 * @param {string} context - Optional context ('storage', 'computing', 'general')
 * @returns {string} - A single narrative sentence
 */
export function generateCarbonNarrative(carbonKg, context = 'general') {
  // Determine impact level
  const level = carbonKg < 10 ? 'minimal' :
                carbonKg < 50 ? 'small' :
                carbonKg < 200 ? 'moderate' :
                carbonKg < 1000 ? 'significant' :
                carbonKg < 5000 ? 'substantial' :
                'major';
  
  const cars = Math.round(calculateCarMiles(carbonKg));
  const trees = Math.round(calculateTreesNeeded(carbonKg));
  const flight = calculateFlightDistance(carbonKg);
  
  // Context-specific narratives
  const contextPrefix = {
    storage: 'Your data storage footprint ',
    computing: 'Your computing operations ',
    general: 'This carbon footprint '
  }[context] || 'This carbon footprint ';
  
  // Generate narrative based on impact level
  switch (level) {
    case 'minimal':
      return `${contextPrefix}is minimal—equivalent to driving less than ${cars} miles or planting a fraction of a tree.`;
    case 'small':
      return `${contextPrefix}is modest—about the same as a short car trip or one ${trees} tree planted.`;
    case 'moderate':
      return `${contextPrefix}is moderate—comparable to ${trees} trees needed for offset or a weekend road trip of ${cars} miles.`;
    case 'significant':
      return `${contextPrefix}is significant—equivalent to ${trees} mature trees or a long-distance flight of ${Math.round(flight / 1000)}k kilometers.`;
    case 'substantial':
      return `${contextPrefix}is substantial—requiring ${trees} trees to offset, or equivalent to extensive vehicle travel of ${Math.round(cars / 1000)}k miles.`;
    case 'major':
      return `${contextPrefix}is major—would require ${trees}+ trees for offset and represents substantial environmental consideration.`;
    default:
      return `${contextPrefix}represents ${Math.round(carbonKg)} kg of CO2 equivalent annually.`;
  }
}

/**
 * Get all story elements at once for efficient rendering
 * Returns an object with all formatted equivalences
 * 
 * @param {number} carbonKg - CO2 equivalent in kg
 * @param {string} context - Optional context for narrative (default: 'general')
 * @returns {Object} - Complete story data { cars, trees, flight, led, narrative }
 */
export function getCarbonStory(carbonKg, context = 'general') {
  return {
    cars: formatCarMilesStory(carbonKg),
    trees: formatTreesStory(carbonKg),
    flight: formatFlightStory(carbonKg),
    led: formatLedStory(carbonKg),
    narrative: generateCarbonNarrative(carbonKg, context),
    raw: {
      kg: carbonKg,
      pounds: carbonKg * 2.20462
    }
  };
}

/**
 * Get a single formatted equivalence for compact display
 * Useful for sidebar or summary views
 * 
 * @param {number} carbonKg - CO2 equivalent in kg
 * @param {string} type - Type of equivalence: 'cars', 'trees', 'flight', or 'led'
 * @returns {string} - Formatted equivalence text
 */
export function getCompactEquivalence(carbonKg, type = 'trees') {
  const stories = {
    cars: () => {
      const story = formatCarMilesStory(carbonKg);
      return `${story.distance} driving`;
    },
    trees: () => {
      const story = formatTreesStory(carbonKg);
      return `${story.count} to offset`;
    },
    flight: () => {
      const story = formatFlightStory(carbonKg);
      return `${story.distance} flight`;
    },
    led: () => {
      const story = formatLedStory(carbonKg);
      return `${story.hours} LED usage`;
    }
  };
  
  return (stories[type] || stories.trees)();
}

export default {
  calculateCarMiles,
  calculateTreesNeeded,
  calculateFlightDistance,
  calculateLedHours,
  formatCarMilesStory,
  formatTreesStory,
  formatFlightStory,
  formatLedStory,
  generateCarbonNarrative,
  getCarbonStory,
  getCompactEquivalence
};
