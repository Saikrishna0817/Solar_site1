"""
SolarSite-India — Census 2024 population projection + CEA CUF.
Uses compound growth formula: Pop(2024) = Pop(2011) × (1.01)^13
For post-reorganization districts, estimates from state avg density × area.
"""
import pandas as pd
from pathlib import Path

GROWTH_RATE = 0.01
YEARS = 13

PRE_REORG = [
    ("Adilabad", "Telangana", 708952, 16105),
    ("Hyderabad", "Telangana", 3943323, 217),
    ("Karimnagar", "Telangana", 1005711, 11823),
    ("Khammam", "Telangana", 796583, 16029),
    ("Mahabubnagar", "Telangana", 1063302, 18432),
    ("Medak", "Telangana", 757273, 9699),
    ("Nalgonda", "Telangana", 994451, 14240),
    ("Nizamabad", "Telangana", 1054906, 7956),
    ("Ranga Reddy", "Telangana", 1395438, 7493),
    ("Warangal", "Telangana", 1351966, 12846),
    ("Anantapuram", "Andhra Pradesh", 4083315, 19130),
    ("Chittoor", "Andhra Pradesh", 4170374, 15152),
    ("East Godavari", "Andhra Pradesh", 5138296, 10807),
    ("Guntur", "Andhra Pradesh", 4887813, 11391),
    ("Krishna", "Andhra Pradesh", 4529009, 8727),
    ("Kurnool", "Andhra Pradesh", 4053463, 17658),
    ("Sri Potti Sriramulu Nellore", "Andhra Pradesh", 2884524, 13076),
    ("Prakasam", "Andhra Pradesh", 3397448, 17626),
    ("Srikakulam", "Andhra Pradesh", 2699471, 5837),
    ("Visakhapatnam", "Andhra Pradesh", 4294059, 11161),
    ("Vizianagaram", "Andhra Pradesh", 2342868, 6539),
    ("West Godavari", "Andhra Pradesh", 3934782, 7742),
    ("YSR Kadapa", "Andhra Pradesh", 2884524, 15359),
]

NEW_DISTRICTS = {
    "Telangana": [
        ("Hanumakonda", 1309), ("Medchal-Malkajgiri", 1084), ("Sangareddy", 4464), ("Siddipet", 3632),
        ("Jogulamba Gadwal", 2928), ("Jangaon", 2188), ("Vikarabad", 3386),
        ("Mancherial", 4056), ("Kumuram Bheem Asifabad", 4879),
        ("Nirmal", 3845), ("Peddapalli", 2236), ("Jagtial", 2419),
        ("Rajanna Sircilla", 2010), ("Bhadradri Kothagudem", 7483),
        ("Jayashankar Bhupalapally", 6175), ("Mahabubabad", 2877),
        ("Suryapet", 3607), ("Nagarkurnool", 6102), ("Wanaparthy", 2462),
        ("Yadadri Bhuvanagiri", 3091), ("Kamareddy", 3652),
        ("Mulugu", 3881), ("Narayanpet", 2100),
    ],
    "Andhra Pradesh": [
        ("Alluri Sitharama Raju", 12251), ("Anakapalli", 4293),
        ("Dr. B. R. Ambedkar Konaseema", 2083), ("Kakinada", 3019),
        ("Eluru", 6702), ("NTR", 3305), ("Bapatla", 3829),
        ("Palnadu", 7298), ("Nandyal", 9682), ("Sri Sathya Sai", 8925),
        ("Tirupati", 8231), ("Annamayya", 7954),
        ("Parvathipuram Manyam", 3659), ("Markapuram", 2100),
    ],
}

STATE_DENSITY = {"Telangana": 312, "Andhra Pradesh": 308}


def process(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    results = []

    for district, state, pop2011, area in PRE_REORG:
        pop2024 = int(pop2011 * (1 + GROWTH_RATE) ** YEARS)
        density = round(pop2024 / area, 1) if area > 0 else 0
        results.append({
            "district": district, "state": state,
            "pop_2011": pop2011, "pop_2024_projected": pop2024,
            "area_sqkm": area, "population_density_per_sqkm": density,
            "source": "Census 2011 + 1%/yr compound growth × 13yr",
        })

    for state, districts in NEW_DISTRICTS.items():
        for district, area in districts:
            pop2024 = int(STATE_DENSITY[state] * area)
            results.append({
                "district": district, "state": state,
                "pop_2011": None, "pop_2024_projected": pop2024,
                "area_sqkm": area,
                "population_density_per_sqkm": STATE_DENSITY[state],
                "source": f"Est. from {state} avg density × area",
            })

    df = pd.DataFrame(results)
    df.to_csv(outdir / "census_districts.csv", index=False)
    print(f"Census: {len(df)} districts → {outdir / 'census_districts.csv'}")
    print(f"  Pre-reorg: {len(PRE_REORG)}  Post-reorg est: {sum(len(v) for v in NEW_DISTRICTS.values())}")

    # CEA CUF
    cuf = [
        ("Telangana", 4116, 7456),
        ("Andhra Pradesh", 7024, 13540),
    ]
    rows = []
    for state, mw, mu in cuf:
        c = (mu * 1000) / (mw * 8760)
        rows.append({"state": state, "installed_mw": mw, "annual_generation_mu": mu,
                     "capacity_utilization_factor": round(c, 4), "cuf_percent": round(c * 100, 2)})
    pd.DataFrame(rows).to_csv(outdir / "cuf_state.csv", index=False)
    print(f"CEA CUF → {outdir / 'cuf_state.csv'}")


if __name__ == "__main__":
    process("/home/krishna/Desktop/Projects/AAC/Solar_site/backend/data_pipeline/outputs/raw/census_cea")