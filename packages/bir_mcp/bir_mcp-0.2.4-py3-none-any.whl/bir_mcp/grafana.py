import datetime
import enum
import inspect
import ssl
import zoneinfo
from typing import Annotated

import bidict
import fastmcp.prompts
import fastmcp.resources
import fastmcp.tools
import httpx
import mcp
import pydantic

from bir_mcp.utils import araise_for_status, filter_dict_by_keys, to_fastmcp_tool


class InfluxDbQueryType(enum.StrEnum):
    flux = enum.auto()
    influxql = enum.auto()


def get_mcp_resouce_uri_functions() -> bidict.bidict[str, callable]:
    functions = bidict.bidict(
        {
            "instruction://flux": get_flux_instruction,
        }
    )
    return functions


def get_lowest_network_usage_virtual_machines_prompt(metric: str = "network usage") -> str:
    """The prompt for finding virtual machines with the lowest network usage."""
    uri_functions = get_mcp_resouce_uri_functions()
    flux_instruction_uri = uri_functions.inverse[get_flux_instruction]
    prompt = inspect.cleandoc(f"""
        Which virtual machines had the lowest network usage over the last week in the bank, 
        based on Vsphere logs in InfluxDB? To answer this question, follow these steps:
        - Refer to Flux language instructions in the MCP resources {flux_instruction_uri}.
        - Find InfluxDB datasource in the Grafana instance.
        - Find the InfluxDB datasource, bucket and measurement name that relates to Vsphere virtual machines usage in the bank.
        - Find the tag that identifies virtual machines.
        - Construct a query for finding the virtual machines with the lowest network usage using the lowestAverage() Flux function.
        - Present the results.
    """)
    return prompt


