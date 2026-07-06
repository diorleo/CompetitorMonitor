// prices.js — Product price data for MOZA Competitor Price Monitor
// Auto-updated by GitHub Actions (monthly)
// Last manual update: 2026-07

const BRAND_COLORS = {
  'MOZA': '#e63946',
  'Fanatec': '#4895ef',
  'Simagic': '#9b72cf',
  'Logitech': '#2dc653',
  'Thrustmaster': '#f4a261',
  'Asetek': '#43d9d1',
  'PXN': '#ffc107',
  'Thermaltake': '#6c757d',
  'Honeycomb': '#20c997',
  'Virpil': '#e83e8c',
  'VKB': '#fd7e14',
  'Winwing': '#0dcaf0',
};

// Racing sim products data — MOZA prices from us.mozaracing.com (Jul 2026)
const RACING_PRODUCTS = [
  // --- MOZA RS series (official USD prices) ---
  { brand: 'MOZA', cat: 'Bundle', name: 'R5 Racing Simulator Bundle', price: 379, note: 'Sale $599→$379' },
  { brand: 'MOZA', cat: 'Bundle', name: 'R5 Trucking Bundle', price: 379, note: 'Sale $599→$379' },
  { brand: 'MOZA', cat: 'Wheel Base', name: 'R9 V3 Direct Drive (9Nm)', price: 299, note: 'Sale $349→$299' },
  { brand: 'MOZA', cat: 'Wheel Base', name: 'R12 V2 Direct Drive (12Nm)', price: 399, note: 'Sale $469→$399' },
  { brand: 'MOZA', cat: 'Wheel Base', name: 'R21 Ultra Direct Drive (21Nm)', price: 699, note: '21Nm' },
  { brand: 'MOZA', cat: 'Wheel Base', name: 'R25 Ultra True Torque (25Nm)', price: 899, note: '25Nm' },
  { brand: 'MOZA', cat: 'Steering Wheel', name: 'ES Steering Wheel', price: 129, note: 'Entry' },
  { brand: 'MOZA', cat: 'Steering Wheel', name: 'CS V2P Steering Wheel', price: 229, note: 'Sale $279→$229' },
  { brand: 'MOZA', cat: 'Steering Wheel', name: 'CS Pro Steering Wheel', price: 329, note: '325mm' },
  { brand: 'MOZA', cat: 'Steering Wheel', name: 'RS V2 Steering Wheel', price: 369, note: 'Sale $439→$369' },
  { brand: 'MOZA', cat: 'Steering Wheel', name: 'KS Steering Wheel', price: 229, note: 'Sale $279→$229' },
  { brand: 'MOZA', cat: 'Steering Wheel', name: 'KS Pro Steering Wheel', price: 329, note: '300mm' },
  { brand: 'MOZA', cat: 'Steering Wheel', name: 'GS V2P GT Wheel', price: 369, note: 'Sale $399→$369' },
  { brand: 'MOZA', cat: 'Steering Wheel', name: 'FSR2 Formula Wheel', price: 649, note: '280mm' },
  { brand: 'MOZA', cat: 'Steering Wheel', name: 'Vision GS Steering Wheel', price: 699, note: 'Sale $749→$699' },
  { brand: 'MOZA', cat: 'Steering Wheel', name: 'TSW Truck Wheel', price: 229, note: 'Sale $299→$229' },
  { brand: 'MOZA', cat: 'Steering Wheel', name: 'Lamborghini Essenza SCV12', price: 1299, note: 'Licensed' },
  { brand: 'MOZA', cat: 'Steering Wheel', name: 'Porsche MISSION R SW', price: 1299, note: 'Licensed' },
  { brand: 'MOZA', cat: 'Pedal', name: 'SRP2 Pedals', price: 149, note: 'Dual 100kg' },
  { brand: 'MOZA', cat: 'Pedal', name: 'CRP2 Load Cell Pedals', price: 369, note: 'Sale $399→$369' },
  { brand: 'MOZA', cat: 'Pedal', name: 'mBooster Active Pedal', price: 759, note: 'Sale $799→$759' },
  { brand: 'MOZA', cat: 'Pedal', name: 'mBooster Pedal Set', price: 949, note: 'Sale $999→$949' },
  { brand: 'MOZA', cat: 'Accessory', name: 'HGP Shifter', price: 149, note: '' },
  { brand: 'MOZA', cat: 'Accessory', name: 'HBP Handbrake', price: 99, note: '' },

  // --- Fanatec (official store prices) ---
  { brand: 'Fanatec', cat: 'Wheel Base', name: 'CSL DD QR2 (5Nm)', price: 399.99, note: 'Entry DD' },
  { brand: 'Fanatec', cat: 'Wheel Base', name: 'CSL DD+ (8Nm)', price: 599.99, note: 'Boost kit' },
  { brand: 'Fanatec', cat: 'Wheel Base', name: 'GT DD Pro (8Nm)', price: 599.99, note: 'PlayStation' },
  { brand: 'Fanatec', cat: 'Wheel Base', name: 'ClubSport DD (15Nm)', price: 699.99, note: '15Nm holding' },
  { brand: 'Fanatec', cat: 'Wheel Base', name: 'Podium DD (25Nm)', price: 1199, note: 'New flagship' },
  { brand: 'Fanatec', cat: 'Steering Wheel', name: 'CSL GT3 Wheel', price: 229.99, note: 'QR2 Lite' },
  { brand: 'Fanatec', cat: 'Steering Wheel', name: 'CSL Elite Porsche VGT', price: 349.99, note: '' },
  { brand: 'Fanatec', cat: 'Steering Wheel', name: 'ClubSport Formula V3', price: 349.99, note: '' },
  { brand: 'Fanatec', cat: 'Steering Wheel', name: 'ClubSport RS V2', price: 369.99, note: '' },
  { brand: 'Fanatec', cat: 'Steering Wheel', name: 'Podium Porsche 911 GT3 R', price: 774.99, note: 'Leather' },
  { brand: 'Fanatec', cat: 'Steering Wheel', name: 'Podium BMW M4 GT3', price: 1599.99, note: '' },
  { brand: 'Fanatec', cat: 'Pedal', name: 'CSL Pedals', price: 139.99, note: 'Entry' },
  { brand: 'Fanatec', cat: 'Pedal', name: 'CSL Pedals LC', price: 199.99, note: 'Load cell' },
  { brand: 'Fanatec', cat: 'Pedal', name: 'CSL Elite Pedals V2', price: 329.99, note: '90kg' },
  { brand: 'Fanatec', cat: 'Pedal', name: 'ClubSport Pedals V3', price: 429.99, note: '90kg' },
  { brand: 'Fanatec', cat: 'Pedal', name: 'ClubSport Pedals V3 Inverted', price: 449.99, note: '' },
  { brand: 'Fanatec', cat: 'Accessory', name: 'CSL Shifter', price: 249.99, note: 'SQ V1.5' },
  { brand: 'Fanatec', cat: 'Accessory', name: 'ClubSport Handbrake V2', price: 229.99, note: '' },
  { brand: 'Fanatec', cat: 'Bundle', name: 'CSL DD QR2 Ready2Race', price: 540, note: 'Base+wheel+pedals' },
  { brand: 'Fanatec', cat: 'Bundle', name: 'GT DD Pro Ready2Race', price: 999, note: 'PS bundle' },

  // --- Simagic ---
  { brand: 'Simagic', cat: 'Wheel Base', name: 'Alpha EVO Sport (9Nm)', price: 399, note: '9Nm' },
  { brand: 'Simagic', cat: 'Wheel Base', name: 'Alpha EVO (12Nm)', price: 549, note: '12Nm' },
  { brand: 'Simagic', cat: 'Wheel Base', name: 'Alpha EVO Pro (18Nm)', price: 699, note: '18Nm' },
  { brand: 'Simagic', cat: 'Wheel Base', name: 'Alpha EVO Ultra (28Nm)', price: 999, note: '28Nm' },
  { brand: 'Simagic', cat: 'Steering Wheel', name: 'GT Neo Steering Wheel', price: 239, note: 'Carbon fiber' },
  { brand: 'Simagic', cat: 'Steering Wheel', name: 'FX Pro Steering Wheel', price: 449, note: '' },
  { brand: 'Simagic', cat: 'Steering Wheel', name: 'FX EVO Steering Wheel', price: 549, note: '' },
  { brand: 'Simagic', cat: 'Pedal', name: 'P500 Pedals', price: 249, note: 'Load cell' },
  { brand: 'Simagic', cat: 'Pedal', name: 'P1000 Pedals', price: 499, note: '3-pedal' },
  { brand: 'Simagic', cat: 'Pedal', name: 'P700 Pedals (dual)', price: 299, note: '2-pedal' },
  { brand: 'Simagic', cat: 'Accessory', name: 'DS-8X Shifter', price: 219, note: '' },
  { brand: 'Simagic', cat: 'Bundle', name: 'EVO Sport + GT Neo Bundle', price: 599, note: '9Nm+wheel' },
  { brand: 'Simagic', cat: 'Bundle', name: 'EVO Pro + FX Pro Bundle', price: 1049, note: '18Nm+wheel' },

  // --- Asetek ---
  { brand: 'Asetek', cat: 'Wheel Base', name: 'Initium Direct Drive Base', price: 349, note: '~5Nm est.' },
  { brand: 'Asetek', cat: 'Wheel Base', name: 'Initium Boost Kit (8Nm)', price: 89, note: 'Upgrade' },
  { brand: 'Asetek', cat: 'Steering Wheel', name: 'Initium Steering Wheel', price: 149, note: '' },
  { brand: 'Asetek', cat: 'Pedal', name: 'Initium Pedal Set', price: 119, note: '2-pedal' },
  { brand: 'Asetek', cat: 'Pedal', name: 'Initium Clutch Upgrade', price: 39, note: '' },
  { brand: 'Asetek', cat: 'Bundle', name: 'Initium Racing Bundle (PC)', price: 599, note: 'Base+wheel+pedals' },
  { brand: 'Asetek', cat: 'Bundle', name: 'La Prima Formula + Base', price: 669, note: '' },
  { brand: 'Asetek', cat: 'Bundle', name: 'La Prima GT + Base', price: 711, note: '' },

  // --- Logitech (official store prices) ---
  { brand: 'Logitech', cat: 'Wheel Base', name: 'G923 TRUEFORCE (2.3Nm)', price: 299.99, note: 'Sale $50 off' },
  { brand: 'Logitech', cat: 'Wheel Base', name: 'G29 / G920 (2.3Nm)', price: 199, note: 'PS/PC or Xbox/PC' },
  { brand: 'Logitech', cat: 'Wheel Base', name: 'PRO Racing Wheel (11Nm DD)', price: 999, note: 'Direct Drive' },
  { brand: 'Logitech', cat: 'Pedal', name: 'PRO Racing Pedals', price: 349, note: 'Load cell' },
  { brand: 'Logitech', cat: 'Accessory', name: 'Driving Force Shifter', price: 59.99, note: '' },
  { brand: 'Logitech', cat: 'Bundle', name: 'G923 Racing Wheel + Pedals', price: 299.99, note: '2.3Nm, shifter free' },

  // --- Thrustmaster (official store prices) ---
  { brand: 'Thrustmaster', cat: 'Wheel Base', name: 'T128 (2Nm)', price: 199, note: 'Entry' },
  { brand: 'Thrustmaster', cat: 'Wheel Base', name: 'T248 (3Nm)', price: 349.99, note: 'Hybrid drive' },
  { brand: 'Thrustmaster', cat: 'Wheel Base', name: 'T300 RS GT (3.5Nm)', price: 399.99, note: 'Belt-driven' },
  { brand: 'Thrustmaster', cat: 'Wheel Base', name: 'TX Racing Wheel (3.5Nm)', price: 299.99, note: 'Xbox' },
  { brand: 'Thrustmaster', cat: 'Wheel Base', name: 'T-GT II (3.5Nm)', price: 699.99, note: 'Premium belt' },
  { brand: 'Thrustmaster', cat: 'Pedal', name: 'T-LCM Pedals', price: 229.99, note: 'Load cell' },
  { brand: 'Thrustmaster', cat: 'Pedal', name: 'T3PM Pedals', price: 129.99, note: 'Magnetic' },
  { brand: 'Thrustmaster', cat: 'Bundle', name: 'T248 + T3PM Bundle', price: 349.99, note: 'Xbox/PC' },

  // --- PXN (official store prices) ---
  { brand: 'PXN', cat: 'Wheel Base', name: 'V9 GEN2 Bundle', price: 179.99, note: 'Entry level' },
  { brand: 'PXN', cat: 'Wheel Base', name: 'V10 Ultra Bundle', price: 259.99, note: '3.2Nm' },
  { brand: 'PXN', cat: 'Wheel Base', name: 'VD6 Base (6Nm)', price: 329, note: 'DD, solo' },
  { brand: 'PXN', cat: 'Wheel Base', name: 'VD10 Base (10Nm)', price: 369, note: 'DD, solo' },
  { brand: 'PXN', cat: 'Steering Wheel', name: 'GT ONE Steering Wheel', price: 219, note: '' },
  { brand: 'PXN', cat: 'Steering Wheel', name: 'W DS R2 Wheel', price: 199, note: '' },
  { brand: 'PXN', cat: 'Steering Wheel', name: 'W CS R2 Wheel', price: 279, note: '' },
  { brand: 'PXN', cat: 'Pedal', name: 'Vector X Pedals', price: 129, note: '' },
  { brand: 'PXN', cat: 'Pedal', name: 'PD HM Pedals', price: 79, note: '' },
  { brand: 'PXN', cat: 'Accessory', name: 'SF SH Shifter', price: 299, note: '' },
  { brand: 'PXN', cat: 'Accessory', name: 'HB S Handbrake', price: 89, note: '' },
  { brand: 'PXN', cat: 'Bundle', name: 'VD6 Bundle', price: 399, note: 'Base+wheel+pedals' },
  { brand: 'PXN', cat: 'Bundle', name: 'VD10+W CS R2 Bundle', price: 539, note: '10Nm DD' },

  // --- Thermaltake (official store prices) ---
  { brand: 'Thermaltake', cat: 'Bundle', name: 'G6 DD Wheel + Pedals Bundle', price: 699.99, note: '6Nm DD' },
  { brand: 'Thermaltake', cat: 'Wheel Base', name: 'G6 Direct Drive Base (6Nm)', price: 499.99, note: 'Est. USD' },
  { brand: 'Thermaltake', cat: 'Wheel Base', name: 'GRB G15 DD Base (15Nm)', price: 999.99, note: '15Nm DD' },
  { brand: 'Thermaltake', cat: 'Steering Wheel', name: 'F100 Formula Wheel', price: 229.99, note: '' },
  { brand: 'Thermaltake', cat: 'Pedal', name: 'XRP-L1 Loadcell Pedals', price: 1399.99, note: 'High-end' },
];

