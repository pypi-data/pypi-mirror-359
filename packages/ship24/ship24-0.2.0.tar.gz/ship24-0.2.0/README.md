# ship-24

Developer-friendly & type-safe Python SDK specifically catered to leverage _ship-24_ API.

<div align="left">
    <a href="https://www.speakeasy.com/?utm_source=ship-24&utm_campaign=python"><img src="https://custom-icon-badges.demolab.com/badge/-Built%20By%20Speakeasy-212015?style=for-the-badge&logoColor=FBE331&logo=speakeasy&labelColor=545454" /></a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" style="width: 100px; height: 28px;" />
    </a>
</div>

<br /><br />
Generated from a modified [ship24 openapi spec](https://docs.ship24.com/assets/openapi/ship24-tracking-api.yaml)

<!-- Start Summary [summary] -->

## Summary

Ship24 Tracking API: ## Getting started

Make sure to read the [Getting started](https://docs.ship24.com/getting-started) section of our [API Documentation](https://docs.ship24.com/) before using the endpoints presented below.

## Documentation structure

Use the top navigation bar to switch from:

- Our [API Documentation](https://docs.ship24.com/), which contains a comprehensive explanation of how our API works.
- Our [API Reference](https://docs.ship24.com/tracking-api-reference/), which contains the specification of each of our endpoints.
- Our [Support](https://docs.ship24.com/support/introduction) section, which contains help articles for most of the common questions and issues you may encounter.

## Import our documentation into your HTTP client

Our API Reference is available as an Open API 3.1 format file, which is supported by most HTTP clients.

- Latest version: https://docs.ship24.com/assets/openapi/ship24-tracking-api.yaml

| <!-- -->                                                     | <!-- -->                                                                                                                                                            |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ![Postman](/img/postman-logo.svg) Postman                    | In Postman, click on "Import", go on the "Link" tab, and paste this URL `https://docs.ship24.com/assets/openapi/ship24-tracking-api.yaml`                           |
| <img src="/img/insomnia-logo.png" width="32"></img> Insomnia | From Insomnia preferences, locate the "Import data" option, choose "From URL", and paste this URL `https://docs.ship24.com/assets/openapi/ship24-tracking-api.yaml` |

<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->

## Table of Contents

<!-- $toc-max-depth=2 -->

- [ship-24](#ship-24)
  - [Documentation structure](#documentation-structure)
  - [Import our documentation into your HTTP client](#import-our-documentation-into-your-http-client)
  - [SDK Installation](#sdk-installation)
  - [IDE Support](#ide-support)
  - [SDK Example Usage](#sdk-example-usage)
  - [Authentication](#authentication)
  - [Available Resources and Operations](#available-resources-and-operations)
  - [Retries](#retries)
  - [Error Handling](#error-handling)
  - [Server Selection](#server-selection)
  - [Custom HTTP Client](#custom-http-client)
  - [Resource Management](#resource-management)
  - [Debugging](#debugging)
- [Development](#development)
  - [Maturity](#maturity)
  - [Contributions](#contributions)

<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->

## SDK Installation

> [!TIP]
> To finish publishing your SDK to PyPI you must [run your first generation action](https://www.speakeasy.com/docs/github-setup#step-by-step-guide).

> [!NOTE] > **Python version upgrade policy**
>
> Once a Python version reaches its [official end of life date](https://devguide.python.org/versions/), a 3-month grace period is provided for users to upgrade. Following this grace period, the minimum python version supported in the SDK will be updated.

The SDK can be installed with either _pip_ or _poetry_ package managers.

### PIP

_PIP_ is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install git+<UNSET>.git
```

### Poetry

_Poetry_ is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add git+<UNSET>.git
```

### Shell and script usage with `uv`

You can use this SDK in a Python shell with [uv](https://docs.astral.sh/uv/) and the `uvx` command that comes with it like so:

```shell
uvx --from ship24 python
```

It's also possible to write a standalone Python script without needing to set up a whole project like so:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "ship24",
# ]
# ///

from ship24 import Ship24

sdk = Ship24(
  # SDK arguments
)

# Rest of script here...
```

Once that is saved to a file, you can run it with `uv run script.py` where
`script.py` can be replaced with the actual file name.

<!-- End SDK Installation [installation] -->

<!-- Start IDE Support [idesupport] -->

## IDE Support

### PyCharm

Generally, the SDK will work well with most IDEs out of the box. However, when using PyCharm, you can enjoy much better integration with Pydantic by installing an additional plugin.

- [PyCharm Pydantic Plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)
<!-- End IDE Support [idesupport] -->

<!-- Start SDK Example Usage [usage] -->

## SDK Example Usage

### Example

```python
# Synchronous Example
import os
from ship24 import Ship24


with Ship24(
    authorization=os.getenv("SHIP24_AUTHORIZATION", ""),
) as s_client:

    res = s_client.trackers.create_tracker()

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asychronous requests by importing asyncio.

```python
# Asynchronous Example
import asyncio
import os
from ship24 import Ship24

async def main():

    async with Ship24(
        authorization=os.getenv("SHIP24_AUTHORIZATION", ""),
    ) as s_client:

        res = await s_client.trackers.create_tracker_async()

        # Handle response
        print(res)

asyncio.run(main())
```

<!-- End SDK Example Usage [usage] -->

<!-- Start Authentication [security] -->

## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name            | Type   | Scheme  | Environment Variable   |
| --------------- | ------ | ------- | ---------------------- |
| `authorization` | apiKey | API key | `SHIP24_AUTHORIZATION` |

To authenticate with the API the `authorization` parameter must be set when initializing the SDK client instance. For example:

```python
import os
from ship24 import Ship24


with Ship24(
    authorization=os.getenv("SHIP24_AUTHORIZATION", ""),
) as s_client:

    res = s_client.trackers.create_tracker()

    # Handle response
    print(res)

```

<!-- End Authentication [security] -->

<!-- Start Available Resources and Operations [operations] -->

## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [api_for_per_call_plans](docs/sdks/apiforpercallplans/README.md)

- [get_tracking](docs/sdks/apiforpercallplans/README.md#get_tracking) - Get tracking results by tracking number

### [couriers](docs/sdks/couriers/README.md)

- [get_couriers](docs/sdks/couriers/README.md#get_couriers) - Get all couriers

### [trackers](docs/sdks/trackers/README.md)

- [create_tracker](docs/sdks/trackers/README.md#create_tracker) - Create a tracker
- [list_trackers](docs/sdks/trackers/README.md#list_trackers) - List existing Trackers
- [bulk_create_trackers](docs/sdks/trackers/README.md#bulk_create_trackers) - Bulk create trackers
- [create_tracker_and_get_tracking_results](docs/sdks/trackers/README.md#create_tracker_and_get_tracking_results) - Create a tracker and get tracking results
- [get_tracker_by_tracker_id](docs/sdks/trackers/README.md#get_tracker_by_tracker_id) - Get an existing tracker
- [update_tracker_by_tracker_id](docs/sdks/trackers/README.md#update_tracker_by_tracker_id) - Update an existing tracker
- [get_tracking_results_of_trackers_by_tracking_number](docs/sdks/trackers/README.md#get_tracking_results_of_trackers_by_tracking_number) - Get tracking results for existing trackers by tracking number
- [get_tracking_results_of_tracker_by_tracker_id](docs/sdks/trackers/README.md#get_tracking_results_of_tracker_by_tracker_id) - Get tracking results for an existing tracker
- [resend_webhooks](docs/sdks/trackers/README.md#resend_webhooks) - Resend webhooks of an existing tracker

</details>
<!-- End Available Resources and Operations [operations] -->

<!-- Start Retries [retries] -->

## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:

```python
import os
from ship24 import Ship24
from ship24.utils import BackoffStrategy, RetryConfig


with Ship24(
    authorization=os.getenv("SHIP24_AUTHORIZATION", ""),
) as s_client:

    res = s_client.trackers.create_tracker(,
        RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

    # Handle response
    print(res)

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:

```python
import os
from ship24 import Ship24
from ship24.utils import BackoffStrategy, RetryConfig


with Ship24(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
    authorization=os.getenv("SHIP24_AUTHORIZATION", ""),
) as s_client:

    res = s_client.trackers.create_tracker()

    # Handle response
    print(res)

```

<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->

## Error Handling

[`Ship24Error`](./src/ship24/errors/ship24error.py) is the base class for all HTTP error responses. It has the following properties:

| Property           | Type             | Description                                                                             |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------- |
| `err.message`      | `str`            | Error message                                                                           |
| `err.status_code`  | `int`            | HTTP response status code eg `404`                                                      |
| `err.headers`      | `httpx.Headers`  | HTTP response headers                                                                   |
| `err.body`         | `str`            | HTTP body. Can be empty string if no body is returned.                                  |
| `err.raw_response` | `httpx.Response` | Raw HTTP response                                                                       |
| `err.data`         |                  | Optional. Some errors may contain structured data. [See Error Classes](#error-classes). |

### Example

```python
import os
from ship24 import Ship24, errors


with Ship24(
    authorization=os.getenv("SHIP24_AUTHORIZATION", ""),
) as s_client:
    res = None
    try:

        res = s_client.trackers.create_tracker()

        # Handle response
        print(res)


    except errors.Ship24Error as e:
        # The base class for HTTP error responses
        print(e.message)
        print(e.status_code)
        print(e.body)
        print(e.headers)
        print(e.raw_response)

        # Depending on the method different errors may be thrown
        if isinstance(e, errors.ErrorResponseFormat):
            print(e.data.errors)  # Optional[List[models.ErrorResponseFormatError]]
            print(e.data.data)  # OptionalNullable[models.ErrorResponseFormatData]
```

### Error Classes

**Primary errors:**

- [`Ship24Error`](./src/ship24/errors/ship24error.py): The base class for HTTP error responses.
  - [`ErrorResponseFormat`](./src/ship24/errors/errorresponseformat.py): Generic error.

<details><summary>Less common errors (6)</summary>

<br />

**Network errors:**

- [`httpx.RequestError`](https://www.python-httpx.org/exceptions/#httpx.RequestError): Base class for request errors.
  - [`httpx.ConnectError`](https://www.python-httpx.org/exceptions/#httpx.ConnectError): HTTP client was unable to make a request to a server.
  - [`httpx.TimeoutException`](https://www.python-httpx.org/exceptions/#httpx.TimeoutException): HTTP request timed out.

**Inherit from [`Ship24Error`](./src/ship24/errors/ship24error.py)**:

- [`BulkCreateTrackersResponseError`](./src/ship24/errors/bulkcreatetrackersresponseerror.py): Created. Applicable to 1 of 11 methods.\*
- [`ResponseValidationError`](./src/ship24/errors/responsevalidationerror.py): Type mismatch between the response data and the expected Pydantic model. Provides access to the Pydantic validation error via the `cause` attribute.

</details>

\* Check [the method documentation](#available-resources-and-operations) to see if the error is applicable.

<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->

## Server Selection

### Override Server URL Per-Client

The default server can be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:

```python
import os
from ship24 import Ship24


with Ship24(
    server_url="https://api.ship24.com",
    authorization=os.getenv("SHIP24_AUTHORIZATION", ""),
) as s_client:

    res = s_client.trackers.create_tracker()

    # Handle response
    print(res)

```

<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->

## Custom HTTP Client

The Python SDK makes API calls using the [httpx](https://www.python-httpx.org/) HTTP library. In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with your own HTTP client instance.
Depending on whether you are using the sync or async version of the SDK, you can pass an instance of `HttpClient` or `AsyncHttpClient` respectively, which are Protocol's ensuring that the client has the necessary methods to make API calls.
This allows you to wrap the client with your own custom logic, such as adding custom headers, logging, or error handling, or you can just pass an instance of `httpx.Client` or `httpx.AsyncClient` directly.

For example, you could specify a header for every request that this sdk makes as follows:

```python
from ship24 import Ship24
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = Ship24(client=http_client)
```

or you could wrap the client with your own custom logic:

```python
from ship24 import Ship24
from ship24.httpclient import AsyncHttpClient
import httpx

class CustomClient(AsyncHttpClient):
    client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient):
        self.client = client

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault, None
        ] = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: Union[
            bool, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        request.headers["Client-Level-Header"] = "added by client"

        return await self.client.send(
            request, stream=stream, auth=auth, follow_redirects=follow_redirects
        )

    def build_request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        *,
        content: Optional[httpx._types.RequestContent] = None,
        data: Optional[httpx._types.RequestData] = None,
        files: Optional[httpx._types.RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[httpx._types.QueryParamTypes] = None,
        headers: Optional[httpx._types.HeaderTypes] = None,
        cookies: Optional[httpx._types.CookieTypes] = None,
        timeout: Union[
            httpx._types.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
        extensions: Optional[httpx._types.RequestExtensions] = None,
    ) -> httpx.Request:
        return self.client.build_request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )

s = Ship24(async_client=CustomClient(httpx.AsyncClient()))
```

<!-- End Custom HTTP Client [http-client] -->

<!-- Start Resource Management [resource-management] -->

## Resource Management

The `Ship24` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
import os
from ship24 import Ship24
def main():

    with Ship24(
        authorization=os.getenv("SHIP24_AUTHORIZATION", ""),
    ) as s_client:
        # Rest of application here...


# Or when using async:
async def amain():

    async with Ship24(
        authorization=os.getenv("SHIP24_AUTHORIZATION", ""),
    ) as s_client:
        # Rest of application here...
```

<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->

## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.

```python
from ship24 import Ship24
import logging

logging.basicConfig(level=logging.DEBUG)
s = Ship24(debug_logger=logging.getLogger("ship24"))
```

You can also enable a default debug logger by setting an environment variable `SHIP24_DEBUG` to true.

<!-- End Debugging [debug] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically. Any manual changes added to internal files will be overwritten on the next generation.
We look forward to hearing your feedback. Feel free to open a PR or an issue with a proof of concept and we'll do our best to include it in a future release.

### SDK Created by [Speakeasy](https://www.speakeasy.com/?utm_source=ship-24&utm_campaign=python)
