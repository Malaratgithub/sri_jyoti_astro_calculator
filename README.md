# Sri Jyoti Astro Calculator v1.8 — Windows date compatibility fix

Fixes `[Errno 22] Invalid argument` arising when Vimshottari Dasha dates fall before 1970 on Windows. Uses cross-platform datetime arithmetic rather than OS timestamp conversion. No changes to planetary formulas or report design. Added regression tests for 1978 and 1945 birth dates.

For Kishore Prasad: enter **15 August 1978**, **22:45** (10:45 PM), choose **Krishnagiri, Tamil Nadu, India** from the worldwide birthplace search so the latitude/longitude/timezone update correctly. Do not type `22.45 Pm` in a 24-hour time field.

Close older app instances, extract this ZIP into a separate directory, launch START_WINDOWS.bat, then open http://127.0.0.1:8766 and Ctrl+F5 if needed.

---

# Sri Jyoti Astro Calculator v1.6

## How to start the corrected version
1. Extract this ZIP into its own folder (do not overlay older releases).
2. Run START_WINDOWS.bat.
3. Visit **http://127.0.0.1:8766** (new port, prevents displaying a still-running old version).
4. Refresh with Ctrl+F5 if necessary.

## Requested features
- The D1 and D9 charts display planet degrees and minutes **inside each South Indian sign cell**.
- Birthplace search supports towns and cities **worldwide**: enter a place and country and click Search, then select a result. This requires internet access to OpenStreetMap; selecting a result automatically sets latitude, longitude and historical IANA timezone for calculation.
- Quick worldwide preset dropdown also changes coordinates and timezone.
- Prediction Report tab accepts **one large text box**; PNG and PDF exports are generated using **Arial on Windows**, with original fixed master header/footer imagery. Existing artwork includes its own baked-in lettering and is not re-typeset.

# Sri Jyoti Astro — Private Horoscope Calculator (Phase 1)

A local-only horoscope calculator with South Indian square D1 (Rasi) and D9 (Navamsa) charts, sidereal planetary positions, Lagna, nakshatra/pada, Rahu/Ketu, retrograde flags, JSON export and print-to-PDF.

## Start on Windows

1. Install Python 3.11 or newer from https://www.python.org/downloads/ (check **Add Python to PATH**).
2. Extract this ZIP to a folder (do not run from inside the ZIP).
3. Double-click `START_WINDOWS.bat`; it installs the `pyswisseph` and `tzdata` dependencies and starts a private local server.
4. Open http://127.0.0.1:8765 if the browser does not open automatically.
5. Enter **verified** birth date, time, birthplace coordinates and IANA timezone, and click Calculate Horoscope.
6. Use Print / Save as PDF (your browser print dialog) or Export JSON.
7. Stop the server by closing the terminal or Ctrl+C.

**Windows timezone support:** `tzdata` is installed automatically so IANA names such as `Asia/Kolkata` work even on Windows systems without a local IANA timezone database. If updating an earlier version, run `py -3 -m pip install -r requirements.txt` in this folder.

### macOS / Linux

```bash
python3 -m pip install -r requirements.txt
python3 server.py
```

Go to http://127.0.0.1:8765.

## Astronomical implementation

- **Engine:** `pyswisseph` (Swiss Ephemeris library), geocentric ecliptic planetary positions.
- **Ayanamsha:** Lahiri by default; Raman and Krishnamurti also selectable.
- **Nodes:** Mean node by default; true node optional. Ketu is positioned exactly 180° from Rahu.
- **Ascendant:** Swiss Ephemeris `houses_ex` sidereal ASC at birth location. Placidus cusp calculation is not used as a Vedic house model; ASC alone is used.
- **D9:** navamsa sign index = `(rasi_sign_index * 9 + floor(degrees_within_sign / (30/9))) mod 12`.
- **Nakshatra:** 27 equal segments of 13°20′ with four equal padas each.
- **Time:** Python `zoneinfo`/IANA historical timezone handling; nonexistent and ambiguous DST clock times rejected for manual resolution.
- **Precision:** No rounding is performed before sign and navamsa assignment. Display is rounded to seconds of arc.
- **Ephemeris:** The Swiss Ephemeris library can fall back to built-in Moshier astronomy if the external Swiss ephemeris `.se1` files are not present. Each result lists `ephemeris_mode`. This package does **not** include `.se1` files. For guaranteed Swiss-file mode, obtain licensed ephemeris files from Astrodienst and configure `swe.set_ephe_path(...)` in `engine.py` to their local directory. Review their license/availability. The Swiss Ephemeris *library* is still used without those files.
- **Geographical limits:** latitude -66° to +66° for this version; year 1800–2100.

