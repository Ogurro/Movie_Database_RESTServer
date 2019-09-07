from random import randint, sample

from faker import Faker
from rest_framework.test import APITestCase

from movielist.models import Movie, Person


class MovielistTestCase(APITestCase):
    """Creates APITestCase with setUp for multiple use in different applications (i.e. showtimes)"""

    def setUp(self):
        """Populate test database with random data."""
        self.faker = Faker("pl_PL")
        for _ in range(5):
            Person.objects.create(name=self.faker.name())
        for _ in range(3):
            self._create_fake_movie()
        self.movie_id = self._get_movie_id()

    @staticmethod
    def _get_random_movie():
        """Return random movie from db"""
        movies = Movie.objects.all()
        return movies[randint(0, len(movies) - 1)]

    def _get_movie_title(self):
        """Return title of random movie from db"""
        return self._get_random_movie().title

    def _get_movie_id(self):
        """Return a id for random Movie object from db"""
        return self._get_random_movie().id

    @staticmethod
    def _random_person():
        """Return a random Person object from db."""
        people = Person.objects.all()
        return people[randint(0, len(people) - 1)]

    @staticmethod
    def _find_person_by_name(name):
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

    def _compare_key_val(self, response, obj):
        for key, val in obj.items():
            self.assertIn(key, response.data)
            if isinstance(val, list):
                # Compare contents regardless of their order
                self.assertCountEqual(response.data[key], val)
            else:
                self.assertEqual(response.data[key], val)


class MovieTestCase(MovielistTestCase):
    """Tests for Movie Views"""

    def test_post_movie(self):
        movies_before = Movie.objects.count()
        new_movie = self._fake_movie_data()
        response = self.client.post("/movies/", new_movie, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Movie.objects.count(), movies_before + 1)
        self._compare_key_val(response, new_movie)

    def test_get_movie_list(self):
        response = self.client.get("/movies/", {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Movie.objects.count(), len(response.data))

    def test_get_movie_detail(self):
        response = self.client.get(f"/movies/{self.movie_id}/", {}, format='json')
        self.assertEqual(response.status_code, 200)
        for field in ["title", "year", "description", "director", "actors"]:
            self.assertIn(field, response.data)

    def test_delete_movie(self):
        response = self.client.delete(f"/movies/{self.movie_id}/", {}, format='json')
        self.assertEqual(response.status_code, 204)
        movie_ids = [movie.id for movie in Movie.objects.all()]
        self.assertNotIn(self.movie_id, movie_ids)

    def test_update_movie(self):
        response = self.client.get(f"/movies/{self.movie_id}/", {}, format='json')
        movie_data = response.data
        new_year = 2003
        movie_data["year"] = new_year
        new_actors = [self._random_person().name]
        movie_data["actors"] = new_actors
        response = self.client.patch(f"/movies/{self.movie_id}/", movie_data, format='json')
        self.assertEqual(response.status_code, 200)
        movie_obj = Movie.objects.get(id=self.movie_id)
        self.assertEqual(movie_obj.year, new_year)
        db_actor_names = [actor.name for actor in movie_obj.actors.all()]
        self.assertCountEqual(db_actor_names, new_actors)
