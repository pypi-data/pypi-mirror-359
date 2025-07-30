import unittest

from mmragsdk import Client
from dotenv import load_dotenv
import os
from reportlab.pdfgen import canvas

import pytest


load_dotenv()


RANDOM_PATH = 'random_path'
client = Client(token=os.getenv("TOKEN_PAT"))


def create_test_pdf(filename="test.pdf"):
  # Create a canvas object with the given filename
  c = canvas.Canvas(filename)

  # Add some minimal text
  c.drawString(100, 750, "Hello, this is a test PDF.")

  # Finalize the PDF file
  c.save()
  print(f"PDF created: {filename}")


def test_missing_file_path_error():
  with pytest.raises(FileNotFoundError):
    client.upload(RANDOM_PATH)


def test_empty_search_query_raises():
  with pytest.raises(ValueError):
    client.search('')


def test_empty_chat_prompt_raises():
  with pytest.raises(ValueError):
    client.chat('')


def test_chat_success():
  response = client.chat("How are you?")

  assert response.status_code == 200


def test_search_success():
  response = client.search('test')

  assert response.status_code == 200


def test_upload_success():
  path = 'test.txt'
  with open(path, 'w') as f:
    f.write('test')
  response = client.upload(path)

  assert response.status_code == 200

  if os.path.exists(path):
    os.remove(path)


def test_pdf_upload_success():
  path = 'test.pdf'
  create_test_pdf(path)

  try:
    response = client.upload(path)
  except:
    if os.path.exists(path):
      os.remove(path)
    raise

  assert response.status_code == 200


def test_clean_success():
  response = client.clean()
  assert response.status_code == 200


def test_invalid_token_chat_error():
  client.token = 'wrong token'
  response = client.chat('t')
  assert response.status_code == 403


def test_invalid_token_search_error():
  client.token = 'wrong token'
  response = client.search('t')
  assert response.status_code == 403


def test_invalid_token_upload_error():
  client.token = 'wrong token'
  response = client.chat('t')
  assert response.status_code == 403


def test_invalid_token_clean_error():
  client.token = 'wrong token'
  response = client.clean()
  assert response.status_code == 403
