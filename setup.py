from setuptools import setup, find_packages

setup(
    name="transcriber",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask==2.1.0',
        'werkzeug==2.0.1',
        'flask-cors==3.0.10',
        'python-dotenv==1.0.1',
        'pydub==0.25.1',
        'SpeechRecognition==3.8.1',
        'gunicorn==20.1.0',
        'pyaudio>=0.2.11,<0.3.0'
    ],
    entry_points={
        'console_scripts': [
            'transcriber=transcriber.run:main',
        ],
    },
    python_requires=">=3.8",
)
