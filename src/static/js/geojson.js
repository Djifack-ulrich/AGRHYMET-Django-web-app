// Function to load GeoJSON data and display it on the map
function getGeoJSONData(map) {
   // const geojsonUrl = "/static/custom.geo.json"; //"/static/merged_geojson2.geojson" URL of the GeoJSON file to load
    const levelSelect = document.getElementById("level-select");
    let geojsonUrl = "/static/custom.geo.json"; // Valeur par défaut

    let geoJSONLayer; // Variable pour stocker le calque GeoJSON

    levelSelect.addEventListener("change", function() {
        if (this.value === "region") {
            geojsonUrl = "/static/merged_geojson2.geojson"; // Modifier si "Région" est sélectionné
        } else {
            geojsonUrl = "/static/custom.geo.json"; // Valeur par défaut pour les autres options
        }
        
        // Affiche le loader pendant le chargement des données
        document.getElementById('loader').style.display = 'block';

        // Effacer le calque GeoJSON précédent si existant
        if (geoJSONLayer) {
            map.removeLayer(geoJSONLayer); // Retirer le calque précédent de la carte
        }

        // Charger le fichier GeoJSON
        fetch(geojsonUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error loading the GeoJSON file');
                }
                return response.json(); // Si la réponse est OK, la convertir en JSON
            })
            .then(data => {
                // Ajouter les données GeoJSON à la carte avec un style par défaut
                geoJSONLayer = L.geoJSON(data, { // Stocker le calque dans la variable
                    style: function() {
                        return { color: 'black', weight: 0.5 }; // Style par défaut pour les objets GeoJSON
                    },
                    onEachFeature: function(feature, layer) {
                        // Ajouter un gestionnaire d'événements click pour chaque feature dans le GeoJSON
                        layer.on('click', function() {
                            handleRegionClick(feature, layer, map); // Passer layer et map à la fonction
                        });
                    }
                }).addTo(map); // Ajouter les données GeoJSON à la carte

                // Masquer le loader après que les données ont été ajoutées à la carte
                document.getElementById('loader').style.display = 'none';
            })
            .catch(error => {
                console.error('Error loading the GeoJSON file:', error); // Journaliser l'erreur si le chargement échoue
                document.getElementById('loader').style.display = 'none'; // Masquer le loader même en cas d'erreur
            });
    });
}


// Function to handle the click event on a region (feature) in the GeoJSON
function handleRegionClick(feature, layer, map) {
    document.getElementById('loader').style.display = 'block';
    var latitudes = []; // Array to store the latitudes of the coordinates
    var longitudes = []; // Array to store the longitudes of the coordinates

    // Check if the geometry of the feature is a Polygon or MultiPolygon
    if (feature.geometry.type === "Polygon") {
        // If it's a Polygon, extract the coordinates of the first polygon
        feature.geometry.coordinates[0].forEach(coord => {
            longitudes.push(coord[0]); // Add the longitude
            latitudes.push(coord[1]); // Add the latitude
        });
    } else if (feature.geometry.type === "MultiPolygon") {
        // If it's a MultiPolygon, loop through all the polygons
        feature.geometry.coordinates.forEach(polygon => {
            polygon[0].forEach(coord => {
                longitudes.push(coord[0]);
                latitudes.push(coord[1]);
            });
        });
    }

    // Get the polygon coordinates to send to the backend
    const polygonCoordinates = JSON.stringify(feature.geometry.coordinates); // Convert coordinates to JSON
    const variable = $('#variable-select').val();
    const subVariable = $('#sub-variable-select').val();
    console.log(variable)

    // Prepare query parameters for the GET request
    const queryParams = {
        longitudes: longitudes,
        latitudes: latitudes,
        subVariable: subVariable,
        variable:variable
    };

    // Send the GET request using jQuery
    $.ajax({
        url: '/api_stats/',
        type: 'POST',
        contentType: 'application/json', // Spécifie que le contenu est au format JSON
        data: JSON.stringify(queryParams), // Convertit l'objet en chaîne JSON
        success: function(data) {
            // Process the received data to display a chart
            document.getElementById('loader').style.display = 'none';
            console.log(data.data.mean)
            const ctx = document.getElementById('stats').getContext('2d');
            if (window.myChart) {
                window.myChart.destroy();
            }
            window.myChart =new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.data.time, // Dates
                    datasets: [
                        { 
                            label: 'Moyenne', 
                            data: data.data.mean, 
                            borderColor: 'blue', 
                            fill: false
                        },
                        { 
                            label: 'Médiane', 
                            data: data.data.median, 
                            borderColor: 'green', 
                            fill: false 
                        },
                        { 
                            label: 'Min', 
                            data: data.data.min, 
                            borderColor: 'red', 
                            fill: false 
                        },
                        { 
                            label: 'Max', 
                            data: data.data.max, 
                            borderColor: 'purple', 
                            fill: false 
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Statistiques de Précipitations'
                        }
                    }
                }
            });
        },
        error: function(error) {
            console.error('Error sending data:', error); // Log the error if there's an issue with the request
        }
    });
    
    // Update the map style to highlight the clicked region
    map.eachLayer(function(l) {
        // Loop through each layer on the map and reset the style for other regions
        if (l instanceof L.GeoJSON && l !== layer) {
            l.setStyle({ color: 'black', weight: 0.5 }); // Reset the style for other regions
        }
    });

    // Apply an active style to the clicked region (e.g., make it red)
    layer.setStyle({ color: 'red', weight: 1 }); // Apply an active style (color it red)
}