## Private operation and security

- Server binds to `127.0.0.1` only; no cloud storage, accounts, analytics or external services.
- The app does not write birth data to disk. JSON is saved only if you click Export.
- City presets are **approximate city-center coordinates**, not birth hospital coordinates. You can edit them.
- A local IANA timezone is essential; simply assuming UTC+05:30 for all historical Indian dates can be inaccurate.

## Verification before professional use

Test several documented charts in your preferred established astrology software with matching date, exact birth time, latitude/longitude, timezone, ayanamsha and lunar node settings. Check planetary sidereal longitude, ascendant, D1 and D9, particularly on sign/navamsa boundaries. The calculator has been smoke-tested but **has not been independently certified or exhaustively benchmarked**.

## Not in Phase 1

Vimshottari dasha, Bhava Chalit, sunrise/panchanga, transits, birthplace autocomplete/geocoding, persistent client database, PDF branding/photo layout and interpretations are not implemented.

## Licensing

Swiss Ephemeris is dual-licensed under **AGPL** and a **professional license**. Check https://www.astro.com/swisseph/ before distributing this software or operating a public-facing hosted service. `pyswisseph` has its own published licensing notices. The user is responsible for selecting a permitted license model.

This product computes traditional astrological coordinates; horoscope predictions are not scientifically validated.

## Version 1.1 correction and reference-chart discrepancy (25 October 2026)

The previous SVG chart had an incorrect zodiac coordinate table, notably putting Aries outside the chart. Version 1.1 uses the fixed South Indian Rasi layout: Pisces top-left, Aries/Taurus/Gemini along the top, Cancer/Leo down the right, Virgo/Libra/Scorpio/Sagittarius along the bottom, and Capricorn/Aquarius up the left. Both D1 and D9 use the corrected map. Uranus, Neptune and Pluto have been added to the geocentric planetary position results.

The opening form defaults to Sundar Sriram, 29 September 1973, 21:00, Chennai, to make it easy to compare with the supplied reference image. With the included settings (Lahiri, mean nodes, Chennai latitude 13.0827, longitude 80.2707, Asia/Kolkata), the engine produces Taurus Lagna, Sun in Virgo and Moon in Libra. The supplied screenshot labels the Sun in Leo and the Moon in Aquarius. It **does not match** those birth inputs according to the available Swiss Ephemeris calculation. Do not alter astronomical results merely to match a possibly unrelated chart; independently verify the reference image's underlying birth date, time, chart mode and ayanamsha first.

The default implementation may report Moshier fallback when Swiss binary ephemeris files are not supplied. Check the `Ephemeris` method in the calculated result. Five automated smoke checks pass. These are not a substitute for detailed external accuracy certification.


## Version 1.2 reference check — Keerthi Chennuru
1984-07-06, 02:40 IST, V Madugula 17.9078 N 82.8098 E, Lahiri mean node.
D1 Taurus Lagna; Moon Virgo 20°24′43″, Hasta Pada 4. Moon Mahadasha birth balance 2y 2m 9d under 360-day savana-year convention. Screenshot's 'Mo 20' is an integer-degree display, not proof of Pada 3.
Dasha balance is for reference only; a fully configurable Vimshottari period/calendar scheduling module has **not** been implemented.
Location coordinates are approximate. Confirm precise birthplace and app's node/ayanamsha/time convention.

## Version 1.3: Dasha – Bhukti tab

After calculating, select **Dasha – Bhukti**. Click a Mahadasha row to see
Antardasha/Bhukti dates; click a Bhukti to see its Pratyantardasha dates.
Breadcrumbs navigate back to the Mahadasha level. The current interval is
highlighted. Export JSON includes complete periods and subperiods.

**Date conventions matter:** the period start/end engine calculates continuous
365.25-day solar years from the unrounded sidereal Moon longitude. The **birth
balance** remains expressed using traditional 360-day year / 30-day month
notation. The reference from Mindsutra for Keerthi Chennuru matches Jupiter
Mahadasha (14-09-2011 to 14-09-2027), and Jupiter/Rahu Bhukti
(21-04-2025 to 14-09-2027). Some intermediate transitions differ by a day
from the screenshot. This is a limitation of calendar conventions / boundary
rounding and is explicitly *not* claimed to be a vendor-exact replica.

This release does not alter the D1/D9 calculation, and the app is still
localhost-only. Recalculate after upgrading. Verify sensitive boundary dates
against your trusted panchanga before professional forecasting.

## Version 1.4 - Branded prediction report

