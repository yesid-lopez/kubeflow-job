import kfp
from kfp.dsl import pipeline, VolumeOp, VOLUME_MODE_RWO
from kfp import components
from kfp.compiler import Compiler

from generate_products import generate_products
from download_data import download_data

download_data_component = components.create_component_from_func(download_data)
generate_products_component = components.create_component_from_func(generate_products, packages_to_install=["openai"])

@pipeline(name='taxonomy-products-generation', description="Generates products for each taxnonomy path")
def taxonomy_products_generation(n_products: int):
    vop = VolumeOp(
        name="create_volume",
        resource_name="data-volume", 
        size="1Gi", 
        modes=VOLUME_MODE_RWO
    ).add_pod_annotation(name="pipelines.kubeflow.org/max_cache_staleness", value="P0D")

    download_data_task = download_data_component().add_pvolumes({"/mnt": vop.volume})
    generate_products_task = generate_products_component(
        n_products= n_products,
        path_taxonomy=download_data_task.outputs["path_taxonomy"]
    ).pvolumes={"/data": download_data_task.pvolume}

Compiler().compile(taxonomy_products_generation, "taxonomy-products-generation.zip")

run_name = taxonomy_products_generation.__name__ + ' run'
client = kfp.Client()
client.create_run_from_pipeline_func(taxonomy_products_generation, 
                                                  experiment_name="test-yesid", 
                                                  run_name=run_name, 
                                                  arguments={
                                                      "n_products": 20
                                                  })
