# 🧠 SolarSite-India — Complete Project Memory

> **Last Updated**: 2026-03-29  
> **Purpose**: This file captures EVERYTHING about the SolarSite-India project — architecture, design decisions, progress history, file structure, styling system, and outstanding work. Read this file to fully resume context on this project.

---

## 📋 PROJECT OVERVIEW

**SolarSite-India** is an AI-powered solar energy site selection platform for India. It uses a machine learning ensemble model (Random Forest + XGBoost + Gradient Boosting) trained on 127 operational solar plants to predict suitability scores for 30,000+ potential solar deployment locations across India.

### Core Objective
Support India's **500 GW renewable energy target by 2030** by replacing the traditional 6-12 month, ₹50-100 lakh manual site assessment process with an instant, data-driven, AI-powered site selection tool.

### Key Research Metrics
| Metric | Value |
|--------|-------|
| R² Score | 0.88 |
| MAPE | 11.5% |
| RMSE | 0.065 |
| MAE | 0.052 |
| Features Used | 42 (across 8 categories) |
| Training Data | 127 operational solar plants |
| Sites Screened | 30,000+ |
| States Covered | 28 |
| Grid Resolution | 5 km × 5 km |

### ML Ensemble Weights
- **XGBoost**: 50% (lr=0.1, max_depth=8, n_est=300) — Best individual performer
- **Random Forest**: 30% (n_estimators=500, max_depth=12) — Robust to outliers
- **Gradient Boosting**: 20% (lr=0.05, n_est=400) — Fine-grained bias correction

---

## 📂 PROJECT FILE STRUCTURE

```
Solar_site/
├── PROJECT_MEMORY.md                          ← THIS FILE
├── SolarSite-India_Master_Documentation.md    ← Full research documentation
├── SolarSite_Dataset_Methodology.docx         ← Dataset creation methodology
├── SolarSite_District_Dataset_v2.xlsx         ← Training dataset (Excel)
├── SolarSite_India_Complete_Documentation_v3.docx
├── SolarSite_India_Project_Documentation.docx
├── SolarSite_Integrations_Features_Frontend.docx
├── solarsite-india-blueprint.html             ← Early HTML prototype/blueprint
│
└── frontend/                                  ← MAIN REACT APPLICATION
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js                     ← Custom design system tokens
    ├── postcss.config.js
    ├── eslint.config.js
    ├── index.html                             ← Entry HTML with SEO meta tags
    ├── dist/                                  ← Production build output
    ├── public/                                ← Static assets
    │
    └── src/
        ├── main.jsx                           ← React entry point
        ├── App.jsx                            ← Router + AnimatePresence layout
        ├── App.css                            ← Minimal (legacy Vite CSS cleared)
        ├── index.css                          ← 🎨 MAIN DESIGN SYSTEM (500+ lines)
        │
        ├── pages/
        │   ├── Landing.jsx                    ← Hero + Problem/Solution + Pipeline + Features + Calculator + CTA
        │   ├── Dashboard.jsx                  ← Interactive map + filters + coordinate search + polygon draw + site list
        │   ├── SiteAnalysis.jsx               ← Individual site deep-dive (gauge, radar, charts, SHAP, economics)
        │   ├── Methodology.jsx                ← ML pipeline timeline + ensemble model + 42-feature explorer
        │   ├── Results.jsx                    ← Metrics + scatter plot + SHAP waterfall + state chart + top sites table + case studies
        │   └── About.jsx                      ← Mission + research highlights + tech stack + paper info
        │
        ├── components/
        │   ├── layout/
        │   │   ├── Navbar.jsx                 ← Sticky glassmorphic nav with animated indicator + mobile menu
        │   │   └── Footer.jsx                 ← 4-column footer with link-underline animations
        │   │
        │   ├── ui/
        │   │   ├── GlassCard.jsx              ← Reusable glass-morphism card (hover lift, shimmer sweep, corner glow)
        │   │   ├── SectionTitle.jsx            ← Animated gradient heading + subtitle + accent line
        │   │   ├── GradientButton.jsx          ← Solar/outline/tech button variants with Link support
        │   │   └── AnimatedCounter.jsx         ← Number counter animation on scroll into view
        │   │
        │   ├── map/
        │   │   └── MapView.jsx                ← Leaflet map with dark CartoDB tiles, site markers, bbox overlay, polygon drawing
        │   │
        │   ├── charts/
        │   │   ├── ScatterPlot.jsx            ← Predicted vs Actual scatter (Recharts)
        │   │   ├── SHAPWaterfall.jsx           ← Horizontal SHAP feature importance bars
        │   │   ├── SuitabilityGauge.jsx        ← Circular SVG gauge (0-100 score)
        │   │   ├── FeatureRadar.jsx            ← Radar chart for site feature scores
        │   │   └── GenerationChart.jsx         ← Monthly generation + 25-year projection (area charts)
        │   │
        │   ├── three/
        │   │   ├── SolarGlobe.jsx             ← 3D rotating Earth globe (React Three Fiber + Drei)
        │   │   └── ParticleField.jsx           ← Floating particle background for hero
        │   │
        │   └── calculator/
        │       └── SuitabilityCalculator.jsx   ← Interactive slider-based suitability score estimator
        │
        ├── hooks/
        │   ├── useMapData.js                  ← Central state management for map filters, site selection, stats
        │   ├── useAnimatedCounter.js           ← requestAnimationFrame counter hook
        │   └── useInView.js                    ← IntersectionObserver hook for scroll triggers
        │
        ├── data/
        │   ├── constants.js                   ← Colors, feature categories, map config, nav links, model weights
        │   ├── mockSites.js                   ← 30+ enriched mock solar sites with full feature data (~22KB)
        │   ├── mockFeatures.js                ← 42 feature definitions with descriptions, ranges, units (~9KB)
        │   └── stateData.js                   ← State-wise solar potential data for bar charts (~3.6KB)
        │
        ├── services/
        │   ├── api.js                         ← Dual mock/live API service (toggle USE_MOCK flag)
        │   └── calculations.js                ← LCOE, NPV, payback, generation calculations
        │
        └── utils/
            ├── colorScale.js                  ← Suitability-to-color mapping + confidence colors
            └── formatters.js                  ← Number/capacity/score/generation formatters
```

---

## 🎨 DESIGN SYSTEM

### Color Palette
```
Solar Gold:    #F5A623  (primary accent — solar energy)
Solar Orange:  #E8590C  (gradient partner)
Solar Amber:   #D97706  (moderate score)
Tech Cyan:     #06B6D4  (secondary accent — technology)
Tech Teal:     #14B8A6
Tech Blue:     #3B82F6

Space Deep:    #0A0E1A  (body background — near-black blue)
Space Panel:   #0D1B2A  (glass card backgrounds)
Space Surface: #111B2E  (elevated surfaces)
Space Border:  #1E3A52  (border/divider color)
Space Light:   #1B2D45  (hover state backgrounds)

Text Primary:   #E8F4FD  (headings, bright text)
Text Secondary: #8BA8BF  (body text, descriptions)
Text Dim:       #5A7A94  (labels, muted text)

Success:  #10B981  (excellent scores, online status)
Warning:  #8B5CF6  (purple — used for warning/accents)
Error:    #EF4444  (poor scores)
```

### Typography
- **Display**: `Outfit` (headings, titles, big numbers)
- **Body**: `Inter` (all text, labels, descriptions)
- **Code**: `JetBrains Mono` (coordinates, scores, data values)
- **Base font-size**: `16.5px` (slightly above default for readability)

### Glass Morphism System
- `.glass` — Light glass: `rgba(13, 27, 42, 0.6)` + `blur(20px)`
- `.glass-strong` — Stronger: `rgba(13, 27, 42, 0.85)` + `blur(30px)`
- `.glass-card` — Full-featured: glass + border-radius(14px) + hover lift + shimmer sweep + gradient border

### Key UI Patterns
- **Card hover**: `translateY(-4px) scale(1.005)` with gold glow border
- **Shimmer sweep**: On hover, a subtle light sweep passes across the card
- **Corner accent glow**: Radial gradient glow in top-right corner on hover
- **Top edge highlight**: 1px gradient line across card top
- **Animated border**: Rotating conic gradient on `.card-shimmer` hover
- **Link underline**: `scaleX(0) → scaleX(1)` gradient underline animation

### Spacing Philosophy (Post-Polish)
- **Container**: `max-width: 1520px`, padding: `16px` (mobile) → `20px` (tablet) → `24px` (desktop)
- **Section padding**: `80px 0` (was 100px — tightened)
- **Card gaps**: `gap-3` to `gap-4` (was gap-6 — tightened)
- **GlassCard internal padding**: `p-5` (was p-6 — tightened)
- **Section title bottom margin**: `mb-10/mb-12` (was mb-12/mb-16)

