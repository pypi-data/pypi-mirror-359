r'''
# cdk-library-control-tower-lifecycle-events

NOTE: This project is in active development.

This construct library contains events that represent lifecycle events in Control Tower or events related to actions in Control Tower. See the [API](API.md) for full details on the available constructs.

## References

* [Reference](https://github.com/aws/aws-cdk/issues/3235) for creating constructs that extend and existing one more easily
* [Control Tower Lifecycle Events](https://docs.aws.amazon.com/controltower/latest/userguide/lifecycle-events.html) AWS doc
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


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.BaseRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "enabled": "enabled",
        "event_bus": "eventBus",
        "event_state": "eventState",
        "rule_name": "ruleName",
        "targets": "targets",
    },
)
class BaseRuleProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional["EventStates"] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    ) -> None:
        '''
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__330bef8ade77cd3402f72de78d0f55e9cf39c751e67e9d2c203a87731e2fc205)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument event_bus", value=event_bus, expected_type=type_hints["event_bus"])
            check_type(argname="argument event_state", value=event_state, expected_type=type_hints["event_state"])
            check_type(argname="argument rule_name", value=rule_name, expected_type=type_hints["rule_name"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if event_bus is not None:
            self._values["event_bus"] = event_bus
        if event_state is not None:
            self._values["event_state"] = event_state
        if rule_name is not None:
            self._values["rule_name"] = rule_name
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the rule's purpose.

        :default: - A rule for new account creation in Organizations
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the rule is enabled.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_bus(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus]:
        '''The event bus to associate with this rule.

        :default: - The default event bus.
        '''
        result = self._values.get("event_bus")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus], result)

    @builtins.property
    def event_state(self) -> typing.Optional["EventStates"]:
        '''Which event state should this rule trigger for.

        :default: - EventStates.SUCCEEDED
        '''
        result = self._values.get("event_state")
        return typing.cast(typing.Optional["EventStates"], result)

    @builtins.property
    def rule_name(self) -> typing.Optional[builtins.str]:
        '''A name for the rule.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that ID
        for the rule name. For more information, see Name Type.
        '''
        result = self._values.get("rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Targets to invoke when this rule matches an event.

        :default: - No targets.
        '''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CreatedAccountByOrganizationsRule(
    _aws_cdk_aws_events_ceddda9d.Rule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.CreatedAccountByOrganizationsRule",
):
    '''A rule for matching events from CloudTrail where Organizations created a new account.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional["EventStates"] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11a7e73b6e61c4394a520bb20a640d0d5d65ba0bc09566e755e169617c7fa2fc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BaseRuleProps(
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_state=event_state,
            rule_name=rule_name,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class CreatedAccountRule(
    _aws_cdk_aws_events_ceddda9d.Rule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.CreatedAccountRule",
):
    '''A rule for matching events from CloudTrail where Control Tower created a new account.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        ou_id: typing.Optional[builtins.str] = None,
        ou_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional["EventStates"] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ou_id: The OU ID to match.
        :param ou_name: The OU name to match.
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df0be9333691e70162d32bb21fc1c8e0104aa52c77fcbcf94cc5c25bfa585778)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OuRuleProps(
            ou_id=ou_id,
            ou_name=ou_name,
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_state=event_state,
            rule_name=rule_name,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class DeregisteredOrganizationalUnitRule(
    _aws_cdk_aws_events_ceddda9d.Rule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.DeregisteredOrganizationalUnitRule",
):
    '''A rule for matching events from CloudTrail where Control Tower deregistered an Organizational Unit.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        ou_id: typing.Optional[builtins.str] = None,
        ou_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional["EventStates"] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ou_id: The OU ID to match.
        :param ou_name: The OU name to match.
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__116d3138d6e0467df3fdff63ba8793e903bd6ba94f61f763b572589878ee47a3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OuRuleProps(
            ou_id=ou_id,
            ou_name=ou_name,
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_state=event_state,
            rule_name=rule_name,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class DisabledGuardrailRule(
    _aws_cdk_aws_events_ceddda9d.Rule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.DisabledGuardrailRule",
):
    '''A rule for matching events from CloudTrail where a guard rail was disabled via Control Tower for an Organizational Unit.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        guardrail_behavior: typing.Optional["GuardrailBehaviors"] = None,
        guardrail_id: typing.Optional[builtins.str] = None,
        ou_id: typing.Optional[builtins.str] = None,
        ou_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional["EventStates"] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param guardrail_behavior: The guardrail behavior to match.
        :param guardrail_id: The guardrail ID to match.
        :param ou_id: The OU ID to match.
        :param ou_name: The OU name to match.
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5468930d02dfe3e158ff50fd426632fc1a8b0d1e98eb0b5f3983e925f24a231)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GuardrailRuleProps(
            guardrail_behavior=guardrail_behavior,
            guardrail_id=guardrail_id,
            ou_id=ou_id,
            ou_name=ou_name,
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_state=event_state,
            rule_name=rule_name,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class EnabledGuardrailRule(
    _aws_cdk_aws_events_ceddda9d.Rule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.EnabledGuardrailRule",
):
    '''A rule for matching events from CloudTrail where a guardrail was enabled via Control Tower for an Organizational Unit.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        guardrail_behavior: typing.Optional["GuardrailBehaviors"] = None,
        guardrail_id: typing.Optional[builtins.str] = None,
        ou_id: typing.Optional[builtins.str] = None,
        ou_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional["EventStates"] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param guardrail_behavior: The guardrail behavior to match.
        :param guardrail_id: The guardrail ID to match.
        :param ou_id: The OU ID to match.
        :param ou_name: The OU name to match.
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2912d56398fe0648791de639f789e1683c6fa64493a6e3ec522c80927a48bf19)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GuardrailRuleProps(
            guardrail_behavior=guardrail_behavior,
            guardrail_id=guardrail_id,
            ou_id=ou_id,
            ou_name=ou_name,
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_state=event_state,
            rule_name=rule_name,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.enum(
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.EventStates"
)
class EventStates(enum.Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@jsii.enum(
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.GuardrailBehaviors"
)
class GuardrailBehaviors(enum.Enum):
    DETECTIVE = "DETECTIVE"
    PREVENTATIVE = "PREVENTATIVE"


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.GuardrailRuleProps",
    jsii_struct_bases=[BaseRuleProps],
    name_mapping={
        "description": "description",
        "enabled": "enabled",
        "event_bus": "eventBus",
        "event_state": "eventState",
        "rule_name": "ruleName",
        "targets": "targets",
        "guardrail_behavior": "guardrailBehavior",
        "guardrail_id": "guardrailId",
        "ou_id": "ouId",
        "ou_name": "ouName",
    },
)
class GuardrailRuleProps(BaseRuleProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional[EventStates] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
        guardrail_behavior: typing.Optional[GuardrailBehaviors] = None,
        guardrail_id: typing.Optional[builtins.str] = None,
        ou_id: typing.Optional[builtins.str] = None,
        ou_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        :param guardrail_behavior: The guardrail behavior to match.
        :param guardrail_id: The guardrail ID to match.
        :param ou_id: The OU ID to match.
        :param ou_name: The OU name to match.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af4e71d37041687de416d75a4365993b04919fe94dd895e12758381e90a82bac)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument event_bus", value=event_bus, expected_type=type_hints["event_bus"])
            check_type(argname="argument event_state", value=event_state, expected_type=type_hints["event_state"])
            check_type(argname="argument rule_name", value=rule_name, expected_type=type_hints["rule_name"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument guardrail_behavior", value=guardrail_behavior, expected_type=type_hints["guardrail_behavior"])
            check_type(argname="argument guardrail_id", value=guardrail_id, expected_type=type_hints["guardrail_id"])
            check_type(argname="argument ou_id", value=ou_id, expected_type=type_hints["ou_id"])
            check_type(argname="argument ou_name", value=ou_name, expected_type=type_hints["ou_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if event_bus is not None:
            self._values["event_bus"] = event_bus
        if event_state is not None:
            self._values["event_state"] = event_state
        if rule_name is not None:
            self._values["rule_name"] = rule_name
        if targets is not None:
            self._values["targets"] = targets
        if guardrail_behavior is not None:
            self._values["guardrail_behavior"] = guardrail_behavior
        if guardrail_id is not None:
            self._values["guardrail_id"] = guardrail_id
        if ou_id is not None:
            self._values["ou_id"] = ou_id
        if ou_name is not None:
            self._values["ou_name"] = ou_name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the rule's purpose.

        :default: - A rule for new account creation in Organizations
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the rule is enabled.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_bus(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus]:
        '''The event bus to associate with this rule.

        :default: - The default event bus.
        '''
        result = self._values.get("event_bus")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus], result)

    @builtins.property
    def event_state(self) -> typing.Optional[EventStates]:
        '''Which event state should this rule trigger for.

        :default: - EventStates.SUCCEEDED
        '''
        result = self._values.get("event_state")
        return typing.cast(typing.Optional[EventStates], result)

    @builtins.property
    def rule_name(self) -> typing.Optional[builtins.str]:
        '''A name for the rule.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that ID
        for the rule name. For more information, see Name Type.
        '''
        result = self._values.get("rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Targets to invoke when this rule matches an event.

        :default: - No targets.
        '''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], result)

    @builtins.property
    def guardrail_behavior(self) -> typing.Optional[GuardrailBehaviors]:
        '''The guardrail behavior to match.'''
        result = self._values.get("guardrail_behavior")
        return typing.cast(typing.Optional[GuardrailBehaviors], result)

    @builtins.property
    def guardrail_id(self) -> typing.Optional[builtins.str]:
        '''The guardrail ID to match.'''
        result = self._values.get("guardrail_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ou_id(self) -> typing.Optional[builtins.str]:
        '''The OU ID to match.'''
        result = self._values.get("ou_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ou_name(self) -> typing.Optional[builtins.str]:
        '''The OU name to match.'''
        result = self._values.get("ou_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuardrailRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.OuRuleProps",
    jsii_struct_bases=[BaseRuleProps],
    name_mapping={
        "description": "description",
        "enabled": "enabled",
        "event_bus": "eventBus",
        "event_state": "eventState",
        "rule_name": "ruleName",
        "targets": "targets",
        "ou_id": "ouId",
        "ou_name": "ouName",
    },
)
class OuRuleProps(BaseRuleProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional[EventStates] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
        ou_id: typing.Optional[builtins.str] = None,
        ou_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        :param ou_id: The OU ID to match.
        :param ou_name: The OU name to match.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa6cd1d589c2e242301c3e5e624dde5e5f7e4e083b41cb25bec15842a83f8d98)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument event_bus", value=event_bus, expected_type=type_hints["event_bus"])
            check_type(argname="argument event_state", value=event_state, expected_type=type_hints["event_state"])
            check_type(argname="argument rule_name", value=rule_name, expected_type=type_hints["rule_name"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument ou_id", value=ou_id, expected_type=type_hints["ou_id"])
            check_type(argname="argument ou_name", value=ou_name, expected_type=type_hints["ou_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if event_bus is not None:
            self._values["event_bus"] = event_bus
        if event_state is not None:
            self._values["event_state"] = event_state
        if rule_name is not None:
            self._values["rule_name"] = rule_name
        if targets is not None:
            self._values["targets"] = targets
        if ou_id is not None:
            self._values["ou_id"] = ou_id
        if ou_name is not None:
            self._values["ou_name"] = ou_name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the rule's purpose.

        :default: - A rule for new account creation in Organizations
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the rule is enabled.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_bus(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus]:
        '''The event bus to associate with this rule.

        :default: - The default event bus.
        '''
        result = self._values.get("event_bus")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus], result)

    @builtins.property
    def event_state(self) -> typing.Optional[EventStates]:
        '''Which event state should this rule trigger for.

        :default: - EventStates.SUCCEEDED
        '''
        result = self._values.get("event_state")
        return typing.cast(typing.Optional[EventStates], result)

    @builtins.property
    def rule_name(self) -> typing.Optional[builtins.str]:
        '''A name for the rule.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that ID
        for the rule name. For more information, see Name Type.
        '''
        result = self._values.get("rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Targets to invoke when this rule matches an event.

        :default: - No targets.
        '''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], result)

    @builtins.property
    def ou_id(self) -> typing.Optional[builtins.str]:
        '''The OU ID to match.'''
        result = self._values.get("ou_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ou_name(self) -> typing.Optional[builtins.str]:
        '''The OU name to match.'''
        result = self._values.get("ou_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OuRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RegisteredOrganizationalUnitRule(
    _aws_cdk_aws_events_ceddda9d.Rule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.RegisteredOrganizationalUnitRule",
):
    '''A rule for matching events from CloudTrail where Control Tower registered a new Organizational Unit.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional[EventStates] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7504119cf7c38b93f089c721c612344400229d2d19f91b1b6d0c21ced73eeed9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BaseRuleProps(
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_state=event_state,
            rule_name=rule_name,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class SetupLandingZoneRule(
    _aws_cdk_aws_events_ceddda9d.Rule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.SetupLandingZoneRule",
):
    '''A rule for matching events from CloudTrail where a landing zone was setup via Control Tower.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional[EventStates] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7db7fb722172b7ae8c1852e83da8cdc7742b9c3a5a1315fbbbb95eb95660b4d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BaseRuleProps(
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_state=event_state,
            rule_name=rule_name,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class UpdatedLandingZoneRule(
    _aws_cdk_aws_events_ceddda9d.Rule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.UpdatedLandingZoneRule",
):
    '''A rule for matching events from CloudTrail where a landing zone was updated via Control Tower.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional[EventStates] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5614b41fbc46dde74d697fb3a299efdc69d1b05c9f8f3c3a2d49f0412dc94796)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BaseRuleProps(
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_state=event_state,
            rule_name=rule_name,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class UpdatedManagedAccountRule(
    _aws_cdk_aws_events_ceddda9d.Rule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.UpdatedManagedAccountRule",
):
    '''A rule for matching events from CloudTrail where Control Tower updated a managed account.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: typing.Optional[builtins.str] = None,
        account_name: typing.Optional[builtins.str] = None,
        ou_id: typing.Optional[builtins.str] = None,
        ou_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional[EventStates] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account_id: The account ID to match.
        :param account_name: The account name to match.
        :param ou_id: The OU ID to match.
        :param ou_name: The OU name to match.
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7be4f5d6e3704c419d1221b8c6383505fa8766e87ecdfa6689d1cee7b13ecc5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AccountRuleProps(
            account_id=account_id,
            account_name=account_name,
            ou_id=ou_id,
            ou_name=ou_name,
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_state=event_state,
            rule_name=rule_name,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-control-tower-lifecycle-events.AccountRuleProps",
    jsii_struct_bases=[BaseRuleProps],
    name_mapping={
        "description": "description",
        "enabled": "enabled",
        "event_bus": "eventBus",
        "event_state": "eventState",
        "rule_name": "ruleName",
        "targets": "targets",
        "account_id": "accountId",
        "account_name": "accountName",
        "ou_id": "ouId",
        "ou_name": "ouName",
    },
)
class AccountRuleProps(BaseRuleProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
        event_state: typing.Optional[EventStates] = None,
        rule_name: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
        account_id: typing.Optional[builtins.str] = None,
        account_name: typing.Optional[builtins.str] = None,
        ou_id: typing.Optional[builtins.str] = None,
        ou_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: A description of the rule's purpose. Default: - A rule for new account creation in Organizations
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_state: Which event state should this rule trigger for. Default: - EventStates.SUCCEEDED
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param targets: Targets to invoke when this rule matches an event. Default: - No targets.
        :param account_id: The account ID to match.
        :param account_name: The account name to match.
        :param ou_id: The OU ID to match.
        :param ou_name: The OU name to match.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be554a3851a82c86db7664d62cab54c3ad12110c97ef0e4b4853b50dcba5f108)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument event_bus", value=event_bus, expected_type=type_hints["event_bus"])
            check_type(argname="argument event_state", value=event_state, expected_type=type_hints["event_state"])
            check_type(argname="argument rule_name", value=rule_name, expected_type=type_hints["rule_name"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument account_name", value=account_name, expected_type=type_hints["account_name"])
            check_type(argname="argument ou_id", value=ou_id, expected_type=type_hints["ou_id"])
            check_type(argname="argument ou_name", value=ou_name, expected_type=type_hints["ou_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if event_bus is not None:
            self._values["event_bus"] = event_bus
        if event_state is not None:
            self._values["event_state"] = event_state
        if rule_name is not None:
            self._values["rule_name"] = rule_name
        if targets is not None:
            self._values["targets"] = targets
        if account_id is not None:
            self._values["account_id"] = account_id
        if account_name is not None:
            self._values["account_name"] = account_name
        if ou_id is not None:
            self._values["ou_id"] = ou_id
        if ou_name is not None:
            self._values["ou_name"] = ou_name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the rule's purpose.

        :default: - A rule for new account creation in Organizations
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the rule is enabled.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_bus(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus]:
        '''The event bus to associate with this rule.

        :default: - The default event bus.
        '''
        result = self._values.get("event_bus")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus], result)

    @builtins.property
    def event_state(self) -> typing.Optional[EventStates]:
        '''Which event state should this rule trigger for.

        :default: - EventStates.SUCCEEDED
        '''
        result = self._values.get("event_state")
        return typing.cast(typing.Optional[EventStates], result)

    @builtins.property
    def rule_name(self) -> typing.Optional[builtins.str]:
        '''A name for the rule.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that ID
        for the rule name. For more information, see Name Type.
        '''
        result = self._values.get("rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def targets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]]:
        '''Targets to invoke when this rule matches an event.

        :default: - No targets.
        '''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_events_ceddda9d.IRuleTarget]], result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''The account ID to match.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def account_name(self) -> typing.Optional[builtins.str]:
        '''The account name to match.'''
        result = self._values.get("account_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ou_id(self) -> typing.Optional[builtins.str]:
        '''The OU ID to match.'''
        result = self._values.get("ou_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ou_name(self) -> typing.Optional[builtins.str]:
        '''The OU name to match.'''
        result = self._values.get("ou_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AccountRuleProps",
    "BaseRuleProps",
    "CreatedAccountByOrganizationsRule",
    "CreatedAccountRule",
    "DeregisteredOrganizationalUnitRule",
    "DisabledGuardrailRule",
    "EnabledGuardrailRule",
    "EventStates",
    "GuardrailBehaviors",
    "GuardrailRuleProps",
    "OuRuleProps",
    "RegisteredOrganizationalUnitRule",
    "SetupLandingZoneRule",
    "UpdatedLandingZoneRule",
    "UpdatedManagedAccountRule",
]

publication.publish()

def _typecheckingstub__330bef8ade77cd3402f72de78d0f55e9cf39c751e67e9d2c203a87731e2fc205(
    *,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11a7e73b6e61c4394a520bb20a640d0d5d65ba0bc09566e755e169617c7fa2fc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df0be9333691e70162d32bb21fc1c8e0104aa52c77fcbcf94cc5c25bfa585778(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    ou_id: typing.Optional[builtins.str] = None,
    ou_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__116d3138d6e0467df3fdff63ba8793e903bd6ba94f61f763b572589878ee47a3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    ou_id: typing.Optional[builtins.str] = None,
    ou_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5468930d02dfe3e158ff50fd426632fc1a8b0d1e98eb0b5f3983e925f24a231(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    guardrail_behavior: typing.Optional[GuardrailBehaviors] = None,
    guardrail_id: typing.Optional[builtins.str] = None,
    ou_id: typing.Optional[builtins.str] = None,
    ou_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2912d56398fe0648791de639f789e1683c6fa64493a6e3ec522c80927a48bf19(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    guardrail_behavior: typing.Optional[GuardrailBehaviors] = None,
    guardrail_id: typing.Optional[builtins.str] = None,
    ou_id: typing.Optional[builtins.str] = None,
    ou_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af4e71d37041687de416d75a4365993b04919fe94dd895e12758381e90a82bac(
    *,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    guardrail_behavior: typing.Optional[GuardrailBehaviors] = None,
    guardrail_id: typing.Optional[builtins.str] = None,
    ou_id: typing.Optional[builtins.str] = None,
    ou_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa6cd1d589c2e242301c3e5e624dde5e5f7e4e083b41cb25bec15842a83f8d98(
    *,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    ou_id: typing.Optional[builtins.str] = None,
    ou_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7504119cf7c38b93f089c721c612344400229d2d19f91b1b6d0c21ced73eeed9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7db7fb722172b7ae8c1852e83da8cdc7742b9c3a5a1315fbbbb95eb95660b4d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5614b41fbc46dde74d697fb3a299efdc69d1b05c9f8f3c3a2d49f0412dc94796(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7be4f5d6e3704c419d1221b8c6383505fa8766e87ecdfa6689d1cee7b13ecc5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: typing.Optional[builtins.str] = None,
    account_name: typing.Optional[builtins.str] = None,
    ou_id: typing.Optional[builtins.str] = None,
    ou_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be554a3851a82c86db7664d62cab54c3ad12110c97ef0e4b4853b50dcba5f108(
    *,
    description: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    event_bus: typing.Optional[_aws_cdk_aws_events_ceddda9d.IEventBus] = None,
    event_state: typing.Optional[EventStates] = None,
    rule_name: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Sequence[_aws_cdk_aws_events_ceddda9d.IRuleTarget]] = None,
    account_id: typing.Optional[builtins.str] = None,
    account_name: typing.Optional[builtins.str] = None,
    ou_id: typing.Optional[builtins.str] = None,
    ou_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
