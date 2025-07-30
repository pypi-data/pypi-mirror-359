r'''
# cdk-renovo-instance-service

[![build](https://github.com/RenovoSolutions/cdk-library-renovo-instance-service/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-library-renovo-instance-service/actions/workflows/build.yml)
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

import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import constructs as _constructs_77d1e7e8
import managed_instance_role as _managed_instance_role_4b8364e6


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.AmiLookup",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "owners": "owners", "windows": "windows"},
)
class AmiLookup:
    def __init__(
        self,
        *,
        name: builtins.str,
        owners: typing.Optional[typing.Sequence[builtins.str]] = None,
        windows: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param name: The name string to use for AMI lookup.
        :param owners: The owners to use for AMI lookup.
        :param windows: Is this AMI expected to be windows?
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d674b560bd4bc3b219af3059fb55b7053e071d77d2616667b61f7350765bfec0)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument owners", value=owners, expected_type=type_hints["owners"])
            check_type(argname="argument windows", value=windows, expected_type=type_hints["windows"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if owners is not None:
            self._values["owners"] = owners
        if windows is not None:
            self._values["windows"] = windows

    @builtins.property
    def name(self) -> builtins.str:
        '''The name string to use for AMI lookup.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def owners(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The owners to use for AMI lookup.'''
        result = self._values.get("owners")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def windows(self) -> typing.Optional[builtins.bool]:
        '''Is this AMI expected to be windows?'''
        result = self._values.get("windows")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmiLookup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InstanceService(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.InstanceService",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        machine_image: _aws_cdk_aws_ec2_ceddda9d.IMachineImage,
        name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        disable_inline_rules: typing.Optional[builtins.bool] = None,
        enable_cloudwatch_logs: typing.Optional[builtins.bool] = None,
        enabled_no_public_ingress_aspect: typing.Optional[builtins.bool] = None,
        enable_no_db_ports_aspect: typing.Optional[builtins.bool] = None,
        enable_no_remote_management_ports_aspect: typing.Optional[builtins.bool] = None,
        instance_role: typing.Optional[_managed_instance_role_4b8364e6.ManagedInstanceRole] = None,
        key_name: typing.Optional[builtins.str] = None,
        parent_domain: typing.Optional[builtins.str] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        require_imdsv2: typing.Optional[builtins.bool] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
        subnet_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType] = None,
        use_imdsv2_custom_aspect: typing.Optional[builtins.bool] = None,
        user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance_type: The type of instance to launch.
        :param machine_image: AMI to launch.
        :param name: The name of the service the instance is for.
        :param vpc: The VPC to launch the instance in.
        :param allow_all_outbound: Whether the instance could initiate connections to anywhere by default.
        :param availability_zones: Select subnets only in the given AZs.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes
        :param disable_inline_rules: Whether to disable inline ingress and egress rule optimization for the instances security group. If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements. Inlining rules is an optimization for producing smaller stack templates. Sometimes this is not desirable, for example when security group access is managed via tags. The default value can be overriden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'. Default: false
        :param enable_cloudwatch_logs: Whether or not to enable logging to Cloudwatch Logs. Default: true
        :param enabled_no_public_ingress_aspect: Whether or not to prevent security group from containing rules that allow access from the public internet: Any rule with a source from 0.0.0.0/0 or ::/0. If these sources are used when this is enabled and error will be added to CDK metadata and deployment and synth will fail.
        :param enable_no_db_ports_aspect: Whether or not to prevent security group from containing rules that allow access to relational DB ports: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server. If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail. Default: true
        :param enable_no_remote_management_ports_aspect: Whether or not to prevent security group from containing rules that allow access to remote management ports: SSH, RDP, WinRM, WinRM over HTTPs. If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail. Default: true
        :param instance_role: The role to use for this instance. Default: - A new ManagedInstanceRole will be created for this instance
        :param key_name: Name of the SSH keypair to grant access to the instance.
        :param parent_domain: The parent domain of the service.
        :param private_ip_address: Defines a private IP address to associate with the instance.
        :param require_imdsv2: Whether IMDSv2 should be required on this instance. Default: true
        :param security_group: The security group to use for this instance. Default: - A new SecurityGroup will be created for this instance
        :param subnet_type: The subnet type to launch this service in. Default: ec2.SubnetType.PRIVATE_WITH_NAT
        :param use_imdsv2_custom_aspect: Whether to use th IMDSv2 custom aspect provided by this library or the default one provided by AWS. Turned on by default otherwise we need to apply a feature flag to every project using an instance or apply a breaking change to instance construct ids. Default: true
        :param user_data: The user data to apply to the instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e6c6165f88cb76812d03df20762f2a821c24946119dadf31bbfc7466fdb9554)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = InstanceServiceProps(
            instance_type=instance_type,
            machine_image=machine_image,
            name=name,
            vpc=vpc,
            allow_all_outbound=allow_all_outbound,
            availability_zones=availability_zones,
            block_devices=block_devices,
            disable_inline_rules=disable_inline_rules,
            enable_cloudwatch_logs=enable_cloudwatch_logs,
            enabled_no_public_ingress_aspect=enabled_no_public_ingress_aspect,
            enable_no_db_ports_aspect=enable_no_db_ports_aspect,
            enable_no_remote_management_ports_aspect=enable_no_remote_management_ports_aspect,
            instance_role=instance_role,
            key_name=key_name,
            parent_domain=parent_domain,
            private_ip_address=private_ip_address,
            require_imdsv2=require_imdsv2,
            security_group=security_group,
            subnet_type=subnet_type,
            use_imdsv2_custom_aspect=use_imdsv2_custom_aspect,
            user_data=user_data,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="instance")
    def instance(self) -> _aws_cdk_aws_ec2_ceddda9d.Instance:
        '''The underlying instance resource.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Instance, jsii.get(self, "instance"))

    @builtins.property
    @jsii.member(jsii_name="instanceAvailabilityZone")
    def instance_availability_zone(self) -> builtins.str:
        '''The availability zone of the instance.'''
        return typing.cast(builtins.str, jsii.get(self, "instanceAvailabilityZone"))

    @builtins.property
    @jsii.member(jsii_name="instanceCfn")
    def instance_cfn(self) -> _aws_cdk_aws_ec2_ceddda9d.CfnInstance:
        '''The underlying CfnInstance resource.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.CfnInstance, jsii.get(self, "instanceCfn"))

    @builtins.property
    @jsii.member(jsii_name="instanceEc2PrivateDnsName")
    def instance_ec2_private_dns_name(self) -> builtins.str:
        '''Private DNS name for this instance assigned by EC2.'''
        return typing.cast(builtins.str, jsii.get(self, "instanceEc2PrivateDnsName"))

    @builtins.property
    @jsii.member(jsii_name="instanceEc2PublicDnsName")
    def instance_ec2_public_dns_name(self) -> builtins.str:
        '''Public DNS name for this instance assigned by EC2.'''
        return typing.cast(builtins.str, jsii.get(self, "instanceEc2PublicDnsName"))

    @builtins.property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        '''The instance's ID.'''
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @builtins.property
    @jsii.member(jsii_name="instancePrivateIp")
    def instance_private_ip(self) -> builtins.str:
        '''Private IP for this instance.'''
        return typing.cast(builtins.str, jsii.get(self, "instancePrivateIp"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfile")
    def instance_profile(self) -> _aws_cdk_aws_iam_ceddda9d.CfnInstanceProfile:
        '''The instance profile associated with this instance.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.CfnInstanceProfile, jsii.get(self, "instanceProfile"))

    @builtins.property
    @jsii.member(jsii_name="instanceRole")
    def instance_role(self) -> _managed_instance_role_4b8364e6.ManagedInstanceRole:
        '''The instance role associated with this instance.'''
        return typing.cast(_managed_instance_role_4b8364e6.ManagedInstanceRole, jsii.get(self, "instanceRole"))

    @builtins.property
    @jsii.member(jsii_name="osType")
    def os_type(self) -> _aws_cdk_aws_ec2_ceddda9d.OperatingSystemType:
        '''The type of OS the instance is running.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.OperatingSystemType, jsii.get(self, "osType"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.SecurityGroup:
        '''The security group associated with this instance.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SecurityGroup, jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="instanceDnsName")
    def instance_dns_name(
        self,
    ) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.ARecord]:
        '''DNS record for this instance created in Route53.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.ARecord], jsii.get(self, "instanceDnsName"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.InstanceServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "machine_image": "machineImage",
        "name": "name",
        "vpc": "vpc",
        "allow_all_outbound": "allowAllOutbound",
        "availability_zones": "availabilityZones",
        "block_devices": "blockDevices",
        "disable_inline_rules": "disableInlineRules",
        "enable_cloudwatch_logs": "enableCloudwatchLogs",
        "enabled_no_public_ingress_aspect": "enabledNoPublicIngressAspect",
        "enable_no_db_ports_aspect": "enableNoDBPortsAspect",
        "enable_no_remote_management_ports_aspect": "enableNoRemoteManagementPortsAspect",
        "instance_role": "instanceRole",
        "key_name": "keyName",
        "parent_domain": "parentDomain",
        "private_ip_address": "privateIpAddress",
        "require_imdsv2": "requireImdsv2",
        "security_group": "securityGroup",
        "subnet_type": "subnetType",
        "use_imdsv2_custom_aspect": "useImdsv2CustomAspect",
        "user_data": "userData",
    },
)
class InstanceServiceProps:
    def __init__(
        self,
        *,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        machine_image: _aws_cdk_aws_ec2_ceddda9d.IMachineImage,
        name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        disable_inline_rules: typing.Optional[builtins.bool] = None,
        enable_cloudwatch_logs: typing.Optional[builtins.bool] = None,
        enabled_no_public_ingress_aspect: typing.Optional[builtins.bool] = None,
        enable_no_db_ports_aspect: typing.Optional[builtins.bool] = None,
        enable_no_remote_management_ports_aspect: typing.Optional[builtins.bool] = None,
        instance_role: typing.Optional[_managed_instance_role_4b8364e6.ManagedInstanceRole] = None,
        key_name: typing.Optional[builtins.str] = None,
        parent_domain: typing.Optional[builtins.str] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        require_imdsv2: typing.Optional[builtins.bool] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
        subnet_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType] = None,
        use_imdsv2_custom_aspect: typing.Optional[builtins.bool] = None,
        user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
    ) -> None:
        '''
        :param instance_type: The type of instance to launch.
        :param machine_image: AMI to launch.
        :param name: The name of the service the instance is for.
        :param vpc: The VPC to launch the instance in.
        :param allow_all_outbound: Whether the instance could initiate connections to anywhere by default.
        :param availability_zones: Select subnets only in the given AZs.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes
        :param disable_inline_rules: Whether to disable inline ingress and egress rule optimization for the instances security group. If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements. Inlining rules is an optimization for producing smaller stack templates. Sometimes this is not desirable, for example when security group access is managed via tags. The default value can be overriden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'. Default: false
        :param enable_cloudwatch_logs: Whether or not to enable logging to Cloudwatch Logs. Default: true
        :param enabled_no_public_ingress_aspect: Whether or not to prevent security group from containing rules that allow access from the public internet: Any rule with a source from 0.0.0.0/0 or ::/0. If these sources are used when this is enabled and error will be added to CDK metadata and deployment and synth will fail.
        :param enable_no_db_ports_aspect: Whether or not to prevent security group from containing rules that allow access to relational DB ports: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server. If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail. Default: true
        :param enable_no_remote_management_ports_aspect: Whether or not to prevent security group from containing rules that allow access to remote management ports: SSH, RDP, WinRM, WinRM over HTTPs. If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail. Default: true
        :param instance_role: The role to use for this instance. Default: - A new ManagedInstanceRole will be created for this instance
        :param key_name: Name of the SSH keypair to grant access to the instance.
        :param parent_domain: The parent domain of the service.
        :param private_ip_address: Defines a private IP address to associate with the instance.
        :param require_imdsv2: Whether IMDSv2 should be required on this instance. Default: true
        :param security_group: The security group to use for this instance. Default: - A new SecurityGroup will be created for this instance
        :param subnet_type: The subnet type to launch this service in. Default: ec2.SubnetType.PRIVATE_WITH_NAT
        :param use_imdsv2_custom_aspect: Whether to use th IMDSv2 custom aspect provided by this library or the default one provided by AWS. Turned on by default otherwise we need to apply a feature flag to every project using an instance or apply a breaking change to instance construct ids. Default: true
        :param user_data: The user data to apply to the instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adbc60907b40e52c2f3ec1be03a20c5e4e957d8d8b7ae22fe0df279277b9f20e)
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument machine_image", value=machine_image, expected_type=type_hints["machine_image"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument allow_all_outbound", value=allow_all_outbound, expected_type=type_hints["allow_all_outbound"])
            check_type(argname="argument availability_zones", value=availability_zones, expected_type=type_hints["availability_zones"])
            check_type(argname="argument block_devices", value=block_devices, expected_type=type_hints["block_devices"])
            check_type(argname="argument disable_inline_rules", value=disable_inline_rules, expected_type=type_hints["disable_inline_rules"])
            check_type(argname="argument enable_cloudwatch_logs", value=enable_cloudwatch_logs, expected_type=type_hints["enable_cloudwatch_logs"])
            check_type(argname="argument enabled_no_public_ingress_aspect", value=enabled_no_public_ingress_aspect, expected_type=type_hints["enabled_no_public_ingress_aspect"])
            check_type(argname="argument enable_no_db_ports_aspect", value=enable_no_db_ports_aspect, expected_type=type_hints["enable_no_db_ports_aspect"])
            check_type(argname="argument enable_no_remote_management_ports_aspect", value=enable_no_remote_management_ports_aspect, expected_type=type_hints["enable_no_remote_management_ports_aspect"])
            check_type(argname="argument instance_role", value=instance_role, expected_type=type_hints["instance_role"])
            check_type(argname="argument key_name", value=key_name, expected_type=type_hints["key_name"])
            check_type(argname="argument parent_domain", value=parent_domain, expected_type=type_hints["parent_domain"])
            check_type(argname="argument private_ip_address", value=private_ip_address, expected_type=type_hints["private_ip_address"])
            check_type(argname="argument require_imdsv2", value=require_imdsv2, expected_type=type_hints["require_imdsv2"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument subnet_type", value=subnet_type, expected_type=type_hints["subnet_type"])
            check_type(argname="argument use_imdsv2_custom_aspect", value=use_imdsv2_custom_aspect, expected_type=type_hints["use_imdsv2_custom_aspect"])
            check_type(argname="argument user_data", value=user_data, expected_type=type_hints["user_data"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_type": instance_type,
            "machine_image": machine_image,
            "name": name,
            "vpc": vpc,
        }
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if block_devices is not None:
            self._values["block_devices"] = block_devices
        if disable_inline_rules is not None:
            self._values["disable_inline_rules"] = disable_inline_rules
        if enable_cloudwatch_logs is not None:
            self._values["enable_cloudwatch_logs"] = enable_cloudwatch_logs
        if enabled_no_public_ingress_aspect is not None:
            self._values["enabled_no_public_ingress_aspect"] = enabled_no_public_ingress_aspect
        if enable_no_db_ports_aspect is not None:
            self._values["enable_no_db_ports_aspect"] = enable_no_db_ports_aspect
        if enable_no_remote_management_ports_aspect is not None:
            self._values["enable_no_remote_management_ports_aspect"] = enable_no_remote_management_ports_aspect
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if key_name is not None:
            self._values["key_name"] = key_name
        if parent_domain is not None:
            self._values["parent_domain"] = parent_domain
        if private_ip_address is not None:
            self._values["private_ip_address"] = private_ip_address
        if require_imdsv2 is not None:
            self._values["require_imdsv2"] = require_imdsv2
        if security_group is not None:
            self._values["security_group"] = security_group
        if subnet_type is not None:
            self._values["subnet_type"] = subnet_type
        if use_imdsv2_custom_aspect is not None:
            self._values["use_imdsv2_custom_aspect"] = use_imdsv2_custom_aspect
        if user_data is not None:
            self._values["user_data"] = user_data

    @builtins.property
    def instance_type(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''The type of instance to launch.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, result)

    @builtins.property
    def machine_image(self) -> _aws_cdk_aws_ec2_ceddda9d.IMachineImage:
        '''AMI to launch.'''
        result = self._values.get("machine_image")
        assert result is not None, "Required property 'machine_image' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IMachineImage, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the service the instance is for.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC to launch the instance in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether the instance could initiate connections to anywhere by default.'''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Select subnets only in the given AZs.'''
        result = self._values.get("availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def block_devices(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.BlockDevice]]:
        '''Specifies how block devices are exposed to the instance.

        You can specify virtual devices and EBS volumes
        '''
        result = self._values.get("block_devices")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.BlockDevice]], result)

    @builtins.property
    def disable_inline_rules(self) -> typing.Optional[builtins.bool]:
        '''Whether to disable inline ingress and egress rule optimization for the instances security group.

        If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements.

        Inlining rules is an optimization for producing smaller stack templates.
        Sometimes this is not desirable, for example when security group access is managed via tags.

        The default value can be overriden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'.

        :default: false
        '''
        result = self._values.get("disable_inline_rules")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_cloudwatch_logs(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to enable logging to Cloudwatch Logs.

        :default: true
        '''
        result = self._values.get("enable_cloudwatch_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enabled_no_public_ingress_aspect(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to prevent security group from containing rules that allow access from the public internet: Any rule with a source from 0.0.0.0/0 or ::/0.

        If these sources are used when this is enabled and error will be added to CDK metadata and deployment and synth will fail.
        '''
        result = self._values.get("enabled_no_public_ingress_aspect")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_no_db_ports_aspect(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to prevent security group from containing rules that allow access to relational DB ports: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server.

        If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail.

        :default: true
        '''
        result = self._values.get("enable_no_db_ports_aspect")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_no_remote_management_ports_aspect(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Whether or not to prevent security group from containing rules that allow access to remote management ports: SSH, RDP, WinRM, WinRM over HTTPs.

        If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail.

        :default: true
        '''
        result = self._values.get("enable_no_remote_management_ports_aspect")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_role(
        self,
    ) -> typing.Optional[_managed_instance_role_4b8364e6.ManagedInstanceRole]:
        '''The role to use for this instance.

        :default: - A new ManagedInstanceRole will be created for this instance
        '''
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[_managed_instance_role_4b8364e6.ManagedInstanceRole], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''Name of the SSH keypair to grant access to the instance.'''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent_domain(self) -> typing.Optional[builtins.str]:
        '''The parent domain of the service.'''
        result = self._values.get("parent_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_ip_address(self) -> typing.Optional[builtins.str]:
        '''Defines a private IP address to associate with the instance.'''
        result = self._values.get("private_ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def require_imdsv2(self) -> typing.Optional[builtins.bool]:
        '''Whether IMDSv2 should be required on this instance.

        :default: true
        '''
        result = self._values.get("require_imdsv2")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]:
        '''The security group to use for this instance.

        :default: - A new SecurityGroup will be created for this instance
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup], result)

    @builtins.property
    def subnet_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType]:
        '''The subnet type to launch this service in.

        :default: ec2.SubnetType.PRIVATE_WITH_NAT
        '''
        result = self._values.get("subnet_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType], result)

    @builtins.property
    def use_imdsv2_custom_aspect(self) -> typing.Optional[builtins.bool]:
        '''Whether to use th IMDSv2 custom aspect provided by this library or the default one provided by AWS.

        Turned on by default otherwise we need to apply a feature flag to every project using an instance or
        apply a breaking change to instance construct ids.

        :default: true

        :see: https://github.com/jericht/aws-cdk/blob/56c01aedc4f745eec79409c99b749f516ffc39e1/packages/%40aws-cdk/aws-ec2/lib/aspects/require-imdsv2-aspect.ts#L95
        '''
        result = self._values.get("use_imdsv2_custom_aspect")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def user_data(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData]:
        '''The user data to apply to the instance.'''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstanceServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedLoggingPolicy(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.ManagedLoggingPolicy",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        os: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param os: The OS of the instance this policy is for.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__250d7a80abe744f451727d097168e90e5802e7cb034a4e371bc6601984c73958)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ManagedLoggingPolicyProps(os=os)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> _aws_cdk_aws_iam_ceddda9d.ManagedPolicy:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.ManagedPolicy, jsii.get(self, "policy"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.ManagedLoggingPolicyProps",
    jsii_struct_bases=[],
    name_mapping={"os": "os"},
)
class ManagedLoggingPolicyProps:
    def __init__(self, *, os: builtins.str) -> None:
        '''
        :param os: The OS of the instance this policy is for.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__766f3013b3bbcda5f0bc028c1a68c40993ebe6321cf668f202d748fcec7df730)
            check_type(argname="argument os", value=os, expected_type=type_hints["os"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "os": os,
        }

    @builtins.property
    def os(self) -> builtins.str:
        '''The OS of the instance this policy is for.'''
        result = self._values.get("os")
        assert result is not None, "Required property 'os' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedLoggingPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AmiLookup",
    "InstanceService",
    "InstanceServiceProps",
    "ManagedLoggingPolicy",
    "ManagedLoggingPolicyProps",
]

publication.publish()

def _typecheckingstub__d674b560bd4bc3b219af3059fb55b7053e071d77d2616667b61f7350765bfec0(
    *,
    name: builtins.str,
    owners: typing.Optional[typing.Sequence[builtins.str]] = None,
    windows: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e6c6165f88cb76812d03df20762f2a821c24946119dadf31bbfc7466fdb9554(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    machine_image: _aws_cdk_aws_ec2_ceddda9d.IMachineImage,
    name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    disable_inline_rules: typing.Optional[builtins.bool] = None,
    enable_cloudwatch_logs: typing.Optional[builtins.bool] = None,
    enabled_no_public_ingress_aspect: typing.Optional[builtins.bool] = None,
    enable_no_db_ports_aspect: typing.Optional[builtins.bool] = None,
    enable_no_remote_management_ports_aspect: typing.Optional[builtins.bool] = None,
    instance_role: typing.Optional[_managed_instance_role_4b8364e6.ManagedInstanceRole] = None,
    key_name: typing.Optional[builtins.str] = None,
    parent_domain: typing.Optional[builtins.str] = None,
    private_ip_address: typing.Optional[builtins.str] = None,
    require_imdsv2: typing.Optional[builtins.bool] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
    subnet_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType] = None,
    use_imdsv2_custom_aspect: typing.Optional[builtins.bool] = None,
    user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adbc60907b40e52c2f3ec1be03a20c5e4e957d8d8b7ae22fe0df279277b9f20e(
    *,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    machine_image: _aws_cdk_aws_ec2_ceddda9d.IMachineImage,
    name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    disable_inline_rules: typing.Optional[builtins.bool] = None,
    enable_cloudwatch_logs: typing.Optional[builtins.bool] = None,
    enabled_no_public_ingress_aspect: typing.Optional[builtins.bool] = None,
    enable_no_db_ports_aspect: typing.Optional[builtins.bool] = None,
    enable_no_remote_management_ports_aspect: typing.Optional[builtins.bool] = None,
    instance_role: typing.Optional[_managed_instance_role_4b8364e6.ManagedInstanceRole] = None,
    key_name: typing.Optional[builtins.str] = None,
    parent_domain: typing.Optional[builtins.str] = None,
    private_ip_address: typing.Optional[builtins.str] = None,
    require_imdsv2: typing.Optional[builtins.bool] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup] = None,
    subnet_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType] = None,
    use_imdsv2_custom_aspect: typing.Optional[builtins.bool] = None,
    user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__250d7a80abe744f451727d097168e90e5802e7cb034a4e371bc6601984c73958(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    os: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__766f3013b3bbcda5f0bc028c1a68c40993ebe6321cf668f202d748fcec7df730(
    *,
    os: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
