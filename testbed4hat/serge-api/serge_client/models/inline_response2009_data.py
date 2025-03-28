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

class InlineResponse2009Data(object):
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
        'fields_based_on_your_log_schema_': 'object'
    }

    attribute_map = {
        'fields_based_on_your_log_schema_': '[ fields based on your log schema ]'
    }

    def __init__(self, fields_based_on_your_log_schema_=None):  # noqa: E501
        """InlineResponse2009Data - a model defined in Swagger"""  # noqa: E501
        self._fields_based_on_your_log_schema_ = None
        self.discriminator = None
        if fields_based_on_your_log_schema_ is not None:
            self.fields_based_on_your_log_schema_ = fields_based_on_your_log_schema_

    @property
    def fields_based_on_your_log_schema_(self):
        """Gets the fields_based_on_your_log_schema_ of this InlineResponse2009Data.  # noqa: E501


        :return: The fields_based_on_your_log_schema_ of this InlineResponse2009Data.  # noqa: E501
        :rtype: object
        """
        return self._fields_based_on_your_log_schema_

    @fields_based_on_your_log_schema_.setter
    def fields_based_on_your_log_schema_(self, fields_based_on_your_log_schema_):
        """Sets the fields_based_on_your_log_schema_ of this InlineResponse2009Data.


        :param fields_based_on_your_log_schema_: The fields_based_on_your_log_schema_ of this InlineResponse2009Data.  # noqa: E501
        :type: object
        """

        self._fields_based_on_your_log_schema_ = fields_based_on_your_log_schema_

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
        if issubclass(InlineResponse2009Data, dict):
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
        if not isinstance(other, InlineResponse2009Data):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
