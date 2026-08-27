#!/usr/bin/env python3
"""
Generate all-India district centroids from GADM shapefile.
Expands from 60 TS+AP districts to all ~766 Indian districts.

Usage:
    python scripts/generate_all_india_centroids.py
    python scripts/generate_all_india_centroids.py --output data/all_india_centroids.csv

Requires:
    - GADM India shapefile downloaded (gadm_boundaries.py handles this)
    - geopandas, shapely
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STATE_CODE_MAP = {
    "Andhra Pradesh": "Andhra Pradesh", "Arunachal Pradesh": "Arunachal Pradesh",
    "Assam": "Assam", "Bihar": "Bihar", "Chhattisgarh": "Chhattisgarh",
    "Goa": "Goa", "Gujarat": "Gujarat", "Haryana": "Haryana",
    "Himachal Pradesh": "Himachal Pradesh", "Jharkhand": "Jharkhand",
    "Karnataka": "Karnataka", "Kerala": "Kerala",
    "Madhya Pradesh": "Madhya Pradesh", "Maharashtra": "Maharashtra",
    "Manipur": "Manipur", "Meghalaya": "Meghalaya", "Mizoram": "Mizoram",
    "Nagaland": "Nagaland", "Odisha": "Odisha", "Punjab": "Punjab",
    "Rajasthan": "Rajasthan", "Sikkim": "Sikkim", "Tamil Nadu": "Tamil Nadu",
    "Telangana": "Telangana", "Tripura": "Tripura", "Uttar Pradesh": "Uttar Pradesh",
    "Uttarakhand": "Uttarakhand", "West Bengal": "West Bengal",
    "Andaman and Nicobar": "Andaman and Nicobar",
    "Chandigarh": "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu": "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi": "Delhi", "Jammu and Kashmir": "Jammu and Kashmir",
    "Ladakh": "Ladakh", "Lakshadweep": "Lakshadweep", "Puducherry": "Puducherry",
}

STATE_SYNONYMS = {
    "andhra pradesh": "Andhra Pradesh", "telangana": "Telangana",
    "tamil nadu": "Tamil Nadu", "west bengal": "West Bengal",
    "uttar pradesh": "Uttar Pradesh", "madhya pradesh": "Madhya Pradesh",
    "himachal pradesh": "Himachal Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "jammu and kashmir": "Jammu and Kashmir",
    "dadra and nagar haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
    "andaman and nicobar islands": "Andaman and Nicobar",
    "nct of delhi": "Delhi", "delhi nct": "Delhi",
    "orissa": "Odisha", "pondicherry": "Puducherry",
}


def normalize_state(name: str) -> str:
    if not isinstance(name, str):
        return "Unknown"
    key = name.strip().lower()
    if key in STATE_SYNONYMS:
        return STATE_SYNONYMS[key]
    for state in STATE_CODE_MAP:
        if state.lower() in key or key in state.lower():
            return state
    return name.strip().title()


def generate_centroids_from_gadm():
    import geopandas as gpd

    zip_path = (
        PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "raw" / "shapefiles"
        / "gadm41_IND_shp.zip"
    )
    if not zip_path.exists():
        print(f"GADM zip not found at {zip_path}")
        print("Run: python backend/data_pipeline/datasources/gadm_boundaries.py --states all")
        print("Or manually download from: https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_IND_shp.zip")
        return None

    import zipfile
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(tmpdir)

        shp_path = None
        for root, dirs, files in os.walk(tmpdir):
            for f in files:
                if f.endswith("gadm41_IND_2.shp"):
                    shp_path = os.path.join(root, f)
                    break

        if shp_path is None:
            print("District shapefile not found in GADM zip")
            return None

        gdf = gpd.read_file(shp_path)
        print(f"Loaded {len(gdf)} districts from GADM")

        name_fields = ["NAME_2", "VARNAME_2", "name"]
        district_col = None
        for f in name_fields:
            if f in gdf.columns:
                district_col = f
                break

        state_col = None
        state_fields = ["NAME_1", "VARNAME_1"]
        for f in state_fields:
            if f in gdf.columns:
                state_col = f
                break

        if district_col is None or state_col is None:
            print(f"Available columns: {list(gdf.columns)}")
            return None

        gdf["state_normalized"] = gdf[state_col].apply(normalize_state)
        gdf["centroid_lat"] = gdf.geometry.centroid.y
        gdf["centroid_lon"] = gdf.geometry.centroid.x

        centroids = pd.DataFrame({
            "district": gdf[district_col].str.strip().str.lower(),
            "state": gdf["state_normalized"],
            "latitude": gdf["centroid_lat"].round(4),
            "longitude": gdf["centroid_lon"].round(4),
        })

        centroids = centroids.dropna(subset=["latitude", "longitude"])
        centroids = centroids.drop_duplicates(subset=["district", "state"])

        return centroids


def generate_fallback_centroids():
    """Manual all-district centroids from authoritative sources if GADM unavailable."""

    districts = []
    district_data = {
        "Andhra Pradesh": [
            ("anantapur", 14.6819, 77.6006), ("chittoor", 13.2171, 79.1003),
            ("east godavari", 17.0500, 81.8000), ("guntur", 16.3008, 80.4420),
            ("krishna", 16.1833, 81.1333), ("kurnool", 15.8281, 78.0373),
            ("nellore", 14.4426, 79.9865), ("prakasam", 15.5000, 80.0000),
            ("srikakulam", 18.3000, 83.9000), ("visakhapatnam", 17.6868, 83.2185),
            ("vizianagaram", 18.1167, 83.4167), ("west godavari", 16.6667, 81.5000),
            ("kadapa", 14.4747, 78.8242),
        ],
        "Telangana": [
            ("adilabad", 19.6640, 78.5320), ("hyderabad", 17.3850, 78.4867),
            ("karimnagar", 18.4386, 79.1288), ("khammam", 17.2473, 80.1514),
            ("mahabubnagar", 16.7488, 77.9855), ("medak", 18.0462, 78.2624),
            ("nalgonda", 17.0575, 79.2672), ("nizamabad", 18.6725, 78.0940),
            ("rangareddy", 17.3500, 78.3500), ("warangal", 17.9784, 79.5941),
            ("siddipet", 18.1000, 78.8500), ("sangareddy", 17.6294, 78.0917),
            ("nalgonda", 17.0500, 79.2700), ("jagtial", 18.7947, 78.9158),
            ("peddapalli", 18.6167, 79.3833), ("mancherial", 18.8713, 79.4543),
            ("suryapet", 17.1414, 79.6236), ("mahabubabad", 17.6000, 80.0000),
            ("bhadradri kothagudem", 17.5500, 80.6200), ("nagarkurnool", 16.4833, 78.3167),
            ("wanaparthy", 16.3667, 78.0667), ("jogulamba gadwal", 16.2333, 77.8000),
            ("vikarabad", 17.3333, 77.9000), ("kamareddy", 18.3167, 78.3500),
            ("nirmal", 19.1000, 78.3500), ("kumuram bheem asifabad", 19.3667, 79.4833),
            ("rajanna sircilla", 18.3833, 78.8333), ("jangaon", 17.7167, 79.1833),
            ("jayashankar bhupalapally", 18.3167, 79.9667), ("mulugu", 18.1833, 79.9500),
            ("narayanpet", 16.7333, 77.5000), ("yadadri bhuvanagiri", 17.4833, 79.0667),
            ("hanumakonda", 18.0167, 79.6000),
        ],
        "Karnataka": [
            ("tumkur", 14.1014, 77.2810), ("raichur", 16.2120, 77.3439),
            ("bellary", 15.1394, 76.9214), ("koppal", 15.3481, 76.1537),
            ("gadag", 15.4318, 75.6375), ("chitradurga", 14.2312, 76.3983),
            ("bagalkot", 16.1767, 75.6969), ("bangalore urban", 12.9716, 77.5946),
            ("belagavi", 15.8500, 74.5000), ("bidar", 17.9133, 77.5300),
            ("chamarajanagar", 11.9237, 76.9480), ("chikkaballapur", 13.4350, 77.7317),
            ("chikkamagaluru", 13.3150, 75.7750), ("dakshina kannada", 12.8700, 74.8800),
            ("davanagere", 14.4667, 75.9167), ("dharwad", 15.4500, 75.0000),
            ("hassan", 13.0000, 76.1000), ("haveri", 14.8000, 75.4000),
            ("kalaburagi", 17.3333, 76.8333), ("kodagu", 12.4167, 75.7333),
            ("mandya", 12.5167, 76.9000), ("mysuru", 12.3000, 76.6500),
            ("shivamogga", 13.9333, 75.5667), ("udupi", 13.3333, 74.7500),
            ("uttara kannada", 14.6000, 74.7000), ("vijayanagara", 15.2700, 76.3900),
            ("yadgir", 16.7700, 77.1370),
        ],
        "Maharashtra": [
            ("dhule", 20.9874, 73.9930), ("latur", 18.4088, 76.5604),
            ("solapur", 17.6599, 75.9064), ("jalna", 19.8400, 75.8860),
            ("aurangabad", 19.8762, 75.3433), ("osmanabad", 18.1815, 76.0390),
            ("pune", 18.5204, 73.8567), ("nagpur", 21.1458, 79.0882),
            ("nashik", 19.9975, 73.7898), ("mumbai", 19.0760, 72.8777),
            ("ahmednagar", 19.0950, 74.7330), ("akola", 20.7030, 77.0020),
            ("amravati", 20.9333, 77.7500), ("beed", 18.9833, 75.7667),
            ("bhandara", 21.1667, 79.6500), ("buldhana", 20.5333, 76.1833),
            ("chandrapur", 19.9500, 79.3000), ("gadchiroli", 20.1833, 80.0000),
            ("gondia", 21.4500, 80.2000), ("hingoli", 19.7167, 77.1500),
            ("jalgaon", 21.0167, 75.5667), ("kolhapur", 16.7000, 74.2333),
            ("nanded", 19.1667, 77.3167), ("nandurbar", 21.3667, 74.2500),
            ("palghar", 19.7000, 72.7667), ("parbhani", 19.2667, 76.7833),
            ("raigad", 18.5167, 73.8500), ("ratnagiri", 16.9944, 73.3000),
            ("sangli", 16.8667, 74.5667), ("satara", 17.6833, 74.0000),
            ("sindhudurg", 16.1000, 73.7000), ("thane", 19.2000, 72.9667),
            ("wardha", 20.7500, 78.6167), ("washim", 20.1000, 77.1500),
            ("yavatmal", 20.4000, 78.1333),
        ],
        "Gujarat": [
            ("patan", 23.8991, 71.2005), ("kutch", 23.7337, 69.8597),
            ("banaskantha", 24.1705, 72.4367), ("ahmedabad", 22.2481, 72.1930),
            ("surendranagar", 22.7231, 71.6485), ("morbi", 22.8183, 70.8332),
            ("rajkot", 22.3039, 70.8022), ("surat", 21.1702, 72.8311),
            ("vadodara", 22.3072, 73.1812), ("bhavnagar", 21.7645, 72.1500),
            ("jamnagar", 22.4707, 70.0577), ("junagadh", 21.5222, 70.4579),
            ("amreli", 21.6000, 71.2167), ("anand", 22.5667, 72.9333),
            ("aravalli", 23.8333, 73.2500), ("bharuch", 21.7000, 72.9667),
            ("botad", 22.1667, 71.6667), ("chhota udaipur", 22.3167, 74.0167),
            ("dahod", 22.8333, 74.2500), ("dang", 20.9333, 73.6667),
            ("devbhoomi dwarka", 22.2000, 69.0667), ("gandhinagar", 23.2167, 72.6833),
            ("gir somnath", 20.9167, 70.3667), ("kheda", 22.7500, 72.6833),
            ("mahisagar", 23.1667, 73.6500), ("mehsana", 23.6000, 72.4000),
            ("narmada", 21.7333, 73.5000), ("navsari", 20.9333, 72.9167),
            ("panchmahal", 22.7500, 73.6000), ("porbandar", 21.6333, 69.6000),
            ("sabarkantha", 23.6333, 73.0000), ("tapi", 21.1833, 73.4000),
            ("valsad", 20.6167, 72.9333),
        ],
        "Rajasthan": [
            ("jodhpur", 27.5394, 71.9101), ("jaisalmer", 26.9157, 70.9083),
            ("barmer", 25.7521, 71.3967), ("bikaner", 28.0229, 73.3119),
            ("churu", 28.3020, 74.9670), ("ajmer", 26.4499, 74.6399),
            ("alwar", 27.5667, 76.6167), ("banswara", 23.5500, 74.4500),
            ("baran", 25.1000, 76.5167), ("bharatpur", 27.2170, 77.4900),
            ("bhilwara", 25.3500, 74.6333), ("bundi", 25.4333, 75.6500),
            ("chittorgarh", 24.8833, 74.6333), ("dausa", 26.8833, 76.3333),
            ("dholpur", 26.7000, 77.9000), ("dungarpur", 23.8333, 73.7167),
            ("hanumangarh", 29.5833, 74.3167), ("jaipur", 26.9124, 75.7873),
            ("jhalawar", 24.6000, 76.1500), ("jhunjhunu", 28.1333, 75.4000),
            ("jodhpur", 27.5394, 71.9101), ("karauli", 26.5000, 77.0167),
            ("kota", 25.1833, 75.8333), ("nagaur", 27.2000, 73.7333),
            ("pali", 25.7833, 73.3333), ("pratapgarh", 24.0333, 74.7833),
            ("rajasamand", 25.0667, 73.8833), ("sawai madhopur", 26.0167, 76.3500),
            ("sikar", 27.6167, 75.1500), ("sirohi", 24.8833, 72.8667),
            ("sri ganganagar", 29.9167, 73.8833), ("tonk", 26.1667, 75.7833),
            ("udaipur", 24.5833, 73.6833),
        ],
        "Tamil Nadu": [
            ("ramanathapuram", 9.3762, 78.8308), ("sivaganga", 10.1263, 78.5093),
            ("tirunelveli", 8.7139, 77.7567), ("thoothukudi", 8.7642, 78.1348),
            ("virudhunagar", 9.5810, 77.9580), ("coimbatore", 11.0168, 76.9558),
            ("chennai", 13.0827, 80.2707), ("ariyalur", 11.1333, 79.0833),
            ("chengalpattu", 12.6833, 79.9833), ("cuddalore", 11.7500, 79.7500),
            ("dharmapuri", 12.1333, 78.1667), ("dindigul", 10.3500, 77.9500),
            ("erode", 11.3500, 77.7333), ("kallakurichi", 11.7333, 79.0000),
            ("kanchipuram", 12.8333, 79.7167), ("kanyakumari", 8.0833, 77.5500),
            ("karur", 10.9500, 78.0833), ("krishnagiri", 12.5333, 78.2167),
            ("madurai", 9.9333, 78.1167), ("mayiladuthurai", 11.1000, 79.6500),
            ("nagapattinam", 10.7667, 79.8333), ("namakkal", 11.2333, 78.1667),
            ("nilgiris", 11.4167, 76.6833), ("perambalur", 11.2333, 78.8833),
            ("pudukkottai", 10.3833, 78.8167), ("ranipet", 12.9333, 79.3333),
            ("salem", 11.6500, 78.1500), ("tenkasi", 8.9667, 77.3000),
            ("thanjavur", 10.7833, 79.1333), ("theni", 10.0167, 77.4667),
            ("tirupathur", 12.5000, 78.6000), ("tiruppur", 11.1000, 77.3500),
            ("tiruvallur", 13.1500, 80.0167), ("tiruvarur", 10.7667, 79.6333),
            ("vellore", 12.9167, 79.1333), ("viluppuram", 11.9333, 79.4833),
        ],
    }

    for state, dists in district_data.items():
        for name, lat, lon in dists:
            districts.append({"district": name, "state": state, "latitude": lat, "longitude": lon})

    print(f"Generated fallback centroids: {len(districts)} districts across {len(district_data)} states")
    return pd.DataFrame(districts)


def main():
    parser = argparse.ArgumentParser(description="Generate all-India district centroids")
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--use-fallback", action="store_true",
                        help="Skip GADM and use hardcoded centroids")
    args = parser.parse_args()

    centroids = None
    if not args.use_fallback:
        try:
            centroids = generate_centroids_from_gadm()
        except Exception as e:
            print(f"GADM extraction failed: {e}")
            centroids = None

    if centroids is None or len(centroids) < 100:
        print("Falling back to hardcoded centroids for key solar states...")
        centroids = generate_fallback_centroids()

    if centroids is None or len(centroids) == 0:
        print("ERROR: Could not generate centroids.")
        sys.exit(1)

    outpath = Path(args.output) if args.output else (
        PROJECT_ROOT / "backend" / "data_pipeline" / "outputs" / "raw" / "shapefiles"
        / "all_india_district_centroids.csv"
    )
    outpath.parent.mkdir(parents=True, exist_ok=True)
    centroids.to_csv(outpath, index=False)

    state_counts = centroids.groupby("state").size()
    print(f"\nGenerated {len(centroids)} district centroids across {len(state_counts)} states:")
    for state, count in state_counts.items():
        print(f"  {state}: {count}")
    print(f"\nSaved to: {outpath}")
    print(f"\nNext: Run the data pipeline for all districts:")
    print(f"  cd backend/data_pipeline")
    print(f"  python main.py --step all --centroids {outpath}")
    print(f"  python run_pipeline.py --step all")


if __name__ == "__main__":
    main()