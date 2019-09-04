from random import randint, sample

from faker import Faker
from rest_framework.test import APITestCase, APIRequestFactory

from movielist.models import Movie, Person
from movielist.serializers import MovieSerializer


class MovieTestCase(APITestCase):

    def setUp(self):
        """Populate test database with random data."""
        self.faker = Faker("pl_PL")
        for _ in range(5):
            Person.objects.create(name=self.faker.name())
        for _ in range(3):
            self._create_fake_movie()

    def _random_person(self):
        """Return a random Person object from db."""
        people = Person.objects.all()
        return people[randint(0, len(people) - 1)]

    def _find_person_by_name(self, name):
        """Return the first `Person` object that matches `name`."""
        return Person.objects.filter(name=name).first()

    def _fake_movie_data(self):
        """Generate a dict of movie data

        The format is compatible with serializers (`Person` relations
        represented by names).
        """
        movie_data = {
            "title": "{} {}".format(self.faker.job(), self.faker.first_name()),
            "description": self.faker.sentence(),
            "year": int(self.faker.year()),
            "director": self._random_person().name,
        }
        people = Person.objects.all()
        actors = sample(list(people), randint(1, len(people)))
        actor_names = [a.name for a in actors]
        movie_data["actors"] = actor_names
        print(movie_data["title"])
        return movie_data

    def _create_fake_movie(self):
        """Generate new fake movie and save to database."""
        movie_data = self._fake_movie_data()
        movie_data["director"] = self._find_person_by_name(movie_data["director"])
        actors = movie_data["actors"]
        del movie_data["actors"]
        new_movie = Movie.objects.create(**movie_data)
        for actor in actors:
            new_movie.actors.add(self._find_person_by_name(actor))

    def test_post_movie(self):
        movies_before = Movie.objects.count()
        new_movie = self._fake_movie_data()
        response = self.client.post("/movies/", new_movie, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Movie.objects.count(), movies_before + 1)
        for key, val in new_movie.items():
            self.assertIn(key, response.data)
            if isinstance(val, list):
                # Compare contents regardless of their order
                self.assertCountEqual(response.data[key], val)
            else:
                self.assertEqual(response.data[key], val)

    def test_get_movie_list(self):
        response = self.client.get("/movies/", {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Movie.objects.count(), len(response.data))

    def test_get_movie_detail(self):
        response = self.client.get("/movies/1/", {}, format='json')
        self.assertEqual(response.status_code, 200)
        for field in ["title", "year", "description", "director", "actors"]:
            self.assertIn(field, response.data)

    def test_delete_movie(self):
        response = self.client.delete("/movies/1/", {}, format='json')
        self.assertEqual(response.status_code, 204)
        movie_ids = [movie.id for movie in Movie.objects.all()]
        self.assertNotIn(1, movie_ids)

    def test_update_movie(self):
        response = self.client.get("/movies/1/", {}, format='json')
        movie_data = response.data
        new_year = 3
        movie_data["year"] = new_year
        new_actors = [self._random_person().name]
        movie_data["actors"] = new_actors
        response = self.client.patch("/movies/1/", movie_data, format='json')
        self.assertEqual(response.status_code, 200)
        movie_obj = Movie.objects.get(id=1)
        self.assertEqual(movie_obj.year, new_year)
        db_actor_names = [actor.name for actor in movie_obj.actors.all()]
        self.assertCountEqual(db_actor_names, new_actors)
