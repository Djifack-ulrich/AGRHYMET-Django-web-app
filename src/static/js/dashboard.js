$(document).ready(function() {
    // Initialiser la carte au chargement de la page
    const map = L.map('map-container').setView([20, 10], 5); // Coordonées par défaut
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    getGeoJSONData(map) 
    
    

    // Fonction pour charger les sous-variables dynamiquement
    function loadSubVariables(variable) {
        let subVariableOptions = [];
        if (variable === 'Consecutive Dry Days') {
            subVariableOptions = ['','30-day Plot', '30-day Plot + Anomaly'];
        } else if (variable === 'Total Rainfall in mm') {
            subVariableOptions = ['','30-day', 'Week 1', 'Week 2', 'Week 3', 'Week 4'];
        } else if (variable === 'Number of Rainy Days') {
            subVariableOptions = ['','Week 1 - 00 mm', 'Week 2 - 00 mm', 'Week 3 - 00 mm', 'Week 4 - 00 mm','Week 1 - 05 mm', 'Week 2 - 05 mm', 'Week 3 - 05 mm', 'Week 4 - 05 mm','Week 1 - 10 mm', 'Week 2 - 10 mm', 'Week 3 - 10 mm', 'Week 4 - 10 mm','Week 1 - 25 mm', 'Week 2 - 25 mm', 'Week 3 - 25 mm', 'Week 4 - 25 mm','Week 1 - 50 mm', 'Week 2 - 50 mm', 'Week 3 - 50 mm', 'Week 4 - 50 mm'];
        } else if (variable === 'Total Rainfall in mm') {
            subVariableOptions = ['','30-day', 'Week 1', 'Week 2', 'Week 3', 'Week 4'];
        } else if (variable === 'Total Rainfall in mm') {
            subVariableOptions = ['','30-day', 'Week 1', 'Week 2', 'Week 3', 'Week 4'];
        }
        
        // Remplir le menu déroulant des sous-variables
        $('#sub-variable-select').empty();
        subVariableOptions.forEach(function(option) {
            $('#sub-variable-select').append('<option value="' + option + '">' + option + '</option>');
        });
    }

    // Quand la variable est changée, recharger les sous-variables
    $('#variable-select').change(function() {
        const selectedVariable = $(this).val();
        loadSubVariables(selectedVariable);
    });

    // Fonction pour récupérer les données et les afficher
    var i =0
    function getData() {
        i=i+1;
        console.log(i)
        const region = $('#region-select').val();
        const variable = $('#variable-select').val();
        const subVariable = $('#sub-variable-select').val();
        document.getElementById('loader').style.display = 'block';

        $.get('/get_climate_data/', {
            region: region,
            variable: variable,
            sub_variable: subVariable
        }, function(data, textStatus, jqXHR) {
            console.log('Response Status:', textStatus);
            console.log('Received Data:', data); // Log the data received
        
            if (data && data.longitudes && data.latitudes && data.dataValue) {
                updateMap(data);
                // Masquer l'indicateur de chargement
                document.getElementById('loader').style.display = 'none';
            } else {
                console.warn('No data available, showing default map.');
                // Masquer l'indicateur de chargement
                document.getElementById('loader').style.display = 'none';
               // updateMap(); // Affiche une carte par défaut
            }
        });
    }

    // Fonction pour mettre à jour la carte
    // Variable pour stocker le tooltip actuel
    let currentTooltip = null;

    function updateMap(data = null) {
        // Supprimer les couches précédentes
        map.eachLayer(function(layer) {
            if (layer instanceof L.HeatLayer) {
                map.removeLayer(layer);
            }
        });
    
        if (data !== null) {
            // Préparer les données pour la heatmap
            const heatData = [];
            for (let i = 0; i < data.latitudes.length; i++) {
                for (let j = 0; j < data.longitudes.length; j++) {
                    if (data.dataValue[i][j] !== null) { // Vérifier que la valeur n'est pas nulle
                        heatData.push([data.latitudes[i], data.longitudes[j], data.dataValue[i][j]]);
                    }
                }
            }
    
            // Créer la heatmap
            const heatLayer = L.heatLayer(heatData, { radius: 3 }).addTo(map);
            console.log(data.metaData);
            var mapTitle = document.getElementById('mapTitle');
            var mapSubTitle = document.getElementById('mapSubTitle');
            mapTitle.textContent = `Interactive Map: ${data.metaData[0]|| ''}`;
            mapSubTitle.textContent = `${data.metaData[1] || ''}`;
    
            let currentTooltip = null;
    
            // Ajout du tooltip dynamique sur la carte
            map.on('mousemove', function(e) {
                const lat = e.latlng.lat;
                const lng = e.latlng.lng;
                const radiusP = 3;
                // Récupérer les précipitations dans un rayon de 5 unités autour du point survolé
                const dataValueInfo = getNearestDataValueInRadius(lat, lng, radiusP, data);
    
                // Fermer le tooltip précédent s'il existe
                if (currentTooltip) {
                    map.closeTooltip(currentTooltip);
                }
    
                // Afficher un nouveau tooltip si des données de précipitation sont trouvées
                if (dataValueInfo !==null) {
                    // Prendre la première valeur de précipitation (par exemple la plus proche)
                    const dataValue1Value = dataValueInfo.dataValue;
                    const variable = $('#variable-select').val();
    
                    currentTooltip = L.tooltip()
                        .setLatLng(e.latlng)
                        .setContent(`Latitude: ${lat.toFixed(2)}<br>Longitude: ${lng.toFixed(2)}<br>${variable}: ${dataValue1Value}`)
                        .openOn(map);
                }
            });
    
            // Gestionnaire d'événement lorsque la souris quitte la carte
            map.on('mouseout', function() {
                if (currentTooltip) {
                    map.closeTooltip(currentTooltip);
                    currentTooltip = null; // Réinitialiser la variable
                }
            });
        } else {
            // Afficher un message si aucune donnée
            console.log('Carte affichée sans données spécifiques.');
        }
    }
    

    // Fonction pour obtenir la valeur la plus proche dans un rayon donné autour d'une position
    function getNearestDataValueInRadius(lat, lng, radius, data) {
        let nearestDataValueInfo = null;
        let minDistance = Infinity; // Initialiser à une valeur très élevée
    
        for (let i = 0; i < data.latitudes.length; i++) {
            for (let j = 0; j < data.longitudes.length; j++) {
                const distance = getDistance(lat, lng, data.latitudes[i], data.longitudes[j]);
                if (distance <= radius && data.dataValue[i][j] !== null) {
                    // Vérifie si la distance est la plus petite trouvée jusqu'à présent
                    if (distance < minDistance) {
                        minDistance = distance;
                        nearestDataValueInfo = {
                            lat: data.latitudes[i],
                            lng: data.longitudes[j],
                            dataValue: data.dataValue[i][j]
                        };
                    }
                }
            }
        }
    
        return nearestDataValueInfo; // Retourne le point le plus proche ou null s'il n'y a pas de points dans le rayon
    }

    // Fonction pour calculer la distance entre deux points en utilisant la formule de Haversine
    function getDistance(lat1, lng1, lat2, lng2) {
        // Rayon de la Terre en km
        const R = 6371;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLng = (lng2 - lng1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        const distance = R * c; // distance en km

        return distance;
    }


    
    
    // Déclenche la récupération des données lorsque l'utilisateur change un paramètre
    $('#region-select, #variable-select, #sub-variable-select').change(function() {
        getData();
    });
    
    // Initialiser la carte et la première demande de données
    getData();
});
