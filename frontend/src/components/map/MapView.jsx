import { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Rectangle, Polygon, useMap, useMapEvents } from 'react-leaflet';
import { MAP_CONFIG } from '../../data/constants';
import { suitabilityToColor, getMarkerRadius } from '../../utils/colorScale';
import { formatScore, formatCapacity } from '../../utils/formatters';
import 'leaflet/dist/leaflet.css';

const DISTRICT_GEO_URL = '/data/tg_ap_districts.geojson';
const NO_DATA_FILL = '#1E3A52'; // space-border: neutral, reads as "no data" on the dark tiles

/* ─── District geometry loader ──────────────────────────── */
// Module-level cache: the file is immutable for a session, so it is fetched once
// even if MapView remounts (route changes, filter re-renders).
let districtGeoPromise = null;
const loadDistrictGeojson = () => {
  if (!districtGeoPromise) {
    districtGeoPromise = fetch(DISTRICT_GEO_URL)
      .then((res) => {
        if (!res.ok) throw new Error(`district geojson: ${res.status}`);
        return res.json();
      })
      .catch((err) => {
        districtGeoPromise = null; // failed — let the next mount retry
        throw err;
      });
  }
  return districtGeoPromise;
};

// undefined = not requested yet, null = load failed
const useDistrictGeometry = (enabled) => {
  const [geojson, setGeojson] = useState(undefined);
  useEffect(() => {
    if (!enabled) return undefined;
    let alive = true;
    loadDistrictGeojson()
      .then((g) => { if (alive) setGeojson(g); })
      .catch(() => { if (alive) setGeojson(null); });
    return () => { alive = false; };
  }, [enabled]);
  return geojson;
};

// GeoJSON positions are [lng, lat]; Leaflet wants [lat, lng] at every depth.
const swapCoords = (node) => (
  typeof node[0] === 'number' ? [node[1], node[0]] : node.map(swapCoords)
);

// Canonical district keys are lowercase ("east godavari"); show them readable.
const titleCase = (s) => String(s).replace(/\b[a-z]/g, (c) => c.toUpperCase());


/* ─── Fly-to-site helper ───────────────────────────────── */
const FlyToSite = ({ site }) => {
  const map = useMap();
  useEffect(() => {
    if (site) map.flyTo([site.lat, site.lng], 10, { duration: 1.5 });
  }, [site, map]);
  return null;
};

/* ─── Fly-to-bbox helper ───────────────────────────────── */
const FlyToBBox = ({ bounds }) => {
  const map = useMap();
  useEffect(() => {
    if (bounds) {
      map.flyToBounds(bounds, { padding: [60, 60], duration: 1.2 });
    }
  }, [bounds, map]);
  return null;
};

/* ─── Click handler for polygon draw mode ─────────────── */
const DrawHandler = ({ drawMode, onMapClick }) => {
  const map = useMap();

  useEffect(() => {
    const container = map.getContainer();
    if (drawMode) {
      container.classList.add('draw-mode');
    } else {
      container.classList.remove('draw-mode');
    }
    return () => container.classList.remove('draw-mode');
  }, [drawMode, map]);

  useMapEvents({
    click(e) {
      if (drawMode && onMapClick) {
        onMapClick(e.latlng);
      }
    },
  });
  return null;
};

