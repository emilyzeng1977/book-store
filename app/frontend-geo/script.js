let map;
let markers = [];
let circles = [];
const selectedIndexes = new Set();

// Geocoding (client-side via Google Maps JS API)
let geocoder;
const geoCache = new Map(); // index -> { lat, lng }
const geoInFlight = new Map(); // index -> Promise<{lat,lng}>

let locations = [
    // Default entries (can be replaced by CSV upload)
    {name:"Sydney Opera House", address:"Sydney Opera House, Sydney NSW, Australia"},
    {name:"My home", address:"24 Clissold Street, Ashfield, Sydney NSW, Australia"}
];

// 等 DOM + Google Maps JS 加载完成再初始化地图
document.addEventListener("DOMContentLoaded", function() {

    const waitForGMaps = setInterval(function() {
        if(window.google && window.google.maps) {
            clearInterval(waitForGMaps);
            initMap();
        }
    }, 50);

});

function initMap() {
    const mapDiv = document.getElementById('map');
    if(!mapDiv){
        console.error('#map div not found');
        return;
    }

    map = new google.maps.Map(mapDiv, {
        zoom: 11,
        center: {lat:-33.8688, lng:151.2093}
    });

    geocoder = new google.maps.Geocoder();

    // Store defaults to restore when nothing is selected.
    map.__defaultCenter = map.getCenter();
    map.__defaultZoom = map.getZoom();

    renderLocationCheckboxes();
    setupRadiusEvent();
    setupToggleButtons();
    setupCsvUpload();
    updateToggleAllButtonLabel();
}

function renderLocationCheckboxes() {
    const container = document.getElementById('locationList');
    container.innerHTML = '';
    locations.forEach((loc, index) => {
        const label = document.createElement('label');
        label.style.display = 'block';
        const text = loc.name || loc.address || `Location ${index}`;
        label.innerHTML = `<input type="checkbox" value="${index}"> ${text}`;
        container.appendChild(label);
    });

    const checkboxes = getLocationCheckboxes();
    checkboxes.forEach(cb => {
        cb.addEventListener('change', async function() {
            const index = Number(this.value);
            if(this.checked){
                selectedIndexes.add(index);
                await addLocation(index);
            } else {
                selectedIndexes.delete(index);
                removeLocation(index);
            }
            fitMapBounds();
            updateToggleAllButtonLabel();
        });
    });
}

function getLocationCheckboxes(){
    return Array.from(document.querySelectorAll('#locationList input[type="checkbox"]'));
}

async function addLocation(index){
    const loc = locations[index];
    if(!loc) return;

    // Avoid duplicates
    removeLocation(index);

    try {
        const coords = await resolveLatLng(index, loc);
        // User might have unchecked while request in-flight
        if(!selectedIndexes.has(index)) return;

        const radius = getRadius();
        const position = {lat: coords.lat, lng: coords.lng};

        const marker = new google.maps.Marker({
            position,
            map,
            title: loc.name || loc.address || ''
        });

        const circle = new google.maps.Circle({
            map,
            center: position,
            radius,
            strokeColor:"#FF0000",
            strokeOpacity:0.8,
            strokeWeight:2,
            fillColor:"#FF0000",
            fillOpacity:0.2
        });

        markers[index] = marker;
        circles[index] = circle;
    } catch (err){
        console.error(err);
        // Roll back checkbox if geocode fails
        const cb = document.querySelector(`#locationList input[type="checkbox"][value="${index}"]`);
        if(cb){
            cb.checked = false;
        }
        selectedIndexes.delete(index);
    }
}

async function resolveLatLng(index, loc){
    if(typeof loc.lat === 'number' && typeof loc.lng === 'number'){
        return {lat: loc.lat, lng: loc.lng};
    }
    if(geoCache.has(index)) return geoCache.get(index);
    if(geoInFlight.has(index)) return geoInFlight.get(index);

    const query = (loc.address || loc.name || '').trim();
    if(!query) throw new Error(`Location ${index} missing address/name`);
    if(!geocoder) throw new Error('Geocoder not initialized');

    const promise = new Promise((resolve, reject) => {
        geocoder.geocode({ address: query }, (results, status) => {
            if(status !== 'OK' || !results || !results[0]){
                reject(new Error(`Geocode failed (${status}) for: ${query}`));
                return;
            }
            const gLoc = results[0].geometry.location;
            const coords = { lat: gLoc.lat(), lng: gLoc.lng() };
            geoCache.set(index, coords);
            loc.lat = coords.lat;
            loc.lng = coords.lng;
            resolve(coords);
        });
    });

    geoInFlight.set(index, promise);
    try {
        return await promise;
    } finally {
        geoInFlight.delete(index);
    }
}

function removeLocation(index){
    if(markers[index]){
        markers[index].setMap(null);
        markers[index] = null;
    }
    if(circles[index]){
        circles[index].setMap(null);
        circles[index] = null;
    }
}

