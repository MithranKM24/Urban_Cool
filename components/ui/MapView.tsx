"use client";

import { useEffect, useRef, useState } from "react";
import maplibregl, { type Map as MapLibreMap, type MapMouseEvent } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { MetricDefinition } from "@/lib/metrics";
import type { RegionFeature } from "@/lib/api-types";

interface MapViewProps {
  metric: MetricDefinition;
  metricData?: GeoJSON.FeatureCollection;
  dataProperty?: string;
  onRegionSelected?: (region: RegionFeature) => void;
}

const chennaiBoundary = {
  type: "FeatureCollection" as const,
  features: [
    {
      type: "Feature" as const,
      properties: { region: "Central" },
      geometry: { type: "Polygon" as const, coordinates: [[
        [80.1573, 13.141], [80.145, 13.1383], [80.1473, 13.1275], [80.1431, 13.124],
        [80.1399, 13.0979], [80.1456, 13.087], [80.1536, 13.0822], [80.1607, 13.0796],
        [80.1627, 13.0837], [80.1731, 13.0814], [80.1771, 13.0721], [80.1903, 13.0735],
        [80.1913, 13.0625], [80.1854, 13.0516], [80.1912, 13.0255], [80.1958, 13.0288],
        [80.2078, 13.0271], [80.212, 13.0201], [80.2235, 13.016], [80.2291, 13.0248],
        [80.2244, 13.0253], [80.2258, 13.0306], [80.2307, 13.0307], [80.2312, 13.0261],
        [80.2391, 13.0319], [80.24, 13.0271], [80.2492, 13.0185], [80.2596, 13.0256],
        [80.2783, 13.0219], [80.2825, 13.0576], [80.2859, 13.0573], [80.2896, 13.0673],
        [80.2807, 13.0689], [80.2797, 13.0645], [80.2736, 13.0667], [80.2709, 13.059],
        [80.2654, 13.0582], [80.2637, 13.0628], [80.2569, 13.0612], [80.2496, 13.0711],
        [80.2558, 13.0813], [80.2569, 13.0908], [80.2692, 13.0906], [80.2729, 13.0936],
        [80.2721, 13.1069], [80.2708, 13.1049], [80.2652, 13.1097], [80.2524, 13.1084],
        [80.2511, 13.1154], [80.2435, 13.1131], [80.2461, 13.1196], [80.2427, 13.1276],
        [80.2424, 13.1223], [80.233, 13.123], [80.2332, 13.1264], [80.2267, 13.1258],
        [80.2246, 13.1294], [80.2164, 13.1308], [80.1947, 13.1283], [80.1881, 13.1389],
        [80.1824, 13.1352], [80.1684, 13.1411], [80.1644, 13.1338], [80.1573, 13.141],
      ]] },
    },
    {
      type: "Feature" as const,
      properties: { region: "South" },
      geometry: { type: "Polygon" as const, coordinates: [[
        [80.1631, 13.0836], [80.16, 13.0788], [80.1629, 13.0644], [80.1607, 13.041],
        [80.1456, 13.0403], [80.1493, 13.0482], [80.1531, 13.0484], [80.1493, 13.0507],
        [80.1547, 13.0521], [80.1546, 13.0614], [80.1498, 13.0635], [80.1489, 13.0535],
        [80.142, 13.0532], [80.1419, 13.0488], [80.1355, 13.0488], [80.1341, 13.0449],
        [80.1407, 13.0453], [80.1416, 13.0385], [80.1466, 13.0363], [80.1444, 13.0214],
        [80.1472, 13.017], [80.1555, 13.013], [80.1614, 13.0143], [80.1588, 13.0069],
        [80.1633, 13.0063], [80.1602, 12.997], [80.167, 12.9839], [80.1659, 12.9801],
        [80.1765, 12.979], [80.1764, 12.971], [80.1817, 12.9681], [80.1909, 12.9686],
        [80.1876, 12.9583], [80.192, 12.9575], [80.1903, 12.9544], [80.1927, 12.9517],
        [80.2016, 12.9524], [80.1993, 12.9408], [80.1924, 12.9347], [80.1959, 12.9338],
        [80.1949, 12.9256], [80.1976, 12.9239], [80.1946, 12.91], [80.214, 12.9093],
        [80.2133, 12.8916], [80.208, 12.875], [80.2132, 12.8605], [80.2199, 12.8525],
        [80.2322, 12.8521], [80.237, 12.8591], [80.2491, 12.8571], [80.2624, 12.9564],
        [80.2782, 13.0218], [80.2596, 13.0256], [80.2492, 13.0185], [80.24, 13.0271],
        [80.2391, 13.0319], [80.2312, 13.0261], [80.2307, 13.0307], [80.2258, 13.0306],
        [80.2244, 13.0253], [80.2291, 13.0248], [80.2235, 13.016], [80.212, 13.0201],
        [80.2078, 13.0271], [80.1958, 13.0288], [80.1912, 13.0255], [80.1854, 13.0516],
        [80.1913, 13.0625], [80.1903, 13.0734], [80.1771, 13.0721], [80.1731, 13.0814],
        [80.1631, 13.0836],
      ]] },
    },
    {
      type: "Feature" as const,
      properties: { region: "North" },
      geometry: { type: "Polygon" as const, coordinates: [[
        [80.3252, 13.2126], [80.3315, 13.2323], [80.3273, 13.235], [80.3178, 13.2311],
        [80.3063, 13.2116], [80.301, 13.2109], [80.2978, 13.2172], [80.2892, 13.221],
        [80.2839, 13.2274], [80.2672, 13.224], [80.2724, 13.2167], [80.2701, 13.2036],
        [80.2505, 13.206], [80.2494, 13.1985], [80.2287, 13.1976], [80.2314, 13.1847],
        [80.2215, 13.1842], [80.2197, 13.1808], [80.2235, 13.1801], [80.2234, 13.1769],
        [80.2141, 13.1768], [80.212, 13.1803], [80.2103, 13.175], [80.2025, 13.1759],
        [80.2004, 13.1794], [80.1986, 13.1743], [80.194, 13.1757], [80.1933, 13.1725],
        [80.1923, 13.1749], [80.19, 13.1671], [80.1941, 13.1646], [80.1925, 13.1547],
        [80.1831, 13.1472], [80.1785, 13.1507], [80.1781, 13.1475], [80.1755, 13.1486],
        [80.1771, 13.1387], [80.1682, 13.1412], [80.1824, 13.1352], [80.1881, 13.1389],
        [80.1947, 13.1283], [80.2164, 13.1308], [80.2246, 13.1294], [80.2267, 13.1258],
        [80.2332, 13.1264], [80.2329, 13.123], [80.2373, 13.1224], [80.2424, 13.1223],
        [80.2434, 13.1272], [80.2461, 13.1196], [80.2435, 13.1131], [80.2511, 13.1154],
        [80.2524, 13.1084], [80.2652, 13.1097], [80.2708, 13.1049], [80.2721, 13.1069],
        [80.2739, 13.1002], [80.274, 13.0957], [80.2692, 13.0906], [80.2569, 13.0908],
        [80.2558, 13.0813], [80.2495, 13.0715], [80.256, 13.0621], [80.2637, 13.0628],
        [80.2676, 13.0583], [80.2709, 13.059], [80.2736, 13.0667], [80.2797, 13.0645],
        [80.2807, 13.0689], [80.284, 13.0689], [80.2888, 13.0665], [80.3041, 13.0968],
        [80.2976, 13.1011], [80.3021, 13.1168], [80.2967, 13.1246], [80.2965, 13.1318],
        [80.3033, 13.1504], [80.3076, 13.1491], [80.3252, 13.2126],
      ]] },
    },
  ],
};

