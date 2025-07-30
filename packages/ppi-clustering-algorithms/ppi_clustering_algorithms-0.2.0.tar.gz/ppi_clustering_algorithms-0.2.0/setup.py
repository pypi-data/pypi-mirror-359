from setuptools import setup, find_packages

setup(
    name='ppi_clustering_algorithms',
    version='0.2.0',
    description='A library of clustering algorithms for Protein-Protein Interaction (PPI) networks.',
    author='P Soumya Sundar Subudhi',
    author_email='p.soumyasundars@gmail.com',
    packages=find_packages(),
    install_requires=[
        'networkx',
        'numpy',
        'pandas',
        'scipy',
        'plotly',
        'python-louvain',
        'markov-clustering',
        'python-igraph',
        'leidenalg'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
)