function getRadius(){
    return parseInt(document.getElementById("radiusInput").value) || 500;
}

function setupRadiusEvent(){
    document.getElementById("radiusInput").addEventListener("input", function(){
        const radius = getRadius();
        circles.forEach(c => { if(c) c.setRadius(radius); });
    });
}

function setupToggleButtons(){
    const toggleBtn = document.getElementById('toggleAllBtn');
    if(!toggleBtn) return;

    toggleBtn.addEventListener('click', function(){
        const checkboxes = getLocationCheckboxes();
        const allChecked = checkboxes.length > 0 && checkboxes.every(cb => cb.checked);
        const nextChecked = !allChecked;
        checkboxes.forEach(cb => {
            cb.checked = nextChecked;
            cb.dispatchEvent(new Event('change'));
        });
    });
}

function updateToggleAllButtonLabel(){
    const btn = document.getElementById('toggleAllBtn');
    if(!btn) return;
    const checkboxes = getLocationCheckboxes();
    const allChecked = checkboxes.length > 0 && checkboxes.every(cb => cb.checked);
    btn.textContent = allChecked ? "Deselect all" : "Select all";
}

function fitMapBounds(){
    const activeMarkers = markers.filter(Boolean);

    // 0 selected -> restore default view
    if(activeMarkers.length === 0){
        if(map.__defaultCenter) map.setCenter(map.__defaultCenter);
        if(typeof map.__defaultZoom === 'number') map.setZoom(map.__defaultZoom);
        return;
    }

    // 1 selected -> keep a predictable "~1km" resolution (fixed zoom)
    if(activeMarkers.length === 1){
        map.setCenter(activeMarkers[0].getPosition());
        // Zoom 14 is roughly ~1km across on most displays/latitudes.
        map.setZoom(14);
        return;
    }

    // 2+ selected -> fit bounds
    const bounds = new google.maps.LatLngBounds();
    activeMarkers.forEach(m => bounds.extend(m.getPosition()));
    map.fitBounds(bounds);
}

function setupCsvUpload(){
    const input = document.getElementById('csvInput');
    if(!input) return;

    input.addEventListener('change', async function(){
        const file = this.files && this.files[0];
        if(!file) return;

        try {
            const text = await file.text();
            const nextLocations = parseLocationsCsv(text);
            if(nextLocations.length === 0){
                alert('No valid rows found. CSV format must be: name,address');
                return;
            }
            applyLocations(nextLocations);
        } catch (e){
            console.error(e);
            alert('Failed to read/parse CSV.');
        } finally {
            // Allow re-uploading the same file
            input.value = '';
        }
    });
}

function applyLocations(nextLocations){
    // Clear map + selection state
    clearAllSelections();

    // Replace locations + reset caches
    locations = nextLocations;
    geoCache.clear();
    geoInFlight.clear();

    // IMPORTANT: reset per-index map objects so old indices don't leak into new list.
    markers = [];
    circles = [];

    // Re-render list (this replaces the checkbox list)
    renderLocationCheckboxes();
    updateToggleAllButtonLabel();
}

function clearAllSelections(){
    selectedIndexes.clear();

    // Remove all markers/circles
    markers.forEach((m, i) => { if(m) removeLocation(i); });

    // Reset arrays (ensure indices align with future locations)
    markers = [];
    circles = [];

    // Uncheck UI (if present)
    const checkboxes = getLocationCheckboxes();
    checkboxes.forEach(cb => { cb.checked = false; });
}

function parseLocationsCsv(csvText){
    const lines = csvText
        .replace(/^\uFEFF/, '') // strip BOM
        .split(/\r?\n/)
        .map(l => l.trim())
        .filter(l => l.length > 0);

    const out = [];
    for(const line of lines){
        // Skip header if it looks like name,address
        if(/^name\s*,\s*address\s*$/i.test(line)) continue;

        const fields = parseCsvLine(line);
        if(fields.length < 2) continue;

        const name = (fields[0] || '').trim();
        const address = (fields.slice(1).join(',') || '').trim();
        if(!address) continue;

        out.push({ name: name || address, address });
    }
    return out;
}

function parseCsvLine(line){
    // Minimal CSV parser supporting quotes and escaped quotes.
    const res = [];
    let cur = '';
    let inQuotes = false;

    for(let i = 0; i < line.length; i++){
        const ch = line[i];

        if(inQuotes){
            if(ch === '"'){
                const next = line[i + 1];
                if(next === '"'){
                    cur += '"';
                    i++;
                } else {
                    inQuotes = false;
                }
            } else {
                cur += ch;
            }
        } else {
            if(ch === ','){
                res.push(cur);
                cur = '';
            } else if(ch === '"'){
                inQuotes = true;
            } else {
                cur += ch;
            }
        }
    }

    res.push(cur);
    return res;
}
