# Influence of parking pricing on effective accessibility of urban sub-centres 🌃

[![Python](https://img.shields.io/badge/python-3.9.12-green.svg)](https://www.python.org/)
[![Conda](https://img.shields.io/badge/conda-4.10.3-green.svg)](https://docs.conda.io/en/latest/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Acknowledgement

A huge gratitude goes to [Egor Kotov](https://github.com/e-kotov) for his help throughout the work.

## What is it about?
Many cities are actively adopting paid parking policy. While economical reasons are clear — welfare inefficiency of free parking (reflected in pollution and road congestion) — there is still an interesting question about the effect of this policy on accessibility. This case study is trying to show if there is a possibility that welfare increase is going to be undermined by decreasing the economic potential of urban sub-centres.  
The city chosen for the case study is [Kazan, Russia](https://en.wikipedia.org/wiki/Kazan).

## Data analysis
To conduct the research, there was some data gathered and analysed:
1. Public transport telemetry data mined from [busti.me](https://busti.me/)
2. Population data mined from [electoral data](https://www.cikrf.ru), [Federal Information Address System](https://fias.nalog.ru) and [Yandex.Maps](https://yandex.ru/maps/)
3. Employment data exported from [Federal Tax Service](https://www.nalog.gov.ru)
4. Kazan public parking lots data from [parkingkzn.ru](https://parkingkzn.ru/en/)
5. General spatial data from OSM ([openstreetmap.org](https://www.openstreetmap.org/) + [overpass-turbo.eu](http://overpass-turbo.eu/))  

This data has been transformed as such:
1. Filtered telemetry from outliers
2. Aggregated PT stops with K-means and built Voronoi polygons from stops clusters
3. Calculated OD-matrices for public transport and cars (using [OSRM](https://github.com/Project-OSRM/osrm-backend) for cars)
4. Calculated accessibility with pure time OD, [effective costs](https://www.sciencedirect.com/science/article/abs/pii/S1361920919316694) and adjusted parking costs

## Tech stack
- Python 3.9.12
- Conda 4.10.3
- PostgreSQL 14.2
- OSRM-backend 5.26.0
- QGIS 3.22.2-Białowieża (for ad-hoc data wrangling)
- Tableau Public 2021.4.4 (data visualization in the paper)