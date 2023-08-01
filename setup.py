from distutils.core import setup

setup(
    name="dosimat",
    version="0.1",
    description="SDK for Dosimat 876",
    packages=["dosimat_driver", "dosimat_http"],
    install_requires=[
        "pyserial",
        "fastapi",
        "uvicorn",
    ],
)
