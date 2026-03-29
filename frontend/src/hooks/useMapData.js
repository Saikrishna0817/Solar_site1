import { useState, useMemo } from 'react';
import { enrichedSites } from '../data/mockSites';

export const useMapData = () => {
  const [filters, setFilters] = useState({
    state: '',
    minGHI: 0,
    maxGHI: 7,
    minSuitability: 0,
    landTypes: [],
    searchQuery: '',
  });

  const [selectedSiteId, setSelectedSiteId] = useState(null);
  const [comparedSiteIds, setComparedSiteIds] = useState([]);

  const filteredSites = useMemo(() => {
    return enrichedSites.filter(site => {
      if (filters.state && site.state !== filters.state) return false;
      if (site.ghi < filters.minGHI || site.ghi > filters.maxGHI) return false;
      if (site.suitability < filters.minSuitability) return false;
      if (filters.landTypes.length > 0 && !filters.landTypes.includes(site.landType)) return false;
      if (filters.searchQuery) {
        const q = filters.searchQuery.toLowerCase();
        return site.name.toLowerCase().includes(q) ||
               site.state.toLowerCase().includes(q) ||
               site.district.toLowerCase().includes(q);
      }
      return true;
    });
  }, [filters]);

  const selectedSite = useMemo(
    () => enrichedSites.find(s => s.id === selectedSiteId) || null,
    [selectedSiteId]
  );

  const comparedSites = useMemo(
    () => enrichedSites.filter(s => comparedSiteIds.includes(s.id)),
    [comparedSiteIds]
  );

  const stats = useMemo(() => ({
    totalSites: filteredSites.length,
    avgSuitability: filteredSites.length
      ? (filteredSites.reduce((s, site) => s + site.suitability, 0) / filteredSites.length).toFixed(2)
      : 0,
    totalCapacity: filteredSites.reduce((s, site) => s + site.capacity, 0),
    bestSite: filteredSites.length
      ? filteredSites.reduce((best, site) => site.suitability > best.suitability ? site : best, filteredSites[0])
      : null,
    avgGHI: filteredSites.length
      ? (filteredSites.reduce((s, site) => s + site.ghi, 0) / filteredSites.length).toFixed(2)
      : 0,
  }), [filteredSites]);

  const toggleCompare = (siteId) => {
    setComparedSiteIds(prev =>
      prev.includes(siteId)
        ? prev.filter(id => id !== siteId)
        : prev.length < 5 ? [...prev, siteId] : prev
    );
  };

  return {
    filters,
    setFilters,
    filteredSites,
    selectedSite,
    selectedSiteId,
    setSelectedSiteId,
    comparedSites,
    comparedSiteIds,
    toggleCompare,
    stats,
  };
};

export default useMapData;
