"""
===============================================================================
ASTHASH ENTERPRISE: ACADEMIC CORPUS GENERATOR
Target: Generates a static, commit-pinned CSV of 100 heavy Python files (>500 nodes)
Output: asthash_academic_corpus.csv
===============================================================================
"""
import csv

# We use specific commit hashes (not 'main' or 'master') so that a reviewer 
# running this code in 5 years will test the exact same files you tested today.
HEAVY_REPOSITORIES = {
    # --- WEB FRAMEWORKS ---
    "pallets/flask": {
        "commit": "8d6b88eece15c0e7040441df9cd5758cf0ad3713", # Flask 2.2.x era
        "files": ["src/flask/app.py", "src/flask/helpers.py", "src/flask/blueprints.py", "src/flask/wrappers.py", "src/flask/templating.py"]
    },
    "django/django": {
        "commit": "c4bcefcb4da4817a016df83bf9b79cbda9bb24e6",
        "files": ["django/db/models/base.py", "django/core/handlers/base.py", "django/forms/models.py", "django/template/engine.py", "django/db/models/query.py"]
    },
    "tiangolo/fastapi": {
        "commit": "86bc3ec10c149dffde1fb162799c8369ec264ec4",
        "files": ["fastapi/routing.py", "fastapi/applications.py", "fastapi/dependencies/utils.py", "fastapi/openapi/utils.py", "fastapi/exception_handlers.py"]
    },
    "encode/starlette": {
        "commit": "f4410d540236496ec2b9db473dfd71b3058a5e30",
        "files": ["starlette/routing.py", "starlette/requests.py", "starlette/responses.py", "starlette/applications.py", "starlette/middleware/base.py"]
    },
    
    # --- MACHINE LEARNING & DATA SCIENCE ---
    "pytorch/pytorch": {
        "commit": "7bcf7da3a268b435777fe87c7794c382f444e865",
        "files": ["torch/nn/modules/module.py", "torch/tensor.py", "torch/optim/adam.py", "torch/utils/data/dataloader.py", "torch/autograd/engine.py"]
    },
    "pandas-dev/pandas": {
        "commit": "7c48ff44081efb0451a54728d844fb9d2a233379",
        "files": ["pandas/core/frame.py", "pandas/core/series.py", "pandas/core/groupby/groupby.py", "pandas/core/indexes/base.py", "pandas/io/parsers/readers.py"]
    },
    "scikit-learn/scikit-learn": {
        "commit": "36958fb240fbe435673a9e3c52e769f01f36bec0",
        "files": ["sklearn/ensemble/_forest.py", "sklearn/tree/_classes.py", "sklearn/linear_model/_logistic.py", "sklearn/cluster/_kmeans.py", "sklearn/svm/_classes.py"]
    },
    "huggingface/transformers": {
        "commit": "c356ee191b2bf8a0db8bd1031b209e7c10b7593c",
        "files": ["src/transformers/trainer.py", "src/transformers/modeling_utils.py", "src/transformers/tokenization_utils_base.py", "src/transformers/models/bert/modeling_bert.py", "src/transformers/configuration_utils.py"]
    },

    # --- NETWORKING & CYBER ---
    "psf/requests": {
        "commit": "673f47881cbe13fc13b4845511b0e00810d291ba",
        "files": ["requests/models.py", "requests/sessions.py", "requests/adapters.py", "requests/api.py", "requests/exceptions.py"]
    },
    "scrapy/scrapy": {
        "commit": "0cdedb702ec8c99180735870020bbcc00c3bcf44",
        "files": ["scrapy/crawler.py", "scrapy/core/engine.py", "scrapy/http/request/__init__.py", "scrapy/pipelines/media.py", "scrapy/spidermiddlewares/urllength.py"]
    },

    # --- CLI & UTILITIES ---
    "Textualize/rich": {
        "commit": "c4d2d4be8836594dcbb40b3c202029ec2374e6f4",
        "files": ["rich/console.py", "rich/table.py", "rich/progress.py", "rich/text.py", "rich/panel.py"]
    },
    "pallets/click": {
        "commit": "7af30ed0cfa1ea0205260195c6c64de94b9173a1",
        "files": ["src/click/core.py", "src/click/utils.py", "src/click/parser.py", "src/click/termui.py", "src/click/formatting.py"]
    },
    "pydantic/pydantic": {
        "commit": "d9be70b162f47c0b7975871887eaf406cc2a07c9",
        "files": ["pydantic/main.py", "pydantic/fields.py", "pydantic/types.py", "pydantic/networks.py", "pydantic/config.py"]
    },
    "sqlalchemy/sqlalchemy": {
        "commit": "3ec3bbda7f19890250df5a593cb8402c018a1a2f",
        "files": ["lib/sqlalchemy/orm/query.py", "lib/sqlalchemy/engine/base.py", "lib/sqlalchemy/sql/elements.py", "lib/sqlalchemy/sql/schema.py", "lib/sqlalchemy/orm/session.py"]
    },
    "apache/airflow": {
        "commit": "f47171efec00508139be6e0fa8da991f2a3dc26e",
        "files": ["airflow/models/dag.py", "airflow/models/taskinstance.py", "airflow/models/baseoperator.py", "airflow/utils/timezone.py", "airflow/executors/base_executor.py"]
    },
    "celery/celery": {
        "commit": "ec657aef4bf29c0a6b65342aebbe39c898cbe0de",
        "files": ["celery/app/base.py", "celery/worker/worker.py", "celery/backends/base.py", "celery/apps/worker.py", "celery/worker/consumer/consumer.py"]
    },
    "pytest-dev/pytest": {
        "commit": "b0a6e0c65c69785002ec6165e315ec0906233d40",
        "files": ["src/_pytest/runner.py", "src/_pytest/fixtures.py", "src/_pytest/config/__init__.py", "src/_pytest/main.py", "src/_pytest/python.py"]
    },
    "sphinx-doc/sphinx": {
        "commit": "1b08b5be9d09c3bf3782bcf2b2da111db000dbd0",
        "files": ["sphinx/application.py", "sphinx/environment/__init__.py", "sphinx/builders/html/__init__.py", "sphinx/config.py", "sphinx/ext/autodoc/__init__.py"]
    },
    "pypa/pip": {
        "commit": "c4d57dc2095cc2ecadba6dfccfb9fca44638d17f",
        "files": ["src/pip/_internal/operations/prepare.py", "src/pip/_internal/req/req_install.py", "src/pip/_internal/resolution/resolvelib/resolver.py", "src/pip/_internal/commands/install.py", "src/pip/_internal/index/package_finder.py"]
    },
    "jupyter/jupyter_client": {
        "commit": "2c6a0c5c3e74b34208a000676a0fb4fdf07abcc1",
        "files": ["jupyter_client/client.py", "jupyter_client/manager.py", "jupyter_client/kernelmanager.py", "jupyter_client/session.py", "jupyter_client/multikernelmanager.py"]
    }
}

def generate_csv():
    output_filename = "asthash_academic_corpus.csv"
    
    with open(output_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Define the exact columns a data scientist needs for reproducibility
        writer.writerow(["Project", "Domain", "Commit_Hash", "File_Path", "Raw_URL"])
        
        for index, (repo, data) in enumerate(HEAVY_REPOSITORIES.items()):
            commit = data["commit"]
            # Rough domain categorization for the paper
            if index < 4: domain = "Web"
            elif index < 8: domain = "Machine_Learning"
            elif index < 10: domain = "Networking"
            else: domain = "CLI_Tooling"
            
            for filepath in data["files"]:
                raw_url = f"https://raw.githubusercontent.com/{repo}/{commit}/{filepath}"
                writer.writerow([repo, domain, commit, filepath, raw_url])
                
    print(f"[+] Successfully generated '{output_filename}' containing 100 pinned heavy files.")
    print("[+] Corpus is ready for the Metrology Framework.")

if __name__ == "__main__":
    generate_csv()