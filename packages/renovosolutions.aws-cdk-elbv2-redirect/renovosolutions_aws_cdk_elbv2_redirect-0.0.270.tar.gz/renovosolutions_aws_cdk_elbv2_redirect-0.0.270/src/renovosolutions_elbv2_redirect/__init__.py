r'''
# AWS ELBv2 Redirection CDK Construct Library

This library makes it easy to creation redirection rules on Application Load Balancers.

## Usage

### Base redirection construct (Typescript)

```python
// create a vpc
const vpc = new ec2.Vpc(stack, 'vpc');

// create an alb in that vpc
const alb = new elbv2.ApplicationLoadBalancer(stack, 'alb', {
  internetFacing: true,
  vpc,
});

// create a redirect from 8080 to 8443
new Redirect(stack, 'redirect', {
  alb,
  sourcePort: 8080,
  sourceProtocol: elbv2.ApplicationProtocol.HTTP,
  targetPort: 8443,
  targetProtocol: elbv2.ApplicationProtocol.HTTPS,
});
```

### Using the pre-build HTTP to HTTPS construct (Typescript)

```python
// create a vpc
const vpc = new ec2.Vpc(stack, 'vpc');

// create an alb in that vpc
const alb = new elbv2.ApplicationLoadBalancer(stack, 'alb', {
  internetFacing: true,
  vpc,
});

// use the pre-built construct for HTTP to HTTPS
new RedirectHttpHttps(stack, 'redirectHttpHttps', {
  alb,
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

import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import constructs as _constructs_77d1e7e8


class Redirect(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-elbv2-redirect.Redirect",
):
    '''A base redirect construct that takes source and destination ports and protocols.

    Common use cases can be built from this construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        alb: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
        source_port: jsii.Number,
        source_protocol: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol,
        target_port: jsii.Number,
        target_protocol: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param alb: The application load balancer this redirect applies to.
        :param source_port: The source port to redirect from.
        :param source_protocol: The source protocol to redirect from.
        :param target_port: The target port to redirect to.
        :param target_protocol: The target protocol to redirect to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c14402361b5f13aa13172ceafe34e5b2da425b4c94a7cbf348ba3437e88c6a96)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedirectProps(
            alb=alb,
            source_port=source_port,
            source_protocol=source_protocol,
            target_port=target_port,
            target_protocol=target_protocol,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class RedirectHttpHttps(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-elbv2-redirect.RedirectHttpHttps",
):
    '''A construct that redirects HTTP to HTTPS for the given application load balancer.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        alb: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param alb: The application load balancer this redirect applies to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7708d30a249a2ea13afa5d791c1deedf65419e1234fe8d8f4b6e3777b5bb6ce6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedirectHttpHttpsProps(alb=alb)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-elbv2-redirect.RedirectHttpHttpsProps",
    jsii_struct_bases=[],
    name_mapping={"alb": "alb"},
)
class RedirectHttpHttpsProps:
    def __init__(
        self,
        *,
        alb: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
    ) -> None:
        '''Properties for the RedirectHttpHttps construct.

        :param alb: The application load balancer this redirect applies to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23e052a742fd807329da7369ba5f86e9f03ee05f5b44b3419bc6b39c1ff381e1)
            check_type(argname="argument alb", value=alb, expected_type=type_hints["alb"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "alb": alb,
        }

    @builtins.property
    def alb(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer:
        '''The application load balancer this redirect applies to.'''
        result = self._values.get("alb")
        assert result is not None, "Required property 'alb' is missing"
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedirectHttpHttpsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-elbv2-redirect.RedirectProps",
    jsii_struct_bases=[],
    name_mapping={
        "alb": "alb",
        "source_port": "sourcePort",
        "source_protocol": "sourceProtocol",
        "target_port": "targetPort",
        "target_protocol": "targetProtocol",
    },
)
class RedirectProps:
    def __init__(
        self,
        *,
        alb: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
        source_port: jsii.Number,
        source_protocol: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol,
        target_port: jsii.Number,
        target_protocol: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol,
    ) -> None:
        '''The properties for the base redirect construct.

        :param alb: The application load balancer this redirect applies to.
        :param source_port: The source port to redirect from.
        :param source_protocol: The source protocol to redirect from.
        :param target_port: The target port to redirect to.
        :param target_protocol: The target protocol to redirect to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__967bc5d15475b3cc618829dc0f79dfeeb813927c561e3b82a08e1ae56017e5ed)
            check_type(argname="argument alb", value=alb, expected_type=type_hints["alb"])
            check_type(argname="argument source_port", value=source_port, expected_type=type_hints["source_port"])
            check_type(argname="argument source_protocol", value=source_protocol, expected_type=type_hints["source_protocol"])
            check_type(argname="argument target_port", value=target_port, expected_type=type_hints["target_port"])
            check_type(argname="argument target_protocol", value=target_protocol, expected_type=type_hints["target_protocol"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "alb": alb,
            "source_port": source_port,
            "source_protocol": source_protocol,
            "target_port": target_port,
            "target_protocol": target_protocol,
        }

    @builtins.property
    def alb(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer:
        '''The application load balancer this redirect applies to.'''
        result = self._values.get("alb")
        assert result is not None, "Required property 'alb' is missing"
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer, result)

    @builtins.property
    def source_port(self) -> jsii.Number:
        '''The source port to redirect from.'''
        result = self._values.get("source_port")
        assert result is not None, "Required property 'source_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def source_protocol(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol:
        '''The source protocol to redirect from.'''
        result = self._values.get("source_protocol")
        assert result is not None, "Required property 'source_protocol' is missing"
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol, result)

    @builtins.property
    def target_port(self) -> jsii.Number:
        '''The target port to redirect to.'''
        result = self._values.get("target_port")
        assert result is not None, "Required property 'target_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def target_protocol(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol:
        '''The target protocol to redirect to.'''
        result = self._values.get("target_protocol")
        assert result is not None, "Required property 'target_protocol' is missing"
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedirectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Redirect",
    "RedirectHttpHttps",
    "RedirectHttpHttpsProps",
    "RedirectProps",
]

publication.publish()

def _typecheckingstub__c14402361b5f13aa13172ceafe34e5b2da425b4c94a7cbf348ba3437e88c6a96(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    alb: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
    source_port: jsii.Number,
    source_protocol: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol,
    target_port: jsii.Number,
    target_protocol: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7708d30a249a2ea13afa5d791c1deedf65419e1234fe8d8f4b6e3777b5bb6ce6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    alb: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23e052a742fd807329da7369ba5f86e9f03ee05f5b44b3419bc6b39c1ff381e1(
    *,
    alb: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__967bc5d15475b3cc618829dc0f79dfeeb813927c561e3b82a08e1ae56017e5ed(
    *,
    alb: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer,
    source_port: jsii.Number,
    source_protocol: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol,
    target_port: jsii.Number,
    target_protocol: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol,
) -> None:
    """Type checking stubs"""
    pass
