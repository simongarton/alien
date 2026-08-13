
import urllib.parse
import urllib.request
from secrets import API_ENDPOINT, API_KEY
from urllib.error import HTTPError


def call_api(params: dict[str, str], output_path: str) -> None:
    url = f"{API_ENDPOINT}?{urllib.parse.urlencode(params)}"
    # API Gateway only returns raw binary (rather than a base64 string) when
    # the client's Accept header matches the API's binary_media_types.
    request = urllib.request.Request(url, headers={"x-api-key": API_KEY, "Accept": "image/png"})

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read()
    except HTTPError as e:
        print(f"Request failed: {e.code} {e.reason}")
        print(e.read().decode())
        raise

    with open(output_path, "wb") as f:
        f.write(data)

    print(f"Wrote {output_path} ({len(data)} bytes)")


if __name__ == "__main__":
    call_api(
        params={"width": "16", "height": "16", "legs": "3", "arms": "2"},
        output_path="api_test_alien.png",
    )
