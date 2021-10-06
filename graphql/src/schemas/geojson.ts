// This schema was automatically generated from a running
// https://github.com/ghengeveld/graphql-geojson-demo instance by the
// `get-graphql-schema` tool.

export const geoSchema = `
"""Coordinate Reference System (CRS) object."""
type GeoJSONCoordinateReferenceSystem {
  type: GeoJSONCRSType!
  properties: GeoJSONCRSProperties!
}
"""A (multidimensional) set of coordinates following x, y, z order."""
scalar GeoJSONCoordinates
"""CRS object properties."""
union GeoJSONCRSProperties = GeoJSONNamedCRSProperties | GeoJSONLinkedCRSProperties
"""Enumeration of all GeoJSON CRS object types."""
enum GeoJSONCRSType {
  name
  link
}
"""
An object that links a geometry to properties in order to provide context.
"""
type GeoJSONFeature implements GeoJSONInterface {
  type: GeoJSONType!
  crs: GeoJSONCoordinateReferenceSystem!
  bbox: [Float]
  geometry: GeoJSONGeometryInterface @cacheControl(inheritMaxAge: true)
  properties: JSONObject
  id: String
}
"""A set of multiple features."""
type GeoJSONFeatureCollection implements GeoJSONInterface {
  type: GeoJSONType!
  crs: GeoJSONCoordinateReferenceSystem!
  bbox: [Float]
  features: [GeoJSONFeature!]!
}
"""A set of multiple geometries, possibly of various types."""
type GeoJSONGeometryCollection implements GeoJSONInterface {
  type: GeoJSONType!
  crs: GeoJSONCoordinateReferenceSystem!
  bbox: [Float]
  geometries: [GeoJSONGeometryInterface!]!
}
interface GeoJSONGeometryInterface {
  type: GeoJSONType!
  crs: GeoJSONCoordinateReferenceSystem!
  bbox: [Float]
  coordinates: GeoJSONCoordinates
}
interface GeoJSONInterface {
  type: GeoJSONType!
  crs: GeoJSONCoordinateReferenceSystem!
  bbox: [Float]
}
"""Object describing a single connected sequence of geographical points."""
type GeoJSONLineString implements GeoJSONInterface & GeoJSONGeometryInterface {
  type: GeoJSONType!
  crs: GeoJSONCoordinateReferenceSystem!
  bbox: [Float]
  coordinates: GeoJSONCoordinates
}
"""Properties for link based CRS object."""
type GeoJSONLinkedCRSProperties {
  href: String!
  type: String
}
"""Object describing multiple connected sequences of geographical points."""
type GeoJSONMultiLineString implements GeoJSONInterface & GeoJSONGeometryInterface {
  type: GeoJSONType!
  crs: GeoJSONCoordinateReferenceSystem!
  bbox: [Float]
  coordinates: GeoJSONCoordinates
}
"""Object describing multiple geographical points."""
type GeoJSONMultiPoint implements GeoJSONInterface & GeoJSONGeometryInterface {
  type: GeoJSONType!
  crs: GeoJSONCoordinateReferenceSystem!
  bbox: [Float]
  coordinates: GeoJSONCoordinates
}
"""
Object describing multiple shapes formed by sets of geographical points.
"""
type GeoJSONMultiPolygon implements GeoJSONInterface & GeoJSONGeometryInterface {
  type: GeoJSONType!
  crs: GeoJSONCoordinateReferenceSystem!
  bbox: [Float]
  coordinates: GeoJSONCoordinates
}
"""Properties for name based CRS object."""
type GeoJSONNamedCRSProperties {
  name: String!
}
"""Object describing a single geographical point."""
type GeoJSONPoint implements GeoJSONInterface & GeoJSONGeometryInterface {
  type: GeoJSONType!
  crs: GeoJSONCoordinateReferenceSystem!
  bbox: [Float]
  coordinates: GeoJSONCoordinates
}
"""
Object describing a single shape formed by a set of geographical points.
"""
type GeoJSONPolygon implements GeoJSONInterface & GeoJSONGeometryInterface {
  type: GeoJSONType!
  crs: GeoJSONCoordinateReferenceSystem!
  bbox: [Float]
  coordinates: GeoJSONCoordinates
}
"""Enumeration of all GeoJSON object types."""
enum GeoJSONType {
  Point
  MultiPoint
  LineString
  MultiLineString
  Polygon
  MultiPolygon
  GeometryCollection
  Feature
  FeatureCollection
}
"""Arbitrary JSON value"""
scalar JSONObject
`;
