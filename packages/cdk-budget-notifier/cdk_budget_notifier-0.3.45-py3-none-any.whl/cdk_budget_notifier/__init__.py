r'''
# AWS Budget Notifier

Setup a AWS Budget notification using AWS Cloud Development Kit (CDK).
The construct supports notifying to

* users via e-mail. Up to 10 e-mail addresses are supported
* an SNS topic
  The SNS topic needs to exist and publishing to the topic needs to be allowed.

## Properties

[API.md](API.md)

## Example usages

### Notification on breaching forecasted cost

This example is handy for keeping control over your private AWS Bill.
For myself I aim to not spent more than 10 Euro / 10 USD per month and this alarm
reminds me.

```python
const app = new cdk.App();
const stack = new Stack(app, "BudgetNotifierStack");

// Define the SNS topic and setup the resource policy
const topic = new Topic(stack, "topic");

const statement = new PolicyStatement({
  effect: Effect.ALLOW,
  principals: [new ServicePrincipal("budgets.amazonaws.com")],
  actions: ["SNS:Publish"],
  sid: "Allow budget to publish to SNS"
});
topic.addToResourcePolicy(statement);

// Setup the budget notifier and pass the ARN of the SNS topic
new BudgetNotifier(stack, "notifier", {
  topicArn: topic.topicArn,
  // Filter on the availability zone `eu-central-1`
  availabilityZones: ["eu-central-1"],
  costCenter: "myCostCenter",
  // Limit and unit defining the budget limit
  limit: 10,
  unit: "USD",
  // When breaching the threshold of 85% of the 10 USD notifications will be send out.
  threshold: 85,
  notificationType: NotificationType.FORECASTED,
});
```

### Notification via e-Mail

As alternative to the notification via SNS you can specify a list of e-mail
recipients.

```python
const app = new cdk.App();
const stack = new Stack(app, "BudgetNotifierStack");

new BudgetNotifier(stack, 'notifier', {
  recipients: ['john.doe@foo.bar'],
  // Filter on the availability zone `eu-central-1`
  availabilityZones: ['eu-central-1'],
  costCenter: 'MyCostCenter',
  // Limit and unit defining the budget limit
  limit: 10,
  unit: 'USD',
  // When breaching the threshold of 85% of the 10 USD notifications will be send out.
  threshold: 85,
  notificationType: NotificationType.FORECASTED,
});
```

## Contributions

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section --><!-- prettier-ignore-start --><!-- markdownlint-disable --><table>
  <tr>
    <td align="center"><a href="https://github.com/dedominicisfa"><img src="https://avatars.githubusercontent.com/u/23100791?v=4" width="100px;" alt=""/><br /><sub><b>dedominicisfa</b></sub></a></td>
    <td align="center"><a href="http://p6m7g8.github.io"><img src="https://avatars.githubusercontent.com/u/34295?v=4" width="100px;" alt=""/><br /><sub><b>Philip M. Gollucci</b></sub></a></td>
  </tr>
</table><!-- markdownlint-restore --><!-- prettier-ignore-end --><!-- ALL-CONTRIBUTORS-LIST:END -->

## Links

* [AWS Cloud Development Kit (CDK)](https://github.com/aws/aws-cdk)
* [Cost Explorer filters](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ce-filtering.html)
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

import constructs as _constructs_77d1e7e8


class BudgetNotifier(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws_budget_notifier.BudgetNotifier",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        limit: jsii.Number,
        threshold: jsii.Number,
        unit: builtins.str,
        application: typing.Optional[builtins.str] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        cost_center: typing.Optional[builtins.str] = None,
        notification_type: typing.Optional["NotificationType"] = None,
        recipients: typing.Optional[typing.Sequence[builtins.str]] = None,
        service: typing.Optional[builtins.str] = None,
        time_unit: typing.Optional["TimeUnit"] = None,
        topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param limit: The cost associated with the budget threshold.
        :param threshold: The threshold value in percent (0-100).
        :param unit: The unit of measurement that is used for the budget threshold, such as dollars or GB.
        :param application: If specified the application name will be added as tag filter.
        :param availability_zones: If specified the availability zones will be added as tag filter.
        :param cost_center: If specified the cost center will be added as tag filter.
        :param notification_type: Whether the notification is for how much you have spent (ACTUAL) or for how much you're forecasted to spend (FORECASTED).
        :param recipients: Budget notifications will be sent to each of the recipients (e-mail addresses). A maximum of 10 recipients is allowed.
        :param service: If specified the service will be added as tag filter.
        :param time_unit: The length of time until a budget resets the actual and forecasted spend.
        :param topic_arn: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84bfc8e2612536ca8c70cc5d518a5393c60beee341db21121d3852d4a886c318)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BudgetNotifierProps(
            limit=limit,
            threshold=threshold,
            unit=unit,
            application=application,
            availability_zones=availability_zones,
            cost_center=cost_center,
            notification_type=notification_type,
            recipients=recipients,
            service=service,
            time_unit=time_unit,
            topic_arn=topic_arn,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="aws_budget_notifier.BudgetNotifierProps",
    jsii_struct_bases=[],
    name_mapping={
        "limit": "limit",
        "threshold": "threshold",
        "unit": "unit",
        "application": "application",
        "availability_zones": "availabilityZones",
        "cost_center": "costCenter",
        "notification_type": "notificationType",
        "recipients": "recipients",
        "service": "service",
        "time_unit": "timeUnit",
        "topic_arn": "topicArn",
    },
)
class BudgetNotifierProps:
    def __init__(
        self,
        *,
        limit: jsii.Number,
        threshold: jsii.Number,
        unit: builtins.str,
        application: typing.Optional[builtins.str] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        cost_center: typing.Optional[builtins.str] = None,
        notification_type: typing.Optional["NotificationType"] = None,
        recipients: typing.Optional[typing.Sequence[builtins.str]] = None,
        service: typing.Optional[builtins.str] = None,
        time_unit: typing.Optional["TimeUnit"] = None,
        topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Configuration options of the {@link BudgetNotifier BudgetNotifier}.

        :param limit: The cost associated with the budget threshold.
        :param threshold: The threshold value in percent (0-100).
        :param unit: The unit of measurement that is used for the budget threshold, such as dollars or GB.
        :param application: If specified the application name will be added as tag filter.
        :param availability_zones: If specified the availability zones will be added as tag filter.
        :param cost_center: If specified the cost center will be added as tag filter.
        :param notification_type: Whether the notification is for how much you have spent (ACTUAL) or for how much you're forecasted to spend (FORECASTED).
        :param recipients: Budget notifications will be sent to each of the recipients (e-mail addresses). A maximum of 10 recipients is allowed.
        :param service: If specified the service will be added as tag filter.
        :param time_unit: The length of time until a budget resets the actual and forecasted spend.
        :param topic_arn: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21f73a16710abede15940126a33e196b183fc8727121ec667cf4e27b7727d842)
            check_type(argname="argument limit", value=limit, expected_type=type_hints["limit"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
            check_type(argname="argument availability_zones", value=availability_zones, expected_type=type_hints["availability_zones"])
            check_type(argname="argument cost_center", value=cost_center, expected_type=type_hints["cost_center"])
            check_type(argname="argument notification_type", value=notification_type, expected_type=type_hints["notification_type"])
            check_type(argname="argument recipients", value=recipients, expected_type=type_hints["recipients"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument time_unit", value=time_unit, expected_type=type_hints["time_unit"])
            check_type(argname="argument topic_arn", value=topic_arn, expected_type=type_hints["topic_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "limit": limit,
            "threshold": threshold,
            "unit": unit,
        }
        if application is not None:
            self._values["application"] = application
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if cost_center is not None:
            self._values["cost_center"] = cost_center
        if notification_type is not None:
            self._values["notification_type"] = notification_type
        if recipients is not None:
            self._values["recipients"] = recipients
        if service is not None:
            self._values["service"] = service
        if time_unit is not None:
            self._values["time_unit"] = time_unit
        if topic_arn is not None:
            self._values["topic_arn"] = topic_arn

    @builtins.property
    def limit(self) -> jsii.Number:
        '''The cost associated with the budget threshold.'''
        result = self._values.get("limit")
        assert result is not None, "Required property 'limit' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''The threshold value in percent (0-100).'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def unit(self) -> builtins.str:
        '''The unit of measurement that is used for the budget threshold, such as dollars or GB.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def application(self) -> typing.Optional[builtins.str]:
        '''If specified the application name will be added as tag filter.'''
        result = self._values.get("application")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''If specified the availability zones will be added as tag filter.'''
        result = self._values.get("availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cost_center(self) -> typing.Optional[builtins.str]:
        '''If specified the cost center will be added as tag filter.'''
        result = self._values.get("cost_center")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_type(self) -> typing.Optional["NotificationType"]:
        '''Whether the notification is for how much you have spent (ACTUAL) or for how much you're forecasted to spend (FORECASTED).

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-notificationtype
        '''
        result = self._values.get("notification_type")
        return typing.cast(typing.Optional["NotificationType"], result)

    @builtins.property
    def recipients(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Budget notifications will be sent to each of the recipients (e-mail addresses).

        A maximum of 10 recipients is allowed.
        '''
        result = self._values.get("recipients")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''If specified the service will be added as tag filter.'''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_unit(self) -> typing.Optional["TimeUnit"]:
        '''The length of time until a budget resets the actual and forecasted spend.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-timeunit
        '''
        result = self._values.get("time_unit")
        return typing.cast(typing.Optional["TimeUnit"], result)

    @builtins.property
    def topic_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetNotifierProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="aws_budget_notifier.NotificationType")
class NotificationType(enum.Enum):
    ACTUAL = "ACTUAL"
    FORECASTED = "FORECASTED"


@jsii.enum(jsii_type="aws_budget_notifier.TimeUnit")
class TimeUnit(enum.Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"


__all__ = [
    "BudgetNotifier",
    "BudgetNotifierProps",
    "NotificationType",
    "TimeUnit",
]

publication.publish()

def _typecheckingstub__84bfc8e2612536ca8c70cc5d518a5393c60beee341db21121d3852d4a886c318(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    limit: jsii.Number,
    threshold: jsii.Number,
    unit: builtins.str,
    application: typing.Optional[builtins.str] = None,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    cost_center: typing.Optional[builtins.str] = None,
    notification_type: typing.Optional[NotificationType] = None,
    recipients: typing.Optional[typing.Sequence[builtins.str]] = None,
    service: typing.Optional[builtins.str] = None,
    time_unit: typing.Optional[TimeUnit] = None,
    topic_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21f73a16710abede15940126a33e196b183fc8727121ec667cf4e27b7727d842(
    *,
    limit: jsii.Number,
    threshold: jsii.Number,
    unit: builtins.str,
    application: typing.Optional[builtins.str] = None,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    cost_center: typing.Optional[builtins.str] = None,
    notification_type: typing.Optional[NotificationType] = None,
    recipients: typing.Optional[typing.Sequence[builtins.str]] = None,
    service: typing.Optional[builtins.str] = None,
    time_unit: typing.Optional[TimeUnit] = None,
    topic_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
