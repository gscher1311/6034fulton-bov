#!/usr/bin/env python3
"""
BOV Website Builder Template — LAAA Team at Marcus & Millichap
==============================================================
This is a TEMPLATE. All placeholders marked # DEAL-SPECIFIC must be
replaced with actual property data before running.

Usage:
  1. Copy this file to C:/Users/gscher/{slug}-bov/build_bov.py
  2. Replace ALL # DEAL-SPECIFIC placeholders
  3. Copy images to {slug}-bov/images/
  4. Run: python build_bov.py
  5. Output: index.html
"""
import base64, json, os, sys, io, math, urllib.request, urllib.parse, statistics

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, "images")
OUTPUT = os.path.join(SCRIPT_DIR, "index.html")

# ============================================================
# DEAL-SPECIFIC CONFIG — Replace these for every build
# ============================================================
SLUG = "6034fulton"
ADDRESS = "6034 Fulton Ave"
CITY_STATE_ZIP = "Van Nuys, CA 91401"
FULL_ADDRESS = "6034 Fulton Ave, Van Nuys, CA 91401"
SUBMARKET = "Valley Glen / Van Nuys"
CLIENT_NAME = "Berkus Trust"
COVER_MONTH_YEAR = "March 2026"
PROPERTY_SUBTITLE = "12-Unit Mixed Multifamily Investment"

BOV_BASE_URL = f"https://{SLUG}.laaa.com"
PDF_WORKER_URL = "https://laaa-pdf-worker.laaa-team.workers.dev"
PDF_FILENAME = "LAAA-Team-BOV-6034-Fulton-Ave.pdf"
PDF_LINK = (PDF_WORKER_URL + "/?url=" + urllib.parse.quote(BOV_BASE_URL + "/", safe="")
            + "&filename=" + urllib.parse.quote(PDF_FILENAME, safe=""))

# Section inclusion flags — set per deal
INCLUDE_TRANSACTION_HISTORY = False
INCLUDE_DEVELOPMENT_POTENTIAL = False
INCLUDE_ADU_OPPORTUNITY = False
INCLUDE_ON_MARKET_COMPS = True
PROPERTY_TYPE = "value-add"

# Agent lineup — always Glen + Filip minimum
# Add/remove agents as needed per deal
COVER_AGENTS = [
    {"name": "Glen Scher", "title": "Senior Managing Director Investments", "img_key": "glen"},
    {"name": "Filip Niculete", "title": "Senior Managing Director Investments", "img_key": "filip"},
]
FOOTER_AGENTS = [
    {
        "name": "Glen Scher",
        "title": "Senior Managing Director Investments",
        "phone": "(818) 212-2808",
        "email": "Glen.Scher@marcusmillichap.com",
        "license": "01962976",
        "img_key": "glen",
    },
    {
        "name": "Filip Niculete",
        "title": "Senior Managing Director Investments",
        "phone": "(818) 212-2748",
        "email": "Filip.Niculete@marcusmillichap.com",
        "license": "01905352",
        "img_key": "filip",
    },
]