### Animation System
| Animation | Description |
|-----------|-------------|
| `shimmer-text` | Background-position gradient shift for text shimmer |
| `border-rotate` | 360° rotation for conic gradient borders |
| `glow-pulse` | Box-shadow breathing for glow dots |
| `status-pulse` | Opacity + scale pulse for status indicators |
| `float-gentle` | Subtle Y + rotation float |
| `marker-pulse` | Scale + fade-out for map markers |
| `float-up` | `translateY(30px) scale(0.96)` → normal |
| `shimmer-sweep` | `translateX(-100%) → translateX(200%)` light sweep |
| `card-breathe` | Subtle box-shadow breathing (4s loop) |
| `text-glow-pulse` | Text-shadow breathing for headings |
| `entrance-scale` | `scale(0.92) → scale(1)` entrance |
| `fade-in-blur` | `blur(8px) → blur(0)` deblur |
| `gradient-pan` | Background-position pan for gradient animation |
| `underline-expand` | `scaleX(0) → scaleX(1)` for underlines |

---

## 🛠️ TECHNOLOGY STACK

### Frontend (Current — React + Vite)
| Package | Version | Purpose |
|---------|---------|---------|
| React | 18.3.1 | UI framework |
| Vite | 5.4.10 | Build tool / dev server |
| Tailwind CSS | 3.4.19 | Utility-first styling |
| Framer Motion | 12.38.0 | Animations + page transitions |
| React Router DOM | 6.30.3 | Client-side routing |
| Recharts | 3.8.1 | Data visualization charts |
| Leaflet | 1.9.4 | Interactive maps |
| React Leaflet | 4.2.1 | React bindings for Leaflet |
| Three.js | 0.160.0 | 3D globe rendering |
| React Three Fiber | 8.18.0 | React renderer for Three.js |
| @react-three/drei | 9.122.0 | Three.js helpers/primitives |

### Backend (Planned — FastAPI)
| Component | Status |
|-----------|--------|
| FastAPI server | Planned / partially built in earlier conversations |
| scikit-learn models | Trained (RF, XGBoost, GBM) |
| SHAP explainability | Implemented in Python |
| Pandas/NumPy pipeline | Data processing ready |
| API endpoints | Defined in `services/api.js` (mock mode currently ON) |

### API Endpoints (Designed)
```
GET  /api/utility/sites?state=&minSuitability=    → List sites with filters
GET  /api/utility/site/:id                         → Single site details
GET  /api/states                                   → State-wise data
POST /api/utility/analyze { lat, lng }             → Analyze arbitrary coordinates
```

### Data Sources
- NASA POWER — Solar irradiance (GHI, DNI)
- SRTM DEM — Terrain elevation, slope, aspect
- ISRO Bhuvan — Land use / land cover
- CEA / PGCIL — Grid infrastructure data
- IMD — Climate and weather data
- Census / SEDAC — Socioeconomic indicators

---

## 🗺️ KEY FEATURES IMPLEMENTED

### 1. Landing Page (`/`)
- Full-screen hero with 3D rotating globe (React Three Fiber)
- Particle field background animation
- Animated stat counters (500 GW, 30K+ sites, 88% accuracy, 42 features)
- Before/After comparison cards (animated arrows)
- 5-step ML pipeline visualization
- 6 platform feature cards with hover emoji bounce
- Interactive suitability calculator (6 sliders → score gauge)
- CTA section with floating decorative orbs

### 2. Dashboard (`/dashboard`)
- Full-height split layout: Map (left) + Site List (right)
- **Leaflet map** with dark CartoDB tiles and colored site markers
- **Quick stats bar** at top (sites, avg score, capacity, best site, avg GHI)
- **Filter panel**: Search, state dropdown, suitability slider
- **Coordinate search**: Enter lat/lng → 10km×10km bounding box + nearby site detection
- **Polygon area selection**: Click 4 points → Shoelace area calculation + ray-casting site count
- **Suitability legend** with color-coded dots
- **Site list panel**: Sorted by score, shows GHI/capacity/LCOE, expandable "View Analysis" link

