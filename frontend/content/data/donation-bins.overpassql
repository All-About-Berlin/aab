[out:json][timeout:60];

// 1. Identify Berlin by its unique Area ID
area(3600062422)->.searchArea;

// 2. Collect all matching nodes, ways, and relations in one pass
(
  nwr["amenity"="recycling"]["recycling:clothes"="yes"](area.searchArea);
  nwr["amenity"="clothing_donation"](area.searchArea);
);

// 3. Output only the center points and essential tags to reduce data weight
out center qt;