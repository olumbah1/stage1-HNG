# analyzer/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import hashlib
import json


def sha256_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class StringAnalyzerAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # sample strings (ensure these are defined)
        self.palindrome = "madam"
        self.phrase_pal = "Able was I ere I saw Elba"
        self.normal = "hello world"
        self.to_delete = "todelete"

    def test_create_string_success(self):
        resp = self.client.post("/strings", {"value": self.palindrome}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, msg=f"Unexpected response: {resp.content}")
        data = resp.json()

        # top-level fields
        self.assertIn("id", data)
        self.assertIn("value", data)
        self.assertIn("properties", data)
        self.assertIn("created_at", data)
        self.assertEqual(data["value"], self.palindrome)

        # properties checks
        props = data["properties"]
        self.assertEqual(props["length"], len(self.palindrome))
        self.assertTrue(props["is_palindrome"])
        self.assertEqual(props["word_count"], 1)
        self.assertEqual(props["sha256_hash"], data["id"])
        self.assertIsInstance(props["character_frequency_map"], dict)
        self.assertEqual(props["unique_characters"], len(set(self.palindrome)))

    def test_create_duplicate_conflict(self):
        # create once
        resp1 = self.client.post("/strings", {"value": self.normal}, format="json")
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED, msg=f"First create failed: {resp1.content}")
        # create again -> should be 409 Conflict
        resp2 = self.client.post("/strings", {"value": self.normal}, format="json")

        # allow some flexibility: preferred is 409, but if view returns 400/422 that's likely validation; assert no 5xx
        self.assertNotIn(resp2.status_code // 100, (5,), msg=f"Server error on duplicate create: {resp2.content}")
        self.assertIn(resp2.status_code, (status.HTTP_409_CONFLICT, status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY),
                      msg=f"Expected 409/400/422 for duplicate create, got {resp2.status_code}: {resp2.content}")

    def test_get_specific_string(self):
        # create then fetch
        create_resp = self.client.post("/strings", {"value": self.phrase_pal}, format="json")
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED, msg=f"Create failed: {create_resp.content}")

        # Fetch by value (test client will not URL-encode automatically for path string; using same exact string)
        get_resp = self.client.get(f"/strings/{self.phrase_pal}")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK, msg=f"GET specific failed: {get_resp.content}")
        data = get_resp.json()
        self.assertEqual(data["value"], self.phrase_pal)
        self.assertEqual(data["properties"]["sha256_hash"], sha256_hash(self.phrase_pal))

    def test_list_filters_is_palindrome_and_word_count(self):
        # create three strings
        r1 = self.client.post("/strings", {"value": self.palindrome}, format="json")
        r2 = self.client.post("/strings", {"value": self.normal}, format="json")
        r3 = self.client.post("/strings", {"value": "level"}, format="json")
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r3.status_code, status.HTTP_201_CREATED)

        resp = self.client.get("/strings/?is_palindrome=true&word_count=1")
        self.assertEqual(resp.status_code, status.HTTP_200_OK, msg=f"List filter failed: {resp.content}")
        data = resp.json()
        self.assertIn("data", data)
        self.assertIn("count", data)
        self.assertIn("filters_applied", data)

        # all returned items must be palindromic and single-word
        for item in data["data"]:
            props = item["properties"]
            self.assertTrue(props["is_palindrome"], msg=f"Item not palindrome: {item}")
            self.assertEqual(props["word_count"], 1, msg=f"Item not single-word: {item}")

    def test_natural_language_filter(self):
        # create two records that fit "single word palindromic strings"
        c1 = self.client.post("/strings", {"value": "mom"}, format="json")
        c2 = self.client.post("/strings", {"value": "noon"}, format="json")
        c3 = self.client.post("/strings", {"value": "notpal"}, format="json")
        self.assertEqual(c1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(c2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(c3.status_code, status.HTTP_201_CREATED)

        resp = self.client.get("/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings")
        # Accept 200 OK (preferred). If your implementation returns 400/422/404, show helpful debug message.
        if resp.status_code != status.HTTP_200_OK:
            self.fail(f"Natural language filter endpoint returned {resp.status_code}. Response content: {resp.content}")

        data = resp.json()
        self.assertIn("interpreted_query", data)
        parsed = data["interpreted_query"]["parsed_filters"]
        self.assertEqual(parsed.get("word_count"), 1)
        self.assertTrue(parsed.get("is_palindrome"))
        # returned data count should be at least the two palindromes we created
        self.assertGreaterEqual(data["count"], 2, msg=f"Expected >=2 palindromic results, got: {data}")

    def test_delete_string(self):
        # create and delete
        create_resp = self.client.post("/strings", {"value": self.to_delete}, format="json")
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED, msg=f"Create failed: {create_resp.content}")

        del_resp = self.client.delete(f"/strings/{self.to_delete}/delete")
        self.assertIn(del_resp.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK),
                      msg=f"Unexpected delete response: {del_resp.status_code} {del_resp.content}")

        # subsequent GET should return 404 (or no record)
        get_resp = self.client.get(f"/strings/{self.to_delete}")
        self.assertIn(get_resp.status_code, (status.HTTP_404_NOT_FOUND, status.HTTP_200_OK),
                      msg=f"Unexpected GET after delete status: {get_resp.status_code} - {get_resp.content}")
        # If GET returns 200, double-check if record still exists — fail to highlight unexpected behavior
        if get_resp.status_code == status.HTTP_200_OK:
            self.fail(f"Record still exists after delete. GET returned 200 with content: {get_resp.content}")

    def test_create_invalid_missing_value(self):
        resp = self.client.post("/strings", {}, format="json")
        # serializer should return 400 bad request for missing field (or other client error)
        self.assertIn(resp.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY),
                      msg=f"Expected 400/422 for missing value, got {resp.status_code}: {resp.content}")

    def test_invalid_contains_character_filter(self):
        # bad query param (more than one char) should return 400 from our expected validation
        resp = self.client.get("/strings?contains_character=ab")
        if resp.status_code != status.HTTP_400_BAD_REQUEST:
            # allow alternative behavior but fail with helpful message so you can adjust view if needed
            self.fail(f"Expected 400 for invalid contains_character, got {resp.status_code}. Response: {resp.content}")
