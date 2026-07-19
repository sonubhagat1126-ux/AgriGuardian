// AGRO SNAPDRAGON - REALTIME CLIENT CONTROLLER

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const statusBadge = document.getElementById('status-badge');
    const statusText = document.getElementById('status-text');
    
    const valSoil = document.getElementById('val-soil');
    const valSoilRaw = document.getElementById('val-soil-raw');
    const progressSoil = document.getElementById('progress-soil');
    const soilDesc = document.getElementById('soil-desc');
    
    const valTemp = document.getElementById('val-temp');
    const progressTemp = document.getElementById('progress-temp');
    const tempDesc = document.getElementById('temp-desc');
    
    const valHumidity = document.getElementById('val-humidity');
    const progressHumidity = document.getElementById('progress-humidity');
    const humidityDesc = document.getElementById('humidity-desc');
    
    const valSatNdvi = document.getElementById('val-sat-ndvi');
    const valSatSoil = document.getElementById('val-sat-soil');
    const valSatTemp = document.getElementById('val-sat-temp');
    const selectCrop = document.getElementById('select-crop');
    const selectField = document.getElementById('select-field');
    const gpsInputsContainer = document.getElementById('gps-inputs-container');
    const inputLat = document.getElementById('input-lat');
    const inputLon = document.getElementById('input-lon');
    const btnUpdateGps = document.getElementById('btn-update-gps');
    
    const pumpVisualizer = document.getElementById('pump-visualizer');
    const pumpIcon = document.getElementById('pump-icon');
    const toggleAuto = document.getElementById('toggle-auto');
    const togglePump = document.getElementById('toggle-pump');
    const manualSwitchWrapper = document.getElementById('manual-switch-wrapper');
    const sliderThreshold = document.getElementById('slider-threshold');
    const thresholdDisplay = document.getElementById('threshold-display');
    const statusBanner = document.getElementById('status-banner');
    const bannerText = document.getElementById('banner-text');

    // Map setup variables
    let map = null;
    let farmPolygon = null;
    let boundaryPoints = [];
    let mapMarkers = [];
    const btnClearMap = document.getElementById('btn-clear-map');
    const btnSaveField = document.getElementById('btn-save-field');
    const inputSaveFieldName = document.getElementById('input-save-field-name');
    let savedFieldsCount = 0;
    let cachedSavedFields = [];
    let lastFlippedLat = null;
    let lastFlippedLon = null;
    let lastSelectedField = null;

    function rebuildFieldDropdown(data) {
        if (!selectField || !data.saved_fields) return;
        const currentSelected = selectField.value;
        
        // Re-render preset options
        selectField.innerHTML = `
            <option value="none">-- No Field Selected --</option>
            <option value="noida">Noida Research Center (Tomato)</option>
            <option value="field_alpha">Field Alpha (Rice)</option>
            <option value="field_beta">Field Beta (Wheat)</option>
            <option value="custom">Custom Land (Draw on Map)</option>
        `;
        
        // Append saved fields from server database
        data.saved_fields.forEach(field => {
            const opt = document.createElement('option');
            opt.value = field.name;
            opt.innerText = `${field.name} (${field.crop ? field.crop.toUpperCase() : 'TOMATO'})`;
            selectField.appendChild(opt);
        });
        
        // Restore selection state
        if ([...selectField.options].some(o => o.value === currentSelected)) {
            selectField.value = currentSelected;
        } else if (data.selected_field) {
            selectField.value = data.selected_field;
        }
    }

    function initMap(lat, lon) {
        if (map) return;
        
        const streetMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        });

        const satelliteMap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri &mdash; Aerial Imagery',
            maxZoom: 20,
            maxNativeZoom: 18
        });

        map = L.map('farm-map', {
            zoomControl: true,
            scrollWheelZoom: true,
            layers: [satelliteMap]
        }).setView([lat, lon], 16);
        
        const baseMaps = {
            "2D Street Map": streetMap,
            "Satellite Map": satelliteMap
        };
        L.control.layers(baseMaps, null, { position: 'topright' }).addTo(map);

        // Click to add custom polygon nodes manually
        map.on('click', (e) => {
            const coord = e.latlng;
            addBoundaryNode(coord.lat, coord.lng);
        });

        // Current Location found handler
        map.on('locationfound', (e) => {
            // Place a beautiful blue GPS pulse marker
            L.marker(e.latlng, {
                icon: L.divIcon({
                    className: 'user-gps-marker',
                    html: '<div style="width: 14px; height: 14px; border-radius: 50%; background-color: #3b82f6; border: 2px solid #fff; box-shadow: 0 0 8px #3b82f6;"></div>',
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                })
            }).addTo(map)
            .bindPopup("You are here").openPopup();
        });

        map.on('locationerror', (e) => {
            console.warn("Location fetch error:", e.message);
            alert("Could not retrieve precise location. Please ensure GPS/Location services are enabled on your device.");
        });
    }

    function addBoundaryNode(lat, lon, sync = true) {
        boundaryPoints.push([lat, lon]);
        
        // Define custom circular divIcon so standard Leaflet markers look like clean draggable dots
        const dotIcon = L.divIcon({
            className: 'custom-map-dot',
            html: '<div style="width: 10px; height: 10px; border-radius: 50%; background-color: #38bdf8; border: 2px solid #fff; box-shadow: 0 0 4px rgba(0,0,0,0.5);"></div>',
            iconSize: [10, 10],
            iconAnchor: [5, 5]
        });

        // Create draggable marker
        const marker = L.marker([lat, lon], {
            icon: dotIcon,
            draggable: true
        }).addTo(map);
        
        const markerIndex = boundaryPoints.length - 1;
        
        // Live drag listener to redraw polygon outline dynamically
        marker.on('drag', (e) => {
            const newPos = e.target.getLatLng();
            boundaryPoints[markerIndex] = [newPos.lat, newPos.lng];
            drawPolygon(false); // redraw visually without sending WS updates
        });

        // Sync final centroid coordinates on drag release
        marker.on('dragend', () => {
            drawPolygon(true); // send WS update
        });

        mapMarkers.push(marker);
        drawPolygon(sync);
    }

    function drawPolygon(syncCentroid = true) {
        if (farmPolygon) {
            map.removeLayer(farmPolygon);
        }
        
        if (btnSaveField) {
            if (boundaryPoints.length >= 3) {
                btnSaveField.style.display = 'inline-flex';
                if (inputSaveFieldName) inputSaveFieldName.style.display = 'inline-block';
            } else {
                btnSaveField.style.display = 'none';
                if (inputSaveFieldName) inputSaveFieldName.style.display = 'none';
            }
        }
        
        if (boundaryPoints.length < 2) return;

        let color = '#34d399'; // Green
        const ndviVal = parseFloat(valSatNdvi.innerText) || 0.65;
        if (ndviVal < 0.4) {
            color = '#fb7185'; // Red
        } else if (ndviVal < 0.6) {
            color = '#fbbf24'; // Yellow
        }

        farmPolygon = L.polygon(boundaryPoints, {
            color: color,
            fillColor: color,
            fillOpacity: 0.3,
            weight: 2,
            interactive: false // Prevents overlay from blocking subsequent map clicks
        }).addTo(map);

        const cropName = selectCrop.options[selectCrop.selectedIndex].text;
        
        if (syncCentroid) {
            farmPolygon.bindPopup(`
                <div style="font-family: 'Inter', sans-serif; font-size: 0.82rem; color: #fff;">
                    <h4 style="margin: 0 0 0.3rem; color: #38bdf8; font-family: 'Outfit';">Field Boundary Active</h4>
                    <strong>Crop:</strong> ${cropName}<br>
                    <strong>Nodes:</strong> ${boundaryPoints.length} points<br>
                    <strong>Est. Area:</strong> ${calculateArea(boundaryPoints)} m²
                </div>
            `).openPopup();

            if (boundaryPoints.length >= 3) {
                const centroid = getCentroid(boundaryPoints);
                inputLat.value = centroid.lat.toFixed(4);
                inputLon.value = centroid.lon.toFixed(4);
                sendControlCommand('set_field', { field: 'custom', lat: centroid.lat, lon: centroid.lon });
                sendControlCommand('set_boundary', { boundary: boundaryPoints });
            }
        }
    }

    function calculateArea(coords) {
        if (coords.length < 3) return 0;
        
        // Calculate average latitude
        let latSum = 0;
        coords.forEach(pt => latSum += pt[0]);
        const latAvg = latSum / coords.length;
        
        // Convert to local meter coordinates
        const rad = Math.PI / 180;
        const cosLat = Math.cos(latAvg * rad);
        
        const meters = coords.map(pt => {
            return {
                x: pt[1] * 111320 * cosLat,
                y: pt[0] * 110574
            };
        });
        
        // Apply Shoelace formula in meters
        let area = 0;
        for (let i = 0; i < meters.length; i++) {
            let j = (i + 1) % meters.length;
            area += meters[i].x * meters[j].y;
            area -= meters[j].x * meters[i].y;
        }
        
        return Math.abs(Math.round(area / 2));
    }

    function parseCoordinateToDecimal(str) {
        if (!str) return NaN;
        // Normalize curly quotes, primes, smart quotes to standard ' and "
        str = str.trim()
                 .replace(/[\u201C\u201D\u2033””]/g, '"')
                 .replace(/[\u2018\u2019\u2032’’]/g, "'");
        
        // Check if decimal degree
        const decimalMatch = str.match(/^[-+]?[0-9]*\.?[0-9]+$/);
        if (decimalMatch) {
            return parseFloat(str);
        }
        
        // Parse DMS format: e.g., 28°45'33.3"N
        const dmsMatch = str.match(/(\d+)\s*°\s*(\d+)\s*'\s*([\d.]+)\s*"\s*([NSEWnsew]?)/) ||
                         str.match(/(\d+)\s*d\s*(\d+)\s*m\s*([\d.]+)\s*s\s*([NSEWnsew]?)/);
                         
        if (dmsMatch) {
            const degrees = parseFloat(dmsMatch[1]);
            const minutes = parseFloat(dmsMatch[2]);
            const seconds = parseFloat(dmsMatch[3]);
            const direction = dmsMatch[4].toUpperCase();
            
            let decimal = degrees + (minutes / 60.0) + (seconds / 3600.0);
            if (direction === 'S' || direction === 'W') {
                decimal = -decimal;
            }
            return decimal;
        }
        return NaN;
    }

    function getCentroid(coords) {
        let latSum = 0;
        let lonSum = 0;
        coords.forEach(pt => {
            latSum += pt[0];
            lonSum += pt[1];
        });
        return {
            lat: latSum / coords.length,
            lon: lonSum / coords.length
        };
    }

    function drawDefaultCustomField(lat, lon) {
        clearBoundary();
        
        const dotIcon = L.divIcon({
            className: 'custom-map-dot',
            html: '<div style="width: 10px; height: 10px; border-radius: 50%; background-color: #38bdf8; border: 2px solid #fff; box-shadow: 0 0 4px rgba(0,0,0,0.5);"></div>',
            iconSize: [10, 10],
            iconAnchor: [5, 5]
        });

        // 100m square coordinates
        const pts = [
            [lat + 0.0005, lon - 0.0005],
            [lat + 0.0005, lon + 0.0005],
            [lat - 0.0005, lon + 0.0005],
            [lat - 0.0005, lon - 0.0005]
        ];

        boundaryPoints = pts;

        pts.forEach((pt, index) => {
            const marker = L.marker(pt, {
                icon: dotIcon,
                draggable: true
            }).addTo(map);

            marker.on('drag', (e) => {
                const newPos = e.target.getLatLng();
                boundaryPoints[index] = [newPos.lat, newPos.lng];
                drawPolygon(false);
            });

            marker.on('dragend', () => {
                drawPolygon(true);
            });

            mapMarkers.push(marker);
        });

        drawPolygon(true);
    }

    function clearBoundary(sync = true) {
        if (farmPolygon) map.removeLayer(farmPolygon);
        mapMarkers.forEach(m => map.removeLayer(m));
        boundaryPoints = [];
        mapMarkers = [];
        farmPolygon = null;
        if (inputSaveFieldName) {
            inputSaveFieldName.value = '';
            inputSaveFieldName.style.display = 'none';
        }
        if (btnSaveField) {
            btnSaveField.style.display = 'none';
        }
        if (sync) {
            sendControlCommand('set_boundary', { boundary: [] });
        }
    }

    if (btnClearMap) {
        btnClearMap.addEventListener('click', () => clearBoundary(true));
    }

    function showToast(message) {
        let toast = document.getElementById('map-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'map-toast';
            toast.style.position = 'absolute';
            toast.style.bottom = '20px';
            toast.style.left = '50%';
            toast.style.transform = 'translateX(-50%)';
            toast.style.background = 'rgba(30, 41, 59, 0.85)';
            toast.style.backdropFilter = 'blur(8px)';
            toast.style.border = '1px solid rgba(255, 255, 255, 0.1)';
            toast.style.color = '#34d399';
            toast.style.padding = '10px 20px';
            toast.style.borderRadius = '10px';
            toast.style.fontSize = '0.85rem';
            toast.style.fontWeight = '600';
            toast.style.zIndex = '9999';
            toast.style.boxShadow = '0 10px 25px rgba(0,0,0,0.5)';
            toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            toast.style.pointerEvents = 'none';
            
            const mapWrapper = document.querySelector('.map-wrapper');
            if (mapWrapper) {
                mapWrapper.appendChild(toast);
            } else {
                document.body.appendChild(toast);
            }
        }
        toast.innerText = message;
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(-50%) translateY(0)';
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(-50%) translateY(10px)';
        }, 3000);
    }

    if (btnSaveField) {
        btnSaveField.addEventListener('click', () => {
            if (boundaryPoints.length < 3) return;
            
            const cropVal = selectCrop.value;
            const cropText = selectCrop.options[selectCrop.selectedIndex].text;
            const cropName = cropText.split(' ')[0] || 'Custom';
            
            let fieldName = '';
            if (inputSaveFieldName) {
                fieldName = inputSaveFieldName.value.trim();
            }
            
            if (!fieldName) {
                savedFieldsCount++;
                fieldName = `${cropName} Plot ${savedFieldsCount}`;
            }
            
            const centroid = getCentroid(boundaryPoints);
            sendControlCommand('save_field_plot', {
                name: fieldName,
                boundary: boundaryPoints,
                lat: centroid.lat,
                lon: centroid.lon,
                crop: cropVal
            });
            
            showToast(`Field "${fieldName}" saved successfully!`);
            
            if (inputSaveFieldName) {
                inputSaveFieldName.value = '';
                inputSaveFieldName.style.display = 'none';
            }
            btnSaveField.style.display = 'none';
            clearBoundary(false);
        });
    }

    const btnGpsLocate = document.getElementById('btn-gps-locate');
    if (btnGpsLocate) {
        btnGpsLocate.addEventListener('click', (e) => {
            e.stopPropagation(); // prevent map click triggers
            if (map) {
                map.locate({setView: true, maxZoom: 16, enableHighAccuracy: true});
            }
        });
    }

    // Chart Setup variables
    const ctx = document.getElementById('liveChart').getContext('2d');
    const maxDataPoints = 30; // Displays 1 minute of history (at 2s intervals)
    const chartLabels = [];
    const soilData = [];
    const tempData = [];
    const humidityData = [];
    let lastChartUpdateTime = 0;

    // Initialize Chart.js
    let liveChart = null;
    if (typeof Chart !== 'undefined') {
        liveChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartLabels,
                datasets: [
                    {
                        label: 'Soil Moisture (%)',
                        data: soilData,
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.05)',
                        borderWidth: 3,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                        tension: 0.4,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Temperature (°C)',
                        data: tempData,
                        borderColor: '#fb7185',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 2,
                        tension: 0.4,
                        yAxisID: 'y1'
                    },
                    {
                        label: 'Humidity (%)',
                        data: humidityData,
                        borderColor: '#818cf8',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 2,
                        tension: 0.4,
                        yAxisID: 'y'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false // Using custom HTML legend
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: '#0d1527',
                        titleColor: '#f3f4f6',
                        bodyColor: '#9ca3af',
                        borderColor: 'rgba(255,255,255,0.08)',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.03)'
                        },
                        ticks: {
                            color: '#9ca3af',
                            font: { size: 10 }
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        min: 0,
                        max: 100,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#9ca3af',
                            font: { size: 10 }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        min: 0,
                        max: 50,
                        grid: {
                            drawOnChartArea: false // Avoid overlapping grid lines
                        },
                        ticks: {
                            color: '#9ca3af',
                            font: { size: 10 }
                        }
                    }
                }
            }
        });
    }

    // WebSocket Management
    let ws;
    let reconnectTimeout;

    function connectWebSocket() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
        
        console.log(`Connecting to WebSocket: ${wsUrl}`);
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket Connection Active');
            clearTimeout(reconnectTimeout);
            
            // Set default status (will refine based on backend payload)
            statusBadge.className = 'status-badge status-online';
            statusText.innerText = 'System Connected';

            // Resynchronize client-side coordinate state with backend upon connection/reconnection
            if (selectField) {
                const field = selectField.value;
                const lat = parseCoordinateToDecimal(inputLat.value);
                const lon = parseCoordinateToDecimal(inputLon.value);
                if (!isNaN(lat) && !isNaN(lon)) {
                    sendControlCommand('set_field', { field, lat, lon });
                }
            }
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            } catch (err) {
                console.error('Error parsing WebSocket data:', err);
            }
        };

        ws.onclose = (event) => {
            console.log('WebSocket Connection Closed. Attempting reconnect...', event.reason);
            statusBadge.className = 'status-badge status-offline';
            statusText.innerText = 'Server Disconnected';
            
            // Auto reconnect in 3s
            reconnectTimeout = setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (err) => {
            console.error('WebSocket Error:', err);
            ws.close();
        };
    }

    // Update Dashboard DOM elements with new states
    function updateDashboard(data) {
        // 1. Refine Status Badges based on simulation mode flag
        const comPortInfo = document.getElementById('com-port-info');
        if (data.simulation_mode || (data.humidity === 62.0 && data.temperature === 26.5 && !ws)) {
            // Note: If backend sends simulated values
            statusBadge.className = 'status-badge status-simulation';
            statusText.innerText = 'Simulation Mode';
            if (comPortInfo) comPortInfo.innerText = "SIMULATOR ACTIVE";
        } else {
            statusBadge.className = 'status-badge status-online';
            statusText.innerText = 'Live System Active';
            if (comPortInfo && data.serial_port) {
                comPortInfo.innerText = `${data.serial_port} @ ${data.baud_rate || 9600}`;
            }
        }

        // 2. Soil Moisture Card
        valSoil.innerText = data.soil_moisture;
        progressSoil.style.width = `${data.soil_moisture}%`;
        if (valSoilRaw && data.raw_soil !== undefined) {
            valSoilRaw.innerText = `Raw: ${data.raw_soil}`;
        }
        
        let soilQuality = 'Perfect moisture levels';
        if (data.soil_moisture < data.soil_threshold) {
            soilQuality = 'Soil Dry - Relay Automated Trigger';
        } else if (data.soil_moisture < 45) {
            soilQuality = 'Normal/Dry - Approaching threshold';
        } else if (data.soil_moisture > 75) {
            soilQuality = 'Soil Saturated - High moisture';
        }
        soilDesc.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> ${soilQuality}`;

        // 3. Temperature Card
        if (data.temperature != null) {
            valTemp.innerText = data.temperature.toFixed(1);
            // Map 0-50 deg to progress width
            const tempWidth = Math.min(100, Math.max(0, (data.temperature / 50) * 100));
            progressTemp.style.width = `${tempWidth}%`;
        } else {
            valTemp.innerText = '--';
            progressTemp.style.width = '0%';
        }
        
        let tempQuality = 'Optimal ambient temp';
        if (data.temperature != null) {
            if (data.temperature > 32) {
                tempQuality = 'High temperature - monitor closely';
            } else if (data.temperature < 15) {
                tempQuality = 'Cool temperature';
            }
        }
        tempDesc.innerHTML = `<i class="fa-solid fa-gauge-high"></i> ${tempQuality}`;

        // 4. Humidity Card
        if (data.humidity != null) {
            valHumidity.innerText = data.humidity.toFixed(1);
            progressHumidity.style.width = `${data.humidity}%`;
        } else {
            valHumidity.innerText = '--';
            progressHumidity.style.width = '0%';
        }
        
        let humQuality = 'Comfortable environment';
        if (data.humidity != null) {
            if (data.humidity > 80) {
                humQuality = 'High humidity levels';
            } else if (data.humidity < 40) {
                humQuality = 'Dry air environment';
            }
        }
        humidityDesc.innerHTML = `<i class="fa-solid fa-cloud-sun"></i> ${humQuality}`;

        // 4.5 VEDAS Satellite Card
        if (valSatNdvi && data.vegetation_ndvi != null) {
            valSatNdvi.innerText = data.vegetation_ndvi.toFixed(2);
            // Recolor polygon on the map based on the updated NDVI value
            if (farmPolygon && boundaryPoints.length >= 3) {
                drawPolygon(false);
            }
        } else if (valSatNdvi) {
            valSatNdvi.innerText = '--';
        }
        
        if (valSatSoil && data.satellite_soil != null) {
            valSatSoil.innerText = `${data.satellite_soil.toFixed(2)} m³/m³`;
        } else if (valSatSoil) {
            valSatSoil.innerText = '--';
        }
        
        if (valSatTemp && data.satellite_temp != null) {
            valSatTemp.innerText = `${data.satellite_temp.toFixed(1)} °C`;
        } else if (valSatTemp) {
            valSatTemp.innerText = '--';
        }
 
        const satDesc = document.getElementById('sat-desc');
        if (satDesc && data.vegetation_ndvi != null) {
            let healthStatus = '🟢 Crop Health: Excellent (Chlorophyll OK)';
            if (data.vegetation_ndvi < 0.45) {
                healthStatus = '🔴 Crop Health: Severe Stress (Scan Leaves)';
            } else if (data.vegetation_ndvi < 0.65) {
                healthStatus = '🟡 Crop Health: Moderate Stress (Check Water)';
            }
            satDesc.innerHTML = `<i class="fa-solid fa-circle-info"></i> ${healthStatus}`;
        } else if (satDesc) {
            satDesc.innerHTML = `<i class="fa-solid fa-circle-info"></i> Live ISRO data feed`;
        }

        // 5. Pump Visualizer state
        if (pumpVisualizer && pumpIcon) {
            if (data.pump_status) {
                pumpVisualizer.classList.add('pump-active-state');
                pumpIcon.classList.add('pump-running-anim');
            } else {
                pumpVisualizer.classList.remove('pump-active-state');
                pumpIcon.classList.remove('pump-running-anim');
            }
        }

        // 5.5 Crop Type Sync
        if (selectCrop && data.crop_type) {
            selectCrop.value = data.crop_type;
        }

        // 6. Controls Sync
        if (toggleAuto) {
            toggleAuto.checked = data.auto_mode;
        }
        
        // Manual override switch is disabled if Auto mode is active
        if (togglePump) {
            if (data.auto_mode) {
                togglePump.disabled = true;
                if (manualSwitchWrapper) manualSwitchWrapper.classList.add('switch-disabled');
                togglePump.checked = data.pump_status;
            } else {
                togglePump.disabled = false;
                if (manualSwitchWrapper) manualSwitchWrapper.classList.remove('switch-disabled');
                togglePump.checked = data.pump_status;
            }
        }

        // Soil Threshold Slider
        sliderThreshold.value = data.soil_threshold;
        thresholdDisplay.innerText = `${data.soil_threshold}%`;

        if (data.saved_fields) {
            savedFieldsCount = data.saved_fields.length;
            cachedSavedFields = data.saved_fields;
            rebuildFieldDropdown(data);
        }

        // Map Initialization & Fly logic
        if (!map) {
            const startLat = data.latitude || 28.5355;
            const startLon = data.longitude || 77.3910;
            initMap(startLat, startLon);
            lastFlippedLat = startLat;
            lastFlippedLon = startLon;
            lastSelectedField = data.selected_field;
            
            // Draw initial boundary based on active field
            clearBoundary(false);
            const savedField = data.saved_fields ? data.saved_fields.find(f => f.name === data.selected_field) : null;
            if (data.selected_field === 'noida') {
                const pts = [[28.5360, 77.3905], [28.5360, 77.3915], [28.5350, 77.3915], [28.5350, 77.3905]];
                pts.forEach((pt, idx) => addBoundaryNode(pt[0], pt[1], idx === pts.length - 1));
            } else if (data.selected_field === 'field_alpha') {
                const pts = [[30.9015, 75.8568], [30.9015, 75.8578], [30.9005, 75.8578], [30.9005, 75.8568]];
                pts.forEach((pt, idx) => addBoundaryNode(pt[0], pt[1], idx === pts.length - 1));
            } else if (data.selected_field === 'field_beta') {
                const pts = [[22.3077, 73.1807], [22.3077, 73.1817], [22.3067, 73.1817], [22.3067, 73.1807]];
                pts.forEach((pt, idx) => addBoundaryNode(pt[0], pt[1], idx === pts.length - 1));
            } else if (data.selected_field === 'custom' && data.custom_boundary && data.custom_boundary.length > 0) {
                data.custom_boundary.forEach((pt, idx) => addBoundaryNode(pt[0], pt[1], idx === data.custom_boundary.length - 1));
            } else if (savedField) {
                if (savedField.boundary && savedField.boundary.length > 0) {
                    savedField.boundary.forEach((pt, idx) => addBoundaryNode(pt[0], pt[1], idx === savedField.boundary.length - 1));
                } else if (savedField.latitude && savedField.longitude) {
                    addBoundaryNode(savedField.latitude, savedField.longitude, false);
                }
            }
        } else {
            // Fly/pan map if coordinates changed (e.g. preset changed or inputs synced)
            // BUT only if it is a real field change (prevents fly loop when dragging custom markers)
            if (data.latitude && data.longitude) {
                if (data.selected_field !== lastSelectedField || 
                    (data.selected_field !== 'custom' && (data.latitude !== lastFlippedLat || data.longitude !== lastFlippedLon))) {
                    
                    lastFlippedLat = data.latitude;
                    lastFlippedLon = data.longitude;
                    
                    const targetZoom = (data.selected_field === 'custom') ? map.getZoom() : 16;
                    map.flyTo([data.latitude, data.longitude], targetZoom);
                }
            }

            // Check if custom boundary changed in real-time (e.g., node added via phone app)
            let customBoundaryChanged = false;
            if (data.selected_field === 'custom' && data.custom_boundary) {
                if (data.custom_boundary.length !== boundaryPoints.length) {
                    customBoundaryChanged = true;
                } else {
                    for (let i = 0; i < data.custom_boundary.length; i++) {
                        if (data.custom_boundary[i][0] !== boundaryPoints[i][0] || 
                            data.custom_boundary[i][1] !== boundaryPoints[i][1]) {
                            customBoundaryChanged = true;
                            break;
                        }
                    }
                }
            }

            // ONLY clear and redraw boundaries if the active field plot selector changes OR boundary changes
            if (data.selected_field !== lastSelectedField || customBoundaryChanged) {
                lastSelectedField = data.selected_field;
                
                clearBoundary(false);
                const savedField = data.saved_fields ? data.saved_fields.find(f => f.name === data.selected_field) : null;
                if (data.selected_field === 'noida') {
                    const pts = [[28.5360, 77.3905], [28.5360, 77.3915], [28.5350, 77.3915], [28.5350, 77.3905]];
                    pts.forEach((pt, idx) => addBoundaryNode(pt[0], pt[1], idx === pts.length - 1));
                } else if (data.selected_field === 'field_alpha') {
                    const pts = [[30.9015, 75.8568], [30.9015, 75.8578], [30.9005, 75.8578], [30.9005, 75.8568]];
                    pts.forEach((pt, idx) => addBoundaryNode(pt[0], pt[1], idx === pts.length - 1));
                } else if (data.selected_field === 'field_beta') {
                    const pts = [[22.3077, 73.1807], [22.3077, 73.1817], [22.3067, 73.1817], [22.3067, 73.1807]];
                    pts.forEach((pt, idx) => addBoundaryNode(pt[0], pt[1], idx === pts.length - 1));
                } else if (data.selected_field === 'custom' && data.custom_boundary && data.custom_boundary.length > 0) {
                    data.custom_boundary.forEach((pt, idx) => addBoundaryNode(pt[0], pt[1], idx === data.custom_boundary.length - 1));
                } else if (savedField) {
                    if (savedField.boundary && savedField.boundary.length > 0) {
                        savedField.boundary.forEach((pt, idx) => addBoundaryNode(pt[0], pt[1], idx === savedField.boundary.length - 1));
                    } else if (savedField.latitude && savedField.longitude) {
                        addBoundaryNode(savedField.latitude, savedField.longitude, false);
                    }
                }
            }
        }

        // 6.5 Field Selection Sync
        if (selectField && data.selected_field) {
            selectField.value = data.selected_field;
            
            // Show/hide custom GPS input box
            if (data.selected_field === 'custom') {
                gpsInputsContainer.style.display = 'flex';
            } else {
                gpsInputsContainer.style.display = 'none';
            }
        }
        if (inputLat && data.latitude !== undefined) {
            // Avoid overwriting active typing when custom is selected
            if (document.activeElement !== inputLat) {
                inputLat.value = data.latitude;
            }
        }
        if (inputLon && data.longitude !== undefined) {
            if (document.activeElement !== inputLon) {
                inputLon.value = data.longitude;
            }
        }

        // 7. Info Banner Text
        if (bannerText) {
            if (data.auto_mode) {
                if (data.pump_status) {
                    bannerText.innerText = `Watering automatically. Soil is at ${data.soil_moisture}% (under threshold of ${data.soil_threshold}%).`;
                } else {
                    bannerText.innerText = `Auto irrigation active. Will trigger water pump if moisture drops below ${data.soil_threshold}%.`;
                }
            } else {
                if (data.pump_status) {
                    bannerText.innerText = "Pump overrides: Relay forced ON manually via Dashboard override.";
                } else {
                    bannerText.innerText = "Pump overrides: Relay forced OFF manually. Auto control deactivated.";
                }
            }
        }

        // 8. Update Live Chart (Throttled to once every 2 seconds to avoid rapid duplicate updates)
        const now = Date.now();
        if (now - lastChartUpdateTime >= 2000) {
            lastChartUpdateTime = now;
            const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            
            chartLabels.push(timestamp);
            soilData.push(data.soil_moisture);
            tempData.push(data.temperature);
            humidityData.push(data.humidity);

            // Keep lists sized to maxDataPoints
            if (chartLabels.length > maxDataPoints) {
                chartLabels.shift();
                soilData.shift();
                tempData.shift();
                humidityData.shift();
            }

            if (liveChart) {
                liveChart.update('none'); // Update smoothly
            }
        }
    }

    // UI Input Event Listeners
    if (toggleAuto) {
        toggleAuto.addEventListener('change', () => {
            const isAuto = toggleAuto.checked;
            sendControlCommand('set_auto', isAuto);
        });
    }

    if (togglePump) {
        togglePump.addEventListener('change', () => {
            const isPumpOn = togglePump.checked;
            sendControlCommand('set_pump', isPumpOn);
        });
    }

    if (sliderThreshold) {
        sliderThreshold.addEventListener('input', () => {
            const val = parseInt(sliderThreshold.value);
            if (thresholdDisplay) thresholdDisplay.innerText = `${val}%`;
        });

        sliderThreshold.addEventListener('change', () => {
            const val = parseInt(sliderThreshold.value);
            sendControlCommand('set_threshold', val);
        });
    }

    if (selectCrop) {
        selectCrop.addEventListener('change', () => {
            const crop = selectCrop.value;
            sendControlCommand('set_crop', crop);
            
            // Auto-change threshold based on standard agricultural values
            let threshold = 30;
            if (crop === 'tomato') threshold = 40;
            else if (crop === 'rice') threshold = 75;
            else if (crop === 'wheat') threshold = 50;
            else if (crop === 'maize') threshold = 35;
            else return; // custom
            
            if (sliderThreshold) sliderThreshold.value = threshold;
            if (thresholdDisplay) thresholdDisplay.innerText = `${threshold}%`;
            sendControlCommand('set_threshold', threshold);
        });
    }

    if (selectField) {
        selectField.addEventListener('change', () => {
            const field = selectField.value;
            let lat = 28.5355;
            let lon = 77.3910;
            
            if (field === 'none') {
                if (gpsInputsContainer) gpsInputsContainer.style.display = 'none';
                if (inputLat) inputLat.value = '';
                if (inputLon) inputLon.value = '';
                clearBoundary(true);
                sendControlCommand('set_field', { field: 'none', lat: null, lon: null });
                return;
            } else if (field === 'noida') {
                lat = 28.5355; lon = 77.3910;
                if (gpsInputsContainer) gpsInputsContainer.style.display = 'none';
            } else if (field === 'field_alpha') {
                lat = 30.9010; lon = 75.8573;
                if (gpsInputsContainer) gpsInputsContainer.style.display = 'none';
            } else if (field === 'field_beta') {
                lat = 22.3072; lon = 73.1812;
                if (gpsInputsContainer) gpsInputsContainer.style.display = 'none';
            } else if (field === 'custom') {
                if (gpsInputsContainer) gpsInputsContainer.style.display = 'flex';
                return; // Wait for the user to type and click sync
            } else {
                const savedField = cachedSavedFields.find(f => f.name === field);
                if (savedField) {
                    lat = savedField.latitude;
                    lon = savedField.longitude;
                }
                if (gpsInputsContainer) gpsInputsContainer.style.display = 'none';
            }
            
            if (inputLat) inputLat.value = lat;
            if (inputLon) inputLon.value = lon;
            sendControlCommand('set_field', { field, lat, lon });
        });
    }

    if (btnUpdateGps) {
        btnUpdateGps.addEventListener('click', () => {
            if (!inputLat || !inputLon) return;
            const lat = parseCoordinateToDecimal(inputLat.value);
            const lon = parseCoordinateToDecimal(inputLon.value);
            if (!isNaN(lat) && !isNaN(lon)) {
                // Draw default bounding square around new coordinates and pan there
                drawDefaultCustomField(lat, lon);
                if (map) map.flyTo([lat, lon], 16);
                sendControlCommand('set_field', { field: 'custom', lat, lon });
            } else {
                alert('Invalid coordinate format. Please use decimal (28.759) or DMS (28°45\'33"N) format.');
            }
        });
    }

    // Auto-split combined coordinate values (e.g. pasted directly into the latitude field)
    if (inputLat) {
        inputLat.addEventListener('input', () => {
            let val = inputLat.value.trim();
            
            // Normalize curly quotes, primes, smart quotes to standard ' and "
            val = val.replace(/[\u201C\u201D\u2033””]/g, '"')
                     .replace(/[\u2018\u2019\u2032’’]/g, "'");
            
            // 1. Check if it's standard decimal degrees separated by comma: e.g. "28.75925, 77.21083"
            const commaParts = val.split(',');
            if (commaParts.length === 2) {
                const parsedLat = parseFloat(commaParts[0].trim());
                const parsedLon = parseFloat(commaParts[1].trim());
                if (!isNaN(parsedLat) && !isNaN(parsedLon)) {
                    inputLat.value = parsedLat;
                    if (inputLon) inputLon.value = parsedLon;
                    return;
                }
            }
            
            // 2. Check if it's DMS coordinates separated by space: e.g. "28°45'33.3"N 77°12'39.0"E"
            const dmsParts = val.match(/([0-9\s°'".dms-]+[NSEWnsew])/g);
            if (dmsParts && dmsParts.length === 2) {
                const latVal = parseCoordinateToDecimal(dmsParts[0]);
                const lonVal = parseCoordinateToDecimal(dmsParts[1]);
                if (!isNaN(latVal) && !isNaN(lonVal)) {
                    inputLat.value = latVal.toFixed(6);
                    if (inputLon) inputLon.value = lonVal.toFixed(6);
                }
            }
        });
    }

    // Sidebar Tab Switching Logic
    const menuItems = document.querySelectorAll('.nav-menu-item');
    const tabPanels = document.querySelectorAll('.tab-panel');
    const activeTabTitle = document.getElementById('active-tab-title');
    const activeTabSubtitle = document.getElementById('active-tab-subtitle');

    const tabSubtitles = {
        'showcase': 'Smart Environmental Automation & Precision Agriculture Dashboard',
        'control-room': 'Live Microclimate Telemetry, Pump Status, & Smart Irrigation Rules',
        'satellite-map': 'High-Resolution Regional Mapping Overlay & Saved Field Bounds',
        'crop-doctor': 'Qualcomm QNN Quantized Leaf Diagnostics Feed & Speech Advisory'
    };

    const tabTitles = {
        'showcase': 'Project Showcase',
        'control-room': 'IoT Control Room',
        'satellite-map': 'Satellite Map Analyzer',
        'crop-doctor': 'AI Crop Doctor'
    };

    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            
            // Toggle active menu items
            menuItems.forEach(mi => mi.classList.remove('active'));
            item.classList.add('active');
            
            // Toggle active panels
            tabPanels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.id === `panel-${targetTab}`) {
                    panel.classList.add('active');
                }
            });

            // Update header text
            if (activeTabTitle) activeTabTitle.innerText = tabTitles[targetTab] || 'AgriGuardian';
            if (activeTabSubtitle) activeTabSubtitle.innerText = tabSubtitles[targetTab] || '';

            // Leaflet Map invalidateSize to recalculate map dimensions when tab reveals
            if (targetTab === 'satellite-map' && map) {
                setTimeout(() => {
                    map.invalidateSize();
                }, 150);
            }
        });
    });

    // AI Crop Doctor Drag and Drop / Upload Logic
    const leafDropZone = document.getElementById('leaf-drop-zone');
    const leafImageInput = document.getElementById('leaf-image-input');
    const leafPreviewImg = document.getElementById('leaf-preview-img');
    const btnWebScan = document.getElementById('btn-web-scan');
    const docPlaceholderState = document.getElementById('doc-placeholder-state');
    const docLoadingSpinner = document.getElementById('doc-loading-spinner');
    const webScanResult = document.getElementById('web-scan-result');

    // UI Result Elements
    const resDiseaseName = document.getElementById('res-disease-name');
    const resSeverityStatus = document.getElementById('res-severity-status');
    const resAdvisoryHindi = document.getElementById('res-advisory-hindi');
    const resActionsToday = document.getElementById('res-actions-today');
    const resActionsMid = document.getElementById('res-actions-mid');
    const resRecoveryTime = document.getElementById('res-recovery-time');

    let selectedLeafFile = null;

    if (leafDropZone && leafImageInput) {
        // Open file picker on click
        leafDropZone.addEventListener('click', () => {
            leafImageInput.click();
        });

        // Drag/Drop Listeners
        ['dragenter', 'dragover'].forEach(eventName => {
            leafDropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                leafDropZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            leafDropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                leafDropZone.classList.remove('dragover');
            }, false);
        });

        leafDropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0) {
                handleSelectedLeafFile(files[0]);
            }
        });

        leafImageInput.addEventListener('change', (e) => {
            if (leafImageInput.files && leafImageInput.files.length > 0) {
                handleSelectedLeafFile(leafImageInput.files[0]);
            }
        });
    }

    function handleSelectedLeafFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file (PNG, JPG, JPEG).');
            return;
        }
        selectedLeafFile = file;

        // Render preview image
        const reader = new FileReader();
        reader.onload = (e) => {
            // Hide the cloud upload icon and browse texts
            const cloudIcon = leafDropZone.querySelector('.cloud-icon');
            const dropText = leafDropZone.querySelector('.drop-text');
            if (cloudIcon) cloudIcon.style.display = 'none';
            if (dropText) dropText.style.display = 'none';

            // Show preview
            leafPreviewImg.src = e.target.result;
            leafPreviewImg.style.display = 'block';
            
            // Show action scan button
            btnWebScan.style.display = 'inline-flex';
        };
        reader.readAsDataURL(file);
    }

    if (btnWebScan) {
        btnWebScan.addEventListener('click', async () => {
            if (!selectedLeafFile) return;

            // Update UI to loading state
            docPlaceholderState.style.display = 'none';
            webScanResult.style.display = 'none';
            docLoadingSpinner.style.display = 'flex';
            btnWebScan.disabled = true;

            const formData = new FormData();
            formData.append('image', selectedLeafFile);

            try {
                const response = await fetch('/api/leaf/detect', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('Detection endpoint returned HTTP error ' + response.status);
                }

                const result = await response.json();
                console.log('Detection response:', result);

                // Populate Diagnostic Details
                let disease = result.disease || 'healthy';
                let severity = 'Healthy Crop';
                let isHealthy = disease.toLowerCase().includes('healthy');

                let advisory = result.advisory || 'आपकी पत्ती का चित्र स्वस्थ प्रतीत होता है।';
                let actionsToday = ['नियमित पानी देते रहें', 'खेत की निगरानी करें'];
                let actionsMid = ['बेहतर धूप का प्रबंध करें'];
                let recovery = 'N/A';

                if (!isHealthy) {
                    severity = 'Infection Detected';
                    actionsToday = ['रोगग्रस्त पत्तियों को तुरंत अलग करें', 'प्रभावित पौधों की कटाई करें'];
                    actionsMid = ['तांबे युक्त कवकनाशी (Fungicide) का छिड़काव करें', 'सिंचाई को अस्थायी रूप से कम करें'];
                    recovery = '7-14 Days';
                }

                if (result.status === 'low_confidence') {
                    disease = (result.top_predictions && result.top_predictions[0] && result.top_predictions[0].disease) || 'Unknown';
                    severity = 'Low Confidence Scan ⚠️';
                    advisory = 'पत्ती का चित्र स्पष्ट नहीं है। कृपया बेहतर रोशनी में साफ़ तस्वीर खींचकर पुनः अपलोड करें।';
                }

                // Render in DOM
                resDiseaseName.innerText = disease.replace(/_/g, ' ').toUpperCase();
                resSeverityStatus.innerText = severity;
                
                // Color formatting inline
                resSeverityStatus.style.background = isHealthy ? 'rgba(52, 211, 153, 0.12)' : 'rgba(251, 113, 133, 0.12)';
                resSeverityStatus.style.borderColor = isHealthy ? 'rgba(52, 211, 153, 0.25)' : 'rgba(251, 113, 133, 0.25)';
                resSeverityStatus.style.color = isHealthy ? 'var(--accent-pump)' : 'var(--accent-temp)';
                
                resAdvisoryHindi.innerText = advisory;
                
                // Render actions
                resActionsToday.innerHTML = actionsToday.map(act => `<li>${act}</li>`).join('');
                resActionsMid.innerHTML = actionsMid.map(act => `<li>${act}</li>`).join('');
                resRecoveryTime.innerText = recovery;

                // Toggle visibility
                docLoadingSpinner.style.display = 'none';
                webScanResult.style.display = 'flex';
            } catch (err) {
                console.error(err);
                docLoadingSpinner.style.display = 'none';
                docPlaceholderState.style.display = 'flex';
                alert('Web diagnostic scan failed: ' + err.message);
            } finally {
                btnWebScan.disabled = false;
            }
        });
    }

    const handleGpsKeyPress = (e) => {
        if (e.key === 'Enter' && btnUpdateGps) {
            btnUpdateGps.click();
        }
    };
    if (inputLat) inputLat.addEventListener('keypress', handleGpsKeyPress);
    if (inputLon) inputLon.addEventListener('keypress', handleGpsKeyPress);

    function sendControlCommand(action, value) {
        if (ws && ws.readyState === WebSocket.OPEN) {
            const cmd = JSON.stringify({ action, value });
            console.log('Sending command:', cmd);
            ws.send(cmd);
        } else {
            console.warn('Cannot send command. WebSocket is not open.');
        }
    }

    // Launch Web Socket Connection
    connectWebSocket();
});
