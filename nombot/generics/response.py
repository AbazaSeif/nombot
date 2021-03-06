"""
Generic response types
"""

from marshmallow import fields, Schema, post_load, pre_load
from nombot.api.response import Result, RESPONSE_MAP


class DefaultSchema(Schema):
    """Default schema parser"""
    #MessageType = fields.Str(required=True)

    @post_load
    def generate_obj(self, data):  # pylint: disable=no-self-use
        """Generate new schema based on message type"""
        return RESPONSE_MAP[data["MessageType"]].dump(data["Data"])

    class Meta:
        """Data field is dyanamic type"""
        additional = ("Data",)


RESPONSE_MAP["default"] = DefaultSchema()


class CommonResponseSchema(Schema):
    """Common response schema"""
    errors = fields.Dict()

    def get_results(self, callname, data):  # pylint: disable=no-self-use
        """
        Retrieve the results from the parsed object
          ~~ Override this to match your API. ~~
        """
        # perform type-specific preperation of data, if it exists
        prep = getattr(RESPONSE_MAP[callname], "prepare", None)
        if callable(prep):
            data = prep(data)
        return data


class ResponseSchema(CommonResponseSchema):
    """Schema defining the data structure the API will respond with"""
    @post_load
    def populate_data(self, data):
        """Parse the incoming schema"""
        if "errors" in data:
            return Result(errors=data["errors"])
        callname = self.context.get("callname")
        results = {
            "callname": callname,
            "results": RESPONSE_MAP[callname]  # type: ignore
                .dump(self.get_results(callname, data))  # NOQA
        }
        return Result(**results)

    class Meta:
        """Stricty"""
        strict = True
        additional = ("result",)


class WSResponseSchema(CommonResponseSchema):
    """
    Schema defining the data structure from published messages on the websock
    """
    channel = fields.Str()

    @pre_load
    def prep_data(self, data):
        """Prepare the data for ingestion"""
        # pylint: disable=E1101
        res_type = self.context.get("response_type")
        try:
            sch = RESPONSE_MAP[res_type]
        except KeyError:
            sch = RESPONSE_MAP["default"]

        self.context["result"] = sch.dump(self.get_result(callname, data)).data  # NOQA
        return self.context

    @post_load
    def populate_data(self, data):
        """Parse the incoming schema"""
        if "errors" in data:
            return Result(errors=data["errors"])
        return Result(**self.context)
