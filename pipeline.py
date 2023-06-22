import kfp
from kfp.dsl import pipeline, VolumeOp, VOLUME_MODE_RWO, PipelineParam
from kfp import components
from kfp.compiler import Compiler
from kubernetes.client.models import V1EnvVar
import os
from generate_products import generate_products
from download_data import download_data

download_data_component = components.create_component_from_func(download_data)
generate_products_component = components.create_component_from_func(
    generate_products, packages_to_install=["openai"]
)


@pipeline(
    name="taxonomy-products-generation",
    description="Generates products for each taxnonomy path",
)
def taxonomy_products_generation(n_products: int):

    vop = VolumeOp(
        name="create_volume",
        resource_name="data-volume",
        size="1Gi",
        modes=VOLUME_MODE_RWO,
    ).add_pod_annotation(name="pipelines.kubeflow.org/max_cache_staleness", value="P0D")

    download_data_task = download_data_component().add_pvolumes({"/mnt": vop.volume})

    env_var = V1EnvVar(name="OPENAI_KEY", value=os.getenv("OPENAI_KEY"))
    generate_products_task = (
        generate_products_component(
            n_products=20,
            path_taxonomy=download_data_task.outputs["path_taxonomy"],
        )
        .add_pvolumes({"/data": download_data_task.pvolume})
        .add_env_variable(env_var)
    )


Compiler().compile(taxonomy_products_generation, "taxonomy-products-generation.yaml")

run_name = taxonomy_products_generation.__name__ + " run"
client = kfp.Client()
run_response = client.create_run_from_pipeline_func(
    taxonomy_products_generation,
    experiment_name="generate_taxonomy_paths",
    run_name=run_name,
    arguments={"n_products": 20},
)
print(run_response)
