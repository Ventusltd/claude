# Published-release link and sentinel crawl

Crawled from GitHub Actions against the LIVE origins, one runner per surface.
INFORMATIONAL: the job exits 0 on every finding. A 404 below is a fact to read,
not an alarm that mailed anyone.

- crawled at: `2026-09-03T23:39:31Z`
- releases crawled: 76 (34 whose page did not answer)
- routes checked: 994, dead: 175
- sentinels checked: 38, dead: 9, **dead AND shipped: 9**

A sentinel is *shipped* when its base URL appears in a module the page actually
imports. A dead sentinel that is only *declared* is a stale record in a manifest.
A dead sentinel that is shipped is what a user gets when they click.

## `globalgrid2050` - 1 releases, 1/107 routes dead, 0/0 sentinels dead (0 shipped)

crawled in 1.2s

| release | state | page | routes dead | sentinels dead (shipped) |
|---|---|---|---|---|
| `homepage` | routes-dead | 200 | 1/107 | 0/0 (0) |

<details><summary>1 distinct dead URLs on this surface</summary>

| status + url | seen in N releases |
|---|---|
| `404` `https://globalgrid2050.com/${encodeURI(r.url)}` | 1 |

</details>

## `gridatlas-atlas` - 10 releases, 170/238 routes dead, 0/0 sentinels dead (0 shipped)

crawled in 3.6s

| release | state | page | routes dead | sentinels dead (shipped) |
|---|---|---|---|---|
| `202608300453-atlas-v9` | routes-dead | 200 | 29/45 | 0/0 (0) |
| `202608292311-atlas-v9` | routes-dead | 200 | 29/45 | 0/0 (0) |
| `202608292126-atlas-v9` | routes-dead | 200 | 29/45 | 0/0 (0) |
| `202608291818-atlas-v9` | routes-dead | 200 | 40/44 | 0/0 (0) |
| `202608291758-atlas-v9` | routes-dead | 200 | 40/43 | 0/0 (0) |
| `202608291430-atlas-v9` | routes-dead | 200 | 1/4 | 0/0 (0) |
| `202608291239-atlas-v9` | routes-dead | 200 | 1/4 | 0/0 (0) |
| `202608291237-atlas-v9` | routes-dead | 200 | 1/4 | 0/0 (0) |

<details><summary>140 distinct dead URLs on this surface</summary>

| status + url | seen in N releases |
|---|---|
| `404` `https://ventusltd.github.io/uk_metros_trams.geojson` | 5 |
| `404` `https://ventusltd.github.io/uk_mainline_railways.geojson` | 5 |
| `404` `https://ventusltd.github.io/uk_motorways.geojson` | 5 |
| `404` `https://ventusltd.github.io/uk_trunk_roads.geojson` | 5 |
| `404` `https://ventusltd.github.io/uk_primary_roads.geojson` | 5 |
| `404` `https://ventusltd.github.io/heavy_emitters_uk.json` | 5 |
| `404` `https://ventusltd.github.io/dist/repd_master.json` | 5 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/` | 3 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/grid_11kv_ukpn.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/supermarkets_tesco.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/supermarkets_sainsburys.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/supermarkets_asda.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/supermarkets_morrisons.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/supermarkets_aldi.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/supermarkets_lidl.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/supermarkets_waitrose.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/supermarkets_ms.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/supermarkets_coop.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/supermarkets_costco.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/supermarkets_booths.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/elizabeth_line.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/london_underground.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/hs2.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/eurostar.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/stadiums.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/subsea_data_cables.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/global_ports.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/global_hydrocarbons.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/motorway_services.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/data/ev_chargers.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/grid_11kv_ukpn.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/supermarkets_tesco.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/supermarkets_sainsburys.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/supermarkets_asda.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/supermarkets_morrisons.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/supermarkets_aldi.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/supermarkets_lidl.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/supermarkets_waitrose.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/supermarkets_ms.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/supermarkets_coop.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/supermarkets_costco.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/supermarkets_booths.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/elizabeth_line.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/london_underground.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/hs2.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/eurostar.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/stadiums.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/subsea_data_cables.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/global_ports.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/global_hydrocarbons.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/motorway_services.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292311-atlas-v9/data/ev_chargers.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292126-atlas-v9/data/grid_11kv_ukpn.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292126-atlas-v9/data/supermarkets_tesco.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292126-atlas-v9/data/supermarkets_sainsburys.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292126-atlas-v9/data/supermarkets_asda.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292126-atlas-v9/data/supermarkets_morrisons.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292126-atlas-v9/data/supermarkets_aldi.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292126-atlas-v9/data/supermarkets_lidl.geojson` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/atlas/releases/202608292126-atlas-v9/data/supermarkets_waitrose.geojson` | 1 |
| ... 80 more | |

</details>

## `pipelinenews-intel` - 29 releases, 0/609 routes dead, 0/29 sentinels dead (0 shipped)

crawled in 13.4s

Every release on this surface answered 200 on every route and sentinel.

## `pipelinenews-releases` - 36 releases, 4/40 routes dead, 9/9 sentinels dead (9 shipped)

crawled in 2.1s

| release | state | page | routes dead | sentinels dead (shipped) |
|---|---|---|---|---|
| `202609032329-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202609032251-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202609032159-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202609031308-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202609030009-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202609022308-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202609021945-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202609020611-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202609020552-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202609020025-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202609020010-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202609012326-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608312339-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608312337-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608312244-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608312212-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608312202-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608312145-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608312114-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608312109-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608312056-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608312037-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608312018-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608311858-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608311816-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608311800-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608311731-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608311645-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608311610-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608311558-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608311557-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608311550-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608311530-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608311343-pipelinenews` | page-unreachable | 404 | 0/0 | 0/0 (0) |
| `202608300309-pipelinenews` | sentinels-dead | 200 | 2/20 | 1/1 (1) |
| `202608291447-pipelinenews` | sentinels-dead | 200 | 2/20 | 8/8 (8) |

<details><summary>11 distinct dead URLs on this surface</summary>

| status + url | seen in N releases |
|---|---|
| `404` `https://ventusltd.github.io/gridatlas/202608300453-atlas-v9/` | 2 |
| `404` `https://ventusltd.github.io/gridatlas/202608291430-atlas-v9/` | 2 |
| `404` `https://ventusltd.github.io/gridatlas/202608300453-atlas-v9/?repd_ref=13599` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/202608291430-atlas-v9/?repd_ref=16135` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/202608291430-atlas-v9/?repd_ref=17494` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/202608291430-atlas-v9/?repd_ref=13599` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/202608291430-atlas-v9/?repd_ref=12453` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/202608291430-atlas-v9/?repd_ref=2484` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/202608291430-atlas-v9/?repd_ref=12780` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/202608291430-atlas-v9/?repd_ref=2535` | 1 |
| `404` `https://ventusltd.github.io/gridatlas/202608291430-atlas-v9/?repd_ref=13429` | 1 |

</details>

