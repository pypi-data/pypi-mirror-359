import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-iam-access-key",
    "version": "0.0.38",
    "description": "AWS CDK Construct Library for generating AWS access keys and storing them in Secrets Manager",
    "license": "Apache-2.0",
    "url": "https://github.com/brandon/cdk-library-aws-iam-access-key.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/brandon/cdk-library-aws-iam-access-key.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "renovosolutions_iam_access_key",
        "renovosolutions_iam_access_key._jsii"
    ],
    "package_data": {
        "renovosolutions_iam_access_key._jsii": [
            "cdk-library-aws-iam-access-key@0.0.38.jsii.tgz"
        ],
        "renovosolutions_iam_access_key": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.202.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.112.0, <2.0.0",
        "publication>=0.0.3",
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
