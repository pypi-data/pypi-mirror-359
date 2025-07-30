from setuptools import setup, find_packages

setup(
    name="updogfx",
    version="0.2.1",
    author="EFXTv",  # Optional but recommended
    description="A Flask-based file upload server with Cloudflare Tunnel integration.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/efxtv/updogfx",  # Replace with real URL
    project_urls={
        "Bug Tracker": "https://github.com/efxtv/updogfx/issues",
    },
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "updogfx = updogfx.app:main",
        ],
    },
    package_data={
        "updogfx": ["templates/*.html"],
    },
    python_requires=">=3.6",
)