After calculating the horoscope, open **Prediction Report**. Enter all astrologer-supplied interpretation in **one text box** and click **Refresh report preview**. Export the result using **Download PNG** or **Download PDF**. Predictions are inserted exactly as typed and are not written or modified by the app.

The header and footer are cropped from the user-supplied design reference and contain the fixed, original logo and practitioner photograph. Neither asset is regenerated. No client photograph is included. Main chart and tables use live horoscope data; the layout recreates the supplied purple-and-gold theme rather than reusing the example client's planetary placements. Long prediction text automatically continues onto extra pages (or is combined vertically for PNG).

The report module adds `Pillow` to requirements. Export is generated on the private localhost server. The report defaults to the currently active Mahadasha's Bhukti table based on the computer's date; verify Dasha boundary dates and Swiss Ephemeris results against your trusted software before using the report professionally.


## v1.5 changes
- D1 and D9 charts show each body's sidereal sign longitude in degrees and minutes (D9 displays derived Navamsa longitude within the Navamsa sign). Retrograde marked *. Full arcseconds in planetary table.
- Worldwide birth-location search using OpenStreetMap Nominatim via the local server. The selected result populates birthplace, latitude, longitude, and IANA timezone together; timezonefinder resolves geographic timezone. Internet needed for search; the app continues to calculate offline for previously selected/manual locations.
- Common world city presets are available offline. Verify selection, especially similarly named villages, historic birth timezones, DST and places close to boundaries. A time zone is geographically inferred and historical offsets are applied by Python zoneinfo; old or ambiguous civil times require further verification.
- Worldwide search sends the typed location phrase to the OpenStreetMap service; calculations and reports stay on localhost. Nominatim public API has fair-use rate limits; do not use bulk automated requests.

## Version 1.7: chart degree format
D1 and D9 charts, including charts embedded in exported PNG/PDF reports, show only completed whole degrees (for example `Ra* 10°`). Planetary positions table and report table retain degrees/minutes/seconds. No astronomical calculations have changed.


## Version 1.8 — Saved birth profiles addition
The form has a **Saved birth details** dropdown and **Save new / Update selected / Delete selected** controls. A saved profile contains the client name, DOB, time, birthplace label, exact latitude/longitude, IANA time zone, Ayanamsha and lunar-node settings. Selecting an entry fills the form; press Calculate horoscope to refresh results. Profiles persist in `saved_birth_profiles.sqlite3` in the application folder, created automatically on first use. Keep the folder writable; back up this database file and protect it because birth data is personal. No cloud service is used for saving profiles. Closing/reopening the app does not clear the data. Uninstalling/removing the extracted folder *will* remove profiles unless you back up that database file. Multiple clients with the same name are supported.

## Report chart typography update
The D1 Lagna chart embedded in exported prediction PNG/PDF reports now uses Arial Bold 19 pixels at 140 DPI (approximately 9.8 pt). Labels show whole degrees; the planetary position table retains degrees, minutes, and seconds. The chart is rendered directly at final resolution to avoid font shrinkage. Other report typography and the interactive D1/D9 charts are unchanged.


## Nakshatra Porutham module
Open http://127.0.0.1:8766/porutham.html or click **Nakshatra Porutham** on the calculator page. Select two saved birth profiles or manually select the 27 birth stars and optional padas. Profiles are calculated using the existing engine; results and printing run locally. The ten-factor table is a traditional preliminary screening: Vasya, unfamiliar Yoni combinations, and regional exceptions require expert review, and some factors are explicitly marked Review. Print → Save as PDF is supported. No claims about marital success are made.

## Marriage matching PDF and PNG report
Open **Nakshatra Porutham — Marriage Matching** from the calculator homepage.
Select two *different saved birth profiles* (bride and groom), click **Calculate Nakshatra Porutham**, optionally enter the astrologer's professional observations, then select **Download Marriage PDF** or **Download Marriage PNG**.

The report includes side-by-side square D1 charts with whole-degree labels, birth-star information, ten Porutham rows, score with unresolved checks explicitly excluded, current Mahadasha/Bhukti periods for both clients and a checklist of full-chart marriage considerations. Full Dasha matching is *not* automatically judged, because date overlap alone is not a validated compatibility rule. Regional Porutham exceptions, unresolved factors and full chart matching must be assessed by the astrologer. The report cannot be exported from manually entered Nakshatras alone, because both calculated D1 charts require full saved birth details. The PNG exports a multipage vertically stacked image, while PDF creates separate pages.
#   s r i _ j y o t i _ a s t r o _ c a l c u l a t o r  
 