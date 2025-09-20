import csv
import os
from django.core.management.base import BaseCommand
from tonguetwister.models import Twister, OldPolish


class Command(BaseCommand):
    help = 'Import data from CSV files into the MySQL database'

    def handle(self, *args, **kwargs):
        # Define file paths for CSV files containing data to import
        files = {
            'twister': '/home/lingwolamki/django-tonguetwister/twister_data.csv',
            'old_polish': '/home/lingwolamki/django-tonguetwister/oldpolish_data.csv'
        }

        # Loop over each file path and model to import data
        for label, file_path in files.items():
            # Check if the file exists; if not, log an error and skip
            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
                continue

            # Select the model to use based on the file label
            model = Twister if label == 'twister' else OldPolish

            # Prepare a list to hold records for bulk creation
            records = []
            try:
                with open(file_path, mode='r') as file:
                    reader = csv.DictReader(file)  # Read CSV data as dictionaries
                    for row in reader:
                        # Define unique field(s) to identify duplicate records
                        unique_fields = {'id': row.get('id')}  # Check if 'id' exists

                        # Skip the row if a record with the same 'id' already exists
                        if not model.objects.filter(**unique_fields).exists():
                            # Append a new model instance to 'records' if it’s unique
                            records.append(model(**row))
                        else:
                            # Log a warning if a duplicate record is found and skipped
                            self.stdout.write(self.style.WARNING(f"Skipping duplicate record: {row}"))

                # Insert all unique records in bulk if there are any
                if records:
                    model.objects.bulk_create(records)
                    self.stdout.write(self.style.SUCCESS(f"{label.capitalize()} data imported successfully!"))
                else:
                    # If no new records were added, display a warning
                    self.stdout.write(self.style.WARNING(f"No new records to import for {label}."))
            except Exception as e:
                # Log any errors encountered during the import process
                self.stdout.write(self.style.ERROR(f"Error importing {label}: {e}"))
