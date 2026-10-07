import { useState, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import MapView from '../components/map/MapView';
import useMapData from '../hooks/useMapData';
import { suitabilityToColor } from '../utils/colorScale';
import { canonicalDistrict } from '../utils/districts';
import { formatCapacity, formatScore } from '../utils/formatters';
import { INDIAN_STATES } from '../data/constants';

const BBOX_SIZE_KM = 5; // bounding box half-size in km
const KM_TO_DEG_LAT = 1 / 111.32;
const kmToLngDeg = (lat) => 1 / (111.32 * Math.cos((lat * Math.PI) / 180));

const Dashboard = () => {
  const {
    filters, setFilters, filteredSites, selectedSite, setSelectedSiteId, stats
  } = useMapData();

  const [showFilters, setShowFilters] = useState(false);
  const [activePanel, setActivePanel] = useState(null); // 'coords' | 'polygon' | null

  // ─── Coordinate input state ─────────────────────
  const [coordLat, setCoordLat] = useState('');
  const [coordLng, setCoordLng] = useState('');
  const [bboxBounds, setBboxBounds] = useState(null);
  const [bboxInfo, setBboxInfo] = useState(null);

  // ─── Polygon draw state ─────────────────────────
  const [polygonPoints, setPolygonPoints] = useState([]);
  const [drawMode, setDrawMode] = useState(false);

  // ─── Handle coordinate search ───────────────────
  const handleCoordSearch = useCallback(() => {
    const lat = parseFloat(coordLat);
    const lng = parseFloat(coordLng);
    if (isNaN(lat) || isNaN(lng)) return;
    if (lat < 6 || lat > 38 || lng < 68 || lng > 98) return;

    const latOffset = BBOX_SIZE_KM * KM_TO_DEG_LAT;
    const lngOffset = BBOX_SIZE_KM * kmToLngDeg(lat);

    const bounds = [
      [lat - latOffset, lng - lngOffset],
      [lat + latOffset, lng + lngOffset],
    ];

    setBboxBounds(bounds);
    setBboxInfo({ lat, lng, area: (2 * BBOX_SIZE_KM) ** 2 });
    setSelectedSiteId(null);

    // Find nearby sites
    const nearby = filteredSites.filter(s => {
      const dLat = Math.abs(s.lat - lat);
      const dLng = Math.abs(s.lng - lng);
      return dLat < latOffset && dLng < lngOffset;
    });
    if (nearby.length > 0) {
      setBboxInfo(prev => ({ ...prev, nearbySites: nearby.length, bestNearby: nearby.sort((a, b) => b.suitability - a.suitability)[0] }));
    }
  }, [coordLat, coordLng, filteredSites, setSelectedSiteId]);

  const clearBbox = useCallback(() => {
    setBboxBounds(null);
    setBboxInfo(null);
    setCoordLat('');
    setCoordLng('');
  }, []);

  // ─── Handle polygon map click ───────────────────
  const handleMapClick = useCallback((latlng) => {
    if (!drawMode) return;
    setPolygonPoints(prev => {
      if (prev.length >= 4) return prev;
      return [...prev, latlng];
    });
  }, [drawMode]);

  const startDraw = useCallback(() => {
    setDrawMode(true);
    setPolygonPoints([]);
    setActivePanel('polygon');
  }, []);

  const clearPolygon = useCallback(() => {
    setDrawMode(false);
    setPolygonPoints([]);
  }, []);

  const finishDraw = useCallback(() => {
    setDrawMode(false);
  }, []);

  // ─── Polygon area stats ─────────────────────────
  const polygonStats = useMemo(() => {
    if (polygonPoints.length < 3) return null;
    const pts = polygonPoints;

    // Shoelace formula for area in sq degrees → approximate to sq km
    let area = 0;
    for (let i = 0; i < pts.length; i++) {
      const j = (i + 1) % pts.length;
      area += pts[i].lng * pts[j].lat;
      area -= pts[j].lng * pts[i].lat;
    }
    area = Math.abs(area) / 2;
    const avgLat = pts.reduce((s, p) => s + p.lat, 0) / pts.length;
    const areaKm = area * 111.32 * 111.32 * Math.cos((avgLat * Math.PI) / 180);

    // Count sites inside polygon (ray casting)
    const insideSites = filteredSites.filter(site => {
      let inside = false;
      const x = site.lng, y = site.lat;
      for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
        const xi = pts[i].lng, yi = pts[i].lat;
        const xj = pts[j].lng, yj = pts[j].lat;
        if (((yi > y) !== (yj > y)) && (x < ((xj - xi) * (y - yi)) / (yj - yi) + xi)) {
          inside = !inside;
        }
      }
      return inside;
    });

    return {
      areaKm: areaKm.toFixed(1),
      sitesInside: insideSites.length,
      avgScore: insideSites.length
        ? (insideSites.reduce((s, st) => s + st.suitability, 0) / insideSites.length * 100).toFixed(0)
        : '—',
      bestSite: insideSites.sort((a, b) => b.suitability - a.suitability)[0] || null,
    };
  }, [polygonPoints, filteredSites]);

  // ─── Choropleth values: mean suitability per district over filteredSites ───
  // Districts present in the geometry but with no site left after the filters
  // are simply absent here, so MapView renders them neutral (no-data).
  const districtValues = useMemo(() => {
    const byDistrict = new Map();
    filteredSites.forEach((site) => {
      const district = canonicalDistrict(site.district);
      if (!district) return;
      const acc = byDistrict.get(district) || { district, state: site.state, sum: 0, count: 0 };
      acc.sum += site.suitability;
      acc.count += 1;
      byDistrict.set(district, acc);
    });
    return [...byDistrict.values()].map(({ district, state, sum, count }) => ({
      district,
      state,
      value: sum / count,
    }));
  }, [filteredSites]);

  return (
    <div className="min-h-screen pt-20 bg-space-deep">
      {/* ═══════ Quick Stats Bar ═══════ */}
      <div className="border-b border-space-border glass-strong">
        <div className="container-custom py-3 flex items-center gap-5 overflow-x-auto text-base">
          {[
            { dot: 'bg-solar-gold', label: 'Sites', value: stats.totalSites },
            { dot: 'bg-tech-cyan', label: 'Avg Score', value: <span className="text-solar-gold font-mono">{(stats.avgSuitability * 100).toFixed(0)}</span> },
            { dot: 'bg-success', label: 'Total Capacity', value: formatCapacity(stats.totalCapacity) },
            stats.bestSite && { dot: 'bg-warning', label: 'Best', value: <span className="text-success">{stats.bestSite.name}</span> },
            { dot: 'bg-tech-blue', label: 'Avg GHI', value: <span className="font-mono">{stats.avgGHI}</span> },
          ].filter(Boolean).map((item, i) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
              className="flex items-center gap-2 whitespace-nowrap"
            >
              <span className={`w-2.5 h-2.5 rounded-full ${item.dot}`} />
              <span className="text-txt-dim">{item.label}:</span>
              <span className="text-txt-primary font-semibold">{item.value}</span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* ═══════ Main Content ═══════ */}
      <div className="flex h-[calc(100vh-128px)]">
        {/* ─── Map ─── */}
        <div className="flex-1 relative">
          <MapView
            sites={filteredSites}
            districts={districtValues}
            selectedSite={selectedSite}
            onSiteSelect={setSelectedSiteId}
            bboxBounds={bboxBounds}
            polygonPoints={polygonPoints}
            drawMode={drawMode}
            onMapClick={handleMapClick}
          />

          {/* ═══════ Map Toolbar ═══════ */}
          <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-2">
            {/* Row 1: Filter + Tools */}
            <div className="flex gap-2">
              <button
                onClick={() => { setShowFilters(!showFilters); setActivePanel(null); }}
                className={`map-tool-btn ${showFilters ? 'active' : ''}`}
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                </svg>
                Filters
              </button>

              <button
                onClick={() => { setActivePanel(activePanel === 'coords' ? null : 'coords'); setShowFilters(false); }}
                className={`map-tool-btn ${activePanel === 'coords' ? 'active' : ''}`}
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Locate Site
              </button>

              <button
                onClick={() => {
                  if (drawMode) {
                    clearPolygon();
                    setActivePanel(null);
                  } else {
                    startDraw();
                    setShowFilters(false);
                  }
                }}
                className={`map-tool-btn ${activePanel === 'polygon' || drawMode ? 'active' : ''}`}
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zM14 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                </svg>
                {drawMode ? 'Cancel Draw' : 'Select Area'}
              </button>
            </div>

            {/* ═══════ Filter Panel ═══════ */}
            <AnimatePresence>
              {showFilters && (
                <motion.div
                  initial={{ opacity: 0, y: -8, scale: 0.96 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -8, scale: 0.96 }}
                  transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                  className="glass-strong rounded-xl p-4 w-72 space-y-4"
                >
                  <div>
                    <label className="text-xs text-txt-dim mb-1 block font-medium">Search</label>
                    <input
                      type="text"
                      placeholder="Site name, state, district..."
                      value={filters.searchQuery}
                      onChange={(e) => setFilters(f => ({ ...f, searchQuery: e.target.value }))}
                      className="coord-input"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-txt-dim mb-1 block font-medium">State</label>
                    <select
                      value={filters.state}
                      onChange={(e) => setFilters(f => ({ ...f, state: e.target.value }))}
                      className="coord-input"
                    >
                      <option value="">All States</option>
                      {INDIAN_STATES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-txt-dim mb-1 flex justify-between font-medium">
                      <span>Min Suitability</span>
                      <span className="text-solar-gold font-mono">{(filters.minSuitability * 100).toFixed(0)}%</span>
                    </label>
                    <input
                      type="range"
                      min={0} max={1} step={0.05}
                      value={filters.minSuitability}
                      onChange={(e) => setFilters(f => ({ ...f, minSuitability: parseFloat(e.target.value) }))}
                      className="w-full"
                      style={{
                        background: `linear-gradient(to right, #F5A623 ${filters.minSuitability * 100}%, #1E3A52 ${filters.minSuitability * 100}%)`,
                      }}
                    />
                  </div>
                  <button
                    onClick={() => setFilters({ state: '', minGHI: 0, maxGHI: 7, minSuitability: 0, landTypes: [], searchQuery: '' })}
                    className="w-full py-2 text-xs text-txt-dim hover:text-solar-gold border border-space-border rounded-lg transition-colors"
                  >
                    Clear Filters
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            {/* ═══════ Coordinate Input Panel ═══════ */}
            <AnimatePresence>
              {activePanel === 'coords' && (
                <motion.div
                  initial={{ opacity: 0, y: -8, scale: 0.96 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -8, scale: 0.96 }}
                  transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                  className="glass-strong rounded-xl p-4 w-80 space-y-3"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-solar-gold" />
                    <span className="text-xs font-semibold text-txt-primary tracking-wide uppercase">Locate Site by Coordinates</span>
                  </div>
                  <p className="text-[11px] text-txt-dim leading-relaxed">
                    Enter latitude/longitude to place a {BBOX_SIZE_KM * 2}km × {BBOX_SIZE_KM * 2}km bounding box and check for nearby sites.
                  </p>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-[10px] text-txt-dim mb-1 block font-medium uppercase tracking-wider">Latitude</label>
                      <input
                        type="number"
                        step="0.0001"
                        placeholder="e.g. 27.54"
                        value={coordLat}
                        onChange={(e) => setCoordLat(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleCoordSearch()}
                        className="coord-input"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] text-txt-dim mb-1 block font-medium uppercase tracking-wider">Longitude</label>
                      <input
                        type="number"
                        step="0.0001"
                        placeholder="e.g. 71.91"
                        value={coordLng}
                        onChange={(e) => setCoordLng(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleCoordSearch()}
                        className="coord-input"
                      />
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={handleCoordSearch}
                      disabled={!coordLat || !coordLng}
                      className="flex-1 py-2 text-xs font-semibold rounded-lg bg-gradient-to-r from-solar-gold to-solar-orange text-space-deep disabled:opacity-30 disabled:cursor-not-allowed transition-all hover:shadow-glow-gold hover:-translate-y-0.5"
                    >
                      Search Location
                    </button>
                    {bboxBounds && (
                      <button
                        onClick={clearBbox}
                        className="px-3 py-2 text-xs text-txt-dim hover:text-red-400 border border-space-border rounded-lg transition-colors"
                      >
                        Clear
                      </button>
                    )}
                  </div>

                  {/* ─── BBox Results ─── */}
                  <AnimatePresence>
                    {bboxInfo && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="pt-3 border-t border-space-border space-y-2">
                          <div className="flex items-center gap-2">
                            <div className="status-dot online" />
                            <span className="text-xs text-txt-primary font-medium">Bounding Box Active</span>
                          </div>
                          <div className="grid grid-cols-2 gap-2 text-[11px]">
                            <div className="flex justify-between">
                              <span className="text-txt-dim">Center:</span>
                              <span className="text-txt-primary font-mono">{bboxInfo.lat.toFixed(4)}°N</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-txt-dim">Long:</span>
                              <span className="text-txt-primary font-mono">{bboxInfo.lng.toFixed(4)}°E</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-txt-dim">Area:</span>
                              <span className="text-solar-gold font-mono">{bboxInfo.area} km²</span>
                            </div>
                            {bboxInfo.nearbySites && (
                              <div className="flex justify-between">
                                <span className="text-txt-dim">Sites:</span>
                                <span className="text-success font-semibold">{bboxInfo.nearbySites} found</span>
                              </div>
                            )}
                          </div>
                          {bboxInfo.bestNearby && (
                            <div className="glass rounded-lg p-2 flex items-center justify-between">
                              <span className="text-xs text-txt-dim">Best nearby:</span>
                              <span className="text-xs text-success font-semibold">{bboxInfo.bestNearby.name}</span>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              )}
            </AnimatePresence>

            {/* ═══════ Polygon Draw Panel ═══════ */}
            <AnimatePresence>
              {activePanel === 'polygon' && (
                <motion.div
                  initial={{ opacity: 0, y: -8, scale: 0.96 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -8, scale: 0.96 }}
                  transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                  className="glass-strong rounded-xl p-4 w-80 space-y-3"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-tech-cyan" />
                    <span className="text-xs font-semibold text-txt-primary tracking-wide uppercase">Area Selection Tool</span>
                  </div>

                  {drawMode ? (
                    <>
                      <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-tech-cyan/8 border border-tech-cyan/20">
                        <div className="status-dot warning" />
                        <span className="text-xs text-tech-cyan font-medium">
                          Click on the map to place points ({polygonPoints.length}/4)
                        </span>
                      </div>

                      {/* Point list */}
                      <div className="space-y-1">
                        {[0, 1, 2, 3].map(i => (
                          <div key={i} className={`flex items-center gap-2 text-[11px] px-2 py-1.5 rounded-lg ${
                            polygonPoints[i] ? 'bg-space-surface' : 'opacity-30'
                          }`}>
                            <span className={`w-4 h-4 rounded-full text-[9px] flex items-center justify-center font-bold ${
                              polygonPoints[i]
                                ? 'bg-tech-cyan/20 text-tech-cyan border border-tech-cyan/30'
                                : 'bg-space-border text-txt-dim'
                            }`}>
                              {i + 1}
                            </span>
                            <span className="font-mono text-txt-dim flex-1">
                              {polygonPoints[i]
                                ? `${polygonPoints[i].lat.toFixed(4)}°N, ${polygonPoints[i].lng.toFixed(4)}°E`
                                : 'Click map to set...'}
                            </span>
                          </div>
                        ))}
                      </div>

                      <div className="flex gap-2">
                        {polygonPoints.length >= 3 && (
                          <button
                            onClick={finishDraw}
                            className="flex-1 py-2 text-xs font-semibold rounded-lg bg-gradient-to-r from-tech-cyan to-tech-blue text-space-deep transition-all hover:-translate-y-0.5"
                          >
                            Finish ({polygonPoints.length} points)
                          </button>
                        )}
                        <button
                          onClick={clearPolygon}
                          className="px-3 py-2 text-xs text-txt-dim hover:text-red-400 border border-space-border rounded-lg transition-colors"
                        >
                          Reset
                        </button>
                      </div>
                    </>
                  ) : polygonPoints.length >= 3 ? (
                    <>
                      <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-success/8 border border-success/20">
                        <div className="status-dot online" />
                        <span className="text-xs text-success font-medium">Area selected</span>
                      </div>

                      {polygonStats && (
                        <div className="space-y-2">
                          <div className="grid grid-cols-2 gap-2 text-[11px]">
                            <div className="glass rounded-lg p-2 text-center">
                              <p className="text-txt-dim mb-0.5">Area</p>
                              <p className="text-solar-gold font-bold font-mono">{polygonStats.areaKm} km²</p>
                            </div>
                            <div className="glass rounded-lg p-2 text-center">
                              <p className="text-txt-dim mb-0.5">Sites Inside</p>
                              <p className="text-tech-cyan font-bold">{polygonStats.sitesInside}</p>
                            </div>
                            <div className="glass rounded-lg p-2 text-center">
                              <p className="text-txt-dim mb-0.5">Avg Score</p>
                              <p className="text-success font-bold">{polygonStats.avgScore}</p>
                            </div>
                            {polygonStats.bestSite && (
                              <div className="glass rounded-lg p-2 text-center">
                                <p className="text-txt-dim mb-0.5">Best Site</p>
                                <p className="text-success font-bold text-[10px] truncate">{polygonStats.bestSite.name}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      <div className="flex gap-2">
                        <button
                          onClick={startDraw}
                          className="flex-1 py-2 text-xs font-semibold rounded-lg border border-tech-cyan/30 text-tech-cyan hover:bg-tech-cyan/10 transition-colors"
                        >
                          Redraw Area
                        </button>
                        <button
                          onClick={() => { clearPolygon(); setActivePanel(null); }}
                          className="px-3 py-2 text-xs text-txt-dim hover:text-red-400 border border-space-border rounded-lg transition-colors"
                        >
                          Clear
                        </button>
                      </div>
                    </>
                  ) : (
                    <p className="text-xs text-txt-dim">
                      Define an analysis boundary by clicking 4 points on the map. The enclosed region will be analyzed for solar potential.
                    </p>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* ═══════ Legend ═══════ */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="absolute bottom-4 left-4 z-[1000] glass-strong rounded-xl px-4 py-3"
          >
            <p className="text-xs text-txt-dim mb-2 font-semibold uppercase tracking-wider">Suitability Score</p>
            <p className="text-xs text-txt-dim/80 -mt-1 mb-2">Mock-site scores — not model output</p>
            <div className="flex items-center gap-3 text-sm">
              {[
                { label: 'Excellent', color: '#10B981' },
                { label: 'Good', color: '#F5A623' },
                { label: 'Moderate', color: '#D97706' },
                { label: 'Poor', color: '#EF4444' },
              ].map(item => (
                <div key={item.label} className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color, boxShadow: `0 0 8px ${item.color}50` }} />
                  <span className="text-txt-dim">{item.label}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* ═══════ Side Panel — Site List ═══════ */}
        <motion.div
          initial={{ x: 40, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="w-80 xl:w-[420px] border-l border-space-border glass-strong overflow-y-auto hidden md:block"
        >
          <div className="p-4 border-b border-space-border flex items-center justify-between">
            <h2 className="font-display font-semibold text-txt-primary text-xl">
              Solar Sites
              <span className="text-txt-dim text-base font-normal ml-2">({filteredSites.length})</span>
            </h2>
            {/* ponytail: this panel and the map are fed by useMapData → mockSites,
                never by the API, so the label must not follow isLive. Ceiling =
                says "Demo data" even after the hook is wired to /v1/sites.
                Upgrade path = have useMapData expose its source and switch here. */}
            <div className="flex items-center gap-1.5">
              <div className="status-dot warning" />
              <span className="text-xs text-txt-dim">Demo data</span>
            </div>
          </div>

          <div className="divide-y divide-space-border/30">
            {[...filteredSites]
              .sort((a, b) => b.suitability - a.suitability)
              .map((site, i) => (
                <motion.div
                  key={site.id}
                  initial={{ opacity: 0, x: 16 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: Math.min(i * 0.025, 0.4), type: 'spring', damping: 25, stiffness: 300 }}
                  onClick={() => setSelectedSiteId(site.id)}
                  className={`p-3.5 cursor-pointer transition-all duration-300 hover:bg-space-light/30 ${
                    selectedSite?.id === site.id
                      ? 'bg-space-light/40 border-l-2 border-solar-gold'
                      : 'border-l-2 border-transparent'
                  }`}
                >
                  <div className="flex items-start justify-between mb-1">
                    <h3 className="text-base font-semibold text-txt-primary truncate flex-1">{site.name}</h3>
                    <span
                      className="text-sm font-bold font-mono ml-2 px-2 py-0.5 rounded-md"
                      style={{ color: suitabilityToColor(site.suitability), background: `${suitabilityToColor(site.suitability)}12` }}
                    >
                      {formatScore(site.suitability)}
                    </span>
                  </div>
                  <p className="text-sm text-txt-dim mb-2">{site.district}, {site.state}</p>
                  <div className="flex gap-3 text-sm">
                    <span className="text-txt-dim">GHI: <span className="text-solar-gold font-mono">{site.ghi}</span></span>
                    <span className="text-txt-dim">Cap: <span className="text-txt-primary">{formatCapacity(site.capacity)}</span></span>
                    <span className="text-txt-dim">LCOE: <span className="text-txt-primary">₹{site.lcoe}</span></span>
                  </div>

                  <AnimatePresence>
                    {selectedSite?.id === site.id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <Link
                          to={`/site/${site.id}`}
                          className="mt-3 block text-center text-sm py-2.5 rounded-lg border border-solar-gold/30 text-solar-gold hover:bg-solar-gold/10 transition-all hover:-translate-y-0.5 font-medium"
                        >
                          View Detailed Analysis →
                        </Link>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
