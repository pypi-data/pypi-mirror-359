r'''
# cdk-library-managed-instance-role

[![build](https://github.com/RenovoSolutions/cdk-library-managed-instance-role/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-library-managed-instance-role/workflows/build.yml)

This CDK Construct Library includes a construct (`ManagedInstanceRole`) which creates an AWS instance profile. By default this instance profile includes the basic policies required for instance management in SSM and the ability to Domain Join the instance.

The purpose of this CDK Construct Library is to ease the creation of instance roles by not needing to code the inclusion of baseline management roles for evey single different role implementation every time. Instance profiles only support a single role so its important the role includes all required access. This construct allows making additions to those baseline policies with ease.

The construct defines an interface (`IManagedInstanceRoleProps`) to configure the managed policies of the role as well as manage the inclusion of the default roles.

## Dev

### Pre-reqs:

You will need:

* npm installed on your machine
* AWS CDK installed on your machine
* python installed on your machine
* dotnet installed on your machine
* a github account

This project is managed with `projen`. Modify the `.projenrc.js` file and run `npx projen`. You can also modify this `README` file and the `src` code directory as needed. Github actions take care of publishing utilizing the automatically created workflows from `projen`.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8


class ManagedInstanceRole(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-managed-instance-role.ManagedInstanceRole",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        create_instance_profile: typing.Optional[builtins.bool] = None,
        domain_join_enabled: typing.Optional[builtins.bool] = None,
        managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.ManagedPolicy]] = None,
        retention_policy: typing.Optional[builtins.bool] = None,
        ssm_management_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param create_instance_profile: Whether or not to associate the role with an instance profile. Default: true
        :param domain_join_enabled: Should the role include directory service access with SSM.
        :param managed_policies: The managed policies to apply to the role in addition to the default policies.
        :param retention_policy: The retention policy for this role.
        :param ssm_management_enabled: Should the role include SSM management. By default if domainJoinEnabled is true then this role is always included.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83f560e4dc759ebe2ceca3b46424c095a7f4f3617f778ecd424d8a1078704302)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ManagedInstanceRoleProps(
            create_instance_profile=create_instance_profile,
            domain_join_enabled=domain_join_enabled,
            managed_policies=managed_policies,
            retention_policy=retention_policy,
            ssm_management_enabled=ssm_management_enabled,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''The role arn.'''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The role name.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''The role.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfile")
    def instance_profile(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.CfnInstanceProfile]:
        '''The CfnInstanceProfile automatically created for this role.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.CfnInstanceProfile], jsii.get(self, "instanceProfile"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-managed-instance-role.ManagedInstanceRoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "create_instance_profile": "createInstanceProfile",
        "domain_join_enabled": "domainJoinEnabled",
        "managed_policies": "managedPolicies",
        "retention_policy": "retentionPolicy",
        "ssm_management_enabled": "ssmManagementEnabled",
    },
)
class ManagedInstanceRoleProps:
    def __init__(
        self,
        *,
        create_instance_profile: typing.Optional[builtins.bool] = None,
        domain_join_enabled: typing.Optional[builtins.bool] = None,
        managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.ManagedPolicy]] = None,
        retention_policy: typing.Optional[builtins.bool] = None,
        ssm_management_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param create_instance_profile: Whether or not to associate the role with an instance profile. Default: true
        :param domain_join_enabled: Should the role include directory service access with SSM.
        :param managed_policies: The managed policies to apply to the role in addition to the default policies.
        :param retention_policy: The retention policy for this role.
        :param ssm_management_enabled: Should the role include SSM management. By default if domainJoinEnabled is true then this role is always included.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dc346b2a1a5c2a6efa7437dd14db41986afb15e073cd0b7f07a5535dff51898)
            check_type(argname="argument create_instance_profile", value=create_instance_profile, expected_type=type_hints["create_instance_profile"])
            check_type(argname="argument domain_join_enabled", value=domain_join_enabled, expected_type=type_hints["domain_join_enabled"])
            check_type(argname="argument managed_policies", value=managed_policies, expected_type=type_hints["managed_policies"])
            check_type(argname="argument retention_policy", value=retention_policy, expected_type=type_hints["retention_policy"])
            check_type(argname="argument ssm_management_enabled", value=ssm_management_enabled, expected_type=type_hints["ssm_management_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create_instance_profile is not None:
            self._values["create_instance_profile"] = create_instance_profile
        if domain_join_enabled is not None:
            self._values["domain_join_enabled"] = domain_join_enabled
        if managed_policies is not None:
            self._values["managed_policies"] = managed_policies
        if retention_policy is not None:
            self._values["retention_policy"] = retention_policy
        if ssm_management_enabled is not None:
            self._values["ssm_management_enabled"] = ssm_management_enabled

    @builtins.property
    def create_instance_profile(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to associate the role with an instance profile.

        :default: true
        '''
        result = self._values.get("create_instance_profile")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain_join_enabled(self) -> typing.Optional[builtins.bool]:
        '''Should the role include directory service access with SSM.'''
        result = self._values.get("domain_join_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def managed_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.ManagedPolicy]]:
        '''The managed policies to apply to the role in addition to the default policies.'''
        result = self._values.get("managed_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.ManagedPolicy]], result)

    @builtins.property
    def retention_policy(self) -> typing.Optional[builtins.bool]:
        '''The retention policy for this role.'''
        result = self._values.get("retention_policy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ssm_management_enabled(self) -> typing.Optional[builtins.bool]:
        '''Should the role include SSM management.

        By default if domainJoinEnabled is true then this role is always included.
        '''
        result = self._values.get("ssm_management_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ManagedInstanceRole",
    "ManagedInstanceRoleProps",
]

publication.publish()

def _typecheckingstub__83f560e4dc759ebe2ceca3b46424c095a7f4f3617f778ecd424d8a1078704302(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    create_instance_profile: typing.Optional[builtins.bool] = None,
    domain_join_enabled: typing.Optional[builtins.bool] = None,
    managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.ManagedPolicy]] = None,
    retention_policy: typing.Optional[builtins.bool] = None,
    ssm_management_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dc346b2a1a5c2a6efa7437dd14db41986afb15e073cd0b7f07a5535dff51898(
    *,
    create_instance_profile: typing.Optional[builtins.bool] = None,
    domain_join_enabled: typing.Optional[builtins.bool] = None,
    managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.ManagedPolicy]] = None,
    retention_policy: typing.Optional[builtins.bool] = None,
    ssm_management_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
