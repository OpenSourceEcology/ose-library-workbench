"""Require explicit results: FreeCAD can exit zero after a Python exception."""
import json
from pathlib import Path
import sys


def main(path):
    report = json.loads(Path(path).read_text())
    assert report['passed'] is True
    expected = {'extwall_standard', 'axis_idler_spacer', 'axis_carriage',
                'axis_idler_side', 'axis_2007_carriage', 'axis_2007_idler',
                'axis_2007_top_holder', 'power_cube_1708', 'ceb_drawer_guide'}
    assert {entry['id'] for entry in report['entries']} == expected
    assert len(report['entries']) == len(expected)
    for entry in report['entries']:
        failures = ['output:overlap'] if entry['id'] in {'power_cube_1708', 'ceb_drawer_guide'} else []
        assert entry['objects'] > 0 and entry['failed_checks'] == failures
    for check in ['replacement_no_duplicates', 'unrelated_geometry_preserved',
                  'failed_replacement_rolled_back', 'wrong_document_rejected',
                  'edited_geometry_checked_against_expectations',
                  'saved_document_binding_restored']:
        assert report[check] is True, check
    print('Verified FreeCAD workbench integration report')


if __name__ == '__main__':
    main(sys.argv[1])
