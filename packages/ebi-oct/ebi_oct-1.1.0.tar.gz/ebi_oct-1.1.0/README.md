# oct_analysis

oct_analysis is a Python library for the processing of image data for optical methods (foremost optical coherence tomography (OCT)).

## Installation

```bash
pip install oct_analysis
```

## Features

The oct_analysis python package includes various functions for:

- Unpacking *.oct files and loading tiff files as numpy array
- Preprocessing functions to identify and remove objects/boundaries
- Image segmentation and binarization
- Post-processing funtions for the calcuation and saving of structural parameters from the imaging stacks

## Usage
The documentation can be found in https://oct-analysis.readthedocs.io/en/latest/index.html

Examples for the usage of the functions are described in https://github.com/AndreasNetsch/oct_analysis/tree/main/examples

```python
from oct_analysis import (
    read_tiff,
    select_tiff_folder,
    convert_to_8bit,
    find_substratum,
    voxel_count,
    find_max_zero,
    untilt,
    generate_Height_Map
)
```

## Collaboration and Development

### Setup

1. Clone the repository:

```bash
git clone https://github.com/AndreasNetsch/oct_analysis.git
cd oct_analysis
```

2. Create a virtual environment and install development dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Testing

Run tests with pytest:

```bash
pytest
```

### Code Formatting and Linting

This project uses pre-commit hooks to ensure code quality. After installing the development dependencies, set up the pre-commit hooks:

```bash
pre-commit install
```

This will automatically format your code with Black and check it with Flake8 before each commit. You can also run the hooks manually:

```bash
pre-commit run --all-files
```

### Building the package

```bash
python -m build
```

### Documentation

This project uses Sphinx for documentation. To build the documentation locally:

```bash
cd docs
make html
```

The generated documentation will be available in `docs/build/html/index.html`.

#### ReadTheDocs Integration

The documentation is also configured to be built automatically on [ReadTheDocs](https://readthedocs.org/). To set it up:

1. Push your code to GitHub
2. Sign up for a ReadTheDocs account
3. Import your repository on ReadTheDocs
4. ReadTheDocs will automatically build and host the documentation

You can customize the build process by modifying `.readthedocs.yml` and the Sphinx configuration files in the `docs` directory.

## CI/CD

This project uses GitHub Actions for:

- Running tests on multiple Python versions
- Linting the code
- Building and publishing the package to PyPI when a new version tag is pushed

### Creating Releases

The CI/CD pipeline is configured to automatically build and publish the package to PyPI when a new version tag is pushed to the repository. This process ensures that only properly versioned, tagged releases get published.

To create and publish a new release:

1. Update the version number in `setup.py`
2. Commit your changes:
   ```bash
   git add setup.py
   git commit -m "Bump version to x.y.z"
   ```
3. Create a new version tag (tag name must start with "v"):
   ```bash
   git tag vx.y.z
   ```
4. Push the tag to GitHub:
   ```bash
   git push origin vx.y.z
   ```

Once the tag is pushed, GitHub Actions will:

1. Run all tests on multiple Python versions
2. If tests pass, build the package
3. Publish the package to PyPI using the configured PyPI API token

Note: Make sure you've added a `PYPI_API_TOKEN` secret to your GitHub repository settings under "Settings > Secrets and Variables > Actions" before triggering a release.

## License

MIT License
