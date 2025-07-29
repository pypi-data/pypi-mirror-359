import json
from typing import Mapping, Any

import grpc

from sapiopycommons.ai.api.fielddefinitions.proto.fields_pb2 import FieldValuePbo
from sapiopycommons.ai.api.plan.tool.proto.entry_pb2 import DataTypePbo, StepBinaryContainerPbo, StepCsvRowPbo, \
    StepCsvHeaderRowPbo, StepCsvContainerPbo, StepJsonContainerPbo, StepImageContainerPbo, StepTextContainerPbo, \
    StepItemContainerPbo, StepInputBatchPbo
from sapiopycommons.ai.api.plan.tool.proto.tool_pb2 import ProcessStepResponsePbo, ProcessStepRequestPbo
from sapiopycommons.ai.api.plan.tool.proto.tool_pb2_grpc import ToolServiceStub
from sapiopycommons.ai.api.session.proto.sapio_conn_info_pb2 import SapioConnectionInfoPbo, SapioUserSecretTypePbo


class TestOutput:
    """
    A class for holding the output of a TestClient that calls a ToolService. TestOutput objects an be
    printed to show the output of the tool in a human-readable format.
    """
    binary_output: list[bytes]
    csv_output: list[dict[str, Any]]
    json_output: list[Any]
    image_output: list[bytes]
    text_output: list[str]

    new_records: list[Mapping[str, FieldValuePbo]]

    logs: list[str]

    def __init__(self):
        self.binary_output = []
        self.csv_output = []
        self.json_output = []
        self.image_output = []
        self.text_output = []
        self.new_records = []
        self.logs = []

    def __str__(self):
        ret_val: str = ""
        ret_val += f"Binary Output: {len(self.binary_output)} item(s)\n"
        for binary in self.binary_output:
            ret_val += f"\t{len(binary)} byte(s)\n"
            ret_val += f"\t{binary[:50]}...\n"
        ret_val += f"CSV Output: {len(self.csv_output)} item(s)\n"
        if self.csv_output:
            ret_val += f"\tHeaders: {', '.join(self.csv_output[0].keys())}\n"
            for i, csv_row in enumerate(self.csv_output):
                ret_val += f"\t{i}: {', '.join(f'{v}' for k, v in csv_row.items())}\n"
        ret_val += f"JSON Output: {len(self.json_output)} item(s)\n"
        if self.json_output:
            ret_val += f"\t{json.dumps(self.json_output, indent=2)}\n"
        ret_val += f"Image Output: {len(self.image_output)} item(s)\n"
        for image in self.image_output:
            ret_val += f"\t{len(image)} bytes\n"
            ret_val += f"\t{image[:50]}...\n"
        ret_val += f"Text Output: {len(self.text_output)} item(s)\n"
        for text in self.text_output:
            ret_val += f"\t{text}...\n"
        ret_val += f"New Records: {len(self.new_records)} item(s)\n"
        for record in self.new_records:
            ret_val += f"\t{json.dumps(record, indent=2)}\n"
        ret_val += f"Logs: {len(self.logs)} item(s)\n"
        for log in self.logs:
            ret_val += f"\t{log}\n"
        return ret_val


class TestClient:
    """
    A client for testing a ToolService. This client can be used to send requests to a tool and receive
    responses.
    """
    server_url: str
    tool_name: str
    connection: SapioConnectionInfoPbo
    request_inputs: list[Any]

    def __init__(self, server_url: str, tool_name: str):
        """
        :param server_url: The URL of the gRPC server to connect to.
        :param tool_name: The name of the tool to call on the server.
        """
        self.create_user()
        self.server_url = server_url
        self.tool_name = tool_name
        self.request_inputs = []

    def create_user(self):
        """
        Create a SapioConnectionInfoPbo object with test credentials. This method can be overridden to
        create a user with specific credentials for testing.
        """
        self.connection = SapioConnectionInfoPbo()
        self.connection.username = "Testing"
        self.connection.webservice_url = "https://localhost:8080/webservice/api"
        self.connection.app_guid = "1234567890"
        self.connection.secret_type = SapioUserSecretTypePbo.PASSWORD
        self.connection.rmi_host.append("Testing")
        self.connection.rmi_port = 9001
        self.connection.secret = "password"

    def add_input_input(self, input_data: list[bytes]) -> None:
        """
        Add a binary input to the the next request.
        """
        self._add_input(DataTypePbo.BINARY, StepBinaryContainerPbo(items=input_data))

    def add_csv_input(self, input_data: list[dict[str, Any]]) -> None:
        """
        Add a CSV input to the next request.
        """
        csv_items = []
        for row in input_data:
            csv_items.append(StepCsvRowPbo(cells=[str(value) for value in row.values()]))
        header = StepCsvHeaderRowPbo(cells=list(input_data[0].keys()))
        self._add_input(DataTypePbo.CSV, StepCsvContainerPbo(header=header, items=csv_items))

    def add_json_input(self, input_data: list[dict[str, Any]]) -> None:
        """
        Add a JSON input to the next request.
        """
        self._add_input(DataTypePbo.JSON, StepJsonContainerPbo(items=[json.dumps(x) for x in input_data]))

    def add_image_input(self, input_data: list[bytes], image_format: str = "png") -> None:
        """
        Add an image input to the next request.
        """
        self._add_input(DataTypePbo.IMAGE, StepImageContainerPbo(items=input_data, image_format=image_format))

    def add_text_input(self, input_data: list[str]) -> None:
        """
        Add a text input to the next request.
        """
        self._add_input(DataTypePbo.TEXT, StepTextContainerPbo(items=input_data))

    def _add_input(self, data_type: DataTypePbo, items: Any) -> None:
        """
        Helper method for adding inputs to the next request.
        """
        match data_type:
            case DataTypePbo.BINARY:
                container = StepItemContainerPbo(dataType=data_type, binary_container=items)
            case DataTypePbo.CSV:
                container = StepItemContainerPbo(dataType=data_type, csv_container=items)
            case DataTypePbo.JSON:
                container = StepItemContainerPbo(dataType=data_type, json_container=items)
            case DataTypePbo.IMAGE:
                container = StepItemContainerPbo(dataType=data_type, image_container=items)
            case DataTypePbo.TEXT:
                container = StepItemContainerPbo(dataType=data_type, text_container=items)
            case _:
                raise ValueError(f"Unsupported data type: {data_type}")
        self.request_inputs.append(container)

    def send_request(self) -> TestOutput:
        """
        Send the request to the tool service. This will send all the inputs that have been added using the
        add_X_input functions.

        :return: A TestOutput object containing the results of the tool service call.
        """
        with grpc.insecure_channel(self.server_url) as channel:
            stub = ToolServiceStub(channel)

            response: ProcessStepResponsePbo = stub.ProcessData(
                ProcessStepRequestPbo(
                    sapio_user=self.connection,
                    tool_name=self.tool_name,
                    input=[
                        StepInputBatchPbo(is_partial=False, item_container=item)
                        for item in self.request_inputs
                    ]
                )
            )

            results = TestOutput()

            for item in response.output:
                container = item.item_container

                results.binary_output.extend(container.binary_container.items)
                for header in container.csv_container.header.cells:
                    output_row: dict[str, Any] = {}
                    for i, row in enumerate(container.csv_container.items):
                        output_row[header] = row.cells[i]
                    results.csv_output.append(output_row)
                results.json_output.extend([json.loads(x) for x in container.json_container.items])
                results.image_output.extend(container.image_container.items)
                results.text_output.extend(container.text_container.items)

            for record in response.new_records:
                results.new_records.append(record.fields)

            results.logs.extend(response.log)

            return results