### 3. Site Analysis (`/analyze?id=X`)
- Breadcrumb navigation back to Dashboard
- **Suitability gauge** (circular SVG, 0-100)
- Site header with name, location, coordinates, suitability badge
- 4 quick metrics: GHI, Capacity, Land Type, Confidence
- **Feature radar chart** (6-axis: Solar, Temperature, Terrain, Road, Grid, Land)
- **Monthly generation profile** (area chart, 12 months)
- **25-year projection chart** (area chart with degradation)
- **SHAP waterfall** (per-site feature contributions)
- **Economic analysis cards**: LCOE, NPV, Payback, Annual Generation
- **Site parameters table**: 9 parameters in a 4-column grid

### 4. Methodology (`/methodology`)
- **Timeline visualization**: 4-stage pipeline with alternating left/right layout
  - Stage 1: Data Acquisition (6 data sources)
  - Stage 2: Feature Engineering (42 features, normalization)
  - Stage 3: Model Training (RF, XGBoost, GBM with hyperparameters)
  - Stage 4: Ensemble & Scoring (weighted average, SHAP, economics)
- **Ensemble model cards**: 3 models with weights, params, strengths
- **42-Feature explorer**: Category tabs + search + feature cards showing name, importance, range, unit

### 5. Results (`/results`)
- **4 metric cards**: R², MAPE, RMSE, MAE (animated counters)
- **Predicted vs Actual scatter plot**
- **Global SHAP waterfall** (top 10 features)
- **State bar chart**: Top 12 states by utility-scale potential (GW)
- **Top 20 sites table**: Sortable by suitability/GHI/capacity/LCOE
- **3 case studies**: Bhadla Solar Park validation, Mahbubnagar discovery, 500 GW target assessment (expandable)

### 6. About (`/about`)
- Mission statement (why traditional methods fail → AI solution)
- 8 research highlight cards
- 4-column tech stack grid (Frontend, Backend, Data Sources, ML Models)
- Research paper info with key contributions
- Download paper / explore CTA buttons

---

## 📜 CONVERSATION HISTORY & PROGRESS

### Conversation 1 — "Designing SolarSite Frontend Interface" (2026-03-28)
**Goal**: Design and implement a high-end React frontend for the SolarSite-India ML project.  
**What happened**:
- Discussed the overall vision: publication-ready dashboard with 3D visualizations
- Established the need for a modular, scalable architecture
- Decided on React + Vite + Tailwind + Framer Motion stack
- Initial design concept was outlined

### Conversation 2 — "Developing SolarSite Frontend Dashboard" (2026-03-28)
**Goal**: Build out the full frontend with geospatial features and premium visual polish.  
**What was built**:
- **Complete 6-page application** from scratch (Landing, Dashboard, SiteAnalysis, Methodology, Results, About)
- **3D SolarGlobe** with React Three Fiber
- **Particle field** background for the hero section
- **Interactive Leaflet map** with dark tiles and site markers
- **Coordinate-based bounding box search** (enter lat/lng → 10km×10km BBOX)
- **4-point polygon area selection** (click on map → area calculation + site detection)
- **42-feature explorer** with category filtering and search
- **Suitability calculator** with real-time score output
- **Full glassmorphic design system** (glass, glass-strong, glass-card)
- **Mock data layer** with 30+ enriched sites + state data + feature definitions
- **API service** with mock/live toggle for future FastAPI integration
- All charts: scatter plot, SHAP waterfall, suitability gauge, feature radar, generation profiles
- Animated page transitions with Framer Motion
- Responsive mobile menu in Navbar

### Conversation 3 — "Current Conversation" (2026-03-29)
**Goal**: Further polish the UI with:
1. ✅ Increased font sizes (everything was too small)
2. ✅ Decreased padding/gaps between cards (too much whitespace between boxes)
3. ✅ Decreased side spacing (too much blank space on the edges)
4. ✅ More animations and micro-interactions

**Specific changes made**:
- **Base HTML font-size**: 16px → 16.5px
- **Hero heading**: text-4xl/5xl/6xl → text-5xl/6xl/7xl
- **All body text**: bumped up one size category across every page
- **Container max-width**: 1400px → 1520px
- **Container side padding**: responsive (16/20/24px instead of fixed 24px)
- **Removed App.css** legacy Vite constraints (max-width: 1280px, padding: 2rem)
- **Card gaps**: gap-6 → gap-4 everywhere
- **GlassCard padding**: p-6 → p-5
- **Section padding**: 100px → 80px
- **Section title margins**: reduced by 2-4 units
- **Glass card border-radius**: 16px → 14px
- **Card hover**: enhanced to translateY(-4px) scale(1.005) with stronger glow
- **New CSS animations**: float-up, shimmer-sweep, card-breathe, text-glow-pulse, entrance-scale, fade-in-blur, gradient-pan, underline-expand
- **Shimmer sweep on glass cards**: Light passes across card on hover
- **Spring-physics** entrance animations on icons, numbers, pipeline steps
- **Animated arrow** in before/after cards
- **Emoji bounce** on hover for feature icons
- **Step number spin** (360° rotate) for pipeline
- **Floating decorative orbs** in CTA section
- **Link underline animation** in footer
- **Dashboard side panel**: widened to 420px, larger text
- **Navbar**: larger logo (text-xl → text-2xl), nav text (text-sm → text-base)
- **Footer**: all text bumped up, link-underline class added to nav links

