import os
import sys


from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from hits.models import HitTemplate
from unicodecsv import DictWriter


def results_data(completed_hits):
    """
    All completed HITs must come from the same template so that they have the
    same field names.
    """
    fieldnames = sorted(
        set([u'Input.' + k for ch in completed_hits for k in ch.input_csv_fields.keys()])
        | set([u'Answer.' + k for ch in completed_hits for k in ch.answers.keys()])
    )

    rows = []
    for hit in completed_hits:
        row = {}
        row.update({u'Input.' + k: v for k, v in hit.input_csv_fields.items()})
        row.update({u'Answer.' + k: v for k, v in hit.answers.items()})
        rows.append(row)

    return fieldnames, rows


class Command(BaseCommand):

    args = '<template_file_path> <results_csv_file_path>'
    help = (
        'Dumps results of the completed HITs for the template '
        '<template_file_path> '
        'to a file at <results_csv_file_path>'
    )

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError(
                'usage: python manage.py dump_results '
                '<template_file_path> '
                '<results_csv_file_path>'
            )

        # Get paths from args, and normalize them to absolute paths:
        template_file_path, results_csv_file_path = map(os.path.abspath, args)

        try:
            template = HitTemplate.objects.get(name=template_file_path)
        except ObjectDoesNotExist:
            sys.exit('There is no matching <template_file_path>.')

        completed_hits = template.hit_set.filter(completed=True)
        if not completed_hits.exists():
            sys.exit('There are no completed HITs.')

        fieldnames, rows = results_data(completed_hits)
        with open(results_csv_file_path, 'wb') as fh:
            writer = DictWriter(csvfile = fh, fieldnames = fieldnames, restval = '')
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
