from setuptools import setup, find_packages

setup(
    name="scpert",
    version="0.1.1",
    author="AI4VirualCell",
    author_email="younanxin@zju.edu.cn",
    description="Single-cell perturbation modeling toolkit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AI4VirtualCell/scPert",
    packages=find_packages(),
    package_data={
        'scpert': ['data/embeddings/*.npy']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'anndata==0.9.2',
        'scanpy==1.9.8',
        'torch==2.3.0',
        'torch-geometric==2.6.1',
        'scvi-tools==0.20.3',
        'pandas==2.0.3',
        'numpy==1.24.4',
        'scipy==1.10.1',
        'cell-gears==0.0.2',
        'nvidia-cublas-cu12==12.1.3.1',
        'nvidia-cudnn-cu12==8.9.2.26',
        'flash_attn==0.2.8'
    ],
    entry_points={
        'console_scripts': [
            'scpert-train=scpertpy.cli:train_command',
            'scpert-infer=scpertpy.cli:infer_command'
        ],
    },
)
