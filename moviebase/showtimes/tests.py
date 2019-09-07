from movielist.tests import MovielistTestCase

from .models import Cinema, Screening

from django.utils import timezone
from random import randint


class ShowtimesTestCase(MovielistTestCase):
    def setUp(self):
        super(ShowtimesTestCase, self).setUp()
        for _ in range(3):
            Cinema.objects.create(name=self.faker.company(), city=self.faker.city())
        for cinema in Cinema.objects.all():
            for _ in range(3):
                movie = self._get_random_movie()
                date = self.faker.date_time_between(start_date="now", end_date="+1y",
                                                    tzinfo=timezone.get_current_timezone())
                Screening.objects.create(cinema=cinema, movie=movie, date=date)
        self.cinema_id = self._get_cinema_id()

    @staticmethod
    def _get_random_cinema():
        cinemas = Cinema.objects.all()
        return cinemas[randint(0, len(cinemas) - 1)]

    def _get_cinema_id(self):
        return self._get_random_cinema().id

    def _fake_cinema_data(self):
        cinema_data = {
            'name': self.faker.company(),
            'city': self.faker.city(),
        }
        return cinema_data


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
