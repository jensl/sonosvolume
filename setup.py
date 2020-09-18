from setuptools import setup

setup(name='sonosvolume',
      version='0.1',
      description='Light-weight Sonos volume web UI',
      author='Jens Widell',
      author_email='jl@jenswidell.se',
      license='MIT',
      packages=['sonosvolume'],
      include_package_data=True,
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'sonosvolume = sonosvolume:main'
          ]
      })