/* ─── Main MapView ───────────────────────────────── */
// ponytail: props are intentionally untyped (repo-wide — propTypes were dropped,
// see the note in App.jsx); ceiling = eslint react/prop-types errors here.
// Upgrade path = PropTypes blocks or a TS .tsx port when a prop bug bites.
const MapView = ({
  sites = [],
  selectedSite,
  onSiteSelect,
  bboxBounds,
  polygonPoints = [],
  drawMode = false,
  onMapClick,
  districts,
  className = '',
}) => {
  // Optional district choropleth — omitted entirely (no fetch, no layers) when
  // the prop is not passed, so existing callers behave exactly as before.
  const districtGeojson = useDistrictGeometry(Boolean(districts));

  const districtEntries = useMemo(() => {
    if (!districts) return null;
    const byDistrict = new Map();
    districts.forEach((d) => byDistrict.set(d.district, d));
    return byDistrict;
  }, [districts]);

  return (
    <div className={`relative w-full h-full rounded-xl overflow-hidden border border-space-border ${className}`}>
      <MapContainer
        center={MAP_CONFIG.center}
        zoom={MAP_CONFIG.zoom}
        minZoom={MAP_CONFIG.minZoom}
        maxZoom={MAP_CONFIG.maxZoom}
        className="w-full h-full"
        style={{ background: '#0A0E1A' }}
        zoomControl={true}
      >
        <TileLayer
          url={MAP_CONFIG.tileUrl}
          attribution={MAP_CONFIG.tileAttribution}
        />

        {selectedSite && <FlyToSite site={selectedSite} />}
        {bboxBounds && <FlyToBBox bounds={bboxBounds} />}

        <DrawHandler drawMode={drawMode} onMapClick={onMapClick} />

        {/* ─── Bounding Box Rectangle ────── */}
        {bboxBounds && (
          <Rectangle
            bounds={bboxBounds}
            pathOptions={{
              color: '#F5A623',
              weight: 2,
              opacity: 0.9,
              fillColor: '#F5A623',
              fillOpacity: 0.08,
              dashArray: '8, 4',
            }}
          />
        )}

        {/* ─── Polygon Area Selection ────── */}
        {polygonPoints.length >= 3 && (
          <Polygon
            positions={polygonPoints}
            pathOptions={{
              color: '#06B6D4',
              weight: 2,
              opacity: 0.9,
              fillColor: '#06B6D4',
              fillOpacity: 0.1,
              dashArray: polygonPoints.length < 4 ? '6, 4' : 'none',
            }}
          />
        )}

        {/* ─── Polygon Vertex Markers ────── */}
        {polygonPoints.map((point, i) => (
          <CircleMarker
            key={`poly-${i}`}
            center={[point.lat, point.lng]}
            radius={6}
            pathOptions={{
              color: '#06B6D4',
              fillColor: i === 0 ? '#F5A623' : '#06B6D4',
              fillOpacity: 1,
              weight: 2,
            }}
          >
            <Popup>
              <div style={{ background: '#0D1B2A', color: '#E8F4FD', padding: '8px 12px', borderRadius: '8px', fontSize: '12px' }}>
                <span style={{ color: '#06B6D4', fontWeight: 600 }}>Point {i + 1}</span>
                <br />
                <span style={{ fontFamily: 'JetBrains Mono, monospace', color: '#8BA8BF' }}>
                  {point.lat.toFixed(4)}°N, {point.lng.toFixed(4)}°E
                </span>
              </div>
            </Popup>
          </CircleMarker>
        ))}

        {/* ─── District Choropleth (under the site markers) ────── */}
        {districtEntries && districtGeojson?.features?.map((feature) => {
          const { district, state } = feature.properties;
          const entry = districtEntries.get(district);
          const geometry = feature.geometry;
          if (!geometry || (geometry.type !== 'Polygon' && geometry.type !== 'MultiPolygon')) return null;
          return (
            <Polygon
              key={`${state}-${district}`}
              positions={swapCoords(geometry.coordinates)}
              pathOptions={{
                color: '#0D1B2A',
                weight: 0.8,
                opacity: 0.9,
                // `value` is mean site suitability for the district — already on
                // the 0..1 scale suitabilityToColor() expects, so no rescale.
                // ponytail: if a CUF/percentage ever lands here instead, divide by
                // 100 first; upgrade path = a typed metric + scale enum on the prop.
                fillColor: entry ? suitabilityToColor(entry.value) : NO_DATA_FILL,
                fillOpacity: entry ? 0.55 : 0.3,
              }}
            >
              <Popup className="dark-popup">
                <div style={{ background: '#0D1B2A', color: '#E8F4FD', padding: '8px 12px', borderRadius: '8px', fontSize: '12px', minWidth: '160px' }}>
                  <span style={{ color: '#E8F4FD', fontWeight: 600 }}>{titleCase(district)}</span>
                  <br />
                  <span style={{ color: '#8BA8BF', fontSize: '11px' }}>{state}</span>
                  <br />
                  {entry.metric === 'cuf' ? (
                    // Phase 5.8: measured vs predicted CUF with uncertainty
                    <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '11px', lineHeight: 1.6 }}>
                      <span style={{ color: '#06B6D4' }}>
                        Pred CUF: {entry.cuf.toFixed(4)}
                      </span>
                      <br />
                      <span style={{ color: '#8BA8BF' }}>
                        90% interval: {entry.interval[0].toFixed(4)}–{entry.interval[1].toFixed(4)}
                      </span>
                      <br />
                      <span style={{ color: '#F5A623' }}>
                        {entry.measured != null
                          ? `Measured: ${entry.measured.toFixed(4)}`
                          : 'Measured: no label'}
                      </span>
                      <br />
                      <span style={{ color: '#5A7A94', fontSize: '10px' }}>
                        C0: {entry.c0.toFixed(4)} · Gate 3 {entry.gate3 ? 'pass' : 'fail'}
                      </span>
                    </span>
                  ) : entry ? (
                    <span style={{ fontFamily: 'JetBrains Mono, monospace', color: suitabilityToColor(entry.value) }}>
                      Mean suitability: {formatScore(entry.value)}
                    </span>
                  ) : (
                    <span style={{ color: '#5A7A94', fontSize: '11px' }}>
                      No sites match the current filters
                    </span>
                  )}
                </div>
              </Popup>
            </Polygon>
          );
        })}

        {/* ─── Site Markers ────── */}
        {sites.map(site => (
          <CircleMarker
            key={site.id}
            center={[site.lat, site.lng]}
            radius={getMarkerRadius(site.capacity)}
            pathOptions={{
              color: suitabilityToColor(site.suitability),
              fillColor: suitabilityToColor(site.suitability),
              fillOpacity: 0.7,
              weight: selectedSite?.id === site.id ? 3 : 1.5,
              opacity: selectedSite?.id === site.id ? 1 : 0.8,
            }}
            eventHandlers={{
              click: () => !drawMode && onSiteSelect?.(site.id),
            }}
          >
            <Popup className="dark-popup">
              <div style={{ background: '#0D1B2A', color: '#E8F4FD', padding: '12px 14px', borderRadius: '10px', minWidth: '210px' }}>
                <h3 style={{ color: '#E8F4FD', fontWeight: 600, fontSize: '13px', marginBottom: '4px' }}>{site.name}</h3>
                <p style={{ color: '#8BA8BF', fontSize: '11px', marginBottom: '8px' }}>{site.district}, {site.state}</p>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: '11px' }}>
                  <div>
                    <span style={{ color: '#8BA8BF' }}>Score: </span>
                    <span style={{ color: suitabilityToColor(site.suitability), fontWeight: 700 }}>{formatScore(site.suitability)}</span>
                  </div>
                  <div>
                    <span style={{ color: '#8BA8BF' }}>GHI: </span>
                    <span style={{ color: '#F5A623', fontFamily: 'JetBrains Mono, monospace' }}>{site.ghi}</span>
                  </div>
                  <div>
                    <span style={{ color: '#8BA8BF' }}>Cap: </span>
                    <span style={{ color: '#E8F4FD' }}>{formatCapacity(site.capacity)}</span>
                  </div>
                  <div>
                    <span style={{ color: '#8BA8BF' }}>LCOE: </span>
                    <span style={{ color: '#E8F4FD' }}>₹{site.lcoe}</span>
                  </div>
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      {/* ─── Choropleth geometry missing (honest empty state) ────── */}
      {districts && districtGeojson === null && (
        <div className="absolute bottom-4 right-4 z-[1000] glass-strong rounded-lg px-3 py-2 max-w-[260px]">
          <p className="text-xs text-txt-dim leading-snug">
            District geometry missing — run{' '}
            <span className="font-mono text-txt-secondary">
              .venv/bin/python scripts/build_district_geojson.py
            </span>
          </p>
        </div>
      )}
    </div>
  );
};

export default MapView;
