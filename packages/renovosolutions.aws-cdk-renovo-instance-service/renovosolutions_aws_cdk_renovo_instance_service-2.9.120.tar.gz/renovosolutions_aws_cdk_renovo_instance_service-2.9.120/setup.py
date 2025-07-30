import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-cdk-renovo-instance-service",
    "version": "2.9.120",
    "description": "CDK Construct Library to create instance based services utilizing default configurations for Renovo Solutions.",
    "license": "Apache-2.0",
    "url": "https://github.com/RenovoSolutions/cdk-library-renovo-instance-service.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/RenovoSolutions/cdk-library-renovo-instance-service.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "renovosolutions_instance_service",
        "renovosolutions_instance_service._jsii"
    ],
    "package_data": {
        "renovosolutions_instance_service._jsii": [
            "cdk-library-renovo-instance-service@2.9.120.jsii.tgz"
        ],
        "renovosolutions_instance_service": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.202.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.112.0, <2.0.0",
        "publication>=0.0.3",
        "renovosolutions.aws-cdk-aspects-security-group>=2.0.43, <3.0.0",
        "renovosolutions.aws-cdk-managed-instance-role>=2.2.3, <3.0.0",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
