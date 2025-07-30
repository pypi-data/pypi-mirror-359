import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-cdk-managed-instance-role",
    "version": "2.3.112",
    "description": "AWS CDK Construct Library to create an instance role for instances managed by SSM and capable of joining an AWS managed domain.",
    "license": "Apache-2.0",
    "url": "https://github.com/RenovoSolutions/cdk-library-managed-instance-role.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/RenovoSolutions/cdk-library-managed-instance-role.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "renovosolutions_managed_instance_role",
        "renovosolutions_managed_instance_role._jsii"
    ],
    "package_data": {
        "renovosolutions_managed_instance_role._jsii": [
            "cdk-library-managed-instance-role@2.3.112.jsii.tgz"
        ],
        "renovosolutions_managed_instance_role": [
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
