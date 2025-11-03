"""
This script contains the functions that will be used to create XML filter and WFS query creation. 
"""
#==========================================================================================================
# Libraries
#==========================================================================================================

# Third-party packages
import xml.etree.ElementTree as ET
from shapely.geometry import (
    Polygon, MultiPolygon,
    LineString, MultiLineString,
    Point, MultiPoint
)

#==========================================================================================================
# Function to generate poslists (coordinate strings) from geometries in a GeoDataFrame
#==========================================================================================================
def get_poslists_from_gdf(geodataframe):
    """
    Extracts poslists (coordinate strings) from geometries in a GeoDataFrame.
    Supports Polygon, MultiPolygon, LineString, MultiLineString, Point, and MultiPoint.
    Returns a list of poslist strings.
    """

    poslists = []

    for _, row in geodataframe.iterrows():
        geom = row.geometry

        if geom is None or geom.is_empty:
            continue

        geom_type = geom.geom_type

        # --- Polygon and MultiPolygon ---
        if isinstance(geom, (Polygon, MultiPolygon)):
            polygons = [geom] if isinstance(geom, Polygon) else geom.geoms
            for poly in polygons:
                coords = list(poly.exterior.coords)
                poslist = " ".join(f"{y:.6f} {x:.6f}" for x, y in coords)
                poslists.append(poslist)

        # --- LineString and MultiLineString ---
        elif isinstance(geom, (LineString, MultiLineString)):
            lines = [geom] if isinstance(geom, LineString) else geom.geoms
            for line in lines:
                coords = list(line.coords)
                poslist = " ".join(f"{y:.6f} {x:.6f}" for x, y in coords)
                poslists.append(poslist)

        # --- Point and MultiPoint ---
        elif isinstance(geom, (Point, MultiPoint)):
            points = [geom] if isinstance(geom, Point) else geom.geoms
            for pt in points:
                poslist = f"{pt.y:.6f} {pt.x:.6f}"
                poslists.append(poslist)

        # --- Unsupported geometries (optional warning) ---
        else:
            print(f"Warning: Unsupported geometry type '{geom_type}' — skipped.")

    return poslists


#=======================================================================================================
# Helper functions to build geometry-specific GML elements
#=======================================================================================================

def _create_gml_polygon_element(namespaces, poslist):
    polygon_elem = ET.Element(ET.QName(namespaces["gml"], "Polygon"), attrib={"srsName": "urn:ogc:def:crs:EPSG::4326"})
    exterior_elem = ET.SubElement(polygon_elem, ET.QName(namespaces["gml"], "exterior"))
    linearRing_elem = ET.SubElement(exterior_elem, ET.QName(namespaces["gml"], "LinearRing"))
    posList_elem = ET.SubElement(linearRing_elem, ET.QName(namespaces["gml"], "posList"))
    posList_elem.text = poslist.strip()
    return polygon_elem


def _create_gml_linestring_element(namespaces, poslist):
    line_elem = ET.Element(ET.QName(namespaces["gml"], "LineString"), attrib={"srsName": "urn:ogc:def:crs:EPSG::4326"})
    posList_elem = ET.SubElement(line_elem, ET.QName(namespaces["gml"], "posList"))
    posList_elem.text = poslist.strip()
    return line_elem


def _create_gml_point_element(namespaces, poslist):
    point_elem = ET.Element(ET.QName(namespaces["gml"], "Point"), attrib={"srsName": "urn:ogc:def:crs:EPSG::4326"})
    pos_elem = ET.SubElement(point_elem, ET.QName(namespaces["gml"], "pos"))
    pos_elem.text = poslist.strip()
    return point_elem


#=======================================================================================================
# Function that generates a WFS 2.0 XML filter for multiple geometry types
#=======================================================================================================

def creating_xml_filter(layer_geometry, geodataframe):
    """
    Creates a WFS 2.0 XML filter string that matches geometries
    (Polygon, MultiPolygon, LineString, MultiLineString, Point, MultiPoint)
    in the provided GeoDataFrame using <fes:Or> and <fes:Intersects>.
    """

    poslists = get_poslists_from_gdf(geodataframe)

    # Namespaces
    namespaces = {
        "fes": "http://www.opengis.net/fes/2.0",
        "gml": "http://www.opengis.net/gml/3.2"
    }

    # Root <fes:Filter>
    filter_elem = ET.Element(ET.QName(namespaces["fes"], "Filter"), nsmap=namespaces)

    # Wrap all intersections inside <fes:Or>
    or_elem = ET.SubElement(filter_elem, ET.QName(namespaces["fes"], "Or"))

    for idx, (poslist, geom) in enumerate(zip(poslists, geodataframe.geometry)):
        if geom is None or geom.is_empty:
            continue

        geom_type = geom.geom_type

        # <fes:Intersects>
        intersects_elem = ET.SubElement(or_elem, ET.QName(namespaces["fes"], "Intersects"))

        # <fes:ValueReference>
        value_ref_elem = ET.SubElement(intersects_elem, ET.QName(namespaces["fes"], "ValueReference"))
        value_ref_elem.text = layer_geometry.strip()

        # Determine geometry type and build corresponding GML element
        if isinstance(geom, (Polygon, MultiPolygon)):
            gml_geom_elem = _create_gml_polygon_element(namespaces, poslist)

        elif isinstance(geom, (LineString, MultiLineString)):
            gml_geom_elem = _create_gml_linestring_element(namespaces, poslist)

        elif isinstance(geom, (Point, MultiPoint)):
            gml_geom_elem = _create_gml_point_element(namespaces, poslist)

        else:
            print(f"Warning: Unsupported geometry type '{geom_type}' — skipped.")
            continue

        intersects_elem.append(gml_geom_elem)

    # Convert to XML string
    xml_filter = ET.tostring(filter_elem, encoding="utf-8", xml_declaration=True).decode("utf-8")

    return xml_filter



#================================================================================================================
# Creating a function to construct the "data" parameter of the POST request
#================================================================================================================

def data_to_post(geodataframe, layer_name, layer_geometry):
    
    ''' The function constructs the final xml to be used in the POST request. It integrates the output of the function "creating xml_filter". '''
    
    # Defining namespaces
    ns = {
        "wfs": "http://www.opengis.net/wfs/2.0",
        "fes": "http://www.opengis.net/fes/2.0",
        "gml": "http://www.opengis.net/gml/3.2",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        }
    for prefix, uri in ns.items(): # Registering namespaces so the prefixes appear correctly in the output
        ET.register_namespace(prefix, uri)

    # Root element <wfs:GetFeature>
    get_feature_elem = ET.Element(
        ET.QName(ns["wfs"], "GetFeature"),
        {
            "service": "WFS",
            "version": "2.0.0",
            ET.QName(ns["xsi"], "schemaLocation"):
                "http://www.opengis.net/wfs/2.0 "
                "http://schemas.opengis.net/wfs/2.0/wfs.xsd"
        }
    )

    # Add <wfs:Query> element with attributes and the xml_filter
    query_elem = ET.SubElement(
        get_feature_elem,
        ET.QName(ns["wfs"], "Query"),
        {
            "typeNames": layer_name,
            "srsName": "EPSG:4326"
        }
    )

    xml_filter = creating_xml_filter(layer_geometry, geodataframe) # Retrieving the filter
    xml_filter = ET.fromstring (xml_filter)
    query_elem.append(xml_filter)
    
    # Generating the POST data xml
    data = ET.tostring(get_feature_elem, encoding="utf-8", xml_declaration=True).decode("utf-8")
    return data