const mapStyle = {
  version: 8 as const,
  sources: {
    openstreetmap: {
      type: "raster" as const,
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "© OpenStreetMap contributors",
    },
  },
  layers: [
    {
      id: "map-background",
      type: "background" as const,
      paint: { "background-color": "#dce6df" },
    },
    {
      id: "openstreetmap",
      type: "raster" as const,
      source: "openstreetmap",
      paint: { "raster-opacity": 0.9 },
    },
  ],
};

export default function MapView({ metric, metricData, dataProperty, onRegionSelected }: MapViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const metricDataRef = useRef(metricData);
  const startRef = useRef<{ x: number; y: number } | null>(null);
  const drawingRef = useRef(false);
  const endRef = useRef<{ x: number; y: number } | null>(null);
  const [drawing, setDrawing] = useState(false);
  const [selected, setSelected] = useState(false);
  const [rectangle, setRectangle] = useState({ left: 0, top: 0, width: 0, height: 0 });
  const [mapError, setMapError] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: mapStyle,
      center: [80.22, 13.045],
      zoom: 10.15,
      minZoom: 9,
      maxZoom: 16,
      maxBounds: [[79.85, 12.55], [80.60, 13.40]],
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right");
    map.on("error", () => setMapError(true));

    map.on("load", () => {
      map.addSource("chennai-boundary", { type: "geojson", data: chennaiBoundary });
      map.addLayer({
        id: "chennai-boundary-fill",
        type: "fill",
        source: "chennai-boundary",
        paint: { "fill-color": "#39785b", "fill-opacity": 0.16 },
      });
      map.addLayer({
        id: "chennai-boundary-line",
        type: "line",
        source: "chennai-boundary",
        paint: { "line-color": "#39785b", "line-width": 2 },
      });
      map.addSource("analysis-grid", { type: "geojson", data: metricDataRef.current ?? { type: "FeatureCollection", features: [] } });
      map.addLayer({
        id: "analysis-grid-points",
        type: "circle",
        source: "analysis-grid",
        paint: {
          "circle-radius": 4,
          "circle-color": ["interpolate", ["linear"], ["coalesce", ["get", dataProperty ?? metric.id], 0], 0, "#dcebdc", 50, "#e6c77b", 100, "#b45f42"],
          "circle-opacity": 0.78,
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 0.4,
        },
      });
    });

    const onMouseDown = (event: MapMouseEvent) => {
      drawingRef.current = true;
      startRef.current = { x: event.point.x, y: event.point.y };
      setDrawing(true);
      setSelected(false);
      map.dragPan.disable();
      map.getCanvas().style.cursor = "crosshair";
    };
    const onMouseMove = (event: MapMouseEvent) => {
      if (!drawingRef.current || !startRef.current) return;
      const start = startRef.current;
      endRef.current = { x: event.point.x, y: event.point.y };
      const deltaX = event.point.x - start.x;
      const deltaY = event.point.y - start.y;
      const size = Math.max(Math.abs(deltaX), Math.abs(deltaY));
      setRectangle({
        left: deltaX < 0 ? start.x - size : start.x,
        top: deltaY < 0 ? start.y - size : start.y,
        width: size,
        height: size,
      });
    };
    const finishDrawing = (event?: MapMouseEvent) => {
      if (!drawingRef.current) return;
      const start = startRef.current;
      const end = event?.point ?? endRef.current;
      drawingRef.current = false;
      startRef.current = null;
      endRef.current = null;
      setDrawing(false);
      if (start && end && Math.abs(end.x - start.x) > 8 && Math.abs(end.y - start.y) > 8) {
        const a = map.unproject([Math.min(start.x, end.x), Math.min(start.y, end.y)]);
        const b = map.unproject([Math.max(start.x, end.x), Math.max(start.y, end.y)]);
        onRegionSelected?.({
          type: "Feature",
          properties: { source: "map_selection" },
          geometry: {
            type: "Polygon",
            coordinates: [[[a.lng, a.lat], [b.lng, a.lat], [b.lng, b.lat], [a.lng, b.lat], [a.lng, a.lat]]],
          },
        });
        setSelected(true);
      }
      map.dragPan.enable();
      map.getCanvas().style.cursor = "grab";
    };

    map.on("mousedown", onMouseDown);
    map.on("mousemove", onMouseMove);
    map.on("mouseup", finishDrawing);
    map.on("mouseleave", finishDrawing);
    map.getCanvas().style.cursor = "grab";

    const resizeObserver = new ResizeObserver(() => map.resize());
    resizeObserver.observe(containerRef.current);
    requestAnimationFrame(() => map.resize());

    return () => {
      resizeObserver.disconnect();
      map.remove();
      mapRef.current = null;
    };
  }, [metric.id, metric.stops, dataProperty, onRegionSelected]);

  useEffect(() => {
    metricDataRef.current = metricData;
    const source = mapRef.current?.getSource("analysis-grid") as maplibregl.GeoJSONSource | undefined;
    if (source && metricData) source.setData(metricData);
  }, [metricData]);

  return (
    <div className="relative h-full min-h-0 flex-1 overflow-hidden border border-[#cfd5d0] bg-[#dce6df]">
      <div ref={containerRef} className="absolute inset-0 h-full w-full" />
      {mapError && <div className="pointer-events-none absolute left-4 top-4 z-10 rounded bg-white/90 px-3 py-2 text-sm text-[#b45f42] shadow-sm">Map tiles could not be loaded</div>}
      {(drawing || selected) && <div className="pointer-events-none absolute z-10 border-2 border-dashed border-[#1e3a5f] bg-[#8db59a]/25" style={rectangle} />}
      <div className="pointer-events-none absolute bottom-4 left-4 z-10 min-w-[220px] border border-[#cfd5d0] bg-[#f7f8f5]/95 p-3.5">
        <div className="mb-2 text-sm font-semibold text-[#4a463c]">{metric.label}</div>
        <div className="h-2.5 rounded-full" style={{ background: `linear-gradient(90deg, ${metric.stops.join(",")})` }} />
        <div className="mt-1.5 flex justify-between text-sm font-mono text-[#8a8578]"><span>{metric.minLabel}</span><span>{metric.maxLabel}</span></div>
      </div>
    </div>
  );
}
