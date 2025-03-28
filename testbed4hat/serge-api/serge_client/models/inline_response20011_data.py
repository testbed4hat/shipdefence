# coding: utf-8

"""
    Serge API

    API documentation for Serge server  # noqa: E501

    OpenAPI spec version: 1.0.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class InlineResponse20011Data(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'role': 'str',
        'activity_time': 'str',
        'activity_type': 'str'
    }

    attribute_map = {
        'role': 'role',
        'activity_time': 'activityTime',
        'activity_type': 'activityType'
    }

    def __init__(self, role=None, activity_time=None, activity_type=None):  # noqa: E501
        """InlineResponse20011Data - a model defined in Swagger"""  # noqa: E501
        self._role = None
        self._activity_time = None
        self._activity_type = None
        self.discriminator = None
        if role is not None:
            self.role = role
        if activity_time is not None:
            self.activity_time = activity_time
        if activity_type is not None:
            self.activity_type = activity_type

    @property
    def role(self):
        """Gets the role of this InlineResponse20011Data.  # noqa: E501


        :return: The role of this InlineResponse20011Data.  # noqa: E501
        :rtype: str
        """
        return self._role

    @role.setter
    def role(self, role):
        """Sets the role of this InlineResponse20011Data.


        :param role: The role of this InlineResponse20011Data.  # noqa: E501
        :type: str
        """

        self._role = role

    @property
    def activity_time(self):
        """Gets the activity_time of this InlineResponse20011Data.  # noqa: E501


        :return: The activity_time of this InlineResponse20011Data.  # noqa: E501
        :rtype: str
        """
        return self._activity_time

    @activity_time.setter
    def activity_time(self, activity_time):
        """Sets the activity_time of this InlineResponse20011Data.


        :param activity_time: The activity_time of this InlineResponse20011Data.  # noqa: E501
        :type: str
        """

        self._activity_time = activity_time

    @property
    def activity_type(self):
        """Gets the activity_type of this InlineResponse20011Data.  # noqa: E501


        :return: The activity_type of this InlineResponse20011Data.  # noqa: E501
        :rtype: str
        """
        return self._activity_type

    @activity_type.setter
    def activity_type(self, activity_type):
        """Sets the activity_type of this InlineResponse20011Data.


        :param activity_type: The activity_type of this InlineResponse20011Data.  # noqa: E501
        :type: str
        """

        self._activity_type = activity_type

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(InlineResponse20011Data, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, InlineResponse20011Data):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