class Grafana:
    def __init__(
        self,
        url: str,
        auth: tuple[str, str],
        http_timeout_seconds: int = 30,
        timezone: str = "UTC",
        tag: str = "grafana",
        max_output_length: int | None = None,
        ssl_verify: bool | str = True,
    ):
        verify = (
            ssl.create_default_context(cafile=ssl_verify)
            if isinstance(ssl_verify, str)
            else ssl_verify
        )
        self.client = httpx.AsyncClient(
            auth=auth,
            base_url=url,
            event_hooks={"response": [araise_for_status]},
            timeout=http_timeout_seconds,
            verify=verify,
        )
        self.timezone = zoneinfo.ZoneInfo(timezone)
        self.tag = tag
        self.max_output_length = max_output_length

    def get_mcp_tools(self) -> list[fastmcp.tools.FunctionTool]:
        functions = [
            self.list_all_datasources,
            self.query_influxdb_datasource,
        ]
        tools = [
            to_fastmcp_tool(
                function,
                tags={self.tag},
                annotations=mcp.types.ToolAnnotations(readOnlyHint=True, destructiveHint=False),
                max_output_length=self.max_output_length,
            )
            for function in functions
        ]
        return tools

    def get_mcp_resources(self) -> list[fastmcp.resources.Resource]:
        resources = [
            fastmcp.resources.Resource.from_function(function, uri=uri, tags={self.tag})
            for uri, function in get_mcp_resouce_uri_functions().items()
        ]
        return resources

    def get_prompts(self) -> list[fastmcp.prompts.Prompt]:
        prompts = [
            get_lowest_network_usage_virtual_machines_prompt,
        ]
        prompts = [
            fastmcp.prompts.Prompt.from_function(function, tags={self.tag}) for function in prompts
        ]
        return prompts

    def build_mcp_server(self) -> fastmcp.FastMCP:
        server = fastmcp.FastMCP(
            name="Bir Grafana MCP server",
            instructions=inspect.cleandoc("""
                Grafana related tools.
            """),
            tools=self.get_mcp_tools(),
        )
        for resource in self.get_mcp_resources():
            server.add_resource(resource)

        for prompt in self.get_prompts():
            server.add_prompt(prompt)

        return server

    async def list_all_datasources(self) -> dict:
        """Lists all datasources in the Grafana instance."""
        response = await self.client.get("/api/datasources")
        datasources = {
            "datasources": [
                filter_dict_by_keys(d, ["uid", "name", "typeName"]) for d in response.json()
            ]
        }
        return datasources

    async def query_influxdb_datasource(
        self,
        datasource_uid: Annotated[
            str,
            pydantic.Field(description="The uid of an InfluxDB Grafana datasource."),
        ],
        query: Annotated[
            str,
            pydantic.Field(description="The query to execute."),
        ],
        start_time: Annotated[
            str,
            pydantic.Field(
                description=inspect.cleandoc("""
                    The start time for the query in relative Grafana time units like "now", "now-5m", 
                    "now-1h", "now-7d", or in ISO 8601 format "YYYY-MM-DDTHH:MM:SS+HH:MM".
                    Can be refered to as "v.timeRangeStart" in queries.
                    Should not be older than one month for query efficiency and because data is probably 
                    not retained longer than that anyway.
                """)
            ),
        ] = "now-1h",
        end_time: Annotated[
            str,
            pydantic.Field(
                description=inspect.cleandoc("""
                    The end time for the query, in same format as start_time. 
                    Can be refered to as "v.timeRangeStop" in queries.
                """)
            ),
        ] = "now",
        query_language: Annotated[
            InfluxDbQueryType,
            pydantic.Field(
                description=inspect.cleandoc(f"""
                The language of query to execute, {InfluxDbQueryType.influxql} for SQL-like Influx query language, 
                and {InfluxDbQueryType.flux} for Flux functional data scripting language.
            """)
            ),
        ] = InfluxDbQueryType.flux,
    ) -> dict:
        """
        Executes a query against an InfluxDB datasource in the Grafana instance.
        Note that InfluxQL may not be supported by the InfluxDB datasource.
        If query returns too much data, it will lead to HTTP timeouts.
        To avoid this, the start to end time range should be as small as possible,
        and the query should aggregate data by time windows.
        Refer to Flux instruction in the MCP resources for details about the Flux language, and to
        [Grafana endpoint docs](https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#query-a-data-source)
        for details about the used endpoint.
        """
        ref_id = "A"
        query = {
            "datasource": {"uid": datasource_uid},
            "refId": ref_id,
            "query": query,
            "queryType": query_language.value,
            "format": "table",
        }
        payload = {
            "queries": [query],
            "from": to_grafana_time_format(start_time),
            "to": to_grafana_time_format(end_time),
        }
        response = await self.client.post("/api/ds/query", json=payload)
        tables = []
        for frame in response.json()["results"][ref_id]["frames"]:
            table = filter_dict_by_keys(frame["schema"], ["name", "fields"])
            table["data"] = frame["data"]["values"]
            tables.append(table)

        tables = {"tables": tables}
        return tables


def to_grafana_time_format(date: str) -> str | int:
    try:
        date = datetime.datetime.fromisoformat(date)
    except ValueError:
        pass
    else:
        date = int(date.timestamp() * 1000)

    return date


