r'''
# cdk-library-renovo-s3-bucket

An AWS CDK construct library to create S3 buckets with some desirable defaults. Also provides some other helpers to make it easier to apply certain common rules we use.
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

import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


class RenovoS3Bucket(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-renovo-s3-bucket.RenovoS3Bucket",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        lifecycle_rules: typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]],
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime.
        :param name: The name of the bucket.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d81177e9db9a5ef8f99f869c6f42852803673d28ac0b796db3748153fc83f97)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RenovoS3BucketProps(lifecycle_rules=lifecycle_rules, name=name)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.get(self, "bucket"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-renovo-s3-bucket.RenovoS3BucketProps",
    jsii_struct_bases=[],
    name_mapping={"lifecycle_rules": "lifecycleRules", "name": "name"},
)
class RenovoS3BucketProps:
    def __init__(
        self,
        *,
        lifecycle_rules: typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]],
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime.
        :param name: The name of the bucket.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b9125af25c070b060e6cc7be4915b13b28132995931ea63df34818c471f1e95)
            check_type(argname="argument lifecycle_rules", value=lifecycle_rules, expected_type=type_hints["lifecycle_rules"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "lifecycle_rules": lifecycle_rules,
        }
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def lifecycle_rules(self) -> typing.List[_aws_cdk_aws_s3_ceddda9d.LifecycleRule]:
        '''Rules that define how Amazon S3 manages objects during their lifetime.'''
        result = self._values.get("lifecycle_rules")
        assert result is not None, "Required property 'lifecycle_rules' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_s3_ceddda9d.LifecycleRule], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the bucket.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RenovoS3BucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RenovoS3Bucket",
    "RenovoS3BucketProps",
]

publication.publish()

def _typecheckingstub__6d81177e9db9a5ef8f99f869c6f42852803673d28ac0b796db3748153fc83f97(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    lifecycle_rules: typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]],
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b9125af25c070b060e6cc7be4915b13b28132995931ea63df34818c471f1e95(
    *,
    lifecycle_rules: typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]],
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
