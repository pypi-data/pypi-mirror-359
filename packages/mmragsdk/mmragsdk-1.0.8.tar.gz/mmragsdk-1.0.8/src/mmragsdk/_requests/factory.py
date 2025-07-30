import os

from requests import Request


URL = "https://0jl0v93oi5.execute-api.eu-central-1.amazonaws.com/"


def get_request(function_name: str, api: str, user_input: str) -> Request:
  if function_name == "chat":
    return Request(
      "POST",
      url=URL + '/chat',
      headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api}"
      },
      json={
        "query": user_input,
      }
    )
  elif function_name == "search":
    return Request(
      "POST",
      url=URL + '/search',
      headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api}"
      },
      json={
        "query": user_input,
      }
    )
  elif function_name == "upload":
    with open(user_input, 'rb') as f:
      req = Request(
        "POST",
        url=URL + '/upload-file',
        headers={
          "Authorization": f"Bearer {api}"
        },
        files={
          "file": (os.path.basename(user_input), f.read(), "multipart/form-data")
        }
      )
    return req
  elif function_name == "clean":
    return Request(
      "POST",
      url=URL + '/cleanUp',
      headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api}"
      },
      json={}
    )
  else:
    raise NotImplementedError(
      f"Function {function_name} not implemented"
    )