---

## ⚙️ HOW TO RUN

```bash
# Navigate to frontend
cd Solar_site/frontend

# Install dependencies (if not already done)
npm install

# Development server (hot reload)
npm run dev
# → Opens at http://localhost:5173/

# Production build
npm run build
# → Output to dist/

# Preview production build
npm run preview
```

### Environment Variables
```
VITE_API_URL=http://localhost:8000/api    # FastAPI backend URL (when ready)
```

### Mock vs Live Mode
In `src/services/api.js`:
```js
const USE_MOCK = true;   // ← Toggle to false when FastAPI backend is live
```

---

## 🔮 OUTSTANDING / FUTURE WORK

### High Priority
- [ ] **Connect to FastAPI backend**: Set `USE_MOCK = false` and ensure `/api` endpoints match
- [ ] **Real site data**: Replace mock sites with actual ML model predictions from the dataset
- [ ] **SHAP integration**: Pipe real SHAP values from Python into the frontend
- [ ] **Authentication** (if needed for deployment)

### Medium Priority
- [ ] **Site comparison mode**: Compare up to 5 sites side-by-side (hook already scaffolded in `useMapData`)
- [ ] **Export functionality**: PDF reports, CSV downloads for site data
- [ ] **Rooftop analysis page**: 300M buildings assessment (mentioned in feature cards)
- [ ] **Advanced map layers**: Heatmap overlay, satellite imagery toggle
- [ ] **Real-time data**: Connect to NASA POWER API for live GHI data

### Low Priority / Nice to Have
- [ ] **Dark/light mode toggle**
- [ ] **User preferences persistence** (localStorage)
- [ ] **Loading skeletons** for charts and data sections
- [ ] **Error boundaries** for graceful failure handling
- [ ] **Performance optimization**: Code-split large chunks (Three.js is 800KB gzipped)
- [ ] **PWA support**: Service worker for offline capability
- [ ] **Internationalization**: Hindi / regional language support

---

## 🧩 IMPORTANT DESIGN DECISIONS & NOTES

1. **Why Tailwind CSS 3**: The project uses Tailwind via PostCSS. It's imported with `@tailwind` directives in `index.css`. Custom design tokens are in `tailwind.config.js` under `theme.extend`.

2. **Why mock data**: The frontend was built before the FastAPI backend was fully ready. The `api.js` service layer abstracts this — switching to live mode requires zero frontend code changes, just flip `USE_MOCK`.

3. **Leaflet over Google Maps**: Chose Leaflet + CartoDB dark tiles for the space-themed dark UI. No API key required. The map component handles bounding boxes, polygon drawing, and marker click events.

