import { useState, useCallback, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Rectangle, Polygon, useMap, useMapEvents } from 'react-leaflet';
import { MAP_CONFIG } from '../../data/constants';
import { suitabilityToColor, getMarkerRadius } from '../../utils/colorScale';
import { formatScore, formatCapacity } from '../../utils/formatters';
import 'leaflet/dist/leaflet.css';

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
const MapView = ({
  sites = [],
  selectedSite,
  onSiteSelect,
  bboxBounds,
  polygonPoints = [],
  drawMode = false,
  onMapClick,
  className = '',
}) => {
  return (
    <div className={`w-full h-full rounded-xl overflow-hidden border border-space-border ${className}`}>
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
    </div>
  );
};

export default MapView;
