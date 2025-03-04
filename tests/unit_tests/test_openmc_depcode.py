"""Test OpenMCDepcode functions"""
import pytest

import numpy as np
from pathlib import Path

import openmc


def test_read_depcode_metadata(openmc_depcode):
    old_output_path = openmc_depcode.output_path
    openmc_depcode.output_path = Path(__file__).parents[1] / 'openmc_data/saltproc_runtime_ref'
    openmc_depcode.read_depcode_metadata()
    assert openmc_depcode.depcode_metadata['depcode_name'] == 'openmc'
    assert openmc_depcode.depcode_metadata['depcode_version'] == '0.13.3'
    assert openmc_depcode.depcode_metadata['title'] == ''
    assert openmc_depcode.depcode_metadata['depcode_input_filename'] == ''
    assert openmc_depcode.depcode_metadata['depcode_working_dir'] == \
       str((Path(__file__).parents[1] / 'openmc_data/saltproc_runtime_ref').resolve())


def test_read_step_metadata(openmc_depcode):
    old_output_path = openmc_depcode.output_path
    openmc_depcode.output_path = Path(__file__).parents[1] / 'openmc_data/saltproc_runtime_ref'
    openmc_depcode.read_step_metadata()
    assert openmc_depcode.step_metadata['MPI_tasks'] == -1
    assert openmc_depcode.step_metadata['OMP_threads'] == -1
    assert openmc_depcode.step_metadata['memory_optimization_mode'] == -1
    assert openmc_depcode.step_metadata['depletion_timestep_size'] == 259200.0
    assert openmc_depcode.step_metadata['step_memory_usage'] == -1
    np.testing.assert_almost_equal(openmc_depcode.step_metadata['step_execution_time'], 423.90163846)


def test_check_for_material_names(cwd, openmc_depcode):
   matfile = openmc_depcode.template_input_file_path['materials']
   nameless_matfile = str(cwd / 'openmc_data' / 'msbr_materials_nameless.xml')
   # should pass
   openmc_depcode._check_for_material_names(matfile)

   with pytest.raises(ValueError, match="Material 1 has no name."):
       openmc_depcode._check_for_material_names(nameless_matfile)


def test_create_mass_percents_dictionary(cwd, openmc_depcode):
    wo_matfile = str(cwd / 'openmc_data' / 'msbr_materials_wo.xml')
    ao_matfile = str(cwd / 'openmc_data' / 'msbr_materials_ao.xml')


    wo_materials = openmc.Materials.from_xml(wo_matfile)
    ao_materials = openmc.Materials.from_xml(ao_matfile)

    for idx, ao_material in enumerate(ao_materials):
        wo_test_dictionary_1 = openmc_depcode._create_mass_percents_dictionary(ao_material)

        wo_material = wo_materials[idx]
        wo_test_dictionary_2 = openmc_depcode._create_mass_percents_dictionary(wo_material, percent_type='wo')
        mass_percents = []
        nucs = []
        for nuc, pt, tp in wo_material.nuclides:
            nucs.append(nuc)
            mass_percents.append(pt)
        wo_ref_dictionary = dict(zip(nucs, mass_percents))

        for key in wo_ref_dictionary.keys():
            np.testing.assert_almost_equal(wo_ref_dictionary[key], wo_test_dictionary_1[key], decimal=5)
            np.testing.assert_almost_equal(wo_ref_dictionary[key], wo_test_dictionary_2[key], decimal=5)


def test_name_to_nuclide_code(openmc_depcode):
    assert openmc_depcode.name_to_nuclide_code('H1') == 1001
    assert openmc_depcode.name_to_nuclide_code('U238') == 92238
    assert openmc_depcode.name_to_nuclide_code('Ag110_m1') == 47510
    assert openmc_depcode.name_to_nuclide_code('Am242') == 95242
    assert openmc_depcode.name_to_nuclide_code('Am242_m1') == 95642
