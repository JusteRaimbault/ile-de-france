import data.osm.osmosis
import os, os.path, gzip
import shapely.geometry as geo

"""
This file reads the OSM data in PBF format specified by the "osm_path"
and "data_path" configuration options. The data is read from
"data_path/osm_path". Note that you can define a list of input files separated
by ";" in the "osm_path" option. These OSM files will be merged, for instance,
if you want to merge the old Languedoc and Midi-Pyrénées regional snapshots
from Geofabrik to create a continuous file for the new Occitanie region.

This stage furthermore filters the file such that only highway elmenets and
railway elements of the OSM data remain. This makes it easier for the downstream
MATSim converter to work with the data.

Additionally, the stage cuts the OSM data to the requested region of the pipeline.
"""

def configure(context):
    context.config("data_path")
    context.config("osm_path", "osm/ile-de-france-latest.osm.pbf")

    context.config("osm_highways", "*")
    context.config("osm_railways", "*")

    context.stage("data.osm.osmosis")
    context.stage("data.spatial.municipalities")

def write_poly(df, path, geometry_column = "geometry"):
    df2 = df
    df2["aggregate"] = 0
    area2 = df2.dissolve(by = "aggregate")[geometry_column].values[0]
    print("Lambert 93 Bbox for osm filtering polygon : xmin = "+str(min([c[0] for c in area2.exterior.coords]))+" ; xmax = "+str(max([c[0] for c in area2.exterior.coords]))+" ; ymin = "+str(min([c[1] for c in area2.exterior.coords]))+" ; ymax = "+str(max([c[1] for c in area2.exterior.coords])))
    # ! already in wgs84 -> pb iris file?

    df = df.to_crs("EPSG:4326")

    df["aggregate"] = 0
    area = df.dissolve(by = "aggregate")[geometry_column].values[0]

    if not hasattr(area, "exterior"):
        print("Selected area is not connected -> Using convex hull.")
        area = area.convex_hull

    data = []
    data.append("polyfile")
    data.append("polygon")

    print("Bbox for osm filtering polygon : xmin = "+str(min([c[0] for c in area.exterior.coords]))+" ; xmax = "+str(max([c[0] for c in area.exterior.coords]))+" ; ymin = "+str(min([c[1] for c in area.exterior.coords]))+" ; ymax = "+str(max([c[1] for c in area.exterior.coords])))
    # issue in reprojection from Lambert 93 (EPSG:2154) to wgs84? (bbox is -1.86,-5)   
 
    for coordinate in area.exterior.coords:
        data.append("    %e    %e" % coordinate)

    data.append("END")
    data.append("END")

    with open(path, "w+") as f:
        f.write("\n".join(data))

def execute(context):
    input_files = context.config("osm_path").split(";")

    # Prepare bounding area
    df_area = context.stage("data.spatial.municipalities")
    write_poly(df_area, "%s/boundary.poly" % context.path())

    # Filter input files for quicker processing
    for index, path in enumerate(input_files):
        print("Filtering %s ..." % path)
        print("Depending on the amount of OSM data, this may take quite some time!")

        mode = "pbf" if path.endswith("pbf") else "xml"

        highway_tags = context.config("osm_highways")
        railway_tags = context.config("osm_railways")

        data.osm.osmosis.run(context, [
            "--read-%s" % mode, "../../%s/%s" % (context.config("data_path"), path),
            "--tag-filter", "accept-ways", "highway=%s" % highway_tags, "railway=%s" % railway_tags,
            "--bounding-polygon", "file=%s/boundary.poly" % context.path(), "completeWays=yes",
            "--write-pbf", "filtered_%d.osm.pbf" % index
        ])
        
        #print("Filtered osm file for index "+str(index)+" has size "+str(os.path.getsize("filtered_%d.osm.pbf" % index)))

    # Merge filtered files if there are multiple ones
    print("Merging and compressing OSM data...")

    command = []
    for index in range(len(input_files)):
        command += ["--read-pbf", "filtered_%d.osm.pbf" % index]

    for index in range(len(input_files) - 1):
        command += ["--merge"]

    command += ["--write-xml", "compressionMethod=gzip", "output.osm.gz"]

    data.osm.osmosis.run(context, command)

    # Remove temporary files
    for index, path in enumerate(input_files):
        print("Removing temporary file for %s ..." % path)
        os.remove("%s/filtered_%d.osm.pbf" % (context.path(), index))

    return "output.osm.gz"

def validate(context):
    input_files = context.config("osm_path").split(";")
    total_size = 0

    for path in input_files:
        if not os.path.exists("%s/%s" % (context.config("data_path"), path)):
            raise RuntimeError("OSM data is not available: %s" % path)
        else:
            total_size += os.path.getsize("%s/%s" % (context.config("data_path"), path))

    return total_size
