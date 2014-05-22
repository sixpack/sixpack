import cStringIO as StringIO
import csv


class ExportExperiment(object):

    def __init__(self, experiment=None):
        self.experiment = experiment

    def __call__(self):
        csvfile = StringIO.StringIO()
        writer = csv.writer(csvfile)
        writer.writerow(['Alternative Details'])
        writer.writerow(['date', 'alternative', 'participants', 'conversions'])
        obj = self.experiment.objectify_by_period('day')
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
