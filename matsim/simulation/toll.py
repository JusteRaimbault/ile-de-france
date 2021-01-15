import shutil
import os.path

import matsim.runtime.eqasim as eqasim

def configure(context):
    context.stage("matsim.simulation.prepare") # need the network
    context.stage("matsim.runtime.java")
    context.stage("matsim.runtime.eqasim")

def execute(context):

    # add cordon toll around Paris
    tollprice = context.config("cordon_toll_price")
    if tollprice is None:
        tollprice = 0.0
    if context.config("cordon_toll_shapefile") is not None and context.config("cordon_toll_name") is not None:
        eqasim.run(context, "org.eqasim.core.scenario.spatial.RunCordonTollSetup", [
            "--input-path", "%snetwork.xml.gz" % context.config("output_prefix"),
            "--output-path", "%stoll_links.xml" % context.config("output_prefix"),
            "--shape-path", context.config("data_prefix")+"/"+context.config("cordon_toll_shapefile"),
            "--shape-attribute", "name",
            "--shape-value", context.config("cordon_toll_name"),
            "--price", tollprice
        ])