def get_flux_instruction() -> str:
    """Provides information about InfluxDB Flux language, such as its data model, syntax, and usage examples."""
    instruction = """
    # Flux 
    Flux is a functional data scripting language designed for querying, analyzing, and acting on time-series data in InfluxDB.

    ## Data model
    Flux organizes data into independent buckets, similar to logical databases in SQL.
    Each bucket contains time series data. A single point is composed of:
    - measurement: The name of the thing you are measuring (e.g., "cpu", "http_requests"), similar to an SQL table or Prometheus metric name.
    - tags: Key-value pairs of metadata that describe the data (e.g., `host="server1"`, `region="us-west"`), similar to Prometheus labels.
    - fields: The actual data values (e.g., `usage_percent=99.5`, `request_count=124`), similar to Prometheus metric value.
    - timestamp: The time of the data point.

    ## Syntax
    Flux queries consist of sequentially executed pipeline of functions, joined by the pipe-forward operator "|>".
    It takes the output of one function and sends it as the input to the next function.

    ### Main Flux functions
    - from() - Specifies the InfluxDB bucket to retrieve data from. It's the starting point for query that fetches time-series data.
    - range() - Filters data based on a time range. Mandatory for time-series queries.
    - filter() - Filters rows based on column values (measurement, field, tags).
    - pivot() - Rotates data from a tall format (one row per timestamp/metric) to a wide format.
    - keep() / drop() - Filters data by column names, allowing you to keep or discard specific columns.
    - limit() - Restricts the number of rows returned.
    - group() - Groups rows together based on common column values for aggregation.
    - aggregateWindow() - Segments data into time windows and applies an aggregate function (mean, sum, etc.).
    - map() - Applies a custom function to each row to modify or add columns.
    - mean(), sum(), count(), last() - Common aggregate functions, often used inside aggregateWindow.
    - highestAverage(), highestMax(), lowestAverage(), top() - Efficient "top-n" results from a group, are significantly more performant for datasets with high tag cardinality
    - yield() - Specifies a result set to be delivered from the query.

    ### Meta functions
    - buckets() - Returns a list of all available buckets.
    - schema.measurements() - Returns a list of all measurements within a bucket.
    - schema.tagKeys() / schema.tagValues() - Returns a list of tag keys or tag values for a given measurement.

    ## Usage
    When using Flux through the Grafana's `/api/ds/query` endpoint, several variables are injected into the query,
    the most important are the `v.timeRangeStart` and `v.timeRangeStop`, which correspond to the `start_time` and `end_time` parameters
    passed to the `/api/ds/query` endpoint. So each query that fetches data from time series should look like this:

    ```flux
    // Specify the bucket name here
    from(bucket: "{bucket}")
        |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
        // Filters, transformations, aggegations, etc.
        |> yield(name: "value")
    ```

    ### Examples

    #### Get all buckets
    ```flux
    buckets()
    ```

    #### Get all measurements in a given bucket
    ```flux
    // Import the schema package to access its functions
    import "influxdata/influxdb/schema"
    // Call the measurements function, specifying which bucket to look in
    schema.measurements(bucket: "{bucket}")
    ```

    #### Get all field keys for a given measurement
    ```flux
    import "influxdata/influxdb/schema"
    schema.measurementFieldKeys(
        bucket: "{bucket}",
        measurement: "{measurement}"
    )
    ```

    #### Get all tag keys for a given measurement
    ```flux
    import "influxdata/influxdb/schema"
    schema.measurementTagKeys(
        bucket: "{bucket}",
        measurement: "{measurement}"
    )
    ```

    #### Get all tag values for a given tag key
    ```flux
    import "influxdata/influxdb/schema"
    schema.measurementTagValues(
        bucket: "{bucket}",
        measurement: "{measurement}",
        tag: "{tag}"
    )
    ```

    #### Filtering and aggregation
    ```flux
    from(bucket: "{bucket}")
        |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
        |> filter(fn: (r) => r._measurement == "{measurement}" and r._field == "{field}")
        // Pivot makes each unique field a new column, with timestamps as rows.
        // This is useful for creating tables or graphs with multiple series.
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        // Group data into 10-minute windows and calculate the mean for each window
        |> aggregateWindow(every: 10m, fn: mean)
        |> yield(name: "mean_{field}_10m")
    ```

    #### Finding lowest average values among groups
    ```flux
    from(bucket: "{bucket}")
        |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
        |> filter(fn: (r) => r._measurement == "{measurement}" and r._field == "{field}")
        |> lowestAverage(n: {n}, groupColumns: ["{tag}"])
    ```
    """
    return instruction


# def build_prometheus_from_grafana_datasource_proxy(
#     grafana_url: str, datasource: str, auth: tuple[str, str], **kwargs
# ):
#     """https://grafana.com/docs/grafana/v11.2/developers/http_api/data_source/#data-source-proxy-calls-by-id"""
#     data_sources = fetch_grafana_datasources(grafana_url, auth)
#     data_source = data_sources.filter(pl.col("name") == datasource)
#     if len(data_source) != 1:
#         raise ValueError(f"Couldn't find a singular id for data source {data_source}.")

