from movielist.tests import MovielistTestCase

from .models import Cinema, Screening

from django.utils import timezone

from random import randint
from datetime import datetime


class ShowtimesTestCase(MovielistTestCase):
    def setUp(self):
        super(ShowtimesTestCase, self).setUp()
        for _ in range(3):
            Cinema.objects.create(**self._fake_cinema_data())
        for cinema in Cinema.objects.all():
            for _ in range(3):
                Screening.objects.create(**self._fake_screening_data(cinema=cinema))
        self.cinema_id = self._get_cinema_id()
        self.screening_id = self._get_screening_id()

    @staticmethod
    def _get_random_cinema():
        """Return random cinema from db"""
        cinemas = Cinema.objects.all()
        return cinemas[randint(0, len(cinemas) - 1)]

    def _get_cinema_id(self):
        """Return id of random cinema from db"""
        return self._get_random_cinema().id

    def _get_cinema_name(self):
        """Return name of random cinema from db"""
        return self._get_random_cinema().name

    def _get_cinema_city(self):
        """Return city of random cinema from db"""
        return self._get_random_cinema().city

    def _get_cinema_movie_title(self):
        """Return title of random movie in cinema from db"""
        screenings = self._get_random_cinema().screening_set.all()
        return screenings[randint(0, len(screenings) - 1)].movie.title

    @staticmethod
    def _get_random_screening():
        """Return random screening from db"""
        screenings = Screening.objects.all()
        return screenings[randint(0, len(screenings) - 1)]

    def _get_screening_id(self):
        """Return id of random screening from db"""
        return self._get_random_screening().id

    def _fake_cinema_data(self):
        cinema_data = {
            'name': self.faker.company(),
            'city': self.faker.city(),
        }
        return cinema_data

    def _fake_screening_data(self, cinema=None):
        """
        Returns screening data:
        if cinema is specified, it's used and random movie instance is inserted
        otherwise random cinema.name and movie.title is used
        """
        screening_data = {
            'cinema': cinema if cinema else self._get_cinema_name(),
            'movie': self._get_random_movie() if cinema else self._get_movie_title(),
            'date': self._get_random_date()
        }
        return screening_data

    def _get_random_date(self):
        """
        Returns new formatted date within range(now, +1 year)
        date format: %Y-%m-%dT%H:%M:%SZ
        """
        date = self.faker.date_time_between(start_date="now", end_date="+1y",
                                            tzinfo=timezone.get_current_timezone())
        # date = datetime.strftime(date, '%Y-%m-%dT%H:%M:%SZ')
        return date


class CinemaTestCase(ShowtimesTestCase):

    def test_post_cinema(self):
        cinemas_before = Cinema.objects.count()
        new_cinema = self._fake_cinema_data()
        response = self.client.post('/cinemas/', new_cinema, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Cinema.objects.count(), cinemas_before + 1)
        for key, val in new_cinema.items():
            self.assertIn(key, response.data)
            if isinstance(val, list):
                # Compare contents regardless of their order
                self.assertCountEqual(response.data[key], val)
            else:
                self.assertEqual(response.data[key], val)

    def test_get_cinema_list(self):
        response = self.client.get('/movies/', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cinema.objects.count(), len(response.data))

    def test_get_cinema_detail(self):
        response = self.client.get(f'/cinemas/{self.cinema_id}/', {}, format='json')
        self.assertEqual(response.status_code, 200)
        for field in ['name', 'city', 'movies']:
            self.assertIn(field, response.data)

    def test_delete_cinema(self):
        response = self.client.delete(f'/cinemas/{self.cinema_id}/', {}, format='json')
        self.assertEqual(response.status_code, 204)
        cinema_ids = [cinema.id for cinema in Cinema.objects.all()]
        self.assertNotIn(self.cinema_id, cinema_ids)
        screenings_cinema_ids = [screening.cinema_id for screening in Screening.objects.all()]
        self.assertNotIn(self.cinema_id, screenings_cinema_ids)

    def test_update_cinema(self):
        response = self.client.get(f'/cinemas/{self.cinema_id}/', {}, format='json')
        self.assertEqual(response.status_code, 200)
        cinema_data = response.data
        new_name = self.faker.company()
        cinema_data['name'] = new_name
        new_city = self.faker.city()
        cinema_data['city'] = new_city
        response = self.client.patch(f'/cinemas/{self.cinema_id}/', cinema_data, format='json')
        self.assertEqual(response.status_code, 200)
        cinema_obj = Cinema.objects.get(id=self.cinema_id)
        self.assertEqual(cinema_obj.name, new_name)
        self.assertEqual(cinema_obj.city, new_city)


class ScreeningTestCase(ShowtimesTestCase):

    def test_post_screening(self):
        screenings_before = Screening.objects.count()
        new_screening = self._fake_screening_data()
        response = self.client.post('/screenings/', new_screening, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Screening.objects.count(), screenings_before + 1)

        # change date to match format of date in response.data
        new_screening['date'] = datetime.strftime(new_screening['date'], '%Y-%m-%dT%H:%M:%SZ')

        for key, val in new_screening.items():
            self.assertIn(key, response.data)
            if isinstance(val, list):
                # Compare contents regardless of their order
                self.assertCountEqual(response.data[key], val)
            else:
                self.assertEqual(response.data[key], val)

    def test_get_screening_list(self):
        response = self.client.get('/screenings/', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Screening.objects.count(), len(response.data))

    def test_get_screening_detail(self):
        response = self.client.get(f'/screenings/{self.screening_id}/', {}, format='json')
        self.assertEqual(response.status_code, 200)
        for field in ['cinema', 'movie', 'date']:
            self.assertIn(field, response.data)

    def test_delete_screening(self):
        response = self.client.delete(f'/screenings/{self.screening_id}/', {}, format='json')
        self.assertEqual(response.status_code, 204)
        screening_ids = [screening.id for screening in Screening.objects.all()]
        self.assertNotIn(self.screening_id, screening_ids)

    def test_update_screening(self):
        response = self.client.get(f'/screenings/{self.screening_id}/', {}, format='json')
        self.assertEqual(response.status_code, 200)
        screening_data = response.data
        new_movie = self._get_movie_title()
        screening_data['movie'] = new_movie
        new_date = self._get_random_date()
        screening_data['date'] = new_date
        response = self.client.patch(f'/screenings/{self.screening_id}/', screening_data, format='json')
        self.assertEqual(response.status_code, 200)
        screening = Screening.objects.get(id=self.screening_id)
        self.assertEqual(screening.movie.title, new_movie)
        self.assertEqual(screening.date, new_date)