# ============================================================
# IMAGE LOADING
# ============================================================
def load_image_b64(filename):
    path = os.path.join(IMAGES_DIR, filename)
    if not os.path.exists(path):
        print(f"WARNING: Image not found: {path}")
        return ""
    ext = filename.rsplit(".", 1)[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp"}.get(ext, "image/png")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    print(f"  Loaded: {filename} ({len(data)//1024}KB)")
    return f"data:{mime};base64,{data}"

print("Loading images...")
IMG = {
    # Standard branding (same for every BOV — copy from LAAA-AI-Prompts/branding/)
    "logo": load_image_b64("LAAA_Team_White.png"),
    "logo_blue": load_image_b64("LAAA_Team_Blue.png"),
    "closings_map": load_image_b64("closings-map.png"),
    # Team headshots (copy from LAAA-AI-Prompts/branding/headshots/)
    "glen": load_image_b64("Glen_Scher.png"),
    "filip": load_image_b64("Filip_Niculete.png"),
    "team_aida": load_image_b64("Aida_Memary_Scher.png"),
    "team_morgan": load_image_b64("Morgan_Wetmore.png"),
    "team_luka": load_image_b64("Luka_Leader.png"),
    "team_logan": load_image_b64("Logan_Ward.png"),
    "team_alexandro": load_image_b64("Alexandro_Tapia.png"),
    "team_blake": load_image_b64("Blake_Lewitt.png"),
    "team_mike": load_image_b64("Mike_Palade.png"),
    "team_tony": load_image_b64("Tony_Dang.png"),
    # Deal-specific photos — DEAL-SPECIFIC filenames
    "hero": load_image_b64("6034-Fulton-Ave_Front-Facade_Centered.jpg"),
    "grid1": load_image_b64("6034-Fulton-Ave_Front-Facade_Wide-Centered.jpg"),
    "buyer_photo": load_image_b64("6034-Fulton-Ave_Front-Facade_Angle-Left.jpg"),
}

# ============================================================
# GEOCODING — US Census Bureau Geocoder
# ============================================================
def geocode_census(addr):
    url = (f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
           f"?address={urllib.parse.quote(addr)}&benchmark=Public_AR_Current&format=json")
    try:
        data = json.loads(urllib.request.urlopen(url, timeout=15).read())
        m = data["result"]["addressMatches"]
        if not m:
            print(f"  WARNING: No match for: {addr}")
            return None
        lat, lng = m[0]["coordinates"]["y"], m[0]["coordinates"]["x"]
        print(f"  Geocoded: {addr} -> ({lat:.6f}, {lng:.6f})")
        return (lat, lng)
    except Exception as e:
        print(f"  WARNING: Geocode failed for {addr}: {e}")
        return None

print("\nGeocoding addresses...")
SUBJECT_ADDR = FULL_ADDRESS
SUBJECT_LAT = 34.180423
SUBJECT_LNG = -118.422184
print(f"  Subject coords (hardcoded): ({SUBJECT_LAT}, {SUBJECT_LNG})")

COMP_ADDRESSES = {
    "6234 Woodman Ave, Van Nuys, CA 91401": None,
    "16731 Sherman Way, Van Nuys, CA 91406": None,
    "6716 Sylmar Ave, Van Nuys, CA 91405": None,
    "14239 Gilmore St, Van Nuys, CA 91401": None,
    "14121 Friar St, Van Nuys, CA 91401": None,
    "6606 Hazeltine Ave, Van Nuys, CA 91405": None,
    "6924 Vesper Ave, Van Nuys, CA 91405": None,
    "6451 Kester Ave, Van Nuys, CA 91411": None,
    "7437 Haskell Ave, Van Nuys, CA 91406": None,
    "13430 Victory Blvd, Van Nuys, CA 91401": None,
    "14218 Victory Blvd, Van Nuys, CA 91401": None,
}
RENT_COMP_ADDRESSES = {
    "6202 Fulton Ave #101, Van Nuys": None,
    "6212 Fulton Ave #201, Van Nuys": None,
    "6212 Fulton Ave #205, Van Nuys": None,
    "6041 Fulton Ave, Van Nuys": None,
    "6060 Fulton Ave, Van Nuys": None,
    "6060 Fulton Ave, Van Nuys": None,
    "7453 Haskell Ave #7, Van Nuys": None,
    "5821 Sylmar Ave #2, Van Nuys": None,
}
for addr in COMP_ADDRESSES:
    COMP_ADDRESSES[addr] = geocode_census(addr)
for addr in RENT_COMP_ADDRESSES:
    RENT_COMP_ADDRESSES[addr] = geocode_census(addr)

# Filter out failed geocodes
failed_comps = [a for a, c in COMP_ADDRESSES.items() if c is None]
if failed_comps:
    print(f"WARNING: Failed to geocode {len(failed_comps)} comp addresses: {failed_comps}")
COMP_ADDRESSES = {k: v for k, v in COMP_ADDRESSES.items() if v is not None}
failed_rent = [a for a, c in RENT_COMP_ADDRESSES.items() if c is None]
if failed_rent:
    print(f"WARNING: Failed to geocode {len(failed_rent)} rent comp addresses: {failed_rent}")
RENT_COMP_ADDRESSES = {k: v for k, v in RENT_COMP_ADDRESSES.items() if v is not None}

# ============================================================
# STATIC MAP GENERATION (Pillow + OSM Tiles)
# ============================================================
from PIL import Image, ImageDraw, ImageFont

def lat_lng_to_tile(lat, lng, zoom):
    n = 2 ** zoom
    x = int((lng + 180) / 360 * n)
    lat_rad = math.radians(lat)
    y = int((1 - math.log(math.tan(lat_rad) + 1/math.cos(lat_rad)) / math.pi) / 2 * n)
    return x, y

def generate_static_map(center_lat, center_lng, markers, width=800, height=400, zoom=14):
    cx, cy = lat_lng_to_tile(center_lat, center_lng, zoom)
    tiles_x = math.ceil(width / 256) + 2
    tiles_y = math.ceil(height / 256) + 2
    start_x = cx - tiles_x // 2
    start_y = cy - tiles_y // 2
    big = Image.new("RGB", (tiles_x * 256, tiles_y * 256), (220, 220, 220))
    for tx in range(tiles_x):
        for ty in range(tiles_y):
            tile_url = f"https://tile.openstreetmap.org/{zoom}/{start_x + tx}/{start_y + ty}.png"
            req = urllib.request.Request(tile_url, headers={"User-Agent": "LAAA-BOV-Builder/1.0"})
            try:
                tile_data = urllib.request.urlopen(req, timeout=10).read()
                tile_img = Image.open(io.BytesIO(tile_data))
                big.paste(tile_img, (tx * 256, ty * 256))
            except Exception:
                pass
    n = 2 ** zoom
    offset_px = (center_lng + 180) / 360 * n * 256 - width / 2
    lat_rad = math.radians(center_lat)
    offset_py = (1 - math.log(math.tan(lat_rad) + 1/math.cos(lat_rad)) / math.pi) / 2 * n * 256 - height / 2
    crop_left = int(offset_px - start_x * 256)
    crop_top = int(offset_py - start_y * 256)
    cropped = big.crop((crop_left, crop_top, crop_left + width, crop_top + height))
    draw = ImageDraw.Draw(cropped)
    for m in markers:
        lat, lng, label, color = m["lat"], m["lng"], m.get("label", ""), m.get("color", "#1B3A5C")
        px = int((lng + 180) / 360 * n * 256 - offset_px)
        py = int((1 - math.log(math.tan(math.radians(lat)) + 1/math.cos(math.radians(lat))) / math.pi) / 2 * n * 256 - offset_py)
        r = 14 if label == "★" else 11
        draw.ellipse([px - r, py - r, px + r, py + r], fill=color, outline="white", width=2)
        if label:
            try:
                font = ImageFont.truetype("arial.ttf", 12 if label == "★" else 10)
            except Exception:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), label, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((px - tw // 2, py - th // 2 - 1), label, fill="white", font=font)
    buf = io.BytesIO()
    cropped.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    print(f"  Static map generated: {width}x{height}, {len(markers)} markers, {len(b64)//1024}KB")
    return f"data:image/png;base64,{b64}"

def calc_auto_zoom(markers, width=800, height=300, padding_pct=0.10):
    if len(markers) <= 1:
        return 15
    lats = [m["lat"] for m in markers]
    lngs = [m["lng"] for m in markers]
    lat_span = max(lats) - min(lats)
    lng_span = max(lngs) - min(lngs)
    lat_span = max(lat_span * (1 + padding_pct * 2), 0.002)
    lng_span = max(lng_span * (1 + padding_pct * 2), 0.002)
    zoom_lat = math.log2(height / 256 * 360 / lat_span) if lat_span > 0 else 18
    zoom_lng = math.log2(width / 256 * 360 / lng_span) if lng_span > 0 else 18
    zoom = int(min(zoom_lat, zoom_lng))
    return max(10, min(zoom, 16))

def build_markers_from_comps(comps, addr_dict, comp_color, subject_lat, subject_lng):
    """Build map markers. Tier 1-2 comps get full color, Tier 3 gets muted gray."""
    markers = [{"lat": subject_lat, "lng": subject_lng, "label": "★", "color": "#C5A258"}]
    tier3_color = "#9E9E9E"  # Muted gray for Tier 3 / reference comps
    for i, c in enumerate(comps):
        for a, coords in addr_dict.items():
            if coords and c["addr"].lower() in a.lower():
                color = tier3_color if c.get("tier", 1) == 3 else comp_color
                markers.append({"lat": coords[0], "lng": coords[1], "label": str(i + 1), "color": color})
                break
    return markers

# ============================================================
# FINANCIAL CONSTANTS — DEAL-SPECIFIC (replace ALL)
# ============================================================
LIST_PRICE = 3150000
UNITS = 12
SF = 9614
LOT_SF = 8540
LOT_ACRES = 8540 / 43560  # 0.20 acres
YEAR_BUILT = 1990
TAX_RATE = 0.0117
GSR = 292164  # Monthly $24,347 x 12
PF_GSR = 321600  # Pro forma $26,800 x 12
VACANCY_PCT = 0.03  # Per Glen's direction
OTHER_INCOME = 0  # No laundry income, no pool
NON_TAX_CUR_EXP = 57026  # Total OpEx $71,199 - Property Tax $14,173
NON_TAX_PF_EXP = 58203  # PF OpEx $72,376 - PF Property Tax $14,173

# Financing
INTEREST_RATE = 0.06  # 5yr Treasury 4.01% + 200bps bank spread (3/20/2026)  # Comp-derived baseline
AMORTIZATION_YEARS = 30
MAX_LTV = 0.65  # Backed into from DSCR 1.25x at 6.00% rate, rounded down to nearest 5%
MIN_DCR = 1.25

# Trade range
TRADE_RANGE_LOW = 3000000
TRADE_RANGE_HIGH = 3250000

# ============================================================
# FINANCIAL HELPER FUNCTIONS
# ============================================================
def calc_loan_constant(rate, amort):
    r = rate / 12
    n = amort * 12
    monthly = r * (1 + r)**n / ((1 + r)**n - 1)
    return monthly * 12

LOAN_CONSTANT = calc_loan_constant(INTEREST_RATE, AMORTIZATION_YEARS)

def calc_principal_reduction_yr1(loan_amount, annual_rate, amort_years):
    r = annual_rate / 12
    n = amort_years * 12
    monthly_pmt = loan_amount * (r * (1 + r)**n) / ((1 + r)**n - 1)
    balance = loan_amount
    total_principal = 0
    for _ in range(12):
        interest = balance * r
        principal = monthly_pmt - interest
        total_principal += principal
        balance -= principal
    return total_principal

def calc_metrics(price):
    taxes = price * TAX_RATE
    cur_egi = GSR * (1 - VACANCY_PCT) + OTHER_INCOME
    pf_egi = PF_GSR * (1 - VACANCY_PCT) + OTHER_INCOME
    cur_exp = NON_TAX_CUR_EXP + taxes
    pf_exp = NON_TAX_PF_EXP + taxes
    cur_noi = cur_egi - cur_exp
    pf_noi = pf_egi - pf_exp
    ltv_max_loan = price * MAX_LTV
    dcr_max_loan = cur_noi / (MIN_DCR * LOAN_CONSTANT) if LOAN_CONSTANT > 0 else ltv_max_loan
    loan_amount = min(ltv_max_loan, dcr_max_loan)
    actual_ltv = loan_amount / price if price > 0 else 0
    loan_constraint = "LTV" if ltv_max_loan <= dcr_max_loan else "DCR"
    down_payment = price - loan_amount
    debt_service = loan_amount * LOAN_CONSTANT
    net_cf_cur = cur_noi - debt_service
    net_cf_pf = pf_noi - debt_service
    coc_cur = net_cf_cur / down_payment * 100 if down_payment > 0 else 0
    coc_pf = net_cf_pf / down_payment * 100 if down_payment > 0 else 0
    dcr_cur = cur_noi / debt_service if debt_service > 0 else 0
    dcr_pf = pf_noi / debt_service if debt_service > 0 else 0
    prin_red = calc_principal_reduction_yr1(loan_amount, INTEREST_RATE, AMORTIZATION_YEARS)
    return {
        "price": price, "taxes": taxes,
        "cur_noi": cur_noi, "pf_noi": pf_noi,
        "cur_egi": cur_egi, "pf_egi": pf_egi,
        "cur_exp": cur_exp, "pf_exp": pf_exp,
        "per_unit": price / UNITS if UNITS > 0 else 0,
        "per_sf": price / SF if SF > 0 else 0,
        "cur_cap": cur_noi / price * 100 if price > 0 else 0,
        "pf_cap": pf_noi / price * 100 if price > 0 else 0,
        "grm": price / GSR if GSR > 0 else 0,
        "pf_grm": price / PF_GSR if PF_GSR > 0 else 0,
        "loan_amount": loan_amount, "down_payment": down_payment,
        "actual_ltv": actual_ltv, "loan_constraint": loan_constraint,
        "debt_service": debt_service,
        "net_cf_cur": net_cf_cur, "net_cf_pf": net_cf_pf,
        "coc_cur": coc_cur, "coc_pf": coc_pf,
        "dcr_cur": dcr_cur, "dcr_pf": dcr_pf,
        "prin_red": prin_red,
        "total_return_pct_cur": (net_cf_cur + prin_red) / down_payment * 100 if down_payment > 0 else 0,
        "total_return_pct_pf": (net_cf_pf + prin_red) / down_payment * 100 if down_payment > 0 else 0,
    }

# ============================================================
# PRICING MATRIX
# ============================================================
# Dynamic increment: gap = LIST_PRICE - TRADE_RANGE_LOW
# min_inc = gap/4, max_inc = gap/3
# Pick smallest clean value in [min_inc, max_inc]: 25K, 50K, 75K, 100K, 150K, 200K, 250K
INCREMENT = 25_000  # ($3,150,000 - $3,000,000) / ~6 steps
MATRIX_PRICES = list(range(LIST_PRICE + 5 * INCREMENT, LIST_PRICE - 5 * INCREMENT - 1, -INCREMENT))
MATRIX = [calc_metrics(p) for p in MATRIX_PRICES]
AT_LIST = calc_metrics(LIST_PRICE)

if LIST_PRICE > 0:
    print(f"\nFinancials at list ${LIST_PRICE:,}: Cap {AT_LIST['cur_cap']:.2f}%, GRM {AT_LIST['grm']:.2f}x, NOI ${AT_LIST['cur_noi']:,.0f}")

# ============================================================
# DATA PLACEHOLDERS — DEAL-SPECIFIC (replace ALL)
# ============================================================

# Rent Roll — list of tuples
# Value-add format: (unit, type, sf, current_rent, market_rent)
# Stabilized format: (unit, type, sf, rent, status, notes)
RENT_ROLL = [
    ("101 - 1/1 Flat", "1BR/1BA", 650, 1800, 1950),
    ("102 - 1/1 Flat", "1BR/1BA", 650, 1923, 1950),
    ("103 - 1/1 Flat", "1BR/1BA", 650, 1900, 1950),
    ("104 - 1/1 Flat", "1BR/1BA", 650, 1740, 1950),
    ("105 - 2/2 Flat", "2BR/2BA", 904, 1700, 2500),
    ("106 - 2/2 Flat", "2BR/2BA", 904, 2400, 2500),
    ("201 - 1+L/1 Loft", "1+L/1BA", 850, 1893, 2250),
    ("202 - 1+L/1 Loft", "1+L/1BA", 850, 2012, 2250),
    ("203 - 1+L/1 Loft", "1+L/1BA", 850, 2050, 2250),
    ("204 - 1+L/1 Loft", "1+L/1BA", 850, 2190, 2250),
    ("205 - 2/2 Flat", "2BR/2BA", 904, 2430, 2500),
    ("206 - 2/2 Flat", "2BR/2BA", 904, 2309, 2500),
]

# Sale Comps
# Fields: num, addr, units, yr, sf, price, ppu, psf, cap, grm, date, dom, notes, tier, laaa
# - cap: verified cap rate (recalculated from NOI / sale price). Use "--" if NOI unavailable.
# - tier: 1 (primary), 2 (supporting), 3 (reference) — from COMP_ANALYSIS_PROTOCOL.md
# - laaa: True if Glen/Filip/LAAA Team sold this comp (gets gold badge in table)
SALE_COMPS = [
    {"num": 1, "addr": "6234 Woodman Ave, Van Nuys", "units": 9, "yr": 1987, "sf": 9265, "price": 2648250, "ppu": 294250, "psf": 286, "cap": 5.12, "grm": 11.72, "date": "10/2025", "dom": 65, "notes": "Non-RSO, mixed 1BR/2BR", "tier": 1, "laaa": False},
    {"num": 2, "addr": "16731 Sherman Way, Van Nuys", "units": 13, "yr": 1986, "sf": 11326, "price": 3250000, "ppu": 250000, "psf": 287, "cap": 6.63, "grm": 10.11, "date": "09/2025", "dom": 26, "notes": "13 units, mixed BR", "tier": 1, "laaa": False},
    {"num": 3, "addr": "6716 Sylmar Ave, Van Nuys", "units": 12, "yr": 1984, "sf": 9996, "price": 3500000, "ppu": 291667, "psf": 350, "cap": 6.34, "grm": 10.21, "date": "05/2025", "dom": 26, "notes": "LAAA Team sale. Exact size match, non-RSO", "tier": 1, "laaa": True},
    {"num": 4, "addr": "14239 Gilmore St, Van Nuys", "units": 8, "yr": 1986, "sf": 6224, "price": 1737500, "ppu": 217188, "psf": 279, "cap": 5.30, "grm": 11.74, "date": "01/2026", "dom": 11, "notes": "Same zip, 1BR/2BR mix", "tier": 2, "laaa": False},
    {"num": 5, "addr": "14121 Friar St, Van Nuys", "units": 7, "yr": 1998, "sf": 6526, "price": 2050000, "ppu": 292857, "psf": 314, "cap": 6.33, "grm": 11.11, "date": "12/2025", "dom": 120, "notes": "All 2BR, AB 1482", "tier": 2, "laaa": False},
    {"num": 6, "addr": "6606 Hazeltine Ave, Van Nuys", "units": 13, "yr": 2001, "sf": 14943, "price": 3600000, "ppu": 276923, "psf": 241, "cap": 5.96, "grm": 10.30, "date": "06/2025", "dom": 0, "notes": "Newer, 3BR-heavy, subterranean", "tier": 2, "laaa": False},
    {"num": 7, "addr": "6924 Vesper Ave, Van Nuys", "units": 14, "yr": 1991, "sf": "--", "price": 4100000, "ppu": 292857, "psf": "--", "cap": "--", "grm": "--", "date": "11/2024", "dom": "--", "notes": "Minimal data, $/unit ref only", "tier": 2, "laaa": False},
    {"num": 8, "addr": "6451 Kester Ave, Van Nuys", "units": 14, "yr": 1988, "sf": 13650, "price": 4680000, "ppu": 334286, "psf": 343, "cap": 5.66, "grm": 11.22, "date": "07/2025", "dom": 48, "notes": "Subterranean parking, all 2BR", "tier": 2, "laaa": False},
]

# On-Market Comps
ON_MARKET_COMPS = [
    {"num": 1, "addr": "7437 Haskell Ave, Van Nuys", "units": 10, "yr": 1987, "sf": 8830, "price": 2895000, "ppu": 289500, "psf": 328, "dom": "--", "notes": "All 1BR"},
    {"num": 2, "addr": "13430 Victory Blvd, Van Nuys", "units": 10, "yr": 2003, "sf": 11730, "price": 2950000, "ppu": 295000, "psf": 251, "dom": "--", "notes": "Deep value-add"},
    {"num": 3, "addr": "14218 Victory Blvd, Van Nuys", "units": 8, "yr": 1988, "sf": 7960, "price": 3579000, "ppu": 447375, "psf": 450, "dom": "--", "notes": "Fully renovated TH - ceiling"},
]

# Rent Comps
RENT_COMPS = [
    {"addr": "6202 Fulton Ave #101, Van Nuys", "type": "2BR/2BA", "sf": 1000, "rent": 2500, "rent_sf": 2.50, "source": "MLS Leased 3/22/2026"},
    {"addr": "6212 Fulton Ave #201, Van Nuys", "type": "2BR/2BA", "sf": 1203, "rent": 2795, "rent_sf": 2.32, "source": "MLS Leased 3/18/2026"},
    {"addr": "6212 Fulton Ave #205, Van Nuys", "type": "2BR/2BA", "sf": 1105, "rent": 2745, "rent_sf": 2.48, "source": "MLS Leased 1/20/2026"},
    {"addr": "6041 Fulton Ave, Van Nuys", "type": "1BR/1BA", "sf": 713, "rent": 2295, "rent_sf": 3.22, "source": "Rentometer 2/17/2026"},
    {"addr": "6060 Fulton Ave, Van Nuys", "type": "1BR/1BA", "sf": 800, "rent": 2195, "rent_sf": 2.74, "source": "Rentometer 4/24/2025"},
    {"addr": "6060 Fulton Ave, Van Nuys", "type": "2BR/1.5BA", "sf": 970, "rent": 2150, "rent_sf": 2.22, "source": "Rentometer 12/26/2025"},
    {"addr": "7453 Haskell Ave #7, Van Nuys", "type": "1BR/1BA", "sf": 800, "rent": 1995, "rent_sf": 2.49, "source": "MLS Leased 1/29/2026"},
    {"addr": "5821 Sylmar Ave #2, Van Nuys", "type": "2BR/2BA", "sf": 1100, "rent": 2400, "rent_sf": 2.18, "source": "MLS Leased 3/19/2026"},
]

# Expense line items — (label, current_value, note_number)
# Max 12 items. Taxes calculated dynamically from price.
expense_lines = [
    ("Real Estate Taxes", 36855, 1),
    ("Insurance", 12014, 2),
    ("Water / Sewer", 6400, 3),
    ("Trash", 3600, 0),
    ("Gas (Central Boiler)", 1200, 4),
    ("Common Area Electric", 2125, 5),
    ("Repairs & Maintenance", 12000, 6),
    ("Contract Services", 3000, 0),
    ("Administrative", 1500, 0),
    ("Management Fee (4% GSR)", 11687, 7),
    ("Reserves", 3000, 8),
    ("Other/Misc", 500, 0),
]

# Operating Statement Notes
OS_NOTES = {
    1: "Property Taxes: Buyer Year 1 tax at list price ($3,150,000 x 1.17%). Reassesses at close per Prop 13.",
    2: "Insurance: (12 units x $200) + (9,614 SF x $1.00/SF) = $12,014.",
    3: "Water/Sewer: 16 BD x $400 = $6,400. No pool, no laundry add-ons.",
    4: "Gas: Owner pays hot water via central boiler only. Tenants individually metered.",
    5: "Electric: Tier 2 base common area $2,125. No elevator, no laundry, no pool add-ons.",
    6: "R&M: $1,000/unit x 12 units. No pool maintenance.",
    7: "Management: 4% x $292,164 GSR. Increases to $12,864 at pro forma GSR.",
    8: "Reserves: $250/unit x 12 units.",
}

# ============================================================
# NARRATIVE CONTENT — DEAL-SPECIFIC (replace ALL)
# ============================================================

# Investment Overview (2-3 paragraphs, ~80 words each)
INVESTMENT_OVERVIEW_P1 = "The LAAA Team is proud to present 6034 Fulton Avenue, a 12-unit multifamily property located on a quiet residential block in the Valley Glen / Van Nuys border submarket of the San Fernando Valley. Built in 1990, the two-story building encompasses 9,614 square feet of rentable area on an 8,540 square-foot lot zoned R3-1. The property features a diverse unit mix of four 1-bedroom/1-bath flats, four 1-bedroom-plus-loft/1-bath units, and four 2-bedroom/2-bath flats, offering functional layouts ranging from 650 to 904 square feet."
INVESTMENT_OVERVIEW_P2 = "The property is exempt from the City of Los Angeles Rent Stabilization Ordinance (RSO), subject only to AB 1482 (the California Tenant Protection Act), which allows annual rent increases of 5% plus CPI. All 12 units are individually metered for gas and electric, with the owner responsible only for cold water and central boiler hot water. The diverse unit mix appeals to a broad tenant pool - from singles and students (Valley College is 0.5 miles away) to couples and small families - supporting stable occupancy and organic demand throughout market cycles."
INVESTMENT_OVERVIEW_P3 = "With in-place rents averaging $2,029 per month and achievable market rents of $2,233 per month, the property presents a 10.1% rent upside opportunity for a new buyer. The 30-year ownership under the Berkus Estate represents the first offering of this asset since 1996, positioning it as a rare acquisition opportunity in a supply-constrained corridor. TOC Tier 3 eligibility provides additional long-term density bonus potential for a future development play, adding strategic optionality beyond the near-term income upside."

# Investment Highlights (5-6 items, ~30 words each)
HIGHLIGHTS = [
    ("Non-RSO / AB 1482 Only", "Exempt from the City of LA's Rent Stabilization Ordinance. Rents are governed solely by AB 1482 (5% + CPI annual increases), giving owners maximum flexibility to capture market rent growth without LAHD registration or annual rent adjustment limitations."),
    ("LAAA Team Comp Intelligence", "The LAAA Team closed 6716 Sylmar Avenue - a 12-unit non-RSO property in Van Nuys 91405 - for $3.5M ($291,667/unit) in May 2025. This direct transaction experience provides firsthand pricing intelligence on the subject's exact submarket and product type. Additionally, the LAAA Team represented the sale of 6228 Fulton Avenue, a 30-unit property on Fulton Avenue itself."),
    ("10.1% Rent Upside", "Current rents average $2,029/month across all unit types. Market rents supported by direct MLS leased comps on Fulton Avenue - including 6202 Fulton at $2,500 for a 2/2 (leased 3/22/2026, one block away) and 6212 Fulton at $2,745-$2,795 for 2/2 units - indicate achievable pro forma rents of $1,950 (1BR), $2,250 (loft), and $2,500 (2BR)."),
    ("Diverse Unit Mix", "The property offers three distinct floor plans across 12 units: 1-bedroom flats (650 SF), 1-bedroom-plus-loft units (850 SF), and 2-bedroom/2-bath flats (904 SF). This variety creates natural tenant segmentation, reduces concentration risk, and supports strong occupancy across multiple renter demographics."),
    ("First Offering in 30 Years", "Acquired in 1996 as an REO sale and held continuously by the Berkus Estate, this property has never been offered for sale on the open market. Estate-held assets in supply-constrained corridors represent rare acquisition opportunities that attract a wide buyer pool."),
]

# Location Overview (2-3 paragraphs, ~80 words each)
LOCATION_P1 = "6034 Fulton Avenue is situated on a mid-block residential stretch in the Valley Glen / Van Nuys border area of the central San Fernando Valley. The immediate neighborhood is characterized by dense apartment buildings from the 1980s and 1990s, interspersed with single-family homes. Valley Glen's residential branding - distinct from the Van Nuys 91401 zip code - offers a quieter, neighborhood-oriented environment compared to the commercial arterials of Sherman Way or Victory Boulevard. The block benefits from a stable renter base drawn by relative affordability and central Valley access."
LOCATION_P2 = "The property is approximately 0.5 miles from Los Angeles Valley College, providing a consistent source of student and faculty housing demand. Commuter access is strong via the 405 Freeway (1.5 miles west) and the 101 Freeway (2 miles south). Metro bus routes 164 and 165 serve the Victory/Fulton corridor, and the Metro G Line (Orange Line) has a temporary stop at Oxnard Street approximately 0.7 miles south during the East San Fernando Valley Light Rail Transit construction. Major employment centers in Burbank, Warner Center, and the Sepulveda Pass corridor are all within a 15-minute drive."
LOCATION_P3 = "The central San Fernando Valley multifamily market continues to benefit from significant infrastructure investment. The East SFV Light Rail Transit project will add fixed-rail service along Van Nuys Boulevard, and the Sepulveda Transit Corridor is advancing toward construction. New Class A apartment deliveries such as the 405-unit project at 6728 Sepulveda Boulevard (expected January 2027) target a higher price point that does not directly compete with the subject's Class B positioning. Rentometer data shows a 1-bedroom median of $1,985 and a 2-bedroom median of $2,400 within 0.75 miles, confirming strong achievable rents in this corridor."

# Location Details Table rows
LOCATION_TABLE_ROWS = [
    ("Walk Score", "~71 (Very Walkable)"),
    ("Nearest Metro/Bus", "Routes 164, 165 at Victory/Fulton"),
    ("Metro G Line", "~0.7 mi (Oxnard temporary stop)"),
    ("Nearest Freeway", "US-101 (~2 mi) / I-405 (~1.5 mi)"),
    ("Valley College", "0.5 mi"),
    ("Nearest Grocery", "Ralphs (Victory Blvd, ~0.6 mi)"),
    ("Nearest Park", "Valley Glen Community Park (~0.3 mi)"),
    ("Hazard Zone", "Liquefaction Zone (NHD disclosure)"),
    ("Median HH Income", "~$55,000 (Van Nuys 91401)"),
    ("Renter %", "~72%"),
]

# Mission paragraphs for Track Record (~60 words each)
MISSION_P1 = "The LAAA Team at Marcus & Millichap is one of the San Fernando Valley's most active multifamily brokerage groups, with 456 closings totaling $1.45 billion in career sales volume. In the San Fernando Valley alone, the team has completed 93 transactions representing $335 million in total value. In Van Nuys specifically, the LAAA Team has closed 32 deals totaling $107.7 million, establishing deep market intelligence and an extensive buyer network for this submarket."
MISSION_P2 = "The LAAA Team's direct transactional experience on Fulton Avenue and in the immediate submarket provides a distinct pricing advantage for this offering. The team represented the sale of 6716 Sylmar Avenue - a 12-unit non-RSO property that closed at $3.5M ($291,667/unit) in May 2025 - which serves as the highest-weighted comparable for the subject. The team also closed 6228 Fulton Avenue, a 30-unit property on Fulton Avenue itself, demonstrating established credibility and buyer relationships on this specific corridor."
MISSION_P3 = "With active buyer relationships cultivated through 32 Van Nuys closings and current market intelligence from the Sylmar and Fulton Avenue transactions, the LAAA Team is uniquely positioned to identify qualified buyers, generate competitive offers, and execute a transaction at the property's full market value. The team's institutional knowledge of this corridor - including achievable rents, buyer cap rate expectations, and lender appetite - translates directly into pricing confidence and execution certainty."

# Buyer Profile
BUYER_TYPES = [
    ("Value-Add Investors", "Operators targeting the 10.1% rent upside from legacy below-market rents. The non-RSO status allows immediate rent adjustments to market levels upon lease expiration without regulatory constraints."),
    ("1031 Exchange Buyers", "Investors executing tax-deferred exchanges seeking a stabilized, fully occupied 12-unit property in a proven Van Nuys corridor. The $3.0M-$3.25M trade range accommodates common exchange price points."),
    ("Long-Term Hold Investors", "Buyers seeking steady cash flow from a 1990-vintage asset with individually metered utilities, no pool maintenance, and TOC Tier 3 density bonus optionality for future redevelopment."),
    ("First-Time Apartment Buyers", "Investors moving up from duplexes or fourplexes into their first 12-unit building. The diverse unit mix and non-RSO regulatory environment reduce operational complexity."),
]
BUYER_OBJECTIONS = [
    ("Q: The property is in a liquefaction zone. How does that affect value?", "A: The liquefaction designation applies to a broad swath of the San Fernando Valley floor - including many of the comparable sales used in this analysis. The -2% adjustment applied across all comps reflects the standard market discount. Buyers should budget for earthquake insurance (typically $0.25-$0.50/SF annually) and conduct a Phase I environmental review during due diligence."),
    ("Q: With 8 of 12 units being 1-bedroom or loft, isn't the income potential lower?", "A: The 1BR-heavy unit mix generates lower gross rent per unit compared to all-2BR buildings, which is reflected in the 3%-5% unit mix discount applied to comparable sales. However, this mix broadens the tenant pool (students, singles, young professionals) and supports faster lease-up. Rentometer shows 1BR median of $1,985 within 0.75 miles, confirming strong demand for smaller units in this submarket."),
    ("Q: There are code enforcement cases on file. Is this a risk?", "A: Four code enforcement cases and two retrofit items are on file with the City. Status is unverified. Buyers should request case status from LADBS during due diligence. Common items for 1990-vintage properties include minor habitability or maintenance issues. We recommend budgeting $5,000-$15,000 for potential resolution depending on case severity."),
    ("Q: How confident are you in the list price?", "A: Three independent valuation methods - $/unit ($3.13M), GRM ($3.14M), and cap rate at 3% vacancy ($3.23M) - converge tightly around the $3.15M list price. The Tier 1 comp-derived weighted average of $260,760/unit aligns closely with the $262,500/unit asking price. The LAAA Team's direct sale of 6716 Sylmar (12 units, $291,667/unit) provides firsthand pricing validation."),
]
BUYER_CLOSING = "6034 Fulton Avenue combines the stability of a fully occupied, non-RSO 12-unit asset with meaningful rent upside and a first-time market offering from a 30-year estate hold - a rare combination in the supply-constrained Valley Glen / Van Nuys corridor."

# Comp Narratives — HTML string with one <p class="narrative"> per comp
# Order: Tier 1 comps first (LAAA sales first within Tier 1), then Tier 2. Tier 3 omitted.
# Tier 1 narratives ~100 words, Tier 2 ~60 words. See RESEARCH_TO_NARRATIVE_MAP.md.
COMP_NARRATIVES = """<p class="narrative"><strong>6234 Woodman Ave, Van Nuys</strong> -- 9 units, built 1987, sold October 2025 for $2,648,250 ($294,250/unit, $286/SF). This non-RSO property traded at a 5.12% cap rate and 11.72 GRM with a mixed 1BR/2BR unit configuration similar to the subject. At $294,250/unit, Woodman represents the strongest direct comparable. Adjusting downward for the subject's 1BR-heavy unit mix (-3%), size differential (-2%), and liquefaction zone (-2%), this comp implies $273,653/unit for the subject, or $3.28M total - providing support for the upper end of the trade range.</p>

<p class="narrative"><strong>16731 Sherman Way, Van Nuys</strong> -- 13 units, built 1986, sold September 2025 for $3,250,000 ($250,000/unit, $287/SF). This same-era property traded at a 6.63% cap rate and 10.11 GRM with 26 days on market. The comp's mixed 1BR/2BR/3BR unit configuration parallels the subject's diversity. Adjusting for the subject's 1BR-heavy mix (-3%) and liquefaction zone (-2%), offset by a marginal size premium (+1%), the implied value is $240,000/unit - anchoring the floor of the trade range at $2.88M.</p>

<p class="narrative"><strong>6716 Sylmar Ave, Van Nuys</strong> <span class="laaa-badge">LAAA Team Sale</span> -- 12 units, built 1984, sold May 2025 for $3,500,000 ($291,667/unit, $350/SF). This LAAA Team transaction provides direct pricing intelligence: identical unit count, non-RSO status confirmed, and located within Van Nuys 91405. The property traded at a verified 6.34% cap rate (versus 6.00% stated at list) after selling at 94.6% of asking price. Adjusting for Sylmar's all-2BR configuration versus the subject's 1BR-heavy mix (-5%) and liquefaction zone (-2%), the implied value is $271,250/unit ($3.26M). The LAAA Team's firsthand knowledge of this transaction's pricing dynamics and buyer pool directly informs the subject's marketing strategy.</p>

<p class="narrative"><strong>14239 Gilmore St, Van Nuys</strong> -- 8 units, built 1986, sold January 2026 for $1,737,500 ($217,188/unit, $279/SF). The most recent sale in the comp set, closing just 2.3 months ago with only 11 days on market. This AB 1482 property has a similar 1BR/2BR mix to the subject. At $217,188/unit, Gilmore represents the pricing floor, reflecting its 1-story construction and 1BA units. Adjusting modestly for the subject's superior loft and 2BA product (+3%) and liquefaction zone (-2%), the adjusted value of $215,016/unit establishes the lower bound of the range.</p>

<p class="narrative"><strong>14121 Friar St, Van Nuys</strong> -- 7 units, built 1998, sold December 2025 for $2,050,000 ($292,857/unit, $314/SF). A recent AB 1482 sale with complete financial data (6.33% verified cap rate). Friar's all-2BR townhome product is higher-quality than the subject's 1BR-dominant mix. Adjusting for unit mix (-5%), size (-3%), and liquefaction (-2%), the implied value is $269,428/unit.</p>

<p class="narrative"><strong>6451 Kester Ave, Van Nuys</strong> -- 14 units, built 1988, sold July 2025 for $4,680,000 ($334,286/unit, $343/SF). This premium sale at a 5.66% cap rate reflects subterranean parking and an all-2BR configuration. Adjusting for unit mix (-5%), parking quality (-5%), and liquefaction (-2%), the heavily adjusted implied value of $297,514/unit represents the ceiling reference for the subject.</p>"""

# On-Market Narrative (~150 words)
ON_MARKET_NARRATIVE = "Three active listings provide additional market context. 7437 Haskell Avenue (10 units, $289,500/unit) is an all-1BR property asking a 5.48% cap rate, indicating current seller expectations for similar-vintage product. 13430 Victory Boulevard (10 units, $295,000/unit) is a deep value-add play with rents at $1,750 versus $2,750 projected, providing insight into how the market prices significant upside. 14218 Victory Boulevard (8 units, $447,375/unit) represents the post-renovation ceiling for same-vintage townhome product - fully renovated with in-unit washer/dryer and tenant-paid utilities."

# Pricing Rationale (2-3 paragraphs, anchored to tier-weighted comp analysis)
PRICING_RATIONALE = """<p>Our suggested list price of $3,150,000 ($262,500/unit) is anchored by three Tier 1 comparable sales - 6234 Woodman Avenue, 16731 Sherman Way, and 6716 Sylmar Avenue - which, after adjustments for the subject's 1BR-heavy unit mix, liquefaction zone, and size differentials, indicate a Tier 1 weighted average of $260,760/unit. The LAAA Team's direct sale of 6716 Sylmar (12 units, non-RSO, May 2025) provides firsthand pricing intelligence on the identical product type in the immediate submarket.</p>

<p>Based on eight comparable sales spanning May 2024 through January 2026, with three primary comps requiring moderate adjustments primarily for unit mix composition, we have MODERATE-strong support for the $3,000,000 to $3,250,000 trade range. Three independent valuation methods confirm this positioning: the $/unit method yields $3.13M, the GRM method yields $3.14M, and the income approach at a 5.85% cap rate (tax-adjusted) produces $3.23M - a tight convergence that reinforces pricing accuracy. At the $3.15M list price, the property offers a 6.02% current cap rate and 10.78 GRM on tax-adjusted income, with 10.1% rent upside to a 6.32% pro forma cap rate.</p>

<p>The pricing reflects appropriate discounts for the subject's 1BR-heavy unit mix (67% of units are 1-bedroom or loft configurations versus the predominantly 2BR comp set) and liquefaction zone designation, while capturing the premium associated with non-RSO status, 100% occupancy, and a first-time market offering from a 30-year estate hold. The property is positioned to attract value-add operators, 1031 exchange buyers, and long-term hold investors seeking stable income with near-term upside.</p>"""

# Comp analysis confidence level
COMP_CONFIDENCE = "MODERATE-HIGH"

# Assumptions & Conditions disclaimer
ASSUMPTIONS_DISCLAIMER = "This analysis is based on information believed to be reliable but not guaranteed. Projected rents and expenses are estimates using LAAA Team broker-optimistic benchmarks and comparable market data as of March 2026. Actual results may vary. Buyers should conduct independent due diligence including verification of code enforcement cases, liquefaction zone insurance requirements, and current lease terms."

# Property Info Tables (4 tables for Property Details page)
PROP_OVERVIEW = [
    ("Address", "6034 Fulton Ave, Van Nuys, CA 91401"),
    ("APN", "2331-028-012"),
    ("Year Built", "1990"),
    ("Number of Units", "12"),
    ("Building SF", "9,614 SF"),
    ("Average Unit SF", "801 SF"),
    ("Stories", "2"),
    ("Construction", "Wood Frame / Stucco"),
]
PROP_SITE_ZONING = [
    ("Lot Size (SF)", "8,540 SF"),
    ("Lot Size (Acres)", "0.20 Acres"),
    ("Zoning", "R3-1"),
    ("TOC Tier", "Tier 3"),
    ("TOIA", "Area 2"),
    ("Community Plan", "Van Nuys - North Sherman Oaks"),
    ("Parking", "Surface (count TBD - verify)"),
]
PROP_BUILDING = [
    ("Roof", "Flat / built-up (age unknown)"),
    ("Plumbing", "Copper (original 1990)"),
    ("Electrical", "200A (standard for vintage)"),
    ("HVAC", "Wall units (individual)"),
    ("Water Heaters", "Central boiler (owner pays gas)"),
    ("Laundry", "None confirmed on-site"),
    ("Metering", "Individual gas & electric"),
    ("Recent CapEx", "None reported"),
]
PROP_REGULATORY = [
    ("Rent Control", "NOT RSO (built 1990, post-1978)"),
    ("Just Cause", "Yes (AB 1482 applies)"),
    ("AB 1482", "Subject to CA Tenant Protection Act"),
    ("Soft-Story Retrofit", "Not applicable (post-1978)"),
    ("Code Enforcement", "4 cases + 2 retrofit items (status unverified)"),
]

# Transaction History (optional)
TRANSACTION_ROWS = []  # DEAL-SPECIFIC — list of dicts
TRANSACTION_NARRATIVE = ""  # DEAL-SPECIFIC

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def fc(n):
    """Format currency."""
    if n is None or n == "--":
        return "--"
    return f"${n:,.0f}"

def fp(n):
    """Format percentage."""
    if n is None:
        return "--"
    return f"{n:.2f}%"

# ============================================================
# LEAFLET JS MAP GENERATOR
# ============================================================
def build_map_js(map_id, comps, comp_color, addr_dict, subject_lat, subject_lng, subject_label=None):
    if subject_label is None:
        subject_label = ADDRESS
    js = f"var {map_id} = L.map('{map_id}');\n"
    js += f"L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{attribution: '&copy; OpenStreetMap'}}).addTo({map_id});\n"
    js += f"var {map_id}Markers = [];\n"
    js += f"""var {map_id}Sub = L.marker([{subject_lat}, {subject_lng}], {{icon: L.divIcon({{className: 'custom-marker', html: '<div style="background:#C5A258;color:#fff;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);">&#9733;</div>', iconSize: [32, 32], iconAnchor: [16, 16]}})}})\n.addTo({map_id}).bindPopup('<b>{subject_label}</b><br>Subject Property<br>{UNITS} Units | {SF:,} SF');\n{map_id}Markers.push({map_id}Sub);\n"""
    tier3_color = "#9E9E9E"  # Muted gray for Tier 3 / reference comps
    for i, c in enumerate(comps):
        lat, lng = None, None
        for a, coords in addr_dict.items():
            if coords and c["addr"].lower() in a.lower():
                lat, lng = coords
                break
        if lat is None:
            continue
        label = str(i + 1)
        marker_color = tier3_color if c.get("tier", 1) == 3 else comp_color
        price_str = fc(c.get("price", 0))
        tier_label = f" (Tier {c.get('tier', '')})" if c.get("tier") else ""
        popup = f"<b>#{label}: {c['addr']}</b><br>{c.get('units', '')} Units | {price_str}{tier_label}"
        js += f"""var {map_id}M{label} = L.marker([{lat}, {lng}], {{icon: L.divIcon({{className: 'custom-marker', html: '<div style="background:{marker_color};color:#fff;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;border:2px solid #fff;box-shadow:0 2px 4px rgba(0,0,0,0.3);">{label}</div>', iconSize: [26, 26], iconAnchor: [13, 13]}})}})\n.addTo({map_id}).bindPopup('{popup}');\n{map_id}Markers.push({map_id}M{label});\n"""
    js += f"var {map_id}Group = L.featureGroup({map_id}Markers);\n"
    js += f"{map_id}.fitBounds({map_id}Group.getBounds().pad(0.1));\n"
    return js

# Generate Leaflet JS for each comp section
sale_map_js = build_map_js("saleMap", SALE_COMPS, "#1B3A5C", COMP_ADDRESSES, SUBJECT_LAT, SUBJECT_LNG)
if INCLUDE_ON_MARKET_COMPS:
    active_map_js = build_map_js("activeMap", ON_MARKET_COMPS, "#2E7D32", COMP_ADDRESSES, SUBJECT_LAT, SUBJECT_LNG)
else:
    active_map_js = ""
rent_comps_for_map = [{"addr": rc["addr"], "units": "", "price": 0} for rc in RENT_COMPS]
rent_map_js = build_map_js("rentMap", rent_comps_for_map, "#1B3A5C", RENT_COMP_ADDRESSES, SUBJECT_LAT, SUBJECT_LNG)

# ============================================================
# GENERATE STATIC MAPS
# ============================================================
print("\nGenerating static maps...")
IMG["loc_map"] = generate_static_map(SUBJECT_LAT, SUBJECT_LNG,
    [{"lat": SUBJECT_LAT, "lng": SUBJECT_LNG, "label": "★", "color": "#C5A258"}],
    width=800, height=220, zoom=15)

sale_markers = build_markers_from_comps(SALE_COMPS, COMP_ADDRESSES, "#1B3A5C", SUBJECT_LAT, SUBJECT_LNG)
IMG["sale_map_static"] = generate_static_map(SUBJECT_LAT, SUBJECT_LNG, sale_markers,
    width=800, height=300, zoom=calc_auto_zoom(sale_markers))

if INCLUDE_ON_MARKET_COMPS:
    active_markers = build_markers_from_comps(ON_MARKET_COMPS, COMP_ADDRESSES, "#2E7D32", SUBJECT_LAT, SUBJECT_LNG)
    IMG["active_map_static"] = generate_static_map(SUBJECT_LAT, SUBJECT_LNG, active_markers,
        width=800, height=300, zoom=calc_auto_zoom(active_markers))

rent_markers = build_markers_from_comps(rent_comps_for_map, RENT_COMP_ADDRESSES, "#1B3A5C", SUBJECT_LAT, SUBJECT_LNG)
IMG["rent_map_static"] = generate_static_map(SUBJECT_LAT, SUBJECT_LNG, rent_markers,
    width=800, height=300, zoom=calc_auto_zoom(rent_markers))

# ============================================================
# GENERATE DYNAMIC TABLE HTML
# ============================================================

# Rent Roll
rent_roll_html = ""
total_rent = 0
total_sf = 0
total_market = 0
if PROPERTY_TYPE == "value-add":
    for unit, utype, sf, cur_rent, mkt_rent in RENT_ROLL:
        total_rent += cur_rent
        total_sf += sf
        total_market += mkt_rent
        rent_roll_html += f'<tr><td>{unit}</td><td>{utype}</td><td class="num">{sf:,}</td><td class="num">${cur_rent:,}</td><td class="num">${cur_rent/sf:.2f}</td><td class="num">${mkt_rent:,}</td><td class="num">${mkt_rent/sf:.2f}</td></tr>\n'
    rent_roll_html += f'<tr style="background:#1B3A5C;color:#fff;font-weight:700;"><td>Total</td><td>{len(RENT_ROLL)} Units</td><td class="num">{total_sf:,}</td><td class="num">${total_rent:,}</td><td class="num">${total_rent/total_sf:.2f}</td><td class="num">${total_market:,}</td><td class="num">${total_market/total_sf:.2f}</td></tr>\n'
else:
    for unit, utype, sf, rent, status, notes in RENT_ROLL:
        total_rent += rent
        total_sf += sf
        status_cell = f'<strong>{status}</strong>' if status == "Vacant" else status
        rent_roll_html += f'<tr><td>{unit}</td><td>{utype}</td><td class="num">{sf:,}</td><td class="num">${rent:,}</td><td class="num">${rent/sf:.2f}</td><td>{status_cell}</td><td>{notes}</td></tr>\n'
    rent_roll_html += f'<tr style="background:#1B3A5C;color:#fff;font-weight:700;"><td>Total</td><td>{len(RENT_ROLL)} Units</td><td class="num">{total_sf:,}</td><td class="num">${total_rent:,}</td><td class="num">${total_rent/total_sf:.2f}</td><td></td><td>${total_rent*12:,}/yr</td></tr>\n'

# Sale Comp Table — sorted by tier (Tier 1 first, LAAA sales first within tier)
sale_comp_html = ""
sorted_comps = sorted(SALE_COMPS, key=lambda c: (c.get("tier", 1), 0 if c.get("laaa") else 1))
for c in sorted_comps:
    grm_str = f'{c["grm"]:.1f}x' if c.get("grm") not in (None, "--") else "--"
    cap_str = f'{c["cap"]:.2f}%' if c.get("cap") not in (None, "--") else "--"
    psf_str = f'${c["psf"]:,}' if c.get("psf") not in (None, "--") else "--"
    dom_str = f'{c["dom"]:,}' if c.get("dom") not in (None, "--") else "--"
    sf_str = f'{c["sf"]:,}' if c.get("sf") not in (None, "--") else "--"
    # LAAA Team badge + tier indicator in address cell
    addr_display = c["addr"]
    if c.get("laaa"):
        addr_display += ' <span style="background:#C5A258;color:#fff;font-size:8px;font-weight:700;padding:1px 4px;border-radius:2px;vertical-align:middle;">LAAA TEAM</span>'
    sale_comp_html += f'<tr><td>{c["num"]}</td><td>{addr_display}</td><td class="num">{c["units"]}</td>'
    sale_comp_html += f'<td>{c["yr"]}</td><td class="num">{sf_str}</td>'
    sale_comp_html += f'<td class="num">{fc(c["price"])}</td><td class="num">{fc(c["ppu"])}</td>'
    sale_comp_html += f'<td class="num">{psf_str}</td><td class="num">{cap_str}</td>'
    sale_comp_html += f'<td class="num">{grm_str}</td>'
    sale_comp_html += f'<td>{c["date"]}</td><td class="num">{dom_str}</td></tr>\n'

# Average, median, and Tier 1 average summary rows
if SALE_COMPS:
    sc_prices = [c["price"] for c in SALE_COMPS]
    sc_ppus = [c["ppu"] for c in SALE_COMPS]
    sc_psfs = [c["psf"] for c in SALE_COMPS if c.get("psf") not in (None, "--")]
    sc_caps = [c["cap"] for c in SALE_COMPS if c.get("cap") not in (None, "--")]
    sc_grms = [c["grm"] for c in SALE_COMPS if c.get("grm") not in (None, "--")]
    sc_doms = [c["dom"] for c in SALE_COMPS if c.get("dom") not in (None, "--")]

    avg_price = statistics.mean(sc_prices)
    avg_ppu = statistics.mean(sc_ppus)
    avg_psf = statistics.mean(sc_psfs) if sc_psfs else 0
    avg_cap_str = f'{statistics.mean(sc_caps):.2f}%' if sc_caps else "--"
    avg_grm_str = f'{statistics.mean(sc_grms):.1f}x' if sc_grms else "--"
    avg_dom_str = f'{statistics.mean(sc_doms):.0f}' if sc_doms else "--"
    med_price = statistics.median(sc_prices)
    med_ppu = statistics.median(sc_ppus)
    med_psf = statistics.median(sc_psfs) if sc_psfs else 0
    med_cap_str = f'{statistics.median(sc_caps):.2f}%' if sc_caps else "--"
    med_grm_str = f'{statistics.median(sc_grms):.1f}x' if sc_grms else "--"
    med_dom_str = f'{statistics.median(sc_doms):.0f}' if sc_doms else "--"

    # Tier 1 average (if any Tier 1 comps exist)
    t1_comps = [c for c in SALE_COMPS if c.get("tier") == 1]
    t1_row = ""
    if t1_comps:
        t1_ppus = [c["ppu"] for c in t1_comps]
        t1_psfs = [c["psf"] for c in t1_comps if c.get("psf") not in (None, "--")]
        t1_caps = [c["cap"] for c in t1_comps if c.get("cap") not in (None, "--")]
        t1_grms = [c["grm"] for c in t1_comps if c.get("grm") not in (None, "--")]
        t1_ppu = statistics.mean(t1_ppus)
        t1_psf_str = f'${statistics.mean(t1_psfs):,.0f}' if t1_psfs else "--"
        t1_cap_str = f'{statistics.mean(t1_caps):.2f}%' if t1_caps else "--"
        t1_grm_str = f'{statistics.mean(t1_grms):.1f}x' if t1_grms else "--"
        t1_style = 'style="background:#E8F0E8;font-weight:600;"'
        t1_row = f'<tr {t1_style}><td></td><td>Tier 1 Average</td><td class="num"></td><td></td><td class="num"></td>'
        t1_row += f'<td class="num"></td><td class="num">{fc(t1_ppu)}</td>'
        t1_row += f'<td class="num">{t1_psf_str}</td><td class="num">{t1_cap_str}</td>'
        t1_row += f'<td class="num">{t1_grm_str}</td>'
        t1_row += f'<td></td><td class="num"></td></tr>\n'

    summary_row_style = 'style="background:#FFF8E7;font-weight:600;"'
    sale_comp_html += f'<tr {summary_row_style}><td></td><td>Average</td><td class="num"></td><td></td><td class="num"></td>'
    sale_comp_html += f'<td class="num">{fc(avg_price)}</td><td class="num">{fc(avg_ppu)}</td>'
    sale_comp_html += f'<td class="num">${avg_psf:,.0f}</td><td class="num">{avg_cap_str}</td>'
    sale_comp_html += f'<td class="num">{avg_grm_str}</td>'
    sale_comp_html += f'<td></td><td class="num">{avg_dom_str}</td></tr>\n'
    sale_comp_html += f'<tr {summary_row_style}><td></td><td>Median</td><td class="num"></td><td></td><td class="num"></td>'
    sale_comp_html += f'<td class="num">{fc(med_price)}</td><td class="num">{fc(med_ppu)}</td>'
    sale_comp_html += f'<td class="num">${med_psf:,.0f}</td><td class="num">{med_cap_str}</td>'
    sale_comp_html += f'<td class="num">{med_grm_str}</td>'
    sale_comp_html += f'<td></td><td class="num">{med_dom_str}</td></tr>\n'
    if t1_row:
        sale_comp_html += t1_row

# On-Market Comp Table
on_market_html = ""
for c in ON_MARKET_COMPS:
    psf_str = f'${c["psf"]}' if c.get("psf") and c["psf"] != "--" else "--"
    sf_str = f'{c["sf"]:,}' if c.get("sf") and c["sf"] != "--" else "--"
    on_market_html += f'<tr><td>{c["num"]}</td><td>{c["addr"]}</td><td class="num">{c["units"]}</td>'
    on_market_html += f'<td>{c["yr"]}</td><td class="num">{sf_str}</td>'
    on_market_html += f'<td class="num">{fc(c["price"])}</td><td class="num">{fc(c["ppu"])}</td>'
    on_market_html += f'<td class="num">{psf_str}</td><td class="num">{c["dom"]}</td>'
    on_market_html += f'<td>{c["notes"]}</td></tr>\n'

# Rent Comp Table
rent_comp_html = ""
for i, rc in enumerate(RENT_COMPS, 1):
    rent_comp_html += f'<tr><td>{i}</td><td>{rc["addr"]}</td><td>{rc["type"]}</td>'
    rent_comp_html += f'<td class="num">{rc["sf"]:,}</td><td class="num">${rc["rent"]:,}</td>'
    rent_comp_html += f'<td class="num">${rc["rent_sf"]:.2f}</td><td>{rc["source"]}</td></tr>\n'

# Operating Statement
TAXES_AT_LIST = AT_LIST["taxes"]
CUR_EGI = AT_LIST["cur_egi"]

os_income_html = ""
vacancy_amt = GSR * VACANCY_PCT
eri = GSR - vacancy_amt
os_income_html += f'<tr><td>Gross Scheduled Rent</td><td class="num">${GSR:,.0f}</td><td class="num">${GSR/UNITS:,.0f}</td><td class="num">${GSR/SF:.2f}</td><td class="num"> - </td></tr>\n'
os_income_html += f'<tr><td>Less: Vacancy ({VACANCY_PCT*100:.0f}%)</td><td class="num">$({vacancy_amt:,.0f})</td><td class="num">$({vacancy_amt/UNITS:,.0f})</td><td class="num">$({vacancy_amt/SF:.2f})</td><td class="num"> - </td></tr>\n'
if OTHER_INCOME > 0:
    os_income_html += f'<tr><td>Other Income <span class="note-ref">[*]</span></td><td class="num">${OTHER_INCOME:,.0f}</td><td class="num">${OTHER_INCOME/UNITS:,.0f}</td><td class="num">${OTHER_INCOME/SF:.2f}</td><td class="num"> - </td></tr>\n'
os_income_html += f'<tr class="summary"><td><strong>Effective Gross Income</strong></td><td class="num"><strong>${CUR_EGI:,.0f}</strong></td><td class="num"><strong>${CUR_EGI/UNITS:,.0f}</strong></td><td class="num"><strong>${CUR_EGI/SF:.2f}</strong></td><td class="num"><strong>100.0%</strong></td></tr>\n'

os_expense_html = ""
total_exp_calc = 0
for label, val, note_num in expense_lines:
    total_exp_calc += val
    ref = f' <span class="note-ref">[{note_num}]</span>' if note_num else ""
    os_expense_html += f'<tr><td>{label}{ref}</td><td class="num">${val:,.0f}</td><td class="num">${val/UNITS:,.0f}</td><td class="num">${val/SF:.2f}</td><td class="num">{val/CUR_EGI*100:.1f}%</td></tr>\n'

NOI_AT_LIST = CUR_EGI - total_exp_calc
os_expense_html += f'<tr class="summary"><td><strong>Total Expenses</strong></td><td class="num"><strong>${total_exp_calc:,.0f}</strong></td><td class="num"><strong>${total_exp_calc/UNITS:,.0f}</strong></td><td class="num"><strong>${total_exp_calc/SF:.2f}</strong></td><td class="num"><strong>{total_exp_calc/CUR_EGI*100:.1f}%</strong></td></tr>\n'
os_expense_html += f'<tr class="summary"><td><strong>Net Operating Income</strong></td><td class="num"><strong>${NOI_AT_LIST:,.0f}</strong></td><td class="num"><strong>${NOI_AT_LIST/UNITS:,.0f}</strong></td><td class="num"><strong>${NOI_AT_LIST/SF:.2f}</strong></td><td class="num"><strong>{NOI_AT_LIST/CUR_EGI*100:.1f}%</strong></td></tr>\n'

# OS Notes HTML
os_notes_html = ""
for num in sorted(OS_NOTES.keys()):
    os_notes_html += f'<p><strong>[{num}]</strong> {OS_NOTES[num]}</p>\n'

# Pricing Matrix
matrix_html = ""
if PROPERTY_TYPE == "value-add":
    for m in MATRIX:
        cls = ' class="highlight"' if m["price"] == LIST_PRICE else ""
        matrix_html += f'<tr{cls}><td class="num">${m["price"]:,}</td>'
        matrix_html += f'<td class="num">{m["cur_cap"]:.2f}%</td>'
        matrix_html += f'<td class="num">{m["pf_cap"]:.2f}%</td>'
        matrix_html += f'<td class="num">{m["coc_cur"]:.2f}%</td>'
        matrix_html += f'<td class="num">${m["per_sf"]:.0f}</td>'
        matrix_html += f'<td class="num">${m["per_unit"]:,.0f}</td>'
        matrix_html += f'<td class="num">{m["pf_grm"]:.2f}x</td></tr>\n'
else:
    for m in MATRIX:
        cls = ' class="highlight"' if m["price"] == LIST_PRICE else ""
        matrix_html += f'<tr{cls}><td class="num">${m["price"]:,}</td>'
        matrix_html += f'<td class="num">{m["cur_cap"]:.2f}%</td>'
        matrix_html += f'<td class="num">{m["coc_cur"]:.2f}%</td>'
        matrix_html += f'<td class="num">${m["per_unit"]:,.0f}</td>'
        matrix_html += f'<td class="num">${m["per_sf"]:.0f}</td>'
        matrix_html += f'<td class="num">{m["grm"]:.2f}x</td>'
        matrix_html += f'<td class="num">{m["dcr_cur"]:.2f}x</td></tr>\n'

# Summary page expense rows
sum_expense_html = ""
for label, val, _ in expense_lines:
    label_clean = label.replace("&amp;", "&")
    sum_expense_html += f'<tr><td>{label_clean}</td><td class="num">${val:,.0f}</td></tr>\n'

if LIST_PRICE > 0:
    print(f"NOI at list (reassessed): ${NOI_AT_LIST:,.0f}")
    print(f"Total expenses: ${total_exp_calc:,.0f}")

# ============================================================
# HTML ASSEMBLY
# ============================================================
html_parts = []

# HEAD
html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="Broker Opinion of Value - {FULL_ADDRESS}">
<meta property="og:description" content="{PROPERTY_SUBTITLE} - {CITY_STATE_ZIP} | LAAA Team - Marcus &amp; Millichap">
<meta property="og:image" content="{BOV_BASE_URL}/preview.png">
<meta property="og:url" content="{BOV_BASE_URL}/">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Broker Opinion of Value - {FULL_ADDRESS}">
<meta name="twitter:description" content="{PROPERTY_SUBTITLE} - {CITY_STATE_ZIP} | LAAA Team - Marcus &amp; Millichap">
<meta name="twitter:image" content="{BOV_BASE_URL}/preview.png">
<title>BOV - {FULL_ADDRESS} | LAAA Team</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
""")

# ============================================================
# DESKTOP CSS (verbatim from blueprint)
# ============================================================
html_parts.append("""
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', sans-serif; color: #333; line-height: 1.6; background: #fff; }
html { scroll-padding-top: 50px; }
p { margin-bottom: 16px; font-size: 14px; line-height: 1.7; }

/* Cover */
.cover { position: relative; min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; color: #fff; overflow: hidden; }
.cover-bg { position: absolute; inset: 0; background-size: cover; background-position: center; filter: brightness(0.45); z-index: 0; }
.cover-content { position: relative; z-index: 2; padding: 60px 40px; max-width: 860px; }
.cover-logo { width: 320px; margin: 0 auto 30px; display: block; filter: drop-shadow(0 2px 8px rgba(0,0,0,0.3)); }
.cover-label { font-size: 13px; font-weight: 500; letter-spacing: 3px; text-transform: uppercase; color: #C5A258; margin-bottom: 18px; }
.cover-title { font-size: 46px; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px; text-shadow: 0 2px 12px rgba(0,0,0,0.3); }
.cover-stats { display: flex; gap: 32px; justify-content: center; flex-wrap: wrap; margin-bottom: 32px; }
.cover-stat-value { display: block; font-size: 26px; font-weight: 600; color: #fff; }
.cover-stat-label { display: block; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1.5px; color: #C5A258; margin-top: 4px; }
.cover-headshots { display: flex; justify-content: center; gap: 40px; margin-top: 24px; margin-bottom: 16px; }
.cover-headshot { width: 80px; height: 80px; border-radius: 50%; border: 3px solid #C5A258; object-fit: cover; box-shadow: 0 4px 16px rgba(0,0,0,0.4); }
.cover-headshot-name { font-size: 12px; font-weight: 600; margin-top: 6px; color: #fff; }
.cover-headshot-title { font-size: 10px; color: #C5A258; }
.cover-headshot-wrap { text-align: center; }
.cover-stat { text-align: center; }
.cover-address { font-size: 16px; font-weight: 400; letter-spacing: 1px; color: rgba(255,255,255,0.85); margin-top: 4px; }
.client-greeting { font-size: 14px; font-weight: 500; color: #C5A258; letter-spacing: 1px; margin-top: 16px; }
.gold-line { height: 3px; background: #C5A258; margin: 20px 0; }

/* PDF Download Button */
.pdf-float-btn { position: fixed; bottom: 24px; right: 24px; z-index: 9999; padding: 14px 28px; background: #C5A258; color: #1B3A5C; font-size: 14px; font-weight: 700; text-decoration: none; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.35); display: flex; align-items: center; gap: 8px; }
.pdf-float-btn:hover { background: #fff; transform: translateY(-2px); }
.pdf-float-btn svg { width: 18px; height: 18px; fill: currentColor; }

/* TOC Nav */
.toc-nav { background: #1B3A5C; padding: 0 12px; display: flex; flex-wrap: nowrap; justify-content: center; align-items: stretch; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.15); overflow-x: auto; scrollbar-width: none; }
.toc-nav::-webkit-scrollbar { display: none; }
.toc-nav a { color: rgba(255,255,255,0.85); text-decoration: none; font-size: 11px; font-weight: 500; letter-spacing: 0.3px; text-transform: uppercase; padding: 12px 8px; border-bottom: 2px solid transparent; white-space: nowrap; display: flex; align-items: center; }
.toc-nav a:hover { color: #fff; background: rgba(197,162,88,0.12); border-bottom-color: rgba(197,162,88,0.4); }
.toc-nav a.toc-active { color: #C5A258; font-weight: 600; border-bottom-color: #C5A258; }

/* Sections */
.section { padding: 50px 40px; max-width: 1100px; margin: 0 auto; }
.section-alt { background: #f8f9fa; }
.section-title { font-size: 26px; font-weight: 700; color: #1B3A5C; margin-bottom: 6px; }
.section-subtitle { font-size: 13px; color: #C5A258; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 16px; font-weight: 500; }
.section-divider { width: 60px; height: 3px; background: #C5A258; margin-bottom: 30px; }
.sub-heading { font-size: 18px; font-weight: 600; color: #1B3A5C; margin: 30px 0 16px; }

/* Metrics */
.metrics-grid, .metrics-grid-4 { display: grid; gap: 16px; margin-bottom: 30px; }
.metrics-grid { grid-template-columns: repeat(3, 1fr); }
.metrics-grid-4 { grid-template-columns: repeat(4, 1fr); }
.metric-card { background: #1B3A5C; border-radius: 12px; padding: 24px; text-align: center; color: #fff; }
.metric-value { display: block; font-size: 28px; font-weight: 700; }
.metric-label { display: block; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,0.6); margin-top: 6px; }
.metric-sub { display: block; font-size: 12px; color: #C5A258; margin-top: 4px; }

/* Tables */
table { width: 100%; border-collapse: collapse; margin-bottom: 24px; font-size: 13px; }
th { background: #1B3A5C; color: #fff; padding: 10px 12px; text-align: left; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
td { padding: 8px 12px; border-bottom: 1px solid #eee; }
tr:nth-child(even) { background: #f5f5f5; }
tr.highlight { background: #FFF8E7 !important; border-left: 3px solid #C5A258; }
td.num, th.num { text-align: right; }
.table-scroll { overflow-x: auto; margin-bottom: 24px; }
.table-scroll table { min-width: 700px; margin-bottom: 0; }
.info-table td { padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 13px; }
.info-table td:first-child { font-weight: 600; color: #1B3A5C; width: 40%; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }

/* Track Record */
.tr-tagline { font-size: 24px; font-weight: 600; color: #1B3A5C; text-align: center; padding: 16px 24px; margin-bottom: 20px; border-left: 4px solid #C5A258; background: #FFF8E7; border-radius: 0 4px 4px 0; font-style: italic; }
.tr-map-print { display: none; }
.tr-service-quote { margin: 24px 0; }
.tr-service-quote h3 { font-size: 18px; font-weight: 700; color: #1B3A5C; margin-bottom: 8px; }
.tr-service-quote p { font-size: 14px; line-height: 1.7; }
.bio-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin: 24px 0; }
.bio-card { display: flex; gap: 16px; align-items: flex-start; }
.bio-headshot { width: 100px; height: 100px; border-radius: 50%; border: 3px solid #C5A258; object-fit: cover; flex-shrink: 0; }
.bio-name { font-size: 16px; font-weight: 700; color: #1B3A5C; }
.bio-title { font-size: 11px; color: #C5A258; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.bio-text { font-size: 13px; line-height: 1.6; color: #444; }
.team-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 12px 0; }
.team-card { text-align: center; padding: 8px; }
.team-headshot { width: 60px; height: 60px; border-radius: 50%; border: 2px solid #C5A258; object-fit: cover; margin: 0 auto 4px; display: block; }
.team-card-name { font-size: 13px; font-weight: 700; color: #1B3A5C; }
.team-card-title { font-size: 10px; color: #C5A258; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }
.costar-badge { text-align: center; background: #FFF8E7; border: 2px solid #C5A258; border-radius: 8px; padding: 20px 24px; margin: 30px auto 24px; max-width: 600px; }
.costar-badge-title { font-size: 22px; font-weight: 700; color: #1B3A5C; }
.costar-badge-sub { font-size: 12px; color: #C5A258; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-top: 6px; }
.condition-note { background: #FFF8E7; border-left: 4px solid #C5A258; padding: 16px 20px; margin: 24px 0; border-radius: 0 4px 4px 0; font-size: 13px; line-height: 1.6; }
.condition-note-label { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #C5A258; margin-bottom: 8px; }
.achievements-list { font-size: 13px; line-height: 1.8; }
.note-ref { font-size: 9px; color: #C5A258; font-weight: 700; vertical-align: super; }

/* Marketing */
.mkt-quote { background: #FFF8E7; border-left: 4px solid #C5A258; padding: 16px 24px; margin: 20px 0; border-radius: 0 4px 4px 0; font-size: 15px; font-style: italic; line-height: 1.6; color: #1B3A5C; }
.mkt-channels { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
.mkt-channel { background: #f0f4f8; border-radius: 8px; padding: 16px 20px; }
.mkt-channel h4 { color: #1B3A5C; font-size: 14px; margin-bottom: 8px; }
.mkt-channel li { font-size: 13px; line-height: 1.5; margin-bottom: 4px; }
.perf-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
.perf-card { background: #f0f4f8; border-radius: 8px; padding: 16px 20px; }
.perf-card h4 { color: #1B3A5C; font-size: 14px; margin-bottom: 8px; }
.perf-card li { font-size: 13px; line-height: 1.5; margin-bottom: 4px; }
.platform-strip { display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap; margin-top: 24px; padding: 14px 20px; background: #1B3A5C; border-radius: 6px; }
.platform-strip-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: #C5A258; font-weight: 600; }
.platform-name { font-size: 12px; font-weight: 600; color: #fff; }

/* Press Strip */
.press-strip { display: flex; justify-content: center; align-items: center; gap: 28px; flex-wrap: wrap; margin: 16px 0 0; padding: 12px 20px; background: #f0f4f8; border-radius: 6px; }
.press-strip-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: #888; font-weight: 600; }
.press-logo { font-size: 13px; font-weight: 700; color: #1B3A5C; letter-spacing: 0.5px; }

/* Investment Overview */
.inv-split { display: grid; grid-template-columns: 50% 50%; gap: 24px; }
.inv-left .metrics-grid-4 { grid-template-columns: repeat(2, 1fr); }
.inv-text p { font-size: 13px; line-height: 1.6; margin-bottom: 10px; }
.inv-logo { display: none; }
.inv-right { display: flex; flex-direction: column; gap: 16px; padding-top: 70px; }
.inv-photo { height: 280px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.inv-photo img { width: 100%; height: 100%; object-fit: cover; object-position: center; }
.inv-highlights { background: #f0f4f8; border: 1px solid #dce3eb; border-radius: 8px; padding: 16px 20px; flex: 1; }
.inv-highlights h4 { color: #1B3A5C; font-size: 13px; margin-bottom: 8px; }
.inv-highlights li { font-size: 12px; line-height: 1.5; margin-bottom: 5px; }

/* Location */
.loc-grid { display: grid; grid-template-columns: 58% 42%; gap: 28px; align-items: start; }
.loc-left { max-height: 480px; overflow: hidden; }
.loc-left p { font-size: 13.5px; line-height: 1.7; margin-bottom: 14px; }
.loc-right { display: block; max-height: 480px; overflow: hidden; }
.loc-wide-map { width: 100%; height: 200px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-top: 20px; }
.loc-wide-map img { width: 100%; height: 100%; object-fit: cover; object-position: center; }

/* Property Details */
.prop-grid-4 { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: auto auto; gap: 20px; }

/* Operating Statement */
.os-two-col { display: grid; grid-template-columns: 55% 45%; gap: 24px; align-items: stretch; margin-bottom: 24px; }
.os-left { }
.os-right { font-size: 10.5px; line-height: 1.45; color: #555; background: #f8f9fb; border: 1px solid #e0e4ea; border-radius: 6px; padding: 16px 20px; }
.os-right h3 { font-size: 13px; margin: 0 0 8px; }
.os-right p { margin-bottom: 4px; }

/* Financial Summary */
.summary-page { margin-top: 24px; border: 1px solid #dce3eb; border-radius: 8px; padding: 20px; background: #fff; }
.summary-banner { text-align: center; background: #1B3A5C; color: #fff; padding: 10px 16px; font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; border-radius: 4px; margin-bottom: 16px; }
.summary-two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: start; }
.summary-left { }
.summary-right { }
.summary-table { width: 100%; border-collapse: collapse; margin-bottom: 12px; font-size: 12px; border: 1px solid #dce3eb; }
.summary-table th, .summary-table td { padding: 4px 8px; border-bottom: 1px solid #e8ecf0; }
.summary-header { background: #1B3A5C; color: #fff; padding: 5px 8px !important; font-size: 10px !important; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; }
.summary-table tr.summary td { border-top: 2px solid #1B3A5C; font-weight: 700; background: #f0f4f8; }
.summary-table tr:nth-child(even) { background: #fafbfc; }
.summary-trade-range { text-align: center; margin: 24px auto; padding: 16px 24px; border: 2px solid #1B3A5C; border-radius: 6px; max-width: 480px; }
.summary-trade-label { font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #555; font-weight: 600; margin-bottom: 6px; }
.summary-trade-prices { font-size: 26px; font-weight: 700; color: #1B3A5C; }

/* Price Reveal */
.price-reveal { margin-top: 24px; }

/* Track Record Page 2 */
.tr-page2 { padding: 50px 40px; max-width: 1100px; margin: 0 auto; }

/* Buyer Profile & Objections */
.buyer-split { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; align-items: start; }
.buyer-split-left { }
.buyer-split-right { }
.obj-item { margin-bottom: 16px; }
.obj-q { font-weight: 700; color: #1B3A5C; margin-bottom: 4px; font-size: 14px; }
.obj-a { font-size: 13px; color: #444; line-height: 1.6; }
.bp-closing { font-size: 13px; color: #444; margin-top: 12px; font-style: italic; }
.buyer-photo { width: 100%; height: 220px; border-radius: 8px; overflow: hidden; margin-top: 24px; }
.buyer-photo img { width: 100%; height: 100%; object-fit: cover; }

/* Narrative paragraphs */
.narrative { font-size: 14px; line-height: 1.7; color: #444; margin-bottom: 16px; }

/* Maps */
.leaflet-map { height: 400px; border-radius: 4px; border: 1px solid #ddd; margin-bottom: 30px; z-index: 1; }
.map-fallback { display: none; }
.comp-map-print { display: none; }
.embed-map-wrap { position: relative; width: 100%; margin-bottom: 20px; border-radius: 8px; overflow: hidden; }
.embed-map-wrap iframe { display: block; width: 100%; height: 420px; border: 0; }

/* Misc */
.page-break-marker { height: 4px; background: repeating-linear-gradient(90deg, #ddd 0, #ddd 8px, transparent 8px, transparent 16px); }
.photo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 30px; overflow: hidden; }
.photo-grid img { width: 100%; height: 180px; object-fit: cover; border-radius: 4px; }
.highlight-box { background: #f0f4f8; border: 1px solid #dce3eb; border-radius: 8px; padding: 20px 24px; margin: 24px 0; }
.img-float-right { float: right; width: 48%; margin: 0 0 16px 20px; border-radius: 8px; overflow: hidden; }
.img-float-right img { width: 100%; display: block; }

/* Footer */
.footer { background: #1B3A5C; color: #fff; padding: 50px 40px; text-align: center; }
.footer-logo { width: 180px; margin-bottom: 30px; }
.footer-team { display: flex; justify-content: center; gap: 40px; margin-bottom: 30px; flex-wrap: wrap; }
.footer-person { text-align: center; flex: 1; min-width: 280px; }
.footer-headshot { width: 70px; height: 70px; border-radius: 50%; border: 2px solid #C5A258; object-fit: cover; }
.footer-name { font-size: 16px; font-weight: 600; }
.footer-title { font-size: 12px; color: #C5A258; margin-bottom: 8px; }
.footer-contact { font-size: 12px; color: rgba(255,255,255,0.7); line-height: 1.8; }
.footer-contact a { color: rgba(255,255,255,0.7); text-decoration: none; }
.footer-disclaimer { font-size: 10px; color: rgba(255,255,255,0.35); margin-top: 20px; max-width: 800px; margin-left: auto; margin-right: auto; }
""")

# ============================================================
# MOBILE CSS (verbatim from blueprint)
# ============================================================
html_parts.append("""
@media (max-width: 768px) {
  .cover-content { padding: 30px 20px; }
  .cover-title { font-size: 32px; }
  .cover-logo { width: 220px; }
  .cover-headshots { gap: 24px; }
  .cover-headshot { width: 60px; height: 60px; }
  .section { padding: 30px 16px; }
  .photo-grid { grid-template-columns: 1fr; }
  .two-col, .buyer-split, .inv-split, .os-two-col, .loc-grid { grid-template-columns: 1fr; }
  .metrics-grid, .metrics-grid-4 { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .metric-card { padding: 14px 10px; }
  .metric-value { font-size: 22px; }
  .mkt-channels, .perf-grid { grid-template-columns: 1fr; }
  .summary-two-col, .prop-grid-4 { grid-template-columns: 1fr; }
  .pdf-float-btn { padding: 10px 18px; font-size: 12px; bottom: 16px; right: 16px; }
  .toc-nav { padding: 0 6px; }
  .toc-nav a { font-size: 10px; padding: 10px 6px; letter-spacing: 0.2px; }
  .leaflet-map { height: 300px; }
  .embed-map-wrap iframe { height: 320px; }
  .loc-wide-map { height: 180px; margin-top: 16px; }
  .table-scroll table { min-width: 560px; }
  .bio-grid { grid-template-columns: 1fr; gap: 16px; }
  .bio-headshot { width: 60px; height: 60px; }
  .footer-team { flex-direction: column; align-items: center; }
  .press-strip { gap: 16px; }
  .press-logo { font-size: 11px; }
  .costar-badge-title { font-size: 18px; }
  .img-float-right { float: none; width: 100%; margin: 0 0 16px 0; }
  .inv-photo { height: 240px; }
}
@media (max-width: 420px) {
  .cover-title { font-size: 26px; }
  .cover-stat-value { font-size: 20px; }
  .cover-headshots { gap: 16px; }
  .cover-headshot { width: 50px; height: 50px; }
  .metrics-grid-4 { grid-template-columns: 1fr 1fr; }
  .metric-value { font-size: 18px; }
  .section { padding: 20px 12px; }
}
""")

# ============================================================
# PRINT CSS (verbatim from blueprint)
# ============================================================
html_parts.append("""
@media print {
  @page { size: letter landscape; margin: 0.4in 0.5in; }
  body { font-size: 11px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  p { font-size: 11px; line-height: 1.5; margin-bottom: 8px; }
  .pdf-float-btn, .toc-nav, .leaflet-map, .embed-map-wrap, .page-break-marker, .map-fallback { display: none !important; }
  .cover { min-height: 7.5in; page-break-after: always; }
  .cover-bg { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .cover-headshots { display: flex !important; }
  .cover-headshot { width: 55px; height: 55px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .cover-logo { width: 240px; }
  .section { padding: 20px 0; page-break-before: always; }
  .section-title { font-size: 20px; margin-bottom: 4px; }
  .section-subtitle { font-size: 11px; margin-bottom: 10px; }
  .section-divider { margin-bottom: 16px; }
  .metric-card { padding: 12px 8px; border-radius: 6px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .metric-value { font-size: 20px; }
  .metric-label { font-size: 9px; }
  table { font-size: 11px; }
  th { padding: 6px 8px; font-size: 9px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  td { padding: 5px 8px; }
  tr.highlight { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .tr-tagline { font-size: 15px; padding: 8px 14px; margin-bottom: 8px; }
  .tr-map-print { display: block; width: 100%; height: 240px; border-radius: 4px; overflow: hidden; margin-bottom: 8px; }
  .tr-map-print img { width: 100%; height: 100%; object-fit: cover; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .tr-service-quote { margin: 10px 0; }
  .tr-service-quote h3 { font-size: 13px; margin-bottom: 4px; }
  .tr-service-quote p { font-size: 11px; line-height: 1.45; }
  .tr-page2 .section-title { font-size: 18px; margin-bottom: 2px; }
  .tr-page2 .section-divider { margin-bottom: 8px; }
  .bio-grid { gap: 12px; margin: 8px 0; }
  .bio-card { gap: 10px; }
  .bio-headshot { width: 75px; height: 75px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .bio-text { font-size: 11px; }
  .team-grid { gap: 6px; margin: 8px 0; }
  .team-headshot { width: 45px; height: 45px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .team-card-name { font-size: 11px; }
  .team-card-title { font-size: 9px; }
  .costar-badge { padding: 8px 12px; margin: 8px auto; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .costar-badge-title { font-size: 16px; }
  .condition-note { padding: 8px 14px; margin-top: 8px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .achievements-list { font-size: 11px; line-height: 1.5; }
  .press-strip { padding: 6px 12px; gap: 16px; margin-top: 8px; }
  .press-logo { font-size: 10px; }
  #marketing { page-break-before: always; }
  #marketing .section-title { font-size: 18px; margin-bottom: 2px; }
  #marketing .section-subtitle { font-size: 11px; margin-bottom: 4px; }
  #marketing .section-divider { margin-bottom: 6px; }
  #marketing .metrics-grid-4 { gap: 8px; margin-bottom: 8px; grid-template-columns: repeat(4, 1fr); }
  #marketing .metric-card { padding: 8px 6px; }
  #marketing .metric-value { font-size: 18px; }
  #marketing .metric-label { font-size: 8px; }
  .mkt-quote { padding: 8px 14px; margin: 8px 0; font-size: 11px; line-height: 1.4; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .mkt-channels { gap: 10px; margin-top: 8px; grid-template-columns: 1fr 1fr; }
  .mkt-channel { padding: 8px 12px; border-radius: 6px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .mkt-channel h4 { font-size: 11px; margin-bottom: 4px; }
  .mkt-channel li { font-size: 10px; line-height: 1.4; margin-bottom: 2px; }
  .perf-grid { gap: 10px; margin-top: 8px; grid-template-columns: 1fr 1fr; }
  .perf-card { padding: 8px 12px; border-radius: 6px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .perf-card h4 { font-size: 11px; margin-bottom: 4px; }
  .perf-card li { font-size: 10px; line-height: 1.4; margin-bottom: 2px; }
  .platform-strip { padding: 6px 12px; gap: 12px; margin-top: 8px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .platform-strip-label { font-size: 8px; }
  .platform-strip img { height: 18px; }
  .inv-text p { font-size: 11px; line-height: 1.5; margin-bottom: 6px; }
  .inv-logo { display: none !important; }
  .inv-right { padding-top: 30px; }
  .inv-photo { height: 220px; }
  .inv-photo img { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .inv-highlights { padding: 10px 14px; }
  .inv-highlights h4 { font-size: 11px; margin-bottom: 4px; }
  .inv-highlights li { font-size: 10px; line-height: 1.4; margin-bottom: 2px; }
  .loc-grid { display: grid; grid-template-columns: 58% 42%; gap: 14px; page-break-inside: avoid; }
  .loc-left { max-height: 340px; overflow: hidden; }
  .loc-left p { font-size: 10.5px; line-height: 1.4; margin-bottom: 5px; }
  .loc-right { max-height: 340px; overflow: hidden; }
  .loc-right table { font-size: 10px; }
  .loc-right th { font-size: 9px; padding: 4px 6px; }
  .loc-right td { padding: 4px 6px; font-size: 10px; }
  .loc-wide-map { height: 220px; margin-top: 8px; }
  .loc-wide-map img { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  #prop-details { page-break-before: always; }
  .prop-grid-4 { gap: 12px; }
  .prop-grid-4 table { font-size: 10px; }
  .prop-grid-4 th { font-size: 9px; padding: 4px 6px; }
  .prop-grid-4 td { padding: 4px 6px; font-size: 10px; }
  .os-two-col { page-break-before: always; align-items: stretch; gap: 16px; }
  .os-left table { font-size: 10px; }
  .os-left th { font-size: 9px; padding: 4px 6px; }
  .os-left td { padding: 4px 6px; }
  .os-right { font-size: 9.5px; line-height: 1.3; padding: 10px 12px; }
  .os-right p { margin-bottom: 4px; font-size: 9.5px; }
  .os-right .sub-heading { font-size: 12px; margin-bottom: 6px; }
  .summary-page { page-break-before: always; padding: 12px; }
  .summary-banner { font-size: 12px; padding: 6px 12px; margin-bottom: 10px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .summary-two-col { gap: 12px; }
  .summary-table { font-size: 8px; margin-bottom: 8px; }
  .summary-table td { padding: 2px 4px; }
  .summary-table th { padding: 2px 4px; }
  .summary-header { font-size: 7px !important; padding: 3px 4px !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .obj-q { font-size: 11px; margin-bottom: 2px; }
  .obj-a { font-size: 10px; line-height: 1.4; }
  .obj-item { margin-bottom: 8px; }
  .bp-closing { font-size: 10px; }
  .buyer-photo { height: 180px; }
  .buyer-photo img { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  #sale-comps, #on-market, #rent-comps { page-break-before: always; }
  .comp-narratives p.narrative { font-size: 10.5px; line-height: 1.4; margin-bottom: 6px; page-break-inside: avoid; }
  .comp-narratives p.narrative strong { font-size: 10.5px; }
  .comp-map-print { display: block !important; height: 280px; border-radius: 4px; overflow: hidden; margin-bottom: 10px; }
  .comp-map-print img { width: 100%; height: 100%; object-fit: cover; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .tr-page2 { page-break-before: always; }
  #sfv-track-record { page-break-before: always; }
  .footer { page-break-before: always; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .footer-headshot { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .price-reveal { page-break-before: always; }
  #property-info { page-break-before: always; }

  /* --- Page-break discipline --- */
  p { orphans: 3; widows: 3; }
  table { page-break-inside: avoid; }
  .section-title, .section-subtitle, .section-divider { page-break-after: avoid; }
  .metrics-grid { page-break-inside: avoid; }
  .metric-card { page-break-inside: avoid; }
  .highlight-box { page-break-inside: avoid; }
  .obj-item { page-break-inside: avoid; }
  .bio-card { page-break-inside: avoid; }
  .inv-highlights { page-break-inside: avoid; }
  .photo-grid { page-break-inside: avoid; }
  .prop-grid-4 { page-break-inside: avoid; }
  .loc-grid { page-break-inside: avoid; }
  .feature-item { page-break-inside: avoid; }
  .mkt-channel { page-break-inside: avoid; }
  .perf-card { page-break-inside: avoid; }
  .team-grid { page-break-inside: avoid; }
  .costar-badge { page-break-inside: avoid; }
  .press-strip { page-break-inside: avoid; }
  .summary-two-col { page-break-inside: avoid; }
  #pdfOverlay { display: none !important; }
}
""")

# Close style and head
html_parts.append("</style>\n</head>\n<body>\n")

# ============================================================
# PAGE 1: COVER
# ============================================================
cover_headshots = ""
for agent in COVER_AGENTS:
    cover_headshots += f'''<div class="cover-headshot-wrap">
        <img class="cover-headshot" src="{IMG[agent['img_key']]}" alt="{agent['name']}">
        <div class="cover-headshot-name">{agent['name']}</div>
        <div class="cover-headshot-title">{agent['title']}</div>
    </div>\n'''

html_parts.append(f"""
<div class="cover">
  <div class="cover-bg" style="background-image:url('{IMG["hero"]}');"></div>
  <div class="cover-content">
    <img src="{IMG['logo']}" class="cover-logo" alt="LAAA Team">
    <div class="cover-label">Confidential Broker Opinion of Value</div>
    <div class="cover-title">{ADDRESS}</div>
    <div class="cover-address">{CITY_STATE_ZIP}</div>
    <div class="gold-line" style="width:80px;margin:0 auto 24px;"></div>
    <div class="cover-stats">
      <div class="cover-stat"><span class="cover-stat-value">{UNITS}</span><span class="cover-stat-label">Units</span></div>
      <div class="cover-stat"><span class="cover-stat-value">{SF:,}</span><span class="cover-stat-label">Square Feet</span></div>
      <div class="cover-stat"><span class="cover-stat-value">{YEAR_BUILT}</span><span class="cover-stat-label">Year Built</span></div>
      <div class="cover-stat"><span class="cover-stat-value">{LOT_ACRES:.2f}</span><span class="cover-stat-label">Acres</span></div>
    </div>
    <div class="cover-headshots">
      {cover_headshots}
    </div>
    <p class="client-greeting" id="client-greeting">Prepared Exclusively for {CLIENT_NAME}</p>
    <p style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:8px;">{COVER_MONTH_YEAR}</p>
  </div>
</div>
""")

# ============================================================
# TOC NAV
# ============================================================
toc_links = '<a href="#track-record">Track Record</a>'
toc_links += '<a href="#sfv-track-record">SFV Record</a>'
toc_links += '<a href="#marketing">Marketing</a>'
toc_links += '<a href="#investment">Investment</a>'
toc_links += '<a href="#location">Location</a>'
toc_links += '<a href="#prop-details">Property</a>'
toc_links += '<a href="#property-info">Buyer Profile</a>'
toc_links += '<a href="#sale-comps">Sale Comps</a>'
if INCLUDE_ON_MARKET_COMPS:
    toc_links += '<a href="#on-market">On-Market</a>'
toc_links += '<a href="#rent-comps">Rent Comps</a>'
toc_links += '<a href="#financials">Financials</a>'
toc_links += '<a href="#contact">Contact</a>'

html_parts.append(f'<nav class="toc-nav" id="toc-nav">{toc_links}</nav>\n')

# ============================================================
# PAGE 2: TRACK RECORD P1
# ============================================================
html_parts.append(f"""
<div class="section section-alt" id="track-record">
  <div class="section-title">Team Track Record</div>
  <div class="section-subtitle">LA Apartment Advisors at Marcus &amp; Millichap</div>
  <div class="section-divider"></div>
  <div class="tr-tagline">
    <span style="display:block;font-size:1.2em;font-weight:700;margin-bottom:4px;">LAAA Team of Marcus &amp; Millichap</span>
    Expertise, Execution, Excellence.
  </div>
  <div class="metrics-grid-4">
    <div class="metric-card"><span class="metric-value">456</span><span class="metric-label">Closed Transactions</span></div>
    <div class="metric-card"><span class="metric-value">$1.45B</span><span class="metric-label">Total Sales Volume</span></div>
    <div class="metric-card"><span class="metric-value">4,170+</span><span class="metric-label">Units Sold</span></div>
    <div class="metric-card"><span class="metric-value">34</span><span class="metric-label">Median DOM</span></div>
  </div>
  <div class="embed-map-wrap">
    <iframe src="https://www.google.com/maps/d/embed?mid=1ewCjzE3QX9p6m2MqK-md8b6fZitfIzU&ehbc=2E312F&noprof=1" loading="lazy" allowfullscreen></iframe>
  </div>
  <div class="tr-map-print"><img src="{IMG['closings_map']}" alt="LAAA Closings Map"></div>
  <div class="tr-service-quote">
    <h3>"We Didn't Invent Great Service, We Just Work Relentlessly to Provide It."</h3>
    <p>{MISSION_P1}</p>
    <p>{MISSION_P2}</p>
    <p>{MISSION_P3}</p>
  </div>
</div>
""")

# ============================================================
# PAGE 3: TRACK RECORD P2 (Our Team)
# ============================================================
# Team grid — all members except Glen and Filip (who get bio cards)
team_members = [
    ("Aida Memary Scher", "Senior Associate", "team_aida"),
    ("Morgan Wetmore", "Associate", "team_morgan"),
    ("Luka Leader", "Associate", "team_luka"),
    ("Logan Ward", "Associate", "team_logan"),
    ("Alexandro Tapia", "Associate Investments", "team_alexandro"),
    ("Blake Lewitt", "Associate Investments", "team_blake"),
    ("Mike Palade", "Agent Assistant", "team_mike"),
    ("Tony H. Dang", "Business Operations Manager", "team_tony"),
]

team_grid_html = ""
for name, title, img_key in team_members:
    team_grid_html += f'''<div class="team-card">
      <img class="team-headshot" src="{IMG[img_key]}" alt="{name}">
      <div class="team-card-name">{name}</div>
      <div class="team-card-title">{title}</div>
    </div>\n'''

# Glen and Filip bios — DEAL-SPECIFIC (update from team_bios.md)
GLEN_BIO = "Glen Scher is a Senior Managing Director at Marcus &amp; Millichap and co-founder of the LAAA Team, one of Southern California's most active multifamily brokerage groups. A UC Santa Barbara graduate in Economics, Glen launched his career in 2014 and earned Rookie of the Year from the SFV Business Journal by 2016. A former Division I golfer, he captured three collegiate titles and was named UCSB Male Athlete of the Year. Glen has closed over 450 transactions totaling $1.4B+."
FILIP_BIO = "Filip Niculete is a Senior Managing Director at Marcus &amp; Millichap and co-founder of the LAAA Team. Born in Romania and raised in the San Fernando Valley, Filip studied Finance at San Diego State University and began his career at Marcus &amp; Millichap in 2011. Known for execution, integrity, and relentless work ethic, Filip and the LAAA Team have closed over $1.4B in transactions and consistently lead the market in active inventory across the San Fernando Valley."

html_parts.append(f"""
<div class="tr-page2">
  <div style="text-align:center;margin-bottom:8px;">
    <div class="section-title" style="margin-bottom:4px;">Our Team</div>
    <div class="section-divider" style="margin:0 auto 12px;"></div>
  </div>
  <div class="costar-badge" style="margin-top:4px;margin-bottom:8px;">
    <div class="costar-badge-title">#1 Most Active Multifamily Sales Team in LA County</div>
    <div class="costar-badge-sub">CoStar &bull; 2019, 2020, 2021 &bull; #4 in California</div>
  </div>
  <div class="bio-grid">
    <div class="bio-card">
      <img class="bio-headshot" src="{IMG['glen']}" alt="Glen Scher">
      <div>
        <div class="bio-name">Glen Scher</div>
        <div class="bio-title">Senior Managing Director</div>
        <div class="bio-text">{GLEN_BIO}</div>
      </div>
    </div>
    <div class="bio-card">
      <img class="bio-headshot" src="{IMG['filip']}" alt="Filip Niculete">
      <div>
        <div class="bio-name">Filip Niculete</div>
        <div class="bio-title">Senior Managing Director</div>
        <div class="bio-text">{FILIP_BIO}</div>
      </div>
    </div>
  </div>
  <div class="team-grid">
    {team_grid_html}
  </div>
  <div class="condition-note" style="margin-top:20px;">
    <div class="condition-note-label">Key Achievements</div>
    <p class="achievements-list">
      &bull; <strong>Chairman's Club</strong> - a top-tier annual honor at Marcus &amp; Millichap<br>
      &bull; <strong>National Achievement Award</strong> - Consistent top national performer<br>
      &bull; <strong>CoStar #1 Team</strong> - Most active multifamily sales team in LA County<br>
      &bull; <strong>456 Transactions</strong> - Over $1.45 billion in career sales volume<br>
      &bull; <strong>34-Day Median DOM</strong> - Properties sell faster than market average
    </p>
  </div>
  <div class="press-strip">
    <span class="press-strip-label">As Featured In</span>
    <span class="press-logo">BISNOW</span>
    <span class="press-logo">YAHOO FINANCE</span>
    <span class="press-logo">CONNECT CRE</span>
    <span class="press-logo">SFVBJ</span>
    <span class="press-logo">THE PINNACLE LIST</span>
  </div>
</div>
""")

# ============================================================
# SFV TRACK RECORD (Berkus Portfolio specific)
# ============================================================
sfv_closings = [
    {"date": "5/2025", "addr": "6716 Sylmar Ave", "city": "Van Nuys", "units": 12, "price": 3500000, "ppu": 291667, "note": "LAAA Sale Comp", "highlight": True},
    {"date": "9/2025", "addr": "5917 Buffalo Ave", "city": "Van Nuys", "units": 5, "price": 1645000, "ppu": 329000, "note": "", "highlight": False},
    {"date": "12/2024", "addr": "6228 Fulton Ave", "city": "Van Nuys", "units": 30, "price": 8740000, "ppu": 291333, "note": "On Fulton Ave", "highlight": True},
    {"date": "10/2024", "addr": "11616 Burbank Blvd", "city": "North Hollywood", "units": 21, "price": 9627750, "ppu": 458464, "note": "", "highlight": False},
    {"date": "10/2024", "addr": "5630 Fair Ave", "city": "North Hollywood", "units": 15, "price": 7625000, "ppu": 508333, "note": "", "highlight": False},
    {"date": "4/2024", "addr": "7303 Woodley Ave", "city": "Van Nuys", "units": 5, "price": 950000, "ppu": 190000, "note": "On Woodley Ave", "highlight": True},
    {"date": "4/2022", "addr": "4838 Hazeltine Ave", "city": "Sherman Oaks", "units": 16, "price": 6100000, "ppu": 381250, "note": "", "highlight": False},
    {"date": "12/2021", "addr": "15716 Saticoy St", "city": "Van Nuys", "units": 42, "price": 14200000, "ppu": 338095, "note": "", "highlight": False},
    {"date": "10/2021", "addr": "13210 Victory Blvd", "city": "Van Nuys", "units": 30, "price": 5635000, "ppu": 187833, "note": "", "highlight": False},
    {"date": "2/2020", "addr": "14837 Delano St", "city": "Van Nuys", "units": 8, "price": 1762500, "ppu": 220312, "note": "", "highlight": False},
    {"date": "3/2018", "addr": "6551 Woodley Ave", "city": "Van Nuys", "units": 7, "price": 1660000, "ppu": 237143, "note": "On Woodley, 7 units", "highlight": True},
    {"date": "9/2017", "addr": "6551 Woodley Ave", "city": "Van Nuys", "units": 7, "price": 1300000, "ppu": 185714, "note": "Same bldg, prior sale", "highlight": True},
    {"date": "10/2017", "addr": "7453 Haskell Ave", "city": "Van Nuys", "units": 10, "price": 2253000, "ppu": 225300, "note": "", "highlight": False},
    {"date": "8/2018", "addr": "4522 Murietta Ave", "city": "Van Nuys", "units": 13, "price": 3500000, "ppu": 269231, "note": "", "highlight": False},
]

sfv_rows = ""
for c in sfv_closings:
    hl = ' class="highlight"' if c["highlight"] else ""
    note_badge = ' <span style="background:#C5A258;color:#fff;font-size:10px;padding:1px 6px;border-radius:3px;margin-left:4px;">LAAA COMP</span>' if "Sale Comp" in c.get("note","") else ""
    sfv_rows += f'''<tr{hl}>
      <td>{c["date"]}</td>
      <td>{c["addr"]}{note_badge}</td>
      <td>{c["city"]}</td>
      <td class="num">{c["units"]}</td>
      <td class="num">${c["price"]:,.0f}</td>
      <td class="num">${c["ppu"]:,.0f}</td>
      <td style="font-size:11px;color:#666;">{c["note"]}</td>
    </tr>\n'''

html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="sfv-track-record">
  <div class="section-title">Our Track Record in the San Fernando Valley</div>
  <div class="section-subtitle">Exposed and Closed More Multifamily Deals Than Any Team in the Valley</div>
  <div class="section-divider"></div>
  <div class="metrics-grid-4">
    <div class="metric-card"><span class="metric-value">93</span><span class="metric-label">SFV Apartment Closings</span></div>
    <div class="metric-card"><span class="metric-value">$335M+</span><span class="metric-label">SFV Sales Volume</span></div>
    <div class="metric-card"><span class="metric-value">32</span><span class="metric-label">Van Nuys Closings</span></div>
    <div class="metric-card"><span class="metric-value">$107.7M</span><span class="metric-label">Van Nuys Volume</span></div>
  </div>
  <div class="table-scroll" style="margin-top:20px;">
    <table style="font-size:12px;">
      <thead><tr>
        <th>Date</th><th>Address</th><th>City</th>
        <th class="num">Units</th><th class="num">Close Price</th>
        <th class="num">$/Unit</th><th>Notes</th>
      </tr></thead>
      <tbody>
        {sfv_rows}
      </tbody>
    </table>
  </div>
  <p style="font-size:11px;color:#888;text-align:center;margin-top:12px;">Selected closings shown. Full track record available upon request.</p>
</div>
""")

# ============================================================
# PAGE 4: MARKETING & RESULTS (standard — same for every BOV)
# ============================================================
html_parts.append("""
<div class="page-break-marker"></div>
<div class="section" id="marketing">
  <div class="section-title">Our Marketing Approach &amp; Results</div>
  <div class="section-subtitle">Data-Driven Marketing + Proven Performance</div>
  <div class="section-divider"></div>
  <div class="metrics-grid-4">
    <div class="metric-card"><span class="metric-value">30K+</span><span class="metric-label">Targeted Emails</span></div>
    <div class="metric-card"><span class="metric-value">10K+</span><span class="metric-label">Listing Views</span></div>
    <div class="metric-card"><span class="metric-value">3.7</span><span class="metric-label">Avg Offers / Listing</span></div>
    <div class="metric-card"><span class="metric-value">18</span><span class="metric-label">Avg Days to Escrow</span></div>
  </div>
  <div class="mkt-quote">"We are PROACTIVE marketers, not reactive. Every listing gets a custom campaign designed to maximize exposure, create urgency, and drive competitive offers."</div>
  <div class="mkt-channels">
    <div class="mkt-channel"><h4>Direct Phone Outreach</h4><ul>
      <li>500+ targeted calls per listing</li>
      <li>Focus: active buyers in submarket</li>
      <li>Personal follow-up within 48 hours</li>
    </ul></div>
    <div class="mkt-channel"><h4>Email Campaigns</h4><ul>
      <li>30,000+ qualified investor contacts</li>
      <li>Segmented by geography and deal size</li>
      <li>Multi-touch drip campaigns</li>
    </ul></div>
    <div class="mkt-channel"><h4>Online Platforms</h4><ul>
      <li>MarcusMillichap.com, CoStar, Crexi</li>
      <li>LoopNet, CREXi, Ten-X</li>
      <li>Custom property websites</li>
    </ul></div>
    <div class="mkt-channel"><h4>Additional Channels</h4><ul>
      <li>Office-wide agent blast (100+ agents)</li>
      <li>Industry networking events</li>
      <li>Strategic broker co-marketing</li>
    </ul></div>
  </div>
  <div class="metrics-grid-4" style="margin-top:16px;">
    <div class="metric-card"><span class="metric-value">97.6%</span><span class="metric-label">Avg SP/LP Ratio</span></div>
    <div class="metric-card"><span class="metric-value">21%</span><span class="metric-label">Sold Above Ask</span></div>
    <div class="metric-card"><span class="metric-value">10</span><span class="metric-label">Avg Day Contingency</span></div>
    <div class="metric-card"><span class="metric-value">61%</span><span class="metric-label">1031 Exchange Buyers</span></div>
  </div>
  <div class="perf-grid">
    <div class="perf-card"><h4>Pricing Accuracy</h4><ul>
      <li>97.6% average sale-to-list ratio</li>
      <li>21% of listings sold above asking</li>
      <li>Data-driven comp analysis</li>
    </ul></div>
    <div class="perf-card"><h4>Marketing Speed</h4><ul>
      <li>18 average days to accepted offer</li>
      <li>34-day median days on market</li>
      <li>Strategic pricing drives urgency</li>
    </ul></div>
    <div class="perf-card"><h4>Contract Strength</h4><ul>
      <li>10-day average contingency period</li>
      <li>Pre-qualified buyer verification</li>
      <li>Streamlined due diligence process</li>
      <li>98% close rate on accepted offers</li>
    </ul></div>
    <div class="perf-card"><h4>Exchange Expertise</h4><ul>
      <li>61% of buyers are 1031 exchangers</li>
      <li>Dedicated exchange buyer database</li>
      <li>Timeline management expertise</li>
      <li>85% higher cash flow for exchangers</li>
    </ul></div>
  </div>
  <div class="platform-strip">
    <span class="platform-strip-label">Advertised On</span>
    <span class="platform-name">CREXI</span>
    <span class="platform-name">COSTAR</span>
    <span class="platform-name">LOOPNET</span>
    <span class="platform-name">ZILLOW</span>
    <span class="platform-name">REALTOR</span>
    <span class="platform-name">M&amp;M</span>
    <span class="platform-name">APARTMENTS.COM</span>
    <span class="platform-name">REDFIN</span>
    <span class="platform-name">TEN-X</span>
  </div>
</div>
""")

# ============================================================
# PAGE 5: INVESTMENT OVERVIEW
# ============================================================
highlights_html = ""
for bold, text in HIGHLIGHTS:
    highlights_html += f'<li><strong>{bold}</strong> - {text}</li>\n'

html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="investment">
  <div class="section-title">Investment Overview</div>
  <div class="section-subtitle">{SUBMARKET} - {ADDRESS}</div>
  <div class="section-divider"></div>
  <div class="inv-split">
    <div class="inv-left">
      <div class="metrics-grid-4">
        <div class="metric-card"><span class="metric-value">{UNITS}</span><span class="metric-label">Units</span></div>
        <div class="metric-card"><span class="metric-value">{SF:,}</span><span class="metric-label">Square Feet</span></div>
        <div class="metric-card"><span class="metric-value">{LOT_ACRES:.2f}</span><span class="metric-label">Lot Acres</span></div>
        <div class="metric-card"><span class="metric-value">{YEAR_BUILT}</span><span class="metric-label">Year Built</span></div>
      </div>
      <div class="inv-text">
        <p>{INVESTMENT_OVERVIEW_P1}</p>
        <p>{INVESTMENT_OVERVIEW_P2}</p>
        <p>{INVESTMENT_OVERVIEW_P3}</p>
      </div>
    </div>
    <div class="inv-right">
      <div class="inv-photo"><img src="{IMG['grid1']}" alt="Property"></div>
      <div class="inv-highlights">
        <h4>Investment Highlights</h4>
        <ul>
          {highlights_html}
        </ul>
      </div>
    </div>
  </div>
</div>
""")

# ============================================================
# PAGE 6: LOCATION OVERVIEW
# ============================================================
loc_table_rows = ""
for label, value in LOCATION_TABLE_ROWS:
    loc_table_rows += f'<tr><td>{label}</td><td>{value}</td></tr>\n'

html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="location">
  <div class="section-title">Location Overview</div>
  <div class="section-subtitle">{SUBMARKET} - {CITY_STATE_ZIP.split(",")[1].strip() if "," in CITY_STATE_ZIP else CITY_STATE_ZIP}</div>
  <div class="section-divider"></div>
  <div class="loc-grid">
    <div class="loc-left">
      <p>{LOCATION_P1}</p>
      <p>{LOCATION_P2}</p>
      <p>{LOCATION_P3}</p>
    </div>
    <div class="loc-right">
      <table class="info-table">
        <thead><tr><th colspan="2">Location Details</th></tr></thead>
        <tbody>
          {loc_table_rows}
        </tbody>
      </table>
    </div>
  </div>
  <div class="loc-wide-map"><img src="{IMG['loc_map']}" alt="Location Map"></div>
</div>
""")

# ============================================================
# PAGE 7: PROPERTY DETAILS
# ============================================================
def build_info_table(title, rows, colspan=2):
    html = f'<table class="info-table"><thead><tr><th colspan="{colspan}">{title}</th></tr></thead><tbody>\n'
    for row in rows:
        if len(row) == 2:
            html += f'<tr><td>{row[0]}</td><td>{row[1]}</td></tr>\n'
        elif len(row) == 3:
            html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>\n'
    html += '</tbody></table>\n'
    return html

html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="prop-details">
  <div class="section-title">Property Details</div>
  <div class="section-subtitle">{FULL_ADDRESS}</div>
  <div class="section-divider"></div>
  <div class="prop-grid-4">
    <div>{build_info_table("Property Overview", PROP_OVERVIEW)}</div>
    <div>{build_info_table("Site &amp; Zoning", PROP_SITE_ZONING)}</div>
    <div>{build_info_table("Building Systems &amp; Capital Improvements", PROP_BUILDING, 3)}</div>
    <div>{build_info_table("Regulatory &amp; Compliance", PROP_REGULATORY)}</div>
  </div>
</div>
""")

# ============================================================
# OPTIONAL: TRANSACTION HISTORY
# ============================================================
if INCLUDE_TRANSACTION_HISTORY and TRANSACTION_ROWS:
    tx_rows_html = ""
    for tx in TRANSACTION_ROWS:
        tx_rows_html += f'<tr><td>{tx.get("date","")}</td><td>{tx.get("parties","")}</td><td class="num">{fc(tx.get("price",0))}</td><td class="num">{fc(tx.get("ppu",0))}</td><td class="num">{fc(tx.get("psf",0))}</td><td>{tx.get("notes","")}</td></tr>\n'
    html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="transactions">
  <div class="section-title">Transaction History</div>
  <div class="section-subtitle">Ownership &amp; Sale Record</div>
  <div class="section-divider"></div>
  <div class="table-scroll"><table>
    <thead><tr><th>Date</th><th>Grantor / Grantee</th><th class="num">Sale Price</th><th class="num">$/Unit</th><th class="num">$/SF</th><th>Notes</th></tr></thead>
    <tbody>{tx_rows_html}</tbody>
  </table></div>
  <p>{TRANSACTION_NARRATIVE}</p>
</div>
""")

# ============================================================
# PAGE 8: BUYER PROFILE & OBJECTIONS
# ============================================================
buyer_types_html = ""
for btype, desc in BUYER_TYPES:
    buyer_types_html += f'''<div class="obj-item">
        <p class="obj-q">{btype}</p>
        <p class="obj-a">{desc}</p>
    </div>\n'''

buyer_obj_html = ""
for question, answer in BUYER_OBJECTIONS:
    buyer_obj_html += f'''<div class="obj-item">
        <p class="obj-q">"{question}"</p>
        <p class="obj-a">{answer}</p>
    </div>\n'''

html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="property-info">
  <div class="section-title">Buyer Profile &amp; Anticipated Objections</div>
  <div class="section-subtitle">Target Investors &amp; Data-Backed Responses</div>
  <div class="section-divider"></div>
  <div class="buyer-split">
    <div class="buyer-split-left">
      <h3 class="sub-heading">Target Buyer Profile</h3>
      {buyer_types_html}
      <p class="bp-closing">{BUYER_CLOSING}</p>
    </div>
    <div class="buyer-split-right">
      <h3 class="sub-heading">Anticipated Buyer Objections</h3>
      {buyer_obj_html}
    </div>
  </div>
  <div class="buyer-photo"><img src="{IMG['buyer_photo']}" alt="Property"></div>
</div>
""")

# ============================================================
# PAGES 9-11: COMP SECTIONS
# ============================================================

# Sale Comps
html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="sale-comps">
  <div class="section-title">Comparable Sales</div>
  <div class="section-subtitle">Closed Multifamily Transactions</div>
  <div class="section-divider"></div>
  <div class="leaflet-map" id="saleMap"></div>
  <div class="comp-map-print"><img src="{IMG['sale_map_static']}" alt="Sale Comps Map"></div>
  <div class="table-scroll"><table>
    <thead><tr><th>#</th><th>Address</th><th class="num">Units</th><th>Year</th><th class="num">SF</th><th class="num">Price</th><th class="num">$/Unit</th><th class="num">$/SF</th><th class="num">Cap</th><th class="num">GRM</th><th>Date</th><th class="num">DOM</th></tr></thead>
    <tbody>{sale_comp_html}</tbody>
  </table></div>
  <div class="comp-narratives">
    {COMP_NARRATIVES}
  </div>
</div>
""")

# On-Market Comps (conditional)
if INCLUDE_ON_MARKET_COMPS:
    html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="on-market">
  <div class="section-title">On-Market Comparables</div>
  <div class="section-subtitle">Active Multifamily Listings</div>
  <div class="section-divider"></div>
  <div class="leaflet-map" id="activeMap"></div>
  <div class="comp-map-print"><img src="{IMG.get('active_map_static', '')}" alt="On-Market Comps Map"></div>
  <div class="table-scroll"><table>
    <thead><tr><th>#</th><th>Address</th><th class="num">Units</th><th>Year</th><th class="num">SF</th><th class="num">Price</th><th class="num">$/Unit</th><th class="num">$/SF</th><th class="num">DOM</th><th>Notes</th></tr></thead>
    <tbody>{on_market_html}</tbody>
  </table></div>
  <p>{ON_MARKET_NARRATIVE}</p>
</div>
""")

# Rent Comps
html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="rent-comps">
  <div class="section-title">Rent Comparables</div>
  <div class="section-subtitle">Active Rental Listings in Submarket</div>
  <div class="section-divider"></div>
  <div class="leaflet-map" id="rentMap"></div>
  <div class="comp-map-print"><img src="{IMG['rent_map_static']}" alt="Rent Comps Map"></div>
  <div class="table-scroll"><table>
    <thead><tr><th>#</th><th>Address</th><th>Type</th><th class="num">SF</th><th class="num">Rent</th><th class="num">$/SF</th><th>Source</th></tr></thead>
    <tbody>{rent_comp_html}</tbody>
  </table></div>
</div>
""")

# ============================================================
# PAGE 12: FINANCIAL ANALYSIS — RENT ROLL
# ============================================================
if PROPERTY_TYPE == "value-add":
    rr_header = '<thead><tr><th>Unit</th><th>Type</th><th class="num">SF</th><th class="num">Current Rent</th><th class="num">Rent/SF</th><th class="num">Market Rent</th><th class="num">Market/SF</th></tr></thead>'
else:
    rr_header = '<thead><tr><th>Unit</th><th>Type</th><th class="num">SF</th><th class="num">Rent/Mo</th><th class="num">Rent/SF</th><th>Status</th><th>Notes</th></tr></thead>'

html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="financials">
  <div class="section-title">Financial Analysis</div>
  <div class="section-subtitle">Investment Underwriting</div>
  <div class="section-divider"></div>
  <h3 class="sub-heading">Unit Mix &amp; Rent Roll</h3>
  <div class="table-scroll"><table>
    {rr_header}
    <tbody>{rent_roll_html}</tbody>
  </table></div>
""")

# ============================================================
# PAGE 13: OPERATING STATEMENT + NOTES
# ============================================================
html_parts.append(f"""
  <div class="os-two-col">
    <div class="os-left">
      <h3 class="sub-heading">Operating Statement</h3>
      <table>
        <thead><tr><th>Income</th><th class="num">Annual</th><th class="num">Per Unit</th><th class="num">$/SF</th><th class="num">% EGI</th></tr></thead>
        <tbody>{os_income_html}</tbody>
      </table>
      <table>
        <thead><tr><th>Expenses</th><th class="num">Annual</th><th class="num">Per Unit</th><th class="num">$/SF</th><th class="num">% EGI</th></tr></thead>
        <tbody>{os_expense_html}</tbody>
      </table>
    </div>
    <div class="os-right">
      <h3 class="sub-heading">Notes to Operating Statement</h3>
      {os_notes_html}
    </div>
  </div>
""")

# ============================================================
# PAGE 14: FINANCIAL SUMMARY
# ============================================================
m = AT_LIST
down_pct = m["down_payment"] / m["price"] * 100 if m["price"] > 0 else 0

if PROPERTY_TYPE == "value-add":
    returns_label_1, returns_label_2 = "Current", "Pro Forma"
else:
    returns_label_1, returns_label_2 = "Reassessed", ""

html_parts.append(f"""
  <div class="summary-page">
    <div class="summary-banner">Summary</div>
    <div class="summary-two-col">
      <div class="summary-left">
        <table class="summary-table">
          <thead><tr><th colspan="2" class="summary-header">OPERATING DATA</th></tr></thead>
          <tbody>
            <tr><td>Price</td><td class="num">${LIST_PRICE:,}</td></tr>
            <tr><td>Down Payment ({down_pct:.0f}%)</td><td class="num">${m['down_payment']:,.0f}</td></tr>
            <tr><td>Number of Units</td><td class="num">{UNITS}</td></tr>
            <tr><td>Price / Unit</td><td class="num">${m['per_unit']:,.0f}</td></tr>
            <tr><td>Price / SF</td><td class="num">${m['per_sf']:,.0f}</td></tr>
            <tr><td>Gross SF</td><td class="num">{SF:,}</td></tr>
            <tr><td>Lot Size</td><td class="num">{LOT_SF:,} SF ({LOT_ACRES:.2f} ac)</td></tr>
            <tr><td>Year Built</td><td class="num">{YEAR_BUILT}</td></tr>
          </tbody>
        </table>
        <table class="summary-table">
          <thead><tr><th class="summary-header">Returns</th><th class="summary-header num">{returns_label_1}</th>{"<th class='summary-header num'>" + returns_label_2 + "</th>" if returns_label_2 else ""}</tr></thead>
          <tbody>
            <tr><td>Cap Rate</td><td class="num">{m['cur_cap']:.2f}%</td>{"<td class='num'>" + f"{m['pf_cap']:.2f}%" + "</td>" if returns_label_2 else ""}</tr>
            <tr><td>GRM</td><td class="num">{m['grm']:.2f}x</td>{"<td class='num'>" + f"{m['pf_grm']:.2f}x" + "</td>" if returns_label_2 else ""}</tr>
            <tr><td>Cash-on-Cash</td><td class="num">{m['coc_cur']:.2f}%</td>{"<td class='num'>" + f"{m['coc_pf']:.2f}%" + "</td>" if returns_label_2 else ""}</tr>
            <tr><td>DSCR</td><td class="num">{m['dcr_cur']:.2f}x</td>{"<td class='num'>" + f"{m['dcr_pf']:.2f}x" + "</td>" if returns_label_2 else ""}</tr>
          </tbody>
        </table>
        <table class="summary-table">
          <thead><tr><th colspan="2" class="summary-header">FINANCING</th></tr></thead>
          <tbody>
            <tr><td>Loan Amount</td><td class="num">${m['loan_amount']:,.0f}</td></tr>
            <tr><td>Loan Type</td><td class="num">Fixed</td></tr>
            <tr><td>Interest Rate</td><td class="num">{INTEREST_RATE*100:.2f}%</td></tr>
            <tr><td>Amortization</td><td class="num">{AMORTIZATION_YEARS} Years</td></tr>
            <tr><td>Loan Constant</td><td class="num">{LOAN_CONSTANT*100:.2f}%</td></tr>
            <tr><td>LTV ({m['loan_constraint']})</td><td class="num">{m['actual_ltv']*100:.1f}%</td></tr>
            <tr><td>DSCR</td><td class="num">{m['dcr_cur']:.2f}x</td></tr>
          </tbody>
        </table>
      </div>
      <div class="summary-right">
        <table class="summary-table">
          <thead><tr><th class="summary-header">Income</th><th class="summary-header num">{returns_label_1}</th>{"<th class='summary-header num'>" + returns_label_2 + "</th>" if returns_label_2 else ""}</tr></thead>
          <tbody>
            <tr><td>GSR</td><td class="num">${GSR:,}</td>{"<td class='num'>$" + f"{PF_GSR:,}" + "</td>" if returns_label_2 else ""}</tr>
            <tr><td>Vacancy ({VACANCY_PCT*100:.0f}%)</td><td class="num">$({GSR*VACANCY_PCT:,.0f})</td>{"<td class='num'>$(" + f"{PF_GSR*VACANCY_PCT:,.0f}" + ")</td>" if returns_label_2 else ""}</tr>
            <tr><td>Other Income</td><td class="num">${OTHER_INCOME:,}</td>{"<td class='num'>$" + f"{OTHER_INCOME:,}" + "</td>" if returns_label_2 else ""}</tr>
            <tr class="summary"><td><strong>EGI</strong></td><td class="num"><strong>${m['cur_egi']:,.0f}</strong></td>{"<td class='num'><strong>$" + f"{m['pf_egi']:,.0f}" + "</strong></td>" if returns_label_2 else ""}</tr>
          </tbody>
        </table>
        <table class="summary-table">
          <thead><tr><th class="summary-header">Cash Flow</th><th class="summary-header num">{returns_label_1}</th>{"<th class='summary-header num'>" + returns_label_2 + "</th>" if returns_label_2 else ""}</tr></thead>
          <tbody>
            <tr><td>NOI</td><td class="num">${m['cur_noi']:,.0f}</td>{"<td class='num'>$" + f"{m['pf_noi']:,.0f}" + "</td>" if returns_label_2 else ""}</tr>
            <tr><td>Debt Service</td><td class="num">$({m['debt_service']:,.0f})</td>{"<td class='num'>$(" + f"{m['debt_service']:,.0f}" + ")</td>" if returns_label_2 else ""}</tr>
            <tr class="summary"><td><strong>Net Cash Flow</strong></td><td class="num"><strong>${m['net_cf_cur']:,.0f}</strong></td>{"<td class='num'><strong>$" + f"{m['net_cf_pf']:,.0f}" + "</strong></td>" if returns_label_2 else ""}</tr>
            <tr><td>CoC Return</td><td class="num">{m['coc_cur']:.2f}%</td>{"<td class='num'>" + f"{m['coc_pf']:.2f}%" + "</td>" if returns_label_2 else ""}</tr>
            <tr><td>Principal Reduction</td><td class="num">${m['prin_red']:,.0f}</td>{"<td class='num'>$" + f"{m['prin_red']:,.0f}" + "</td>" if returns_label_2 else ""}</tr>
            <tr class="summary"><td><strong>Total Return</strong></td><td class="num"><strong>{m['total_return_pct_cur']:.2f}%</strong></td>{"<td class='num'><strong>" + f"{m['total_return_pct_pf']:.2f}%" + "</strong></td>" if returns_label_2 else ""}</tr>
          </tbody>
        </table>
        <table class="summary-table">
          <thead><tr><th colspan="2" class="summary-header">EXPENSES</th></tr></thead>
          <tbody>
            {sum_expense_html}
            <tr class="summary"><td><strong>Total Expenses</strong></td><td class="num"><strong>${total_exp_calc:,.0f}</strong></td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
""")

# ============================================================
# PAGE 15: PRICE REVEAL + PRICING MATRIX
# ============================================================
if PROPERTY_TYPE == "value-add":
    matrix_header = '<thead><tr><th class="num">Purchase Price</th><th class="num">Current Cap</th><th class="num">Pro Forma Cap</th><th class="num">Cash-on-Cash</th><th class="num">$/SF</th><th class="num">$/Unit</th><th class="num">PF GRM</th></tr></thead>'
else:
    matrix_header = '<thead><tr><th class="num">Purchase Price</th><th class="num">Cap Rate</th><th class="num">Cash-on-Cash</th><th class="num">$/Unit</th><th class="num">$/SF</th><th class="num">GRM</th><th class="num">DSCR</th></tr></thead>'

html_parts.append(f"""
  <div class="price-reveal">
    <div style="text-align:center;margin-bottom:32px;">
      <div style="font-size:13px;text-transform:uppercase;letter-spacing:2px;color:#C5A258;font-weight:600;margin-bottom:8px;">Suggested List Price</div>
      <div style="font-size:56px;font-weight:700;color:#1B3A5C;line-height:1;">${LIST_PRICE:,}</div>
    </div>
    <div class="metrics-grid metrics-grid-4">
      <div class="metric-card"><span class="metric-value">${m['per_unit']:,.0f}</span><span class="metric-label">Price / Unit</span></div>
      <div class="metric-card"><span class="metric-value">${m['per_sf']:,.0f}</span><span class="metric-label">Price / SF</span></div>
      <div class="metric-card"><span class="metric-value">{m['cur_cap']:.2f}%</span><span class="metric-label">Current Cap Rate</span></div>
      <div class="metric-card"><span class="metric-value">{m['grm']:.2f}x</span><span class="metric-label">Current GRM</span></div>
    </div>
    <h3 class="sub-heading">Pricing Matrix</h3>
    <div class="table-scroll"><table>
      {matrix_header}
      <tbody>{matrix_html}</tbody>
    </table></div>
    <div class="summary-trade-range">
      <div class="summary-trade-label">A TRADE PRICE IN THE CURRENT INVESTMENT ENVIRONMENT OF</div>
      <div class="summary-trade-prices">${TRADE_RANGE_LOW:,} &mdash; ${TRADE_RANGE_HIGH:,}</div>
    </div>
    <h3 class="sub-heading">Pricing Rationale</h3>
    <!-- Confidence badge removed -->
    <p>{PRICING_RATIONALE}</p>
    <div class="condition-note"><strong>Assumptions &amp; Conditions:</strong> {ASSUMPTIONS_DISCLAIMER}</div>
  </div>
</div>
""")

# ============================================================
# PAGE 16: FOOTER
# ============================================================
footer_agents_html = ""
for agent in FOOTER_AGENTS:
    footer_agents_html += f'''<div class="footer-person">
      <img src="{IMG[agent['img_key']]}" class="footer-headshot" alt="{agent['name']}">
      <div class="footer-name">{agent['name']}</div>
      <div class="footer-title">{agent['title']}</div>
      <div class="footer-contact">
        <a href="tel:{agent['phone']}">{agent['phone']}</a><br>
        <a href="mailto:{agent['email']}">{agent['email']}</a><br>
        CA License: {agent['license']}
      </div>
    </div>\n'''

html_parts.append(f"""
<div class="footer" id="contact">
  <img src="{IMG['logo']}" class="footer-logo" alt="LAAA Team">
  <div class="footer-team">
    {footer_agents_html}
  </div>
  <div class="footer-office">16830 Ventura Blvd, Ste. 100, Encino, CA 91436 | marcusmillichap.com/laaa-team</div>
  <div class="footer-disclaimer">This information has been secured from sources we believe to be reliable, but we make no representations or warranties, expressed or implied, as to the accuracy of the information. Buyer must verify the information and bears all risk for any inaccuracies. Marcus &amp; Millichap Real Estate Investment Services, Inc. | License: CA 01930580.</div>
</div>
""")

# PDF Download Button
html_parts.append(f"""
<a href="{PDF_LINK}" class="pdf-float-btn" id="pdfBtn" target="_blank">
  <svg viewBox="0 0 24 24"><path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20M12,19L8,15H10.5V12H13.5V15H16L12,19Z"/></svg>
  Download PDF
</a>
<div id="pdfOverlay" style="display:none;position:fixed;inset:0;background:rgba(27,58,92,0.85);z-index:99999;justify-content:center;align-items:center;flex-direction:column;gap:12px;">
  <div style="width:48px;height:48px;border:4px solid rgba(197,162,88,0.3);border-top-color:#C5A258;border-radius:50%;animation:pdfSpin 0.8s linear infinite;"></div>
  <div style="color:#fff;font-size:20px;font-weight:700;letter-spacing:0.5px;">Generating PDF</div>
  <div style="color:#C5A258;font-size:13px;">This typically takes 15–30 seconds. A new tab will open with your download.</div>
</div>
<style>@keyframes pdfSpin {{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}</style>
""")

# ============================================================
# JAVASCRIPT
# ============================================================
html_parts.append(f"""
<script>
// Client personalization
var params = new URLSearchParams(window.location.search);
var client = params.get('client');
if (client) {{
  var el = document.getElementById('client-greeting');
  if (el) el.textContent = 'Prepared Exclusively for ' + client;
}}

// TOC smooth scroll
document.querySelectorAll('.toc-nav a').forEach(function(link) {{
  link.addEventListener('click', function(e) {{
    e.preventDefault();
    var target = document.querySelector(this.getAttribute('href'));
    if (target) {{
      var navHeight = document.getElementById('toc-nav').offsetHeight;
      window.scrollTo({{ top: target.getBoundingClientRect().top + window.pageYOffset - navHeight - 4, behavior: 'smooth' }});
    }}
  }});
}});

// Active TOC highlighting
var tocLinks = document.querySelectorAll('.toc-nav a');
var tocSections = [];
tocLinks.forEach(function(link) {{
  var section = document.getElementById(link.getAttribute('href').substring(1));
  if (section) tocSections.push({{ link: link, section: section }});
}});
function updateActiveTocLink() {{
  var navHeight = document.getElementById('toc-nav').offsetHeight + 20;
  var scrollPos = window.pageYOffset + navHeight;
  var current = null;
  tocSections.forEach(function(item) {{ if (item.section.offsetTop <= scrollPos) current = item.link; }});
  tocLinks.forEach(function(link) {{ link.classList.remove('toc-active'); }});
  if (current) current.classList.add('toc-active');
}}
window.addEventListener('scroll', updateActiveTocLink);
updateActiveTocLink();

// PDF button loading overlay
var pdfBtn = document.getElementById('pdfBtn');
var pdfOverlay = document.getElementById('pdfOverlay');
if (pdfBtn && pdfOverlay) {{
  pdfBtn.addEventListener('click', function() {{
    pdfOverlay.style.display = 'flex';
    setTimeout(function() {{ pdfOverlay.style.display = 'none'; }}, 8000);
  }});
}}

// Leaflet Maps
{sale_map_js}
{active_map_js}
{rent_map_js}
</script>
</body>
</html>
""")

# ============================================================
# WRITE OUTPUT FILE
# ============================================================
print(f"\nAssembling HTML...")
html = "".join(html_parts)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)
file_size = os.path.getsize(OUTPUT)
print(f"Done! Wrote {OUTPUT}")
print(f"File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
print(f"URL: {BOV_BASE_URL}/?client={urllib.parse.quote(CLIENT_NAME)}")
