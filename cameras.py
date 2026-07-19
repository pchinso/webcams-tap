"""Lista de webcams publicas del Cantabrico: Galicia (A Marina) y Asturias.

Fuentes: red Webcams de Asturias / Hispacams (reproductor rtsp.me) y
Angelcam (Viveiro). "embed_url" es la pagina del reproductor de la que
main.py extrae la URL .m3u8 real del stream.

Ordenadas geograficamente de OESTE a ESTE siguiendo la costa (Viveiro ->
La Franca), de modo que "siguiente" recorre el litoral. Al final van las
camaras de interior.
"""

CAMERAS = [
    # ---- Galicia: A Marina / zona Estaca de Bares (oeste -> este) ----
    {
        "town": "Viveiro (Lugo)",
        "title": "Xardíns Noriega Varela e Ponte da Misericordia",
        "lat": 43.6620, "lon": -7.5960,
        "embed_url": "https://v.angelcam.com/iframe?v=enr0e6z7l8&autoplay=1",
    },
    {
        "town": "Burela (Lugo)",
        "title": "Playa de Portelo",
        "lat": 43.6570, "lon": -7.3590,
        "embed_url": "https://rtsp.me/embed/z2tN3n5E/",
    },
    {
        "town": "Burela (Lugo)",
        "title": "Playa de La Marosa",
        "lat": 43.6680, "lon": -7.3430,
        "embed_url": "https://rtsp.me/embed/BEiyZsYf/",
    },
    {
        "town": "Foz (Lugo)",
        "title": "Playa de A Rapadoira",
        "lat": 43.5700, "lon": -7.2530,
        "embed_url": "https://rtsp.me/embed/RGz7K6Y4/",
    },
    {
        "town": "Ribadeo / Castropol",
        "title": "Ría de Ribadeo - Puente de los Santos",
        "lat": 43.5450, "lon": -7.0300,
        "embed_url": "https://rtsp.me/embed/TEsbennT/",
    },

    # ---- Asturias occidente (oeste -> este) ----
    {
        "town": "Figueras (Castropol)",
        "title": "Puerto de As Figueiras",
        "lat": 43.5410, "lon": -7.0080,
        "embed_url": "https://rtsp.me/embed/TkhT3d96/",
    },
    {
        "town": "Castropol",
        "title": "Playa de Peñarronda",
        "lat": 43.5530, "lon": -6.9980,
        "embed_url": "https://rtsp.me/embed/BrKdaEZT/",
    },
    {
        "town": "Tapia de Casariego",
        "title": "Playa de Serantes",
        "lat": 43.5610, "lon": -6.9760,
        "embed_url": "https://rtsp.me/embed/rdQNzD5k/",
    },
    {
        "town": "Tapia de Casariego",
        "title": "Puerto de Tapia",
        "lat": 43.5730, "lon": -6.9440,
        "embed_url": "https://rtsp.me/embed/yeibQrzh/",
    },
    {
        "town": "Tapia de Casariego",
        "title": "Puerto de Tapia II",
        "lat": 43.5731, "lon": -6.9435,
        "embed_url": "https://rtsp.me/embed/ThQGS3dy/",
    },
    {
        "town": "Tapia de Casariego",
        "title": "Playa de Tapia (Anguileiro o La Grande)",
        "lat": 43.5720, "lon": -6.9450,
        "embed_url": "https://rtsp.me/embed/SdzF8ESr/",
    },
    {
        "town": "Tapia de Casariego",
        "title": "Playa La Grande",
        "lat": 43.5715, "lon": -6.9455,
        "embed_url": "https://rtsp.me/embed/SQQzSKaA/",
    },
    {
        "town": "El Franco",
        "title": "Playa de Porcía",
        "lat": 43.5590, "lon": -6.8990,
        "embed_url": "https://rtsp.me/embed/8HsN8QHd/",
    },
    {
        "town": "Viavélez (El Franco)",
        "title": "Puerto de Viavélez",
        "lat": 43.5580, "lon": -6.8430,
        "embed_url": "https://rtsp.me/embed/58da726b/",
    },
    {
        "town": "El Franco",
        "title": "Playa de Pormenande",
        "lat": 43.5560, "lon": -6.8280,
        "embed_url": "https://rtsp.me/embed/8rBfH3YK/",
    },
    {
        "town": "Ortiguera (Coaña)",
        "title": "Playa de Arnielles",
        "lat": 43.5660, "lon": -6.7440,
        "embed_url": "https://rtsp.me/embed/sEkZEHEs/",
    },
    {
        "town": "Navia",
        "title": "Playa de Navia",
        "lat": 43.5430, "lon": -6.7220,
        "embed_url": "https://rtsp.me/embed/GK2E7tkF/",
    },
    {
        "town": "Navia",
        "title": "Playa de Frejulfe",
        "lat": 43.5560, "lon": -6.6780,
        "embed_url": "https://rtsp.me/embed/s2NhG4Nd/",
    },
    {
        "town": "Luarca (Valdés)",
        "title": "Acantilados de Luarca",
        "lat": 43.5480, "lon": -6.5390,
        "embed_url": "https://rtsp.me/embed/Nete9RKA/",
    },
    {
        "town": "Luarca (Valdés)",
        "title": "Panorámica del Puerto de Luarca",
        "lat": 43.5450, "lon": -6.5350,
        "embed_url": "https://rtsp.me/embed/Ti49NGnd/",
    },
    {
        "town": "Cudillero",
        "title": "Playa Concha de Artedo",
        "lat": 43.5670, "lon": -6.1940,
        "embed_url": "https://rtsp.me/embed/7ZD9SkQF/",
    },
    {
        "town": "Cudillero",
        "title": "Playa San Pedro de la Ribera",
        "lat": 43.5660, "lon": -6.1870,
        "embed_url": "https://rtsp.me/embed/Fd8dSQre/",
    },
    {
        "town": "Cudillero",
        "title": "Plaza de la Marina - Ayuntamiento",
        "lat": 43.5630, "lon": -6.1450,
        "embed_url": "https://rtsp.me/embed/4FREaN3F/",
    },
    {
        "town": "Muros de Nalón",
        "title": "Playas de Campofrío y Aguilar",
        "lat": 43.5580, "lon": -6.1070,
        "embed_url": "https://rtsp.me/embed/DsrHF74h/",
    },
    {
        "town": "Muros de Nalón",
        "title": "Playa de Aguilar II",
        "lat": 43.5578, "lon": -6.1060,
        "embed_url": "https://rtsp.me/embed/Qdrh8Qbb/",
    },
    {
        "town": "San Esteban de Pravia",
        "title": "Desembocadura del río Nalón",
        "lat": 43.5590, "lon": -6.0830,
        "embed_url": "https://rtsp.me/embed/db6zNhf9/",
    },
    {
        "town": "San Esteban de Pravia",
        "title": "Bocana de San Esteban de Pravia",
        "lat": 43.5610, "lon": -6.0800,
        "embed_url": "https://rtsp.me/embed/8YhQG32T/",
    },
    {
        "town": "San Juan de la Arena",
        "title": "Playa de Los Quebrantos",
        "lat": 43.5590, "lon": -6.0650,
        "embed_url": "https://rtsp.me/embed/iZBbNZEG/",
    },
    {
        "town": "San Juan de la Arena",
        "title": "Muelle de San Juan de la Arena",
        "lat": 43.5560, "lon": -6.0620,
        "embed_url": "https://rtsp.me/embed/Si7eASDB/",
    },
    {
        "town": "Salinas (Castrillón)",
        "title": "Playa de Salinas",
        "lat": 43.5760, "lon": -5.9600,
        "embed_url": "https://rtsp.me/embed/Z8nGKR9k/",
    },
    {
        "town": "Xagó (Gozón)",
        "title": "Playa de Xagó",
        "lat": 43.5960, "lon": -5.7220,
        "embed_url": "https://rtsp.me/embed/5dRkhTK7/",
    },
    {
        "town": "Xagó (Gozón)",
        "title": "Playa de Xagó - Panorámica",
        "lat": 43.5970, "lon": -5.7210,
        "embed_url": "https://rtsp.me/embed/nsdBY5nz/",
    },
    {
        "town": "Luanco (Gozón)",
        "title": "Muelle de Luanco",
        "lat": 43.6150, "lon": -5.7920,
        "embed_url": "https://rtsp.me/embed/8htntQtQ/",
    },
    {
        "town": "Luanco (Gozón)",
        "title": "Playa de La Ribera",
        "lat": 43.6130, "lon": -5.7930,
        "embed_url": "https://rtsp.me/embed/AT8nniiG/",
    },
    {
        "town": "Luanco (Gozón)",
        "title": "Vista panorámica de Luanco",
        "lat": 43.6140, "lon": -5.7900,
        "embed_url": "https://rtsp.me/embed/4N5f4yt7/",
    },
    {
        "town": "Candás (Carreño)",
        "title": "Paseo marítimo de Candás",
        "lat": 43.5880, "lon": -5.7580,
        "embed_url": "https://rtsp.me/embed/hsDSN6rh/",
    },
    {
        "town": "Xivares (Carreño)",
        "title": "Playa de Xivares",
        "lat": 43.5730, "lon": -5.7000,
        "embed_url": "https://rtsp.me/embed/9QzGk2QD/",
    },
    {
        "town": "Gijón",
        "title": "Puerto Deportivo - Poniente",
        "lat": 43.5450, "lon": -5.6700,
        "embed_url": "https://rtsp.me/embed/ekY9K3Ra/",
    },
    {
        "town": "Gijón",
        "title": "Playa de Poniente - Fomento",
        "lat": 43.5440, "lon": -5.6680,
        "embed_url": "https://rtsp.me/embed/tbdN5Ybr/",
    },
    {
        "town": "Gijón",
        "title": "Iglesia de San Pedro - Cimadevilla",
        "lat": 43.5460, "lon": -5.6600,
        "embed_url": "https://rtsp.me/embed/8NEeNBRH/",
    },
    {
        "town": "Gijón",
        "title": "Playa de San Lorenzo - La Escalerona",
        "lat": 43.5410, "lon": -5.6570,
        "embed_url": "https://rtsp.me/embed/akBSN4td/",
    },
    {
        "town": "Gijón",
        "title": "Playa de San Lorenzo - Panorámica",
        "lat": 43.5400, "lon": -5.6500,
        "embed_url": "https://rtsp.me/embed/Kb6ZRK6F/",
    },
    {
        "town": "Gijón",
        "title": "Playa de San Lorenzo - El Tostaderu",
        "lat": 43.5390, "lon": -5.6440,
        "embed_url": "https://rtsp.me/embed/67Q26etY/",
    },
    {
        "town": "Gijón",
        "title": "Playa de Estaño",
        "lat": 43.5450, "lon": -5.5900,
        "embed_url": "https://rtsp.me/embed/2FYB4iG9/",
    },
    {
        "town": "Villaviciosa",
        "title": "Playa de La Ñora",
        "lat": 43.5450, "lon": -5.5650,
        "embed_url": "https://rtsp.me/embed/Hh6Da3Q8/",
    },
    {
        "town": "Quintes (Villaviciosa)",
        "title": "Playa España",
        "lat": 43.5480, "lon": -5.5310,
        "embed_url": "https://rtsp.me/embed/9taDa6b8/",
    },
    {
        "town": "Tazones (Villaviciosa)",
        "title": "Puerto de Tazones",
        "lat": 43.5460, "lon": -5.3990,
        "embed_url": "https://rtsp.me/embed/YRdYbASy/",
    },
    {
        "town": "Tazones (Villaviciosa)",
        "title": "Playa de Tazones",
        "lat": 43.5450, "lon": -5.3970,
        "embed_url": "https://rtsp.me/embed/HSDKT2aZ/",
    },
    {
        "town": "Rodiles (Villaviciosa)",
        "title": "Surf - Barra de la Playa de Rodiles",
        "lat": 43.5310, "lon": -5.3850,
        "embed_url": "https://rtsp.me/embed/BRhbQzb9/",
    },
    {
        "town": "Rodiles (Villaviciosa)",
        "title": "Playa de Rodiles",
        "lat": 43.5290, "lon": -5.3830,
        "embed_url": "https://rtsp.me/embed/Kh6Z3n4i/",
    },
    {
        "town": "Lastres (Colunga)",
        "title": "Mirador de San Roque",
        "lat": 43.5170, "lon": -5.2700,
        "embed_url": "https://rtsp.me/embed/i9Ki4bYG/",
    },
    {
        "town": "Lastres (Colunga)",
        "title": "Puerto de Lastres",
        "lat": 43.5110, "lon": -5.2650,
        "embed_url": "https://rtsp.me/embed/khA4kE68/",
    },
    {
        "town": "Lastres (Colunga)",
        "title": "Puerto y muelle de Lastres",
        "lat": 43.5112, "lon": -5.2660,
        "embed_url": "https://rtsp.me/embed/i67YHdFQ/",
    },
    {
        "town": "Colunga",
        "title": "Playa de La Griega",
        "lat": 43.5000, "lon": -5.2570,
        "embed_url": "https://rtsp.me/embed/hkY96G3f/",
    },
    {
        "town": "Caravia",
        "title": "Playa Arenal de Morís",
        "lat": 43.4700, "lon": -5.1460,
        "embed_url": "https://rtsp.me/embed/Shy68RNk/",
    },
    {
        "town": "Caravia",
        "title": "Arenal de Morís",
        "lat": 43.4700, "lon": -5.1450,
        "embed_url": "https://rtsp.me/embed/3ZDHGQTd/",
    },
    {
        "town": "Caravia",
        "title": "Costa de Caravia - Arenal de Morís II",
        "lat": 43.4700, "lon": -5.1430,
        "embed_url": "https://rtsp.me/embed/tAQ65BKB/",
    },
    {
        "town": "Caravia",
        "title": "Playas de El Viso",
        "lat": 43.4720, "lon": -5.1310,
        "embed_url": "https://rtsp.me/embed/2HD7EnyK/",
    },
    {
        "town": "Caravia",
        "title": "Playas de La Espasa y La Isla",
        "lat": 43.4720, "lon": -5.1250,
        "embed_url": "https://rtsp.me/embed/QzTGKEaQ/",
    },
    {
        "town": "Caravia",
        "title": "Playa de La Espasa",
        "lat": 43.4720, "lon": -5.1220,
        "embed_url": "https://rtsp.me/embed/5ByRFKFk/",
    },
    {
        "town": "Caravia",
        "title": "Playa de La Espasa II",
        "lat": 43.4721, "lon": -5.1210,
        "embed_url": "https://rtsp.me/embed/QY9k5E7a/",
    },
    {
        "town": "Vega (Ribadesella)",
        "title": "Playa de Vega",
        "lat": 43.4730, "lon": -5.1030,
        "embed_url": "https://rtsp.me/embed/9d6iFr5a/",
    },
    {
        "town": "Ribadesella",
        "title": "Barra de Ribadesella",
        "lat": 43.4640, "lon": -5.0670,
        "embed_url": "https://rtsp.me/embed/8zBzaTzZ/",
    },
    {
        "town": "Ribadesella",
        "title": "La Guía - Playa de Santa Marina",
        "lat": 43.4630, "lon": -5.0640,
        "embed_url": "https://rtsp.me/embed/YBdaibQA/",
    },
    {
        "town": "Ribadesella",
        "title": "Playa de Santa Marina",
        "lat": 43.4620, "lon": -5.0600,
        "embed_url": "https://rtsp.me/embed/YBFFAhDY/",
    },
    {
        "town": "Ribadesella",
        "title": "Paseo Princesa Letizia",
        "lat": 43.4610, "lon": -5.0580,
        "embed_url": "https://rtsp.me/embed/NH5DZBkz/",
    },
    {
        "town": "Bedón (Llanes)",
        "title": "Playa de San Antolín",
        "lat": 43.4410, "lon": -4.8850,
        "embed_url": "https://rtsp.me/embed/5eYFHiYz/",
    },
    {
        "town": "Barro (Llanes)",
        "title": "Playa de Barro",
        "lat": 43.4320, "lon": -4.8330,
        "embed_url": "https://rtsp.me/embed/8TfYQ5fr/",
    },
    {
        "town": "Celoriu (Llanes)",
        "title": "Playas Las Cámaras y La Palombina",
        "lat": 43.4310, "lon": -4.8210,
        "embed_url": "https://rtsp.me/embed/25YiEBZH/",
    },
    {
        "town": "Celorio (Llanes)",
        "title": "Playa Palombina",
        "lat": 43.4310, "lon": -4.8180,
        "embed_url": "https://rtsp.me/embed/Hf8HrKNs/",
    },
    {
        "town": "Poo (Llanes)",
        "title": "Playa de Poo",
        "lat": 43.4250, "lon": -4.7750,
        "embed_url": "https://rtsp.me/embed/8ad2ysdB/",
    },
    {
        "town": "Llanes",
        "title": "El Sablón - Los Cubos de la Memoria",
        "lat": 43.4220, "lon": -4.7570,
        "embed_url": "https://rtsp.me/embed/GEbi35NS/",
    },
    {
        "town": "Llanes",
        "title": "Puerto de Llanes",
        "lat": 43.4210, "lon": -4.7500,
        "embed_url": "https://rtsp.me/embed/SfETz5yS/",
    },
    {
        "town": "Llanes",
        "title": "Playa de Toro - Mirador de Toro",
        "lat": 43.4200, "lon": -4.7400,
        "embed_url": "https://rtsp.me/embed/yGTbHyak/",
    },
    {
        "town": "Andrín (Llanes)",
        "title": "Playa de Andrín",
        "lat": 43.4100, "lon": -4.7050,
        "embed_url": "https://rtsp.me/embed/Q6EtfHKS/",
    },
    {
        "town": "Ribadedeva",
        "title": "Playa de La Franca",
        "lat": 43.3930, "lon": -4.5770,
        "embed_url": "https://rtsp.me/embed/k3HG9EzQ/",
    },

    # ---- Interior / extras ----
    {
        "town": "Avilés",
        "title": "Parque del Muelle",
        "lat": 43.5580, "lon": -5.9230,
        "embed_url": "https://rtsp.me/embed/SYfAkr64/",
    },
    {
        "town": "Oviedo",
        "title": "Oviedo desde El Naranco",
        "lat": 43.3603, "lon": -5.8448,
        "embed_url": "https://rtsp.me/embed/6BhtYDbb/",
    },
    {
        "town": "Somiedo",
        "title": "Pola de Somiedo",
        "lat": 43.0967, "lon": -6.2537,
        "embed_url": "https://rtsp.me/embed/SQ24Da4N/",
    },
    {
        "town": "Pajares (Lena)",
        "title": "Estación Valgrande-Pajares - Cueto Negro / Ubiñas",
        "lat": 42.9897, "lon": -5.7639,
        "embed_url": "https://rtsp.me/embed/rZFSk9tT/",
    },

    # ---- Galicia: Costa da Morte / A Coruña / Ferrol / Ortigueira ----
    # Añadidas al FINAL a propósito, no reordenadas por posición geográfica:
    # captura_eclipse.py indexa las carpetas de capturas/ por posición en
    # esta lista (slug() -> "NN-..."), y ya hay campaña en marcha (desde
    # 17-07-2026). Insertarlas antes desplazaría el índice de las 80
    # cámaras existentes y rompería la serie histórica. Fuentes: Hispacams
    # (rtsp.me) para Fisterra, y G24/CRTVG (radiotelevisión pública de
    # Galicia, streams .m3u8 propios y permanentes) para el resto.
    {
        "town": "Fisterra (A Coruña)",
        "title": "Puerto de Finisterre",
        "lat": 42.9052, "lon": -9.2607,
        "embed_url": "https://rtsp.me/embed/irH5ShN2/",
    },
    {
        "town": "Fisterra (A Coruña)",
        "title": "Playa Langosteira",
        "lat": 42.8958, "lon": -9.2711,
        "embed_url": "https://rtsp.me/embed/3htHTKKr/",
    },
    {
        "town": "Fisterra (A Coruña)",
        "title": "Cabo Fisterra",
        "lat": 42.8797, "lon": -9.2879,
        "embed_url": "https://www.g24.gal/-/cabo-fisterra",
    },
    {
        "town": "Muxía (A Coruña)",
        "title": "Muxía",
        "lat": 43.1043, "lon": -9.2196,
        "embed_url": "https://www.g24.gal/-/mux%C3%ADa",
    },
    {
        "town": "A Coruña",
        "title": "A Coruña - panorámica fija",
        "lat": 43.3623, "lon": -8.4115,
        "embed_url": "https://www.g24.gal/-/a-coru%C3%B1a-fixa-",
    },
    {
        "town": "A Coruña",
        "title": "A Coruña - cámara móvil",
        "lat": 43.3623, "lon": -8.4115,
        "embed_url": "https://www.g24.gal/-/a-coru%C3%B1a-1",
    },
    {
        "town": "Ferrol (A Coruña)",
        "title": "Ferrol",
        "lat": 43.4832, "lon": -8.2372,
        "embed_url": "https://www.g24.gal/-/ferrol",
    },
    {
        "town": "Ortigueira (A Coruña)",
        "title": "Ortigueira",
        "lat": 43.6924, "lon": -7.8532,
        "embed_url": "https://www.g24.gal/-/ortigueira",
    },
]
