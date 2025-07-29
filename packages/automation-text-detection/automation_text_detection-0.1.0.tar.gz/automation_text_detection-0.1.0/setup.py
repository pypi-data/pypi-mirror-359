from setuptools import setup, find_packages

setup(
    name='automation_text_detection',
    version='0.1.0',  # Update this for each release
    author='Shivam Koshta',
    author_email='skoshta@nvidia.com',
    description='OCR text matching tool using EasyOCR',
    packages=find_packages(),
    install_requires=[
        'easyocr',
        'numpy',
        'tqdm'
        # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'automation-text-detection=automation_text_detection.automation_text_detection:main'
        ]
    },
    python_requires='>=3.7',
)
