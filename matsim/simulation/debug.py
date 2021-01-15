import shutil
import os.path

def configure(context):
    context.stage("data.spatial.departments")
    context.config("output_prefix")

def execute(context):
    df_shape = context.stage("data.spatial.departments")[["departement_id", "geometry"]].rename(columns = dict(departement_id = "id"))
    df_shape["id"] = df_shape["id"].astype(str)
    df_shape.to_file("%s/departments.shp" % context.path())
