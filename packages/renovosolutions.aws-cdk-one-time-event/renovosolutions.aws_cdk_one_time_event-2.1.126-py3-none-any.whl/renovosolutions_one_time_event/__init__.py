r'''
# cdk-library-one-time-event

[![build](https://github.com/RenovoSolutions/cdk-library-one-time-event/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-library-one-time-event/workflows/build.yml)

An AWS CDK Construct library to create one time event [schedules](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-events.Schedule.html).

## Features

* Create two types of event [schedules](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-events.Schedule.html) easily:

  * On Deployment: An one time event schedule for directly after deployment. Defaults to 10mins after.
  * At: A one time even schedule for any future `Date()`

## API Doc

See [API](API.md)

## Examples

### Typescript - run after deploy, offset 15mins

```
import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as oneTimeEvents from '@renovosolutions/cdk-library-one-time-event';

export class CdkExampleLambdaStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const handler = new lambda.Function(this, 'handler', {
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset(functionDir + '/function.zip'),
      handler: 'index.handler',
    });

    new events.Rule(this, 'triggerImmediate', {
      schedule: new oneTimeEvents.OnDeploy(this, 'schedule', {
        offsetMinutes: 15
      }).schedule,
      targets: [new targets.LambdaFunction(this.handler)],
    });
```

### Typescript - run in 24 hours

```
import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as oneTimeEvents from '@renovosolutions/cdk-library-one-time-event';

export class CdkExampleLambdaStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const handler = new lambda.Function(this, 'handler', {
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset(functionDir + '/function.zip'),
      handler: 'index.handler',
    });

    var tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)

    new events.Rule(this, 'triggerImmediate', {
      schedule: new oneTimeEvents.At(this, 'schedule', {
        date: tomorrow
      }).schedule,
      targets: [new targets.LambdaFunction(this.handler)],
    });
```
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

import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import constructs as _constructs_77d1e7e8


class At(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-one-time-event.At",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        date: datetime.datetime,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param date: The future date to use for one time event.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01e952a3f332c9d8d6735c6621d3bdc1bea9f1a064f97253ae570032bf1409aa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AtProps(date=date)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> _aws_cdk_aws_events_ceddda9d.Schedule:
        return typing.cast(_aws_cdk_aws_events_ceddda9d.Schedule, jsii.get(self, "schedule"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-one-time-event.AtProps",
    jsii_struct_bases=[],
    name_mapping={"date": "date"},
)
class AtProps:
    def __init__(self, *, date: datetime.datetime) -> None:
        '''
        :param date: The future date to use for one time event.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c14a7ae7e07f1e704557c8a57023580aa722a58e085fc685ba147e21f8d89e1)
            check_type(argname="argument date", value=date, expected_type=type_hints["date"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "date": date,
        }

    @builtins.property
    def date(self) -> datetime.datetime:
        '''The future date to use for one time event.'''
        result = self._values.get("date")
        assert result is not None, "Required property 'date' is missing"
        return typing.cast(datetime.datetime, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AtProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnDeploy(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-one-time-event.OnDeploy",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        offset_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param offset_minutes: The number of minutes to add to the current time when generating the expression. Should exceed the expected time for the appropriate resources to converge. Default: 10
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57956d249da883f4d6c0bcea3c07546bf8c8c07debe96d749e1d0fac4d7981c6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OnDeployProps(offset_minutes=offset_minutes)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> _aws_cdk_aws_events_ceddda9d.Schedule:
        return typing.cast(_aws_cdk_aws_events_ceddda9d.Schedule, jsii.get(self, "schedule"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-one-time-event.OnDeployProps",
    jsii_struct_bases=[],
    name_mapping={"offset_minutes": "offsetMinutes"},
)
class OnDeployProps:
    def __init__(self, *, offset_minutes: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param offset_minutes: The number of minutes to add to the current time when generating the expression. Should exceed the expected time for the appropriate resources to converge. Default: 10
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84bc8a128f08bc78dc5cdb055b19110b265710457c7bf6f00254c0cdff7cd34f)
            check_type(argname="argument offset_minutes", value=offset_minutes, expected_type=type_hints["offset_minutes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if offset_minutes is not None:
            self._values["offset_minutes"] = offset_minutes

    @builtins.property
    def offset_minutes(self) -> typing.Optional[jsii.Number]:
        '''The number of minutes to add to the current time when generating the expression.

        Should exceed the expected time for the appropriate resources to converge.

        :default: 10
        '''
        result = self._values.get("offset_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnDeployProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "At",
    "AtProps",
    "OnDeploy",
    "OnDeployProps",
]

publication.publish()

def _typecheckingstub__01e952a3f332c9d8d6735c6621d3bdc1bea9f1a064f97253ae570032bf1409aa(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    date: datetime.datetime,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c14a7ae7e07f1e704557c8a57023580aa722a58e085fc685ba147e21f8d89e1(
    *,
    date: datetime.datetime,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57956d249da883f4d6c0bcea3c07546bf8c8c07debe96d749e1d0fac4d7981c6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    offset_minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84bc8a128f08bc78dc5cdb055b19110b265710457c7bf6f00254c0cdff7cd34f(
    *,
    offset_minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
