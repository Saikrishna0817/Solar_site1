// District name canonicalisation for map joins.
// Mirrors normalize_district() + DISTRICT_ALIASES in
// backend/data_pipeline/solarpipeline/utils.py so site.district keys meet
// frontend/public/data/tg_ap_districts.geojson, which is built by
// scripts/build_district_geojson.py running that same function.
// ponytail: the 3-key alias map is copied from the backend; ceiling = silent
// key drift if the backend grows aliases. Upgrade path: serve `district`
// already canonical from /v1/sites, or have build_district_geojson.py emit
// the alias map alongside the geojson.
const DISTRICT_ALIASES = {
  anantapur: 'anantapuram',
  kadapa: 'ysr kadapa',
  mahbubnagar: 'mahabubnagar',
};

export const canonicalDistrict = (name) => {
  if (name === null || name === undefined) return null;
  const normalized = String(name)
    .trim()
    .toLowerCase()
    .replace(/\u2013/g, '-')
    .replace(/\u2014/g, '-');
  if (!normalized) return null;
  return DISTRICT_ALIASES[normalized] || normalized;
};

export default canonicalDistrict;
