from setuptools import setup, find_packages

setup(
    name='ArtusAPI',
    version='1.3.18',
    description='API to control Artus Family of Robots by Sarcomere Dynamics Inc',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['data*', 'examples*', 'tests*','venv*', 'urdf*', 'ros2*','changelog*']),
    author='Sarcomere Dynamics Inc.',
    author_email='support@sarcomeredynamics.com',
    install_requires=[
        'psutil==5.9.8',
        'pyserial==3.5',
        'esptool',
        'pyyaml',
        'tqdm',
        'requests'
    ],
    python_requires='>=3.10',
    url='https://sarcomeredynamics.com/home',
    project_urls={
        'Source': 'https://github.com/Sarcomere-Dynamics/Sarcomere_Dynamics_Resources',
    },
    keywords='robotics, artus, sarcomere dynamics, control',
    entry_points={
        'console_scripts': [
            'artusapiflash=ArtusAPI.artus_api:main_flash',
            'artusapi=ArtusAPI.artus_api:main',
        ],
    }
)