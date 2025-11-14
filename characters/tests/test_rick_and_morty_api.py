from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch

from characters.models import Character
from characters.serializers import CharacterSerializer


class RandomCharacterViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.char1 = Character.objects.create(api_id=1, name="Rick", image="rick.png")
        self.char2 = Character.objects.create(api_id=2, name="Morty", image="morty.png")

    @patch("characters.views.random.choice")
    def test_random_character_is_mocked(self, mock_choice):
        mock_choice.return_value = self.char2.pk

        url = reverse("characters:character-random")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), CharacterSerializer(self.char2).data)

        args, kwargs = mock_choice.call_args
        passed_list = args[0]
        self.assertSetEqual(set(passed_list), {self.char1.pk, self.char2.pk})


class CharacterListViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.char1 = Character.objects.create(
            api_id=1, name="Rick Sanchez", image="rick.png"
        )
        self.char2 = Character.objects.create(
            api_id=2, name="Morty Smith", image="morty.png"
        )
        self.char3 = Character.objects.create(
            api_id=3, name="Summer Smith", image="summer.png"
        )

    def test_list_characters_without_filter(self):
        url = reverse("characters:character-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        expected = CharacterSerializer(
            [self.char1, self.char2, self.char3], many=True
        ).data

        self.assertEqual(response.json(), expected)

    def test_list_characters_with_filter(self):
        url = reverse("characters:character-list")
        response = self.client.get(url, {"name": "mor"})

        self.assertEqual(response.status_code, 200)

        expected = CharacterSerializer([self.char2], many=True).data

        self.assertEqual(response.json(), expected)

    def test_filter_no_matches(self):
        url = reverse("characters:character-list")
        response = self.client.get(url, {"name": "xyz"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
