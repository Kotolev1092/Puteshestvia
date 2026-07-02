document.addEventListener('DOMContentLoaded', function () {
    const mapContainer = document.getElementById('map');
    if (!mapContainer) return;

    const places = window.placesData;
    if (!places || !Array.isArray(places) || places.length === 0) return;

    const centerLat = window.cityCenter ? window.cityCenter.lat : 55.75;
    const centerLon = window.cityCenter ? window.cityCenter.lon : 37.62;
    const zoom = window.cityCenter ? 12 : 11;

    const map = L.map('map').setView([centerLat, centerLon], zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    const bounds = [];
    places.forEach(p => {
        if (p.lat && p.lon) {
            const marker = L.marker([p.lat, p.lon]).addTo(map);
            marker.bindPopup(`<b>${p.name}</b><br>${p.description || ''}<br>💰 ${p.cost}<br>🕒 ${p.best_time}`);
            bounds.push([p.lat, p.lon]);
        }
    });

    if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [20, 20] });
    }
});