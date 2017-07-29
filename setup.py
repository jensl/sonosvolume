from setuptools import setup

setup(name='sonosvolume',
      version='0.1',
      description='Light-weight Sonos volume web UI',
      author='Jens Widell',
      author_email='jl@jenswidell.se',
      license='MIT',
      packages=['sonosvolume'],
      install_requires=[
          'falcon',
          'soco',
          'uwsgi',
      ],
      zip_safe=False)
