"""
Management command to import stock history from Excel files.

Usage:
    python manage.py import_stock --file=path/to/file.xlsx --branch=magtik --schema=velton

Strategy:
    - Each sheet = one Material with its InventoryUnits
    - Row 1 = material metadata (brand, grammage, width)
    - Row 2 = column headers
    - Row 3+ = inventory unit records
    - Last sheet (INFORME TOTAL) = skip
"""

import openpyxl
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context
from inventory.models import Material, InventoryUnit
from tenants.models import Branch


def safe_decimal(value, default=Decimal('0')):
    """Convert a value to Decimal safely, ignoring formulas and None."""
    if value is None:
        return default
    str_val = str(value).strip()
    if str_val.startswith('=') or str_val == '' or str_val == 'None':
        return default
    try:
        return Decimal(str_val.replace(',', '.'))
    except InvalidOperation:
        return default


def safe_str(value, default=''):
    """Convert a value to string safely."""
    if value is None:
        return default
    return str(value).strip()


def parse_unit_number(value):
    """Normalize unit numbers — handles cases like '1y2', 1.0, etc."""
    if value is None:
        return None
    str_val = str(value).strip()
    if str_val.startswith('=') or str_val == '' or str_val == 'None':
        return None
    # Remove trailing .0 from floats read as strings
    if str_val.endswith('.0'):
        str_val = str_val[:-2]
    return str_val


def extract_material_meta(sheet):
    """
    Extract material metadata from row 1 of the sheet.
    Returns a dict with name, brand, grammage, width, material_type.
    """
    row1 = [cell.value for cell in sheet[1]]
    name = sheet.title.strip()

    # Detect material type from sheet name
    name_upper = name.upper()
    if 'BANDA' in name_upper or any(x in name_upper for x in ['5LO', '6,35', '3,15', '12,7', 'HIC', 'LOC']):
        material_type = 'MAG_STRIPE'
    elif 'SINTETICO' in name_upper:
        material_type = 'PAPEL_SEMI'
    elif 'TYVEK' in name_upper:
        material_type = 'OTHER'
    elif 'TRIPLEX' in name_upper or 'TRITHERM' in name_upper:
        material_type = 'OTHER'
    else:
        material_type = 'PAPER'

    # Extract grammage from row 1 values
    grammage = None
    width = None
    brand = ''
    for val in row1:
        if val is None:
            continue
        s = str(val).strip().upper()
        if 'GRS' in s or 'GR' in s:
            try:
                grammage = int(''.join(filter(str.isdigit, s.split('GR')[0])))
            except (ValueError, IndexError):
                pass
        if 'MM' in s:
            try:
                width = Decimal(s.replace('MM', '').replace(' ', '').replace(',', '.'))
            except InvalidOperation:
                pass
    # Brand is usually the first non-None value in row 1
    for val in row1:
        if val and not str(val).startswith('='):
            brand = safe_str(val)
            break

    return {
        'name': name,
        'brand': brand,
        'grammage': grammage,
        'width': width,
        'material_type': material_type,
    }


class Command(BaseCommand):
    help = 'Import stock history from an Excel file into PrintFlow inventory'

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True, help='Path to the Excel file')
        parser.add_argument('--branch', required=True, help='Branch name (e.g. magtik)')
        parser.add_argument('--schema', required=True, help='Tenant schema name (e.g. velton)')
        parser.add_argument('--dry-run', action='store_true', help='Simulate import without saving')

    def handle(self, *args, **options):
        file_path = options['file']
        branch_name = options['branch']
        schema_name = options['schema']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('--- DRY RUN MODE — nothing will be saved ---'))

        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
        except FileNotFoundError:
            raise CommandError(f'File not found: {file_path}')

        with schema_context(schema_name):
            # Get branch
            try:
                branch = Branch.objects.get(name__iexact=branch_name)
            except Branch.DoesNotExist:
                raise CommandError(f'Branch "{branch_name}" not found in schema "{schema_name}"')

            total_materials = 0
            total_units = 0
            total_skipped = 0
            errors = []

            for sheet_name in wb.sheetnames:
                # Skip summary sheet
                if 'INFORME' in sheet_name.upper() or 'TOTAL' in sheet_name.upper():
                    self.stdout.write(f'  ⏭  Skipping summary sheet: {sheet_name}')
                    continue

                sheet = wb[sheet_name]
                meta = extract_material_meta(sheet)

                self.stdout.write(f'\n📦  Processing: {sheet_name}')

                if not dry_run:
                    material, created = Material.objects.get_or_create(
                        name=meta['name'],
                        defaults={
                            'brand': meta['brand'],
                            'grammage': meta['grammage'],
                            'width': meta['width'],
                            'material_type': meta['material_type'],
                        }
                    )
                    if created:
                        self.stdout.write(f'  ✅ Material created: {material.name}')
                    else:
                        self.stdout.write(f'  ♻️  Material exists: {material.name}')
                else:
                    material = None

                total_materials += 1
                sheet_units = 0
                sheet_skipped = 0

                # Data starts at row 3 (row 1 = meta, row 2 = headers)
                for row in sheet.iter_rows(min_row=3, values_only=True):
                    # Skip empty rows
                    if not any(row):
                        continue

                    unit_number = parse_unit_number(row[1])
                    if not unit_number:
                        sheet_skipped += 1
                        continue

                    initial_qty = safe_decimal(row[2])
                    width_override = safe_decimal(row[3]) if row[3] else None

                    # Determine status based on fecha_uso
                    fecha_uso = row[4]
                    status = 'EXHAUSTED' if fecha_uso else 'AVAILABLE'

                    if not dry_run and material:
                        try:
                            InventoryUnit.objects.get_or_create(
                                material=material,
                                unit_number=unit_number,
                                branch=branch,
                                defaults={
                                    'initial_quantity': initial_qty,
                                    'current_quantity': initial_qty if status == 'AVAILABLE' else Decimal('0'),
                                    'status': status,
                                    'width_override': width_override if width_override else None,
                                    'purchase_order_id': None,
                                }
                            )
                            sheet_units += 1
                        except Exception as e:
                            errors.append(f'{sheet_name} / unit {unit_number}: {e}')
                            sheet_skipped += 1
                    else:
                        sheet_units += 1

                self.stdout.write(f'  → Units imported: {sheet_units} | Skipped: {sheet_skipped}')
                total_units += sheet_units
                total_skipped += sheet_skipped

            self.stdout.write('\n' + '─' * 50)
            self.stdout.write(self.style.SUCCESS(
                f'✅ Import complete — '
                f'Materials: {total_materials} | '
                f'Units: {total_units} | '
                f'Skipped: {total_skipped}'
            ))

            if errors:
                self.stdout.write(self.style.WARNING(f'\n⚠️  {len(errors)} errors:'))
                for err in errors:
                    self.stdout.write(f'   - {err}')