4. **Three.js lazy loading**: `SolarGlobe` and `ParticleField` are loaded with `React.lazy()` + `Suspense` to avoid blocking the initial page render (they're heavy — 800KB+ chunk).

5. **Framer Motion for everything**: Page transitions via `AnimatePresence`, card entrances via `whileInView`, hover interactions via `whileHover`, spring physics for staggered animations.

6. **Card-shimmer pseudo-element conflict**: The `.glass-card::before` handles the gradient border, while `.glass-card::after` handles the shimmer sweep. The `.card-shimmer::after` handles the rotating conic gradient. Be careful editing these — they layer on top of each other.

7. **Font sizing strategy**: After polish, we use the "one size up" principle — where body text is `text-base` (not `text-sm`), labels are `text-sm` (not `text-xs`), and headings use the display scale (`text-xl` to `text-5xl`).

8. **Container is wider than standard**: At 1520px max-width (typical is 1280px), the layout utilizes more horizontal space. This is intentional per user request to reduce blank side areas.

9. **Dashboard is full-height**: Uses `h-[calc(100vh-128px)]` to fill the viewport below the navbar + stats bar. The map fills `flex-1` and the side panel is fixed-width.

10. **Polygon area tools**: Uses Shoelace formula for area calculation and ray-casting algorithm for point-in-polygon site detection. Supports 3-4 points.

---

## 📊 DATA ARCHITECTURE (Mock Data)

### `mockSites.js` — enrichedSites[] (30+ sites)
Each site object contains:
```js
{
  id, name, state, district, lat, lng,
  suitability,     // 0-1 composite score
  ghi,             // kWh/m²/day (3.5-6.0)
  dni,             // kWh/m²/day
  capacity,        // MW
  elevation,       // meters
  slope,           // degrees
  landType,        // "Barren", "Desert", "Wasteland", etc.
  gridDistance,     // km to nearest grid
  roadDistance,     // km to nearest road
  temperature,     // °C annual avg
  humidity,        // % annual avg
  windSpeed,       // m/s
  rainfall,        // mm/year
  lcoe,            // ₹/kWh
  npv,             // ₹ Cr (25-year NPV)
  paybackYears,    // years
  annualGeneration, // MWh/year
  confidence,      // 0-1 model confidence
  featureScores: { solar, temperature, terrain, road, grid, land },
  monthlyGeneration: [{ month, value }],    // 12 items
  yearlyProjection: [{ year, value }],      // 25 items
  shapValues: [{ feature, value }],         // 8-10 items
}
```

### `mockFeatures.js` — featureDefinitions[] (42 features)
Each feature:
```js
{
  id, name, fullName, category, description,
  range, unit, importance, // "Critical" | "High" | "Medium" | "Low"
}
```

### `stateData.js` — stateData[] (28 states)
```js
{
  state, potentialGW, installedGW, avgGHI,
  suitableSites, topDistrict, color
}
```

### `constants.js` — Configuration
- `SUITABILITY_COLORS` — Score-to-color mapping
- `FEATURE_CATEGORIES` — 8 categories with icons, colors, feature keys
- `CHART_COLORS` — Recharts color tokens
- `MAP_CONFIG` — Leaflet center, zoom, tile URLs
- `INDIAN_STATES` — 28 states array
- `LAND_TYPES` — 8 land type strings
- `KEY_METRICS` — Global project metrics
- `MODEL_WEIGHTS` — Ensemble model weights
- `NAV_LINKS` — Navigation paths

---

## 🔧 EARLIER PROJECT HISTORY (Before Frontend)

### Streamlit Frontend (Deprecated)
- The project originally had a **Streamlit** frontend (Python-based)
- It was decided to replace it with React for a more professional, interactive UI
- The old Streamlit code is NOT in this `Solar_site` folder

### FastAPI Backend (Partially Built)
- In an earlier conversation (2026-03-26), a **FastAPI server** was started to wrap the existing ML models
- It was designed to expose endpoints for depth prediction, rock type classification, and terrain analysis
- **Note**: This was part of a different but related project (ocean floor mapping); the SolarSite FastAPI backend is separate and still needs to be built properly

### Research Paper
- Title: "SolarSite-India: AI-Optimized Solar Energy Site Selection Using Multi-Model Ensemble Learning"
- Focus: Comprehensive ML framework using 42 geospatial, climatic, and economic features
- Status: In preparation / research project

---

## 🏃 QUICK REFERENCE — Common Tasks

### Adding a new page
1. Create `src/pages/NewPage.jsx`
2. Add route in `src/App.jsx` inside `<Routes>`
3. Add nav link in `src/data/constants.js` → `NAV_LINKS`

### Adding a new chart component
1. Create component in `src/components/charts/`
2. Use `Recharts` components (ResponsiveContainer, BarChart, etc.)
3. Use `CHART_COLORS` from constants for consistent theming

### Switching to live API
1. Open `src/services/api.js`
2. Set `const USE_MOCK = false;`
3. Ensure `VITE_API_URL` env var points to FastAPI server
4. Ensure API response shapes match the mock data structure

### Modifying the design system
1. **Colors/fonts/shadows**: Edit `tailwind.config.js` → `theme.extend`
2. **Glass effects/animations**: Edit `src/index.css`
3. **Component-level styling**: Edit individual component files (they use Tailwind classes)

---

*This file should be read in full to restore complete project context. It contains every decision, file, feature, and historical note needed to continue work on SolarSite-India.*