// Flight sim products data — MOZA prices from us.mozaracing.com (Jul 2026)
const FLIGHT_PRODUCTS = [
  // --- MOZA AS series (official USD prices) ---
  { brand: 'MOZA', cat: 'Bundle', name: 'AB6 Flight Simulator', price: 399, note: '6Nm 2-servo' },
  { brand: 'MOZA', cat: 'Base', name: 'AB9 FFB Base (12Nm)', price: 499, note: 'Sale $549→$499' },
  { brand: 'MOZA', cat: 'Base', name: 'AY210 FFB Yoke Base', price: 699, note: '9Nm' },
  { brand: 'MOZA', cat: 'Bundle', name: 'AY210 FFB Yoke Bundle', price: 848, note: 'Sale $868→$848' },
  { brand: 'MOZA', cat: 'Grip', name: 'MHG Flight Stick', price: 99, note: '29 signals' },
  { brand: 'MOZA', cat: 'Grip', name: 'MH16 Flightstick', price: 149, note: 'Sale $169→$149' },
  { brand: 'MOZA', cat: 'Grip', name: 'MA3X Sidestick', price: 79, note: '12 signals' },
  { brand: 'MOZA', cat: 'Grip', name: 'MFY YOKE Grip', price: 129, note: '34 signals' },
  { brand: 'MOZA', cat: 'Throttle', name: 'MTP Throttle Panel', price: 299, note: 'Sale $329→$299' },
  { brand: 'MOZA', cat: 'Throttle', name: 'MTQ Throttle Quadrant', price: 199, note: 'Modular' },
  { brand: 'MOZA', cat: 'Throttle', name: 'MTLP Take-off Landing Panel', price: 149, note: '27 switches' },
  { brand: 'MOZA', cat: 'Rudder', name: 'MRP Rudder Pedals', price: 349, note: 'All-metal' },
  { brand: 'MOZA', cat: 'Accessory', name: 'Z-Axis Module', price: 89, note: '' },
  { brand: 'MOZA', cat: 'Accessory', name: 'Flight Base Table Clamp', price: 49, note: 'Sale $59→$49' },
  { brand: 'MOZA', cat: 'Accessory', name: 'Table Clamp For Yoke', price: 19, note: 'Sale $25→$19' },
  { brand: 'MOZA', cat: 'Accessory', name: 'TQB Throttle Module', price: 39, note: '' },
  { brand: 'MOZA', cat: 'Accessory', name: 'TQA Throttle Module', price: 39, note: '' },
  { brand: 'MOZA', cat: 'Accessory', name: 'MRP Adjustable Damper', price: 65, note: 'Optional' },
  { brand: 'MOZA', cat: 'Accessory', name: 'Flight Base Mount Adapter', price: 25, note: '' },

  // --- Logitech Flight ---
  { brand: 'Logitech', cat: 'Base', name: 'Pro Flight Yoke System', price: 249, note: 'Yoke+throttle' },
  { brand: 'Logitech', cat: 'Throttle', name: 'Pro Flight Throttle Quadrant', price: 99, note: '' },
  { brand: 'Logitech', cat: 'Rudder', name: 'Pro Flight Rudder Pedals', price: 129, note: '' },
  { brand: 'Logitech', cat: 'Grip', name: 'Pro Flight X56 HOTAS', price: 249, note: 'Stick+throttle' },
  { brand: 'Logitech', cat: 'Grip', name: 'Pro Flight X52 HOTAS', price: 169, note: 'Stick+throttle' },

  // --- Thrustmaster Flight ---
  { brand: 'Thrustmaster', cat: 'Grip', name: 'T.Flight HOTAS X', price: 79, note: 'PC/Xbox' },
  { brand: 'Thrustmaster', cat: 'Grip', name: 'T.16000M FCS Flight Pack', price: 199, note: 'Stick+throttle+pedals' },
  { brand: 'Thrustmaster', cat: 'Base', name: 'TCA Yoke Pack (Boeing)', price: 399, note: 'Yoke+throttle' },
  { brand: 'Thrustmaster', cat: 'Throttle', name: 'TCA Captain Pack (Airbus)', price: 299, note: 'Stick+throttle' },
  { brand: 'Thrustmaster', cat: 'Rudder', name: 'TFRP Rudder Pedals', price: 129, note: '' },
  { brand: 'Thrustmaster', cat: 'Grip', name: 'T16000M FCS Flight Stick', price: 69, note: '' },

  // --- Honeycomb (flight focus) (official store prices) ---
  { brand: 'Honeycomb', cat: 'Base', name: 'Alpha Flight Controls Yoke', price: 299.99, note: 'Yoke+switch' },
  { brand: 'Honeycomb', cat: 'Throttle', name: 'Bravo Throttle Quadrant', price: 299.99, note: '' },
  { brand: 'Honeycomb', cat: 'Rudder', name: 'Charlie Rudder Pedals', price: 299.99, note: 'Est. USD' },

  // --- PXN Flight (NAVOS series announced) ---
  { brand: 'PXN', cat: 'Grip', name: 'NAVOS Flight Stick (announced)', price: 149, note: 'Est. USD' },
  { brand: 'PXN', cat: 'Base', name: 'NAVOS Yoke System (announced)', price: 249, note: 'Est. USD' },

  // --- Virpil (EUR converted to USD, official EU store) ---
  { brand: 'Virpil', cat: 'Grip', name: 'Alpha Prime Grip [R]', price: 270, note: '€249.95' },
  { brand: 'Virpil', cat: 'Grip', name: 'Alpha Prime Grip [L]', price: 270, note: '€249.95' },
  { brand: 'Virpil', cat: 'Base', name: 'WarBRD-D Base', price: 240, note: '€219.95' },
  { brand: 'Virpil', cat: 'Base', name: 'MongoosT-50CM3 Base', price: 345, note: '€319.95' },
  { brand: 'Virpil', cat: 'Throttle', name: 'VMAX Prime Throttle', price: 465, note: '€429.95' },
  { brand: 'Virpil', cat: 'Throttle', name: 'CDT-VMAX Throttle', price: 250, note: '€229.95' },

  // --- VKB (mid-high flight) ---
  { brand: 'VKB', cat: 'Grip', name: 'Gunfighter Mk.IV Grip', price: 199, note: '' },
  { brand: 'VKB', cat: 'Base', name: 'Gunfighter Mk.IV Base', price: 249, note: 'Magnetic base' },
  { brand: 'VKB', cat: 'Throttle', name: 'STECS Mini Plus Throttle', price: 179, note: '' },
  { brand: 'VKB', cat: 'Rudder', name: 'TKP-RP Rudders', price: 239, note: '' },

  // --- Winwing (flight) ---
  { brand: 'Winwing', cat: 'Base', name: 'Orion 2 HOTAS Base', price: 199, note: '' },
  { brand: 'Winwing', cat: 'Grip', name: 'F-16EX Grip', price: 129, note: '' },
  { brand: 'Winwing', cat: 'Throttle', name: 'Orion 2 Throttle', price: 249, note: '' },
];
