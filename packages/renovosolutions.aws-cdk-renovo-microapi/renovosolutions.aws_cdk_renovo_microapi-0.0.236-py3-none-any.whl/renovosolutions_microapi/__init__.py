r'''
# Renovo Solutions Private Lambda Micro REST API (`proxy`) Infrastructure Library

[![build](https://github.com/RenovoSolutions/cdk-library-renovo-microapi/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-library-renovo-microapi/workflows/build.yml)

This infrastructure construct library implements a private lambda backed REST API on AWS API Gateway using `proxy+`.

## Features

* Utilizes an internal Micro API project to provide an api via Lambda ([with `proxy+`](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-set-up-simple-proxy.html)) and API Gateway
* Configures the required VPC endpoint attachment automatically
* Configures logging for API requests
* Configures the private gateways policy to restrict access to the VPC endpoint
* Exports the private DNS name to be used in the app

## What this construct does not do

* Provide the VPC endpoint with private DNS enabled. The user utilizing this construct should create a single VPC endpoint with private DNS enabled and share it across all projects utilizing this consturct.

## Private API Gateway traffic flow using VPC Endpoint

API gateways are a managed service that lives outside of our own VPC. Therefore when creating a private gateway this means that in order to access it additional configurations need to occur. Specifically a VPC endpoint must exist for traffic to route to the API Gateway. In addition the Lambda service itself also lives outside our VPC. This can seem a bit complex given that most of our Micro API projects then return to the VPC to route traffic to the database. To help visualize what this looks like here is a diagram of this traffic flow when routing through the api gateway for Micro APIs:

![private api traffic flow](docs/private_api_traffic.png)

## The old setup, using public traffic flow

We used to deploy API gateways as public endpoints. For the sake of comparison here is what the old traffic flow would have looked like:

![public api traffic flow](docs/public_api_traffic.png)

## References

* [Creating a private API in Amazon API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-private-apis.html)
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import constructs as _constructs_77d1e7e8


class MicroApi(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-renovo-microapi.MicroApi",
):
    '''A CDK construct that creates an API Gateway and Lambda function that can be used to expose a Micro API project for RenovoLive.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        allowed_origins: typing.Sequence[builtins.str],
        api_name: builtins.str,
        code: _aws_cdk_aws_lambda_ceddda9d.Code,
        handler: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        vpc_endpoint: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint,
        authorization_type: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.AuthorizationType] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        ephemeral_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        runtime: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Runtime] = None,
        stage_name: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param allowed_origins: The allowed origins for CORS policy on the API Gateway.
        :param api_name: The name of the project this Micro API is for.
        :param code: The lambda code to use for this Micro API.
        :param handler: The name of the method within your code that Lambda calls to execute your function. The format includes the file name. It can also include namespaces and other qualifiers, depending on the runtime. For more information:
        :param vpc: The vpc where the Lambda function will run.
        :param vpc_endpoint: The vpc endpoint to associate the API with.
        :param authorization_type: The type of authorization to use for the API. Default: apigateway.AuthorizationType.IAM
        :param environment: The environment variables the Lambda function will use.
        :param ephemeral_storage_size: The size of the functions ``/tmp`` directory in MB. Default: Size.mebibytes(512)
        :param memory_size: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. Default: 128
        :param runtime: The runtime to use for this Micro API. Default: lambda.Runtime.DOTNET_6
        :param stage_name: The stage name to use for the deployment. Default: 'dev'
        :param timeout: The lambda function timeout. Default: Duration.seconds(30)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__208508095b76f80a88fe17c3adac50eda880230c26ad51ed9f0d7cc56be6b547)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MicroApiProps(
            allowed_origins=allowed_origins,
            api_name=api_name,
            code=code,
            handler=handler,
            vpc=vpc,
            vpc_endpoint=vpc_endpoint,
            authorization_type=authorization_type,
            environment=environment,
            ephemeral_storage_size=ephemeral_storage_size,
            memory_size=memory_size,
            runtime=runtime,
            stage_name=stage_name,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-renovo-microapi.MicroApiProps",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_origins": "allowedOrigins",
        "api_name": "apiName",
        "code": "code",
        "handler": "handler",
        "vpc": "vpc",
        "vpc_endpoint": "vpcEndpoint",
        "authorization_type": "authorizationType",
        "environment": "environment",
        "ephemeral_storage_size": "ephemeralStorageSize",
        "memory_size": "memorySize",
        "runtime": "runtime",
        "stage_name": "stageName",
        "timeout": "timeout",
    },
)
class MicroApiProps:
    def __init__(
        self,
        *,
        allowed_origins: typing.Sequence[builtins.str],
        api_name: builtins.str,
        code: _aws_cdk_aws_lambda_ceddda9d.Code,
        handler: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        vpc_endpoint: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint,
        authorization_type: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.AuthorizationType] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        ephemeral_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        runtime: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Runtime] = None,
        stage_name: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param allowed_origins: The allowed origins for CORS policy on the API Gateway.
        :param api_name: The name of the project this Micro API is for.
        :param code: The lambda code to use for this Micro API.
        :param handler: The name of the method within your code that Lambda calls to execute your function. The format includes the file name. It can also include namespaces and other qualifiers, depending on the runtime. For more information:
        :param vpc: The vpc where the Lambda function will run.
        :param vpc_endpoint: The vpc endpoint to associate the API with.
        :param authorization_type: The type of authorization to use for the API. Default: apigateway.AuthorizationType.IAM
        :param environment: The environment variables the Lambda function will use.
        :param ephemeral_storage_size: The size of the functions ``/tmp`` directory in MB. Default: Size.mebibytes(512)
        :param memory_size: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. Default: 128
        :param runtime: The runtime to use for this Micro API. Default: lambda.Runtime.DOTNET_6
        :param stage_name: The stage name to use for the deployment. Default: 'dev'
        :param timeout: The lambda function timeout. Default: Duration.seconds(30)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__067da552d51a5a93d8e7697ba4896b734f9184fcc5aed41ac8f742975ad7edbc)
            check_type(argname="argument allowed_origins", value=allowed_origins, expected_type=type_hints["allowed_origins"])
            check_type(argname="argument api_name", value=api_name, expected_type=type_hints["api_name"])
            check_type(argname="argument code", value=code, expected_type=type_hints["code"])
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_endpoint", value=vpc_endpoint, expected_type=type_hints["vpc_endpoint"])
            check_type(argname="argument authorization_type", value=authorization_type, expected_type=type_hints["authorization_type"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument ephemeral_storage_size", value=ephemeral_storage_size, expected_type=type_hints["ephemeral_storage_size"])
            check_type(argname="argument memory_size", value=memory_size, expected_type=type_hints["memory_size"])
            check_type(argname="argument runtime", value=runtime, expected_type=type_hints["runtime"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "allowed_origins": allowed_origins,
            "api_name": api_name,
            "code": code,
            "handler": handler,
            "vpc": vpc,
            "vpc_endpoint": vpc_endpoint,
        }
        if authorization_type is not None:
            self._values["authorization_type"] = authorization_type
        if environment is not None:
            self._values["environment"] = environment
        if ephemeral_storage_size is not None:
            self._values["ephemeral_storage_size"] = ephemeral_storage_size
        if memory_size is not None:
            self._values["memory_size"] = memory_size
        if runtime is not None:
            self._values["runtime"] = runtime
        if stage_name is not None:
            self._values["stage_name"] = stage_name
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def allowed_origins(self) -> typing.List[builtins.str]:
        '''The allowed origins for CORS policy on the API Gateway.'''
        result = self._values.get("allowed_origins")
        assert result is not None, "Required property 'allowed_origins' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def api_name(self) -> builtins.str:
        '''The name of the project this Micro API is for.'''
        result = self._values.get("api_name")
        assert result is not None, "Required property 'api_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code(self) -> _aws_cdk_aws_lambda_ceddda9d.Code:
        '''The lambda code to use for this Micro API.'''
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Code, result)

    @builtins.property
    def handler(self) -> builtins.str:
        '''The name of the method within your code that Lambda calls to execute your function.

        The format includes the file name. It can also include namespaces and other qualifiers, depending on the runtime. For more information:

        :see:

        https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-features.html#gettingstarted-features-programmingmodel

        Use ``Handler.FROM_IMAGE`` when defining a function from a Docker image.

        NOTE: If you specify your source code as inline text by specifying the ZipFile property within the Code property, specify index.function_name as the handler.
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The vpc where the Lambda function will run.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def vpc_endpoint(self) -> _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint:
        '''The vpc endpoint to associate the API with.'''
        result = self._values.get("vpc_endpoint")
        assert result is not None, "Required property 'vpc_endpoint' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint, result)

    @builtins.property
    def authorization_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.AuthorizationType]:
        '''The type of authorization to use for the API.

        :default: apigateway.AuthorizationType.IAM
        '''
        result = self._values.get("authorization_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.AuthorizationType], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The environment variables the Lambda function will use.'''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def ephemeral_storage_size(self) -> typing.Optional[_aws_cdk_ceddda9d.Size]:
        '''The size of the functions ``/tmp`` directory in MB.

        :default: Size.mebibytes(512)
        '''
        result = self._values.get("ephemeral_storage_size")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Size], result)

    @builtins.property
    def memory_size(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory, in MB, that is allocated to your Lambda function.

        Lambda uses this value to proportionally allocate the amount of CPU power.

        :default: 128

        :see: https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-common.html#configuration-memory-console
        '''
        result = self._values.get("memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def runtime(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Runtime]:
        '''The runtime to use for this Micro API.

        :default: lambda.Runtime.DOTNET_6
        '''
        result = self._values.get("runtime")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Runtime], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''The stage name to use for the deployment.

        :default: 'dev'
        '''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The lambda function timeout.

        :default: Duration.seconds(30)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicroApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "MicroApi",
    "MicroApiProps",
]

publication.publish()

def _typecheckingstub__208508095b76f80a88fe17c3adac50eda880230c26ad51ed9f0d7cc56be6b547(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    allowed_origins: typing.Sequence[builtins.str],
    api_name: builtins.str,
    code: _aws_cdk_aws_lambda_ceddda9d.Code,
    handler: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    vpc_endpoint: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint,
    authorization_type: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.AuthorizationType] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ephemeral_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    memory_size: typing.Optional[jsii.Number] = None,
    runtime: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Runtime] = None,
    stage_name: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__067da552d51a5a93d8e7697ba4896b734f9184fcc5aed41ac8f742975ad7edbc(
    *,
    allowed_origins: typing.Sequence[builtins.str],
    api_name: builtins.str,
    code: _aws_cdk_aws_lambda_ceddda9d.Code,
    handler: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    vpc_endpoint: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint,
    authorization_type: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.AuthorizationType] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ephemeral_storage_size: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    memory_size: typing.Optional[jsii.Number] = None,
    runtime: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Runtime] = None,
    stage_name: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass
