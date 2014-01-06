from datetime import datetime
from math import log
import operator
import random
import re

from config import CONFIG as cfg
from db import _key, msetbit, sequential_id, first_key_with_bit_set

# This is pretty restrictive, but we can always relax it later.
VALID_EXPERIMENT_ALTERNATIVE_RE = re.compile(r"^[a-z0-9][a-z0-9\-_]*$", re.I)
VALID_KPI_RE = re.compile(r"^[a-z0-9][a-z0-9\-_]*$", re.I)
VALID_EXPERIMENT_OPTS = ('distribution',)
RANDOM_SAMPLE = .2


class Client(object):

    def __init__(self, client_id, redis_conn):
        self.redis = redis_conn
        self.client_id = client_id


class Experiment(object):

    def __init__(self, name, alternatives, redis_conn):
        if len(alternatives) < 2:
            raise ValueError('experiments require at least two alternatives')

        self.name = name
        self.redis = redis_conn
        self.random_sample = RANDOM_SAMPLE
        self.alternatives = self.initialize_alternatives(alternatives)
        self.kpi = None

        # False here is a sentinal value for "not looked up yet"
        self._winner = False
        self._traffic_dist = False
        self._sequential_ids = dict()

    def __repr__(self):
        return '<Experiment: {0})>'.format(self.name)

    def objectify_by_period(self, period):
        objectified = {
            'name': self.name,
            'period': period,
            'alternatives': [],
            'created_at': self.created_at(),
            'total_participants': self.total_participants(),
            'total_conversions': self.total_conversions(),
            'description': self.get_description(),
            'has_winner': self.winner is not None,
            'is_archived': self.is_archived(),
            'kpis': list(self.get_kpis()),
            'kpi': self.kpi
        }

        for alternative in self.alternatives:
            objectified_alt = alternative.objectify_by_period(period)
            objectified['alternatives'].append(objectified_alt)

        return objectified

    def csvify(self):
        import cStringIO as StringIO
        import csv
        csvfile = StringIO.StringIO()
        writer = csv.writer(csvfile)
        writer.writerow(['Alternative Details'])
        writer.writerow(['date', 'alternative', 'participants', 'conversions'])
        obj = self.objectify_by_period('day')
        for alt in obj['alternatives']:
            for datum in alt['data']:
                writer.writerow([datum['date'], alt['name'], datum['participants'], datum['conversions']])
        writer.writerow([])

        writer.writerow(['"{0}" Summary'.format(obj['name'])])
        writer.writerow(['total participants', 'total_conversions', 'has_winner', 'description'])
        writer.writerow([obj['total_participants'], obj['total_conversions'], obj['has_winner'], obj['description']])

        writer.writerow([])
        writer.writerow(['Alternative Summary'])

        writer.writerow(['name', 'participant_count', 'completed_count'])
        for alt in obj['alternatives']:
            writer.writerow([alt['name'], alt['participant_count'], alt['completed_count']])

        return csvfile.getvalue()

    def initialize_alternatives(self, alternatives):
        for alternative_name in alternatives:
            if not Alternative.is_valid(alternative_name):
                raise ValueError('invalid alternative name')

        return [Alternative(n, self, self.redis) for n in alternatives]

    def save(self):
        pipe = self.redis.pipeline()
        if self.is_new_record():
            pipe.sadd(_key('e'), self.name)

        pipe.hset(self.key(), 'created_at', datetime.now())
        if self.traffic_dist is not None:
            pipe.hset(self.key(), 'traffic_dist', self.traffic_dist)

        # reverse here and use lpush to keep consistent with using lrange
        for alternative in reversed(self.alternatives):
            pipe.lpush("{0}:alternatives".format(self.key()), alternative.name)

        pipe.execute()

    @property
    def control(self):
        return self.alternatives[0]

    def created_at(self):
        return self.redis.hget(self.key(), 'created_at')

    def get_alternative_names(self):
        return [alt.name for alt in self.alternatives]

    def is_new_record(self):
        return not self.redis.sismember(_key("e"), self.name)

    def total_participants(self):
        key = _key("p:{0}:_all:all".format(self.name))
        return self.redis.bitcount(key)

    def participants_by_day(self):
        return self._get_stats('participations', 'days')

    def participants_by_month(self):
        return self._get_stats('participations', 'months')

    def participants_by_year(self):
        return self._get_stats('participations', 'years')

    def total_conversions(self):
        key = _key("c:{0}:_all:users:all".format(self.kpi_key()))
        return self.redis.bitcount(key)

    def conversions_by_day(self):
        return self._get_stats('conversions', 'days')

    def conversions_by_month(self):
        return self._get_stats('conversions', 'months')

    def conversions_by_year(self):
        return self._get_stats('conversions', 'years')

    def _get_stats(self, stat_type, stat_range):
        if stat_type == 'participations':
            stat_type = 'p'
            exp_key = self.name
        elif stat_type == 'conversions':
            stat_type = 'c'
            exp_key = self.kpi_key()
        else:
            raise ValueError("Unrecognized stat type: {0}".format(stat_type))

        if stat_range not in ['days', 'months', 'years']:
            raise ValueError("Unrecognized stat range: {0}".format(stat_range))

        pipe = self.redis.pipe()

        stats = {}
        search_key = _key("{0}:{1}:{2}".format(stat_type, exp_key, stat_range))
        keys = self.redis.smembers(search_key)
        for k in keys:
            mod = '' if stat_type == 'p' else "users:"
            range_key = _key("{0}:{1}:_all:{2}{3}".format(stat_type, self.name, mod, k))
            pipe.bitcount(range_key)

        redis_results = pipe.execute()
        for idx, k in enumerate(keys):
            stats[k] = float(redis_results[idx])

        return stats

    def update_description(self, description=None):
        if description == '' or description is None:
            self.redis.hdel(self.key(), 'description')
        else:
            self.redis.hset(self.key(), 'description', description)

    def get_description(self):
        return self.redis.hget(self.key(), 'description')

    def reset(self):
        self.delete()

        name = self.name
        alts = self.get_alternative_names()

        experiment = Experiment(name, alts, self.redis)
        experiment.save()

    def delete(self):
        pipe = self.redis.pipeline()
        pipe.srem(_key('e'), self.name)
        pipe.delete(self.key())
        pipe.delete(_key(self.name))
        pipe.delete(_key('e:{0}'.format(self.name)))

        # Consider a 'non-keys' implementation of this
        keys = self.redis.keys('*:{0}:*'.format(self.name))
        for key in keys:
            pipe.delete(key)

        pipe.execute()

    def archive(self):
        self.redis.hset(self.key(), 'archived', 1)

    def unarchive(self):
        self.redis.hdel(self.key(), 'archived')

    def is_archived(self):
        return self.redis.hexists(self.key(), 'archived')

    def convert(self, client, dt=None, kpi=None):
        alternative = self.existing_alternative(client)
        if not alternative:
            raise ValueError('this client was not participaing')

        if kpi is not None:
            if not Experiment.validate_kpi(kpi):
                raise ValueError('invalid kpi name')
            self.add_kpi(kpi)

        if not self.existing_conversion(client):
            alternative.record_conversion(client, dt=dt)

        return alternative.name

    def set_kpi(self, kpi):
        self.kpi = None

        key = "{0}:kpis".format(self.key())
        if kpi not in self.redis.smembers(key):
            raise ValueError('invalid kpi')

        self.kpi = kpi

    def add_kpi(self, kpi):
        self.redis.sadd("{0}:kpis".format(self.key(include_kpi=False)), kpi)
        self.kpi = kpi

    def get_kpis(self):
        return self.redis.smembers("{0}:kpis".format(self.key(include_kpi=False)))

    @property
    def winner(self):
        if not self._winner:
            self._winner = self.redis.get(self._winner_key)
        return self._winner

    def set_winner(self, alternative_name):
        if alternative_name not in self.get_alternative_names():
            raise ValueError('this alternative is not in this experiment')
        self._winner = alternative_name
        self.redis.set(self._winner_key, alternative_name)

    def reset_winner(self):
        self._winner = None
        self.redis.delete(self._winner_key)

    @property
    def _winner_key(self):
        return "{0}:winner".format(self.key())

    @property
    def traffic_dist(self):
        if not self._traffic_dist:
            try:
                self._traffic_dist = float(self.redis.hget(self.key(), 'traffic_dist'))
            except TypeError:
                self._traffic_dist = None
        return self._traffic_dist

    def set_traffic_dist(self, dist):
        dist = int(dist)
        if not 0 < dist <= 100:
            raise ValueError('invalid distribution range')

        pct = dist / 100.0

        self._traffic_dist = pct

    def sequential_id(self, client):
        """Return the sequential id for this test for the passed in client"""
        if client.client_id not in self._sequential_ids:
            id_ = sequential_id("e:{0}:users".format(self.name), client.client_id)
            self._sequential_ids[client.client_id] = id_
        return self._sequential_ids[client.client_id]

    def get_alternative(self, client, dt=None):
        if self.is_archived():
            return self.control

        chosen_alternative = self.existing_alternative(client)
        if not chosen_alternative:
            chosen_alternative, participate = self.choose_alternative(client=client)
            if participate:
                chosen_alternative.record_participation(client, dt=dt)

        return chosen_alternative

    def exclude_client(self, client):
        key = _key("e:{0}:excluded".format(self.name))
        self.redis.setbit(key, self.sequential_id(client), 1)

    def is_client_excluded(self, client):
        key = _key("e:{0}:excluded".format(self.name))
        return self.redis.getbit(key, self.sequential_id(client))

    def existing_alternative(self, client):
        if self.is_client_excluded(client):
            return self.control

        alts = self.get_alternative_names()
        keys = [_key("p:{0}:{1}:all".format(self.name, alt)) for alt in alts]
        altkey = first_key_with_bit_set(keys=keys, args=[self.sequential_id(client)])
        if altkey:
            idx = keys.index(altkey)
            return Alternative(alts[idx], self, self.redis)

        return None

    def choose_alternative(self, client):
        rnd = round(random.uniform(1, 0.01), 2)
        if self.traffic_dist is not None and rnd >= self.traffic_dist:
            self.exclude_client(client)
            return self.control, False

        if cfg.get('enable_whiplash') and random.random() >= self.random_sample:
            return Alternative(self._whiplash(), self, self.redis), True

        return self._random_choice(), True

    def _random_choice(self):
        return random.choice(self.alternatives)

    def _whiplash(self):
        stats = {}
        for alternative in self.alternatives:
            participant_count = alternative.participant_count()
            completed_count = alternative.completed_count()
            stats[alternative.name] = self._arm_guess(participant_count, completed_count)

        return max(stats.iteritems(), key=operator.itemgetter(1))[0]

    def _arm_guess(self, participant_count, completed_count):
        fairness_score = 7

        a = max([participant_count, 0])
        b = max([participant_count - completed_count, 0])

        return random.betavariate(a + fairness_score, b + fairness_score)

    def existing_conversion(self, client):
        alts = self.get_alternative_names()
        keys = [_key("c:{0}:{1}:users:all".format(self.kpi_key(), alt)) for alt in alts]
        altkey = first_key_with_bit_set(keys=keys, args=[self.sequential_id(client)])
        if altkey:
            idx = keys.index(altkey)
            return Alternative(alts[idx], self, self.redis)

        return None

    def kpi_key(self):
        if self.kpi is not None:
            return "{0}/{1}".format(self.name, self.kpi)
        else:
            return self.name

    def key(self, include_kpi=True):
        if include_kpi:
            return _key("e:{0}".format(self.kpi_key()))
        else:
            return _key("e:{0}".format(self.name))

    @classmethod
    def find(cls, experiment_name, redis_conn):
        if not redis_conn.sismember(_key("e"), experiment_name):
            raise ValueError('experiment does not exist')

        return cls(experiment_name,
                   Experiment.load_alternatives(experiment_name, redis_conn),
                   redis_conn)

    @classmethod
    def find_or_create(cls, experiment_name, alternatives, redis_conn, opts={}):
        if len(alternatives) < 2:
            raise ValueError('experiments require at least two alternatives')

        Experiment.validate_options(opts)

        # We don't use the class method key here
        try:
            experiment = Experiment.find(experiment_name, redis_conn)
        except ValueError:
            experiment = cls(experiment_name, alternatives, redis_conn)
            # TODO: I want to revist this later
            if 'distribution' in opts:
                experiment.set_traffic_dist(opts['distribution'])
            experiment.save()

        # Make sure the alternative options are correct. If they are not,
        # raise an error.
        if sorted(experiment.get_alternative_names()) != sorted(alternatives):
            raise ValueError('experiment alternatives have changed. please delete in the admin')

        return experiment

    @staticmethod
    def all_names(redis_conn):
        return redis_conn.smembers(_key('e'))

    @staticmethod
    def all(redis_conn, exclude_archived=True):
        experiments = []
        keys = redis_conn.smembers(_key('e'))

        for key in keys:
            experiment = Experiment.find(key, redis_conn)
            if experiment.is_archived() and exclude_archived:
                continue
            experiments.append(experiment)
        return experiments

    @staticmethod
    def archived(redis_conn):
        experiments = Experiment.all(redis_conn, False)
        return [exp for exp in experiments if exp.is_archived()]

    @staticmethod
    def load_alternatives(experiment_name, redis_conn):
        key = _key("e:{0}:alternatives".format(experiment_name))
        return redis_conn.lrange(key, 0, -1)

    @staticmethod
    def is_valid(experiment_name):
        return (isinstance(experiment_name, basestring) and
                VALID_EXPERIMENT_ALTERNATIVE_RE.match(experiment_name) is not None)

    @staticmethod
    def validate_options(opts):
        for opt, val in opts.iteritems():
            if opt not in VALID_EXPERIMENT_OPTS:
                raise ValueError('invalid option')

    @staticmethod
    def validate_kpi(kpi):
        return (isinstance(kpi, basestring) and
                VALID_KPI_RE.match(kpi) is not None)


class Alternative(object):

    def __init__(self, name, experiment, redis_conn):
        self.name = name
        self.experiment = experiment
        self.redis = redis_conn

    def __repr__(self):
        return "<Alternative {0} (Experiment {1})".format(self.name, self.experiment.name)

    def objectify_by_period(self, period):
        PERIOD_TO_METHOD_MAP = {
            'day': {
                'participants': self.participants_by_day,
                'conversions': self.conversions_by_day
            },
            'month': {
                'participants': self.participants_by_month,
                'conversions': self.conversions_by_month
            },
            'year': {
                'participants': self.participants_by_year,
                'conversions': self.conversions_by_year
            },
        }

        data = []
        conversion_fn = PERIOD_TO_METHOD_MAP[period]['conversions']
        participants_fn = PERIOD_TO_METHOD_MAP[period]['participants']

        conversions = conversion_fn()
        participants = participants_fn()

        dates = sorted(list(set(conversions.keys() + participants.keys())))
        for date in dates:
            _data = {
                'conversions': conversions.get(date, 0),
                'participants': participants.get(date, 0),
                'date': date
            }
            data.append(_data)

        objectified = {
            'name': self.name,
            'data': data,
            'conversion_rate': float('%.2f' % (self.conversion_rate() * 100)),
            'is_control': self.is_control(),
            'is_winner': self.is_winner(),
            'test_statistic': self.g_stat(),
            'participant_count': self.participant_count(),
            'completed_count': self.completed_count(),
            'confidence_level': self.confidence_level(),
            'confidence_interval': self.confidence_interval()
        }

        return objectified

    def is_control(self):
        return self.experiment.control.name == self.name

    def is_winner(self):
        return self.experiment.winner == self.name

    def participant_count(self):
        key = _key("p:{0}:{1}:all".format(self.experiment.name, self.name))
        return self.redis.bitcount(key)

    def participants_by_day(self):
        return self._get_stats('participations', 'days')

    def participants_by_month(self):
        return self._get_stats('participations', 'months')

    def participants_by_year(self):
        return self._get_stats('participations', 'years')

    def completed_count(self):
        key = _key("c:{0}:{1}:users:all".format(self.experiment.kpi_key(), self.name))
        return self.redis.bitcount(key)

    def conversions_by_day(self):
        return self._get_stats('conversions', 'days')

    def conversions_by_month(self):
        return self._get_stats('conversions', 'months')

    def conversions_by_year(self):
        return self._get_stats('conversions', 'years')

    def _get_stats(self, stat_type, stat_range):
        if stat_type == 'participations':
            stat_type = 'p'
            exp_key = self.experiment.name
        elif stat_type == 'conversions':
            stat_type = 'c'
            exp_key = self.experiment.kpi_key()
        else:
            raise ValueError("Unrecognized stat type: {0}".format(stat_type))

        if stat_range not in ['days', 'months', 'years']:
            raise ValueError("Unrecognized stat range: {0}".format(stat_range))

        stats = {}

        pipe = self.redis.pipeline()

        search_key = _key("{0}:{1}:{2}".format(stat_type, exp_key, stat_range))
        keys = self.redis.smembers(search_key)

        for k in keys:
            name = self.name if stat_type == 'p' else "{0}:users".format(self.name)
            range_key = _key("{0}:{1}:{2}:{3}".format(stat_type, exp_key, name, k))
            pipe.bitcount(range_key)

        redis_results = pipe.execute()
        for idx, k in enumerate(keys):
            stats[k] = float(redis_results[idx])

        return stats

    def record_participation(self, client, dt=None):
        """Record a user's participation in a test along with a given variation"""
        if dt is None:
            date = datetime.now()
        else:
            date = dt

        experiment_key = self.experiment.name

        pipe = self.redis.pipeline()

        pipe.sadd(_key("p:{0}:years".format(experiment_key)), date.strftime('%Y'))
        pipe.sadd(_key("p:{0}:months".format(experiment_key)), date.strftime('%Y-%m'))
        pipe.sadd(_key("p:{0}:days".format(experiment_key)), date.strftime('%Y-%m-%d'))

        pipe.execute()

        keys = [
            _key("p:{0}:_all:all".format(experiment_key)),
            _key("p:{0}:_all:{1}".format(experiment_key, date.strftime('%Y'))),
            _key("p:{0}:_all:{1}".format(experiment_key, date.strftime('%Y-%m'))),
            _key("p:{0}:_all:{1}".format(experiment_key, date.strftime('%Y-%m-%d'))),
            _key("p:{0}:{1}:all".format(experiment_key, self.name)),
            _key("p:{0}:{1}:{2}".format(experiment_key, self.name, date.strftime('%Y'))),
            _key("p:{0}:{1}:{2}".format(experiment_key, self.name, date.strftime('%Y-%m'))),
            _key("p:{0}:{1}:{2}".format(experiment_key, self.name, date.strftime('%Y-%m-%d'))),
        ]
        msetbit(keys=keys, args=([self.experiment.sequential_id(client), 1] * len(keys)))

    def record_conversion(self, client, dt=None):
        """Record a user's conversion in a test along with a given variation"""
        if dt is None:
            date = datetime.now()
        else:
            date = dt

        experiment_key = self.experiment.kpi_key()

        pipe = self.redis.pipeline()

        pipe.sadd(_key("c:{0}:years".format(experiment_key)), date.strftime('%Y'))
        pipe.sadd(_key("c:{0}:months".format(experiment_key)), date.strftime('%Y-%m'))
        pipe.sadd(_key("c:{0}:days".format(experiment_key)), date.strftime('%Y-%m-%d'))

        pipe.execute()

        keys = [
            _key("c:{0}:_all:users:all".format(experiment_key)),
            _key("c:{0}:_all:users:{1}".format(experiment_key, date.strftime('%Y'))),
            _key("c:{0}:_all:users:{1}".format(experiment_key, date.strftime('%Y-%m'))),
            _key("c:{0}:_all:users:{1}".format(experiment_key, date.strftime('%Y-%m-%d'))),
            _key("c:{0}:{1}:users:all".format(experiment_key, self.name)),
            _key("c:{0}:{1}:users:{2}".format(experiment_key, self.name, date.strftime('%Y'))),
            _key("c:{0}:{1}:users:{2}".format(experiment_key, self.name, date.strftime('%Y-%m'))),
            _key("c:{0}:{1}:users:{2}".format(experiment_key, self.name, date.strftime('%Y-%m-%d'))),
        ]
        msetbit(keys=keys, args=([self.experiment.sequential_id(client), 1] * len(keys)))

    def conversion_rate(self):
        try:
            return self.completed_count() / float(self.participant_count())
        except ZeroDivisionError:
            return 0

    def g_stat(self):
        # http://en.wikipedia.org/wiki/G-test

        if self.is_control():
            return 'N/A'

        control = self.experiment.control

        alt_conversions = self.completed_count()
        control_conversions = control.completed_count()
        alt_failures = self.participant_count() - alt_conversions
        control_failures = control.participant_count() - control_conversions

        total_conversions = alt_conversions + control_conversions

        if total_conversions < 20:
            # small sample size of conversions, see where it goes for a bit
            return 'N/A'

        total_participants = self.participant_count() + control.participant_count()

        expected_control_conversions = control.participant_count() * total_conversions / float(total_participants)
        expected_alt_conversions = self.participant_count() * total_conversions / float(total_participants)
        expected_control_failures = control.participant_count() - expected_control_conversions
        expected_alt_failures = self.participant_count() - expected_alt_conversions

        try:
            g_stat = 2 * (      alt_conversions * log(alt_conversions / expected_alt_conversions) \
                        +   alt_failures * log(alt_failures / expected_alt_failures) \
                        +   control_conversions * log(control_conversions / expected_control_conversions) \
                        +   control_failures * log(control_failures / expected_control_failures))

        except ZeroDivisionError:
            return 0

        return round(g_stat, 2)

    def z_score(self):
        if self.is_control():
            return 'N/A'

        control = self.experiment.control
        ctr_e = self.conversion_rate()
        ctr_c = control.conversion_rate()

        e = self.participant_count()
        c = control.participant_count()

        try:
            std_dev = pow(((ctr_e / pow(ctr_c, 3)) * ((e * ctr_e) + (c * ctr_c) - (ctr_c * ctr_e) * (c + e)) / (c * e)), 0.5)
            z_score = ((ctr_e / ctr_c) - 1) / std_dev
            return z_score
        except ZeroDivisionError:
            return 0

    def g_confidence_level(self):
        # g stat is approximated by chi-square, we will use
        # critical values from chi-square distribution with one degree of freedom

        g_stat = self.g_stat()
        if g_stat == 'N/A':
            return g_stat

        ret = ''
        if g_stat == 0.0:
            ret = 'No Change'
        elif g_stat < 3.841:
            ret = 'No Confidence'
        elif g_stat < 6.635:
            ret = '95% Confidence'
        elif g_stat < 10.83:
            ret = '99% Confidence'
        else:
            ret = '99.9% Confidence'

        return ret

    def z_confidence_level(self):
        z_score = self.z_score()
        if z_score == 'N/A':
            return z_score

        z_score = abs(round(z_score, 3))

        ret = ''
        if z_score == 0.0:
            ret = 'No Change'
        elif z_score < 1.96:
            ret = 'No Confidence'
        elif z_score < 2.57:
            ret = '95% Confidence'
        elif z_score < 3.27:
            ret = '99% Confidence'
        else:
            ret = '99.9% Confidence'

        return ret

    def confidence_level(self, conf_type="g"):
        if conf_type == "z":
            return self.z_confidence_level()
        else:
            return self.g_confidence_level()

    def confidence_interval(self):
        try:
            # 80% confidence
            p = self.conversion_rate()
            return pow(p * (1 - p) / self.participant_count(), 0.5) * 1.28 * 100
        except ZeroDivisionError:
            return 0

    def key(self):
        return _key("{0}:{1}".format(self.experiment.name, self.name))

    @staticmethod
    def is_valid(alternative_name):
        return (isinstance(alternative_name, basestring) and
                VALID_EXPERIMENT_ALTERNATIVE_RE.match(alternative_name) is not None)