#     data_source_id = data_source["id"].item()
#     prometheus_url = join_url_components(grafana_url, "api", "datasources", "proxy", data_source_id)
#     prometheus = Prometheus(prometheus_url, auth=auth, **kwargs)
#     return prometheus


# class Prometheus:
#     """https://prometheus.io/docs/prometheus/latest/querying/api"""

#     def __init__(
#         self,
#         url: str,
#         api_version: str = "v1",
#         default_start=datetime.timedelta(days=-1),
#         default_end=None,
#         time_zone: str = "Asia/Baku",
#         auth=None,
#     ):
#         self.url = url
#         self.api_version = api_version
#         self.default_date_keys = {
#             "start": default_start,
#             "end": default_end,
#             "time": default_end,
#         }
#         self.time_zone = time_zone
#         self.auth = auth

#     def request_as_dict(self, *url_components, **params) -> dict:
#         params = {k: v for k, v in params.items() if v}
#         match url_components:
#             case (
#                 ["query"]
#                 | ["query_range"]
#                 | ["series"]
#                 | ["labels"]
#                 | ["label", _, "values"]
#                 | ["query_exemplars"]
#             ):
#                 for key, default in self.default_date_keys.items():
#                     value = params.get(key, default)
#                     params[key] = to_datetime(value).isoformat()

#         url = join_url_components(self.url, "api", self.api_version, *url_components)
#         response_dict = request_as_dict(url, params=params, auth=self.auth)
#         if response_dict["status"] == "error":
#             raise RuntimeError(
#                 f'Prometheus API request for "{join_url_components(*url_components)}" endpoint '
#                 f"with parameters {params} returned an error:\n"
#                 f"{response_dict}"
#             )

#         data = response_dict["data"]
#         return data

#     def response_metric_data_to_dataframe(self, data: dict) -> pl.DataFrame | None:
#         if not (result := data["result"]):
#             return

#         rows = []
#         for series in result:
#             match data["resultType"]:
#                 case "matrix":
#                     values = series["values"]
#                 case "vector":
#                     values = [series["value"]]

#             for timestamp, value in values:
#                 row = series["metric"] | {"timestamp": timestamp, "value": value}
#                 rows.append(row)

#         if not rows:
#             return

#         df = pl.DataFrame(rows)
#         df = df.cast({"value": pl.Float64})
#         df = df.with_columns(pl.from_epoch("timestamp").dt.convert_time_zone(self.time_zone))
#         return df

#     def query(self, query, time=None, timeout: str | None = None) -> pl.DataFrame | None:
#         """https://prometheus.io/docs/prometheus/latest/querying/api/#instant-queries"""
#         query = re.sub(r"\s+", " ", query)
#         data = self.request_as_dict("query", query=query, time=time, timeout=timeout)
#         df = self.response_metric_data_to_dataframe(data)
#         return df

#     def query_range(
#         self,
#         query: str,
#         start=None,
#         end=None,
#         step: str | float = "1m",
#         timeout: str | None = None,
#     ) -> pl.DataFrame | None:
#         """https://prometheus.io/docs/prometheus/latest/querying/api/#range-queries"""
#         data = self.request_as_dict(
#             "query_range",
#             query=re.sub(r"\s+", " ", query),
#             start=start,
#             end=end,
#             step=step,
#             timeout=timeout,
#         )
#         df = self.response_metric_data_to_dataframe(data)
#         return df

#     def get_all_metric_names(self, **kwargs) -> list[str]:
#         """https://prometheus.io/docs/prometheus/latest/querying/api/#querying-label-values"""
#         data = self.request_as_dict("label", "__name__", "values", **kwargs)
#         return data

#     def get_time_series(self, series_selector: str, start=None, end=None) -> pl.DataFrame | None:
#         """https://prometheus.io/docs/prometheus/latest/querying/api/#finding-series-by-label-matchers"""
#         data = self.request_as_dict(
#             "series", **{"match[]": series_selector, "start": start, "end": end}
#         )
#         if not data:
#             return

#         df = pl.DataFrame(data)
#         return df
