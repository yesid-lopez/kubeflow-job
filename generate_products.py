from kfp.components import InputPath, OutputPath

def generate_products(
    n_products: int,
    path_taxonomy: InputPath("txt"), 
    output_json_path: OutputPath("json")
):
    import openai
    import json
    import os
    from openai.error import RateLimitError, APIError, ServiceUnavailableError
    from ast import literal_eval

    openai.api_key = os.getenv("OPENAI_KEY")
    def generate_products(taxonomy_path, product_amount):
        prompt = f"""
        Generate {product_amount} product names for the following path: \

        {taxonomy_path} \

        Do not repeat the product names.

        Format the output as an array of strings. 
        """

        try:
            response = openai.ChatCompletion.create(
              model="gpt-3.5-turbo",
              temperature= 0,
              messages=[
                    {"role": "user", "content": prompt},
                ]
            )
            response = response["choices"][0]["message"]["content"]
            return literal_eval(response)
        except (APIError, RateLimitError, ServiceUnavailableError) as api_error:
            print(f"An error has ocurred {type(api_error)}")
            print(api_error)
            return generate_products(taxonomy_path, product_amount)
        
    taxonomy_paths = []
    with open(path_taxonomy, 'r') as f:
        lines = f.read()
        taxonomy_paths = lines.split("\n")
    print(f"{len(taxonomy_paths)} taxonomy paths loaded")

    paths = {}
    for i, path in enumerate(taxonomy_paths):
        generated_products = generate_products(path, n_products)
        paths[path] = generated_products
        print(f"Products created for {i+1}/{len(taxonomy_paths)} - {path}")

    with open(output_json_path, 'w') as fp:
        json.dump(paths, fp)

    print("Product Generation has finished")

generate_products(2, "taxonomy.txt", "taxonomy.json")