import type { GeoJSONPointInput, LongitudeLatitude } from '../types.js';

// NOTE: This is a collection of GeoJSON* resolvers, not a single resolver!
export function GeoJSONResolvers() {
  return {
    GeoJSONCRSProperties: {
      __resolveType() {
        return null;
      },
    },
    GeoJSONGeometryInterface: {
      __resolveType() {
        return 'GeoJSONPoint';
      },
    },
    GeoJSONInterface: {
      __resolveType() {
        return null;
      },
    },
    GeoJSONPoint: {
      type() {
        return 'Point';
      },
      coordinates(obj: GeoJSONPointInput): LongitudeLatitude | null {
        const long = obj.geometry?.coordinates?.longitude ?? obj.longitude;
        const lat = obj.geometry?.coordinates?.latitude ?? obj.latitude;

        return long && lat ? [long, lat] : null;
      },
    },
    GeoJSONFeature: {
      type() {
        return 'Point';
      },
      geometry(parent: unknown) {
        return parent;
      },
    },
  };
}
