import shutil
import os.path

import matsim.runtime.eqasim as eqasim

def configure(context):
    context.stage("matsim.simulation.prepare") # need the network
    context.stage("matsim.runtime.java")
    context.stage("matsim.runtime.eqasim")

    context.config("cordon_toll_price")
    context.config("cordon_toll_name")
    context.config("cordon_toll_shapefile")
    context.config("data_path")
    context.config("output_path")

def execute(context):

    # add cordon toll around Paris
    tollprice = context.config("cordon_toll_price")
    if tollprice is None:
        tollprice = 0.0

    print("Calling java RunCordonTollSetup from "+context.path())

    if context.config("cordon_toll_shapefile") is not None and context.config("cordon_toll_name") is not None:
        eqasim.run(context, "org.eqasim.core.scenario.spatial.RunCordonTollSetup", [
            "--input-path", "%s/%snetwork.xml.gz" % (context.path("matsim.simulation.prepare"),context.config("output_prefix")),
            "--output-path", "%stoll.xml" % context.config("output_prefix"),
            "--shape-path", context.path()+"/../../"+context.config("data_path")+"/"+context.config("cordon_toll_shapefile"),
            "--shape-attribute", "name",
            "--shape-value", context.config("cordon_toll_name"),
            "--price", tollprice
        ])

        shutil.copy(
            "%s/%s" % (context.path(), "%stoll.xml" % context.config("output_prefix")),
            "%s/%s" % (context.config("output_path"), "%stoll.xml" % context.config("output_prefix"))
        )

        # also copy toll file to matsim.simulation.prepare since the java sim module use its prefix - could have included this step in preparation, but avoids recomputing everything between two scenarii
        shutil.copy(
            "%s/%s" % (context.path(), "%stoll.xml" % context.config("output_prefix")),
            "%s/%s" % (context.path("matsim.simulation.prepare"), "%stoll.xml" % context.config("output_prefix"))
        )

