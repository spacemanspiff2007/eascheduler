from pathlib import Path

from setuptools import find_packages, setup


# Load version number without importing HABApp
def load_version() -> str:
    version: dict[str, str] = {}
    with open('src/eascheduler/__version__.py') as fp:
        exec(fp.read(), version)  # noqa: S102
    return version['__version__']


def load_req() -> list[str]:
    req_file = Path(__file__).with_name('requirements_setup.txt')

    with req_file.open() as f:
        return f.readlines()


__version__ = load_version()

print(f'Version: {__version__}')
print()

# When we run tox tests we don't have these files available so we skip them
readme = Path(__file__).with_name('readme.md')
long_description = ''
if readme.is_file():
    with readme.open('r', encoding='utf-8') as fh:
        long_description = fh.read()

setup(
    name='EAScheduler',
    version=__version__,
    author='spaceman_spiff',
    description='Easy async scheduling with a nice interface',
    keywords=[
        'scheduler',
        'asyncio',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/spacemanspiff2007/eascheduler',
    project_urls={
        'Documentation': 'https://eascheduler.readthedocs.io/',
        'GitHub': 'https://github.com/spacemanspiff2007/eascheduler',
    },
    package_dir={'': 'src'},
    package_data={'eascheduler': ['py.typed']},
    packages=find_packages('src', exclude=['tests*']),
    python_requires='>=3.10',
    install_requires=load_req(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: AsyncIO',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
