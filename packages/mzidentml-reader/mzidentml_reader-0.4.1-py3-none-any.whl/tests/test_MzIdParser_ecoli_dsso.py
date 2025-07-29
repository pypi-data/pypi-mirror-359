"""
ToDo: add test that writes multiple mzids into the db and check that results are written in
    properly.
"""
import numpy as np
from numpy.testing import assert_array_equal
from sqlalchemy import Table
import os
import logging
from sqlalchemy import text
from pyteomics import mgf
from .db_pytest_fixtures import *
from .parse_mzid import parse_mzid_into_postgresql, parse_mzid_into_sqlite_xispec
import struct

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def fixture_path(file):
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, "fixtures", file)


def compare_db_sequence(results):
    assert len(results) == 12
    assert results[0].id == "dbseq_P0C0V0_target"  # id from mzid
    assert results[0].accession == "P0C0V0"  # accession from mzid
    assert results[0].name == (  # name from mzid
        "DEGP_ECOLI Periplasmic serine endoprotease DegP OS=Escherichia coli (strain K12) "
        "OX=83333 GN=degP PE=1 SV=1")
    assert results[0].description == (  # protein description cvParam
        "DEGP_ECOLI Periplasmic serine endoprotease DegP OS=Escherichia coli (strain K12) "
        "OX=83333 GN=degP PE=1 SV=1"
    )
    assert results[0].sequence == (  # <Seq> value from mzid
        "MKKTTLALSALALSLGLALSPLSATAAETSSATTAQQMPSLAPMLEKVMPSVVSINVEGSTTVNTPRMPRNFQQFFGDDSPFCQEG"
        "SPFQSSPFCQGGQGGNGGGQQQKFMALGSGVIIDADKGYVVTNNHVVDNATVIKVQLSDGRKFDAKMVGKDPRSDIALIQIQNPKN"
        "LTAIKMADSDALRVGDYTVAIGNPFGLGETVTSGIVSALGRSGLNAENYENFIQTDAAINRGNSGGALVNLNGELIGINTAILAPD"
        "GGNIGIGFAIPSNMVKNLTSQMVEYGQVKRGELGIMGTELNSELAKAMKVDAQRGAFVSQVLPNSSAAKAGIKAGDVITSLNGKPI"
        "SSFAALRAQVGTMPVGSKLTLGLLRDGKQVNVNLELQQSSQNQVDSSSIFNGIEGAEMSNKGKDQGVVVNNVKTGTPAAQIGLKKG"
        "DVIIGANQQAVKNIAELRKVLDSKPSVLALNIQRGDSTIYLLMQ")
    # ToDo: check more rows?


def compare_peptide_evidence(results):
    assert len(results) == 38
    assert results[0].peptide_id == 0  # id from incrementing count
    #assert results[0].peptide_ref == '29_KVLDSKPSVLALNIQR_30_KFDAKMVGK_1_5_p1'
    assert results[0].dbsequence_id == 'dbseq_P0C0V0_target'
    assert results[0].pep_start == 148  # start from <PeptideEvidence>
    assert not results[0].is_decoy  # is_decoy from <PeptideEvidence>

    assert results[1].peptide_id == 1  # id from incrementing count
    # assert results[0].peptide_ref == '29_KVLDSKPSVLALNIQR_30_KFDAKMVGK_1_5_p1'
    assert results[1].dbsequence_id == 'dbseq_P0C0V0_target'
    assert results[1].pep_start == 449  # start from <PeptideEvidence>
    assert not results[1].is_decoy  # is_decoy from <PeptideEvidence>

    assert results[36].peptide_id == 36  # id from incrementing count
    # assert results[0].peptide_ref == '29_KVLDSKPSVLALNIQR_30_KFDAKMVGK_1_5_p1'
    assert results[36].dbsequence_id == 'dbseq_P0AGE9_target'
    assert results[36].pep_start == 263  # start from <PeptideEvidence>
    assert not results[36].is_decoy  # is_decoy from <PeptideEvidence>

    assert results[37].peptide_id == 37  # id from incrementing count
    # assert results[0].peptide_ref == '29_KVLDSKPSVLALNIQR_30_KFDAKMVGK_1_5_p1'
    assert results[37].dbsequence_id == 'dbseq_P0AGE9_target'
    assert results[37].pep_start == 224  # start from <PeptideEvidence>
    assert not results[37].is_decoy  # is_decoy from <PeptideEvidence>


def compare_modified_peptide(results):
    assert len(results) == 38

    # id from <Peptide> id
    assert results[0].id == 0 #  '29_KVLDSKPSVLALNIQR_30_KFDAKMVGK_1_5_p1'
    assert results[0].base_sequence == 'KFDAKMVGK'  # value of <PeptideSequence>
    assert results[0].mod_accessions == []
    assert results[0].mod_positions == []
    # location of <Modification> with cross-link acceptor/receiver cvParam
    assert results[0].link_site1 == 5
    # monoisotopicMassDelta of <Modification> with cross-link acceptor/receiver cvParam
    assert results[0].crosslinker_modmass == 0
    # value of cross-link acceptor/receiver cvParam
    assert results[0].crosslinker_pair_id == '1.0'

    # id from <Peptide> id
    assert results[1].id == 1 #  '29_KVLDSKPSVLALNIQR_30_KFDAKMVGK_1_5_p0'
    assert results[1].base_sequence == 'KVLDSKPSVLALNIQR'  # value of <PeptideSequence>
    assert results[1].mod_accessions == []
    assert results[1].mod_positions == []
    # location of <Modification> with cross-link acceptor/receiver cvParam
    assert results[1].link_site1 == 1
    # monoisotopicMassDelta of <Modification> with cross-link acceptor/receiver cvParam
    assert results[1].crosslinker_modmass == pytest.approx(158.0037644600003, abs=1e-12)
    # value of cross-link acceptor/receiver cvParam
    assert results[1].crosslinker_pair_id == '1.0'

    # id from <Peptide> id
    assert results[2].id == 2 #  '19_LLAEHNLDmetASAIKGTGVGGR_20_HLAKAPAK_13_4_p1'
    assert results[2].base_sequence == 'HLAKAPAK'  # value of <PeptideSequence>
    assert results[2].mod_accessions == []
    assert results[2].mod_positions == []
    # location of <Modification> with cross-link acceptor/receiver cvParam
    assert results[2].link_site1 == 4
    # monoisotopicMassDelta of <Modification> with cross-link acceptor/receiver cvParam
    assert results[2].crosslinker_modmass == 0
    # value of cross-link acceptor/receiver cvParam
    assert results[2].crosslinker_pair_id == '2.0'

    # id from <Peptide> id
    assert results[3].id == 3 #  '19_LLAEHNLDmetASAIKGTGVGGR_20_HLAKAPAK_13_4_p0'
    assert results[3].base_sequence == 'LLAEHNLDASAIKGTGVGGR'  # value of <PeptideSequence>
    assert results[3].mod_accessions == [{'UNIMOD:34': 'Methyl'}]
    assert results[3].mod_positions == [8]
    # location of <Modification> with cross-link acceptor/receiver cvParam
    assert results[3].link_site1 == 13
    # monoisotopicMassDelta of <Modification> with cross-link acceptor/receiver cvParam
    assert results[3].crosslinker_modmass == pytest.approx(158.0037644600003, abs=1e-12)
    # value of cross-link acceptor/receiver cvParam
    assert results[3].crosslinker_pair_id == '2.0'


def compare_modification(results):
    assert len(results) == 14

    assert results[0].id == 0  # id from incrementing count
    assert results[0].mod_name == '(158.00)'  # name from <SearchModification> cvParam / mod mass in brackets if unknown
    assert results[0].mass == 158.00377  # massDelta from <SearchModification>
    assert results[0].residues == 'STYK'  # residues from <SearchModification>
    assert results[0].specificity_rules == []  # parsed from child <SpecificityRules>
    assert not results[0].fixed_mod  # fixedMod from <SearchModification>
    assert results[0].accession == 'MS:1001460'  # accession from <SearchModification> cvParam
    assert results[0].crosslinker_id == '0.0'  # value from cl donor / acceptor cv term (is a string)

    assert results[1].id == 1  # id from incrementing count
    assert results[1].mod_name == 'crosslink acceptor'  # name from <SearchModification> cvParam
    assert results[1].mass == 0  # massDelta from <SearchModification>
    assert results[1].residues == 'STYK'  # residues from <SearchModification>
    assert results[1].specificity_rules == []  # parsed from child <SpecificityRules>
    assert results[1].fixed_mod  # fixedMod from <SearchModification> (is mistake in xml file)
    assert results[1].accession == 'MS:1002510'  # accession from <SearchModification> cvParam
    assert results[1].crosslinker_id == '0.0'  # value from cl donor  / acceptor cv term (is a string)

    assert results[2].id == 2  # id from incrementing count
    assert results[2].mod_name == '(158.00)'  # name from <SearchModification> cvParam / mod mass in brackets if unknown
    assert results[2].mass == 158.00377  # massDelta from <SearchModification>
    assert results[2].residues == '.'  # residues from <SearchModification>
    assert results[2].specificity_rules == ["MS:1002057"]  # parsed from child <SpecificityRules>
    assert results[2].fixed_mod  # fixedMod from <SearchModification>
    assert results[2].accession == 'MS:1001460'  # accession from <SearchModification> cvParam
    assert results[2].crosslinker_id == '0.0'  # value from cl donor  / acceptor cv term (is a string)

    assert results[3].id == 3  # id from incrementing count
    assert results[3].mod_name == 'crosslink acceptor'  # name from <SearchModification> cvParam
    assert results[3].mass == 158.00377  # massDelta from <SearchModification> (mistake in xml?)
    assert results[3].residues == '.'  # residues from <SearchModification>
    assert results[3].specificity_rules == ["MS:1002057"]  # parsed from child <SpecificityRules>
    assert results[3].fixed_mod  # fixedMod from <SearchModification>
    assert results[3].accession == 'MS:1002510'  # accession from <SearchModification> cvParam
    assert results[3].crosslinker_id == '0.0'  # value from cl donor  / acceptor cv term (is a string)

    assert results[4].id == 4  # id from incrementing count
    assert results[4].mod_name == '(0.00)'  # name from <SearchModification> cvParam / mod mass in brackets if unknown
    assert results[4].mass == 0  # massDelta from <SearchModification>
    assert results[4].residues == '.'  # residues from <SearchModification>
    assert results[4].specificity_rules == []  # parsed from child <SpecificityRules>
    assert not results[4].fixed_mod  # fixedMod from <SearchModification>
    assert results[4].accession == 'MS:1001460'  # accession from <SearchModification> cvParam
    assert results[4].crosslinker_id == '1.0'  # value from cl donor  / acceptor cv term (is a string)

    assert results[5].id == 5  # id from incrementing count
    assert results[5].mod_name == 'crosslink acceptor'  # name from <SearchModification> cvParam
    assert results[5].mass == 0  # massDelta from <SearchModification>
    assert results[5].residues == '.'  # residues from <SearchModification>
    assert results[5].specificity_rules == []  # parsed from child <SpecificityRules>
    assert results[5].fixed_mod  # fixedMod from <SearchModification>
    assert results[5].accession == 'MS:1002510'  # accession from <SearchModification> cvParam
    assert results[5].crosslinker_id == '1.0'  # value from cl donor  / acceptor cv term (is a string)

    assert results[6].id == 6  # id from incrementing count
    assert results[6].mod_name == 'Oxidation'  # name from <SearchModification> cvParam
    assert results[6].mass == 15.99491  # massDelta from <SearchModification>
    assert results[6].residues == 'M'  # residues from <SearchModification>
    assert results[6].specificity_rules == []  # parsed from child <SpecificityRules>
    assert not results[6].fixed_mod  # fixedMod from <SearchModification>
    assert results[6].accession == 'UNIMOD:35'  # accession from <SearchModification> cvParam
    assert results[6].crosslinker_id is None

    assert results[7].id == 7  # id from incrementing count
    assert results[7].mod_name == '(175.03)'  # unknown modification -> name from mass
    assert results[7].mass == 175.03032  # massDelta from <SearchModification>
    assert results[7].residues == 'K'  # residues from <SearchModification>
    assert results[7].specificity_rules == []  # parsed from child <SpecificityRules>
    assert not results[7].fixed_mod  # fixedMod from <SearchModification>
    assert results[7].accession == 'MS:1001460'  # accession from <SearchModification> cvParam
    assert results[7].crosslinker_id is None

    assert results[8].id == 8  # id from incrementing count
    assert results[8].mod_name == '(176.01)'  # unknown modification -> name from mass
    assert results[8].mass == 176.0143295  # massDelta from <SearchModification>
    assert results[8].residues == 'K'  # residues from <SearchModification>
    assert results[8].specificity_rules == []  # parsed from child <SpecificityRules>
    assert not results[8].fixed_mod  # fixedMod from <SearchModification>
    assert results[8].accession == 'MS:1001460'  # accession from <SearchModification> cvParam
    assert results[8].crosslinker_id is None

    assert results[9].id == 9  # id from incrementing count
    assert results[9].mod_name == '(175.03)'  # unknown modification -> name from mass
    assert results[9].mass == 175.03032  # massDelta from <SearchModification>
    assert results[9].residues == '.'  # residues from <SearchModification>
    assert results[9].specificity_rules == ['MS:1002057']  # parsed from child <SpecificityRules>
    assert not results[9].fixed_mod  # fixedMod from <SearchModification>
    assert results[9].accession == 'MS:1001460'  # accession from <SearchModification> cvParam
    assert results[9].crosslinker_id is None

    assert results[10].id == 10  # id from incrementing count
    assert results[10].mod_name == '(176.01)'  # unknown modification -> name from mass
    assert results[10].mass == 176.0143295  # massDelta from <SearchModification>
    assert results[10].residues == '.'  # residues from <SearchModification>
    assert results[10].specificity_rules == ['MS:1002057']  # parsed from child <SpecificityRules>
    assert not results[10].fixed_mod  # fixedMod from <SearchModification>
    assert results[10].accession == 'MS:1001460'  # accession from <SearchModification> cvParam
    assert results[10].crosslinker_id is None

    assert results[11].id == 11  # id from incrementing count
    assert results[11].mod_name == 'Deamidated'  # name from <SearchModification> cvParam
    assert results[11].mass == 0.984016  # massDelta from <SearchModification>
    assert results[11].residues == 'NQ'  # residues from <SearchModification>
    assert results[11].specificity_rules == []  # parsed from child <SpecificityRules>
    assert not results[11].fixed_mod  # fixedMod from <SearchModification>
    assert results[11].accession == 'UNIMOD:7'  # accession from <SearchModification> cvParam
    assert results[11].crosslinker_id is None

    assert results[12].id == 12  # id from incrementing count
    assert results[12].mod_name == 'Methyl'  # name from <SearchModification> cvParam
    assert results[12].mass == 14.01565  # massDelta from <SearchModification>
    assert results[12].residues == 'DE'  # residues from <SearchModification>
    assert results[12].specificity_rules == []  # parsed from child <SpecificityRules>
    assert not results[12].fixed_mod  # fixedMod from <SearchModification>
    assert results[12].accession == 'UNIMOD:34'  # accession from <SearchModification> cvParam
    assert results[12].crosslinker_id is None

    assert results[13].id == 13  # id from incrementing count
    assert results[13].mod_name == 'Carbamidomethyl'  # name from <SearchModification> cvParam
    assert results[13].mass == 57.021465  # massDelta from <SearchModification>
    assert results[13].residues == 'C'  # residues from <SearchModification>
    assert results[13].specificity_rules == []  # parsed from child <SpecificityRules>
    assert results[13].fixed_mod  # fixedMod from <SearchModification>
    assert results[13].accession == 'UNIMOD:4'  # accession from <SearchModification> cvParam
    assert results[13].crosslinker_id is None


def compare_enzyme(results):
    assert len(results) == 1
    assert results[0].id == "Trypsin_0"  # id from Enzyme element
    assert results[0].protocol_id == "SearchProtocol_1_0"
    assert results[0].c_term_gain == "OH"
    assert results[0].min_distance is None
    assert results[0].missed_cleavages == 2
    assert results[0].n_term_gain == "H"
    assert results[0].name == "Trypsin"
    assert results[0].semi_specific is False
    assert results[0].site_regexp == '(?<=[KR])(?\\!P)'
    assert results[0].accession == "MS:1001251"


def compare_spectrum_identification_protocol(results):
    assert len(results) == 1
    # parsed from <FragmentTolerance> in <SpectrumIdentificationProtocol>
    assert results[0].id == 0
    assert results[0].sip_ref == 'SearchProtocol_1_0'  # id from <SpectrumIdentificationProtocol>
    assert results[0].frag_tol == 5.0
    assert results[0].frag_tol_unit == 'ppm'
    # cvParams from <AdditionalSearchParams> 'ion series considered in search' (MS:1002473)

    assert results[0].additional_search_params == {'MS:1001211': 'parent mass type mono',
                                                   'MS:1002494': 'cross-linking search',
                                                   'MS:1001256': 'fragment mass type mono',
                                                   'MS:1001118': 'param: b ion',
                                                   'MS:1001262': 'param: y ion'}

    assert results[0].analysis_software['id'] == "xiFDR_id"


def compare_analysis_collection_mgf(results):
    assert len(results) == 2
    assert (results[0].spectrum_identification_list_ref ==
            'SII_LIST_1_1_0_recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mgf')
    assert results[0].spectrum_identification_protocol_ref == 'SearchProtocol_1_0'
    assert results[0].spectra_data_refs == ['SD_0_recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mgf']
    assert results[0].search_database_refs == ['SDB_0_0']

    assert (results[1].spectrum_identification_list_ref ==
            'SII_LIST_1_1_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf')
    assert results[1].spectrum_identification_protocol_ref == 'SearchProtocol_1_0'
    assert results[1].spectra_data_refs == ['SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf']
    assert results[1].search_database_refs == ['SDB_0_0']


def compare_analysis_collection_mzml(results):
    assert len(results) == 2
    assert (results[0].spectrum_identification_list_ref ==
            'SII_LIST_1_1_0_recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mzML')
    assert results[0].spectrum_identification_protocol_ref == 'SearchProtocol_1_0'
    assert results[0].spectra_data_refs == ['SD_0_recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mzML']
    assert results[0].search_database_refs == ['SDB_0_0']
    assert (results[1].spectrum_identification_list_ref ==
            'SII_LIST_1_1_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mzML')
    assert results[1].spectrum_identification_protocol_ref == 'SearchProtocol_1_0'
    assert results[1].spectra_data_refs == ['SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mzML']
    assert results[1].search_database_refs == ['SDB_0_0']


def compare_spectrum_mgf(conn, peak_list_folder):
    peaklists = [
        'recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mgf',
        'recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf',
    ]
    for pl in peaklists:
        rs = conn.execute(text(f"SELECT * FROM Spectrum WHERE peak_list_file_name = '{pl}'"))
        results = rs.fetchall()
        assert len(results) == 11
        reader = mgf.read(os.path.join(peak_list_folder, pl))
        for r in results:
            # For MGF the index is encoded as e.g. index=3
            reader_idx = int(r.id.replace('index=', ''))
            # noinspection PyUnresolvedReferences
            spectrum = reader[reader_idx]
            # spectrumID from <SpectrumIdentificationResult>
            assert r.id == f'index={reader_idx}'  # a bit circular here
            # spectraData_ref from <SpectrumIdentificationResult>
            assert r.spectra_data_id == peaklists.index(pl) #  ref == f'SD_0_{pl}'
            assert r.peak_list_file_name == pl
            assert r.precursor_mz == spectrum['params']['pepmass'][0]
            assert r.precursor_charge == spectrum['params']['charge'][0]
            # check that mz and intensity values are as expected
            # 1. unpacking the blob
            assert_array_equal(struct.unpack('%sd' % (len(r.mz) // 8), r.mz), spectrum['m/z array'])
            assert_array_equal(struct.unpack('%sd' % (len(r.intensity) // 8), r.intensity), spectrum['intensity array'])
            # 2. using np.frombuffer (this works because np assumes double precision as default)
            assert_array_equal(np.frombuffer(r.mz), spectrum['m/z array'])
            assert_array_equal(np.frombuffer(r.intensity), spectrum['intensity array'])


def test_psql_db_cleared_each_test(use_database, engine):
    """Check that the database is empty."""
    with engine.connect() as conn:
        rs = conn.execute(text("SELECT * FROM Upload"))
        assert 0 == rs.rowcount
    engine.dispose()


def test_psql_mgf_mzid_parser(tmpdir, use_database, engine):
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
    mzid = os.path.join(fixtures_dir, 'mgf_ecoli_dsso.mzid')
    peak_list_folder = os.path.join(fixtures_dir, 'peaklist')

    id_parser = parse_mzid_into_postgresql(mzid, peak_list_folder, tmpdir, logger,
                                           use_database, engine)

    with engine.connect() as conn:
        # DBSequence
        stmt = Table("dbsequence", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        compare_db_sequence(rs.fetchall())

        # SearchModification - parsed from <SearchModification>s
        stmt = Table("searchmodification", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        compare_modification(rs.fetchall())

        # Enzyme - parsed from SpectrumIdentificationProtocols
        stmt = Table("enzyme", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        compare_enzyme(rs.fetchall())

        # PeptideEvidence
        stmt = Table("peptideevidence", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_peptide_evidence(rs.fetchall())

        # ModifiedPeptide
        stmt = Table("modifiedpeptide", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_modified_peptide(rs.fetchall())

        # Spectrum
        compare_spectrum_mgf(conn, peak_list_folder)

        # Match
        stmt = Table("match", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        assert 22 == rs.rowcount
        results = rs.fetchall()
        assert results[0].id == 'SII_3_1'  # id from first <SpectrumIdentificationItem>
        assert results[0].spectrum_id == 'index=3'  # spectrumID from <SpectrumIdentificationResult>
        # spectraData_ref from <SpectrumIdentificationResult>
        # assert results[0].spectra_data_ref == \
        #        'SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf'
        assert results[0].spectra_data_id == 1
        # peptide_ref from <SpectrumIdentificationItem>
        assert results[0].pep1_id == 4 #\
               # '6_VAEmetETPHLIHKVALDPLTGPMPYQGR_11_MGHAGAIIAGGKGTADEK_11_12_p1'
        # peptide_ref from matched <SpectrumIdentificationItem> by crosslink_identification_id
        assert results[0].pep2_id == 5 # \
               # '6_VAEmetETPHLIHKVALDPLTGPMPYQGR_11_MGHAGAIIAGGKGTADEK_11_12_p0'
        assert results[0].charge_state == 5  # chargeState from <SpectrumIdentificationItem>
        assert results[0].pass_threshold  # passThreshold from <SpectrumIdentificationItem>
        assert results[0].rank == 1  # rank from <SpectrumIdentificationItem>
        # scores parsed from score related cvParams in <SpectrumIdentificationItem>
        assert results[0].scores == {'xi:score': 33.814201}
        # experimentalMassToCharge from <SpectrumIdentificationItem>
        assert results[0].exp_mz == 945.677359
        # calculatedMassToCharge from <SpectrumIdentificationItem>
        assert results[0].calc_mz == pytest.approx(945.6784858667701, abs=1e-12)

        # SpectrumIdentificationProtocol
        stmt = Table("spectrumidentificationprotocol", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_spectrum_identification_protocol(rs.fetchall())

        # AnalysisCollection
        stmt = Table("analysiscollectionspectrumidentification", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_analysis_collection_mgf(rs.fetchall())

        # Upload
        stmt = Table("upload", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        assert 1 == rs.rowcount
        results = rs.fetchall()

        assert results[0].identification_file_name == 'mgf_ecoli_dsso.mzid'
        assert results[0].provider == {"id": "PROVIDER", "ContactRole": [
            {"contact_ref": "PERSON_DOC_OWNER", "Role": "researcher"}]}
        assert results[0].audit_collection == {
            'Organization': {'contact name': 'TU Berlin',
                             'id': 'ORG_DOC_OWNER',
                             'name': 'TU Berlin'},
            'Person': {'Affiliation': [{'organization_ref': 'ORG_DOC_OWNER'}],
                       'contact address': 'TIB 4/4-3 Gebäude 17, Aufgang 1, Raum 476 '
                                          'Gustav-Meyer-Allee 25 13355 Berlin',
                       'contact email': 'lars.kolbowski@tu-berlin.de',
                       'firstName': 'Lars',
                       'id': 'PERSON_DOC_OWNER',
                       'lastName': 'Kolbowski'}
        }
        assert results[0].analysis_sample_collection == {}
        assert results[0].bib == []
        assert results[0].spectra_formats == [
            {'FileFormat': 'Mascot MGF format',
             'SpectrumIDFormat': 'multiple peak list nativeID format',
             'id': 'SD_0_recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mgf',
             'location': 'recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mgf'},
            {'FileFormat': 'Mascot MGF format',
             'SpectrumIDFormat': 'multiple peak list nativeID format',
             'id': 'SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf',
             'location': 'recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mgf'}
        ]
        assert results[0].contains_crosslinks
        assert results[0].upload_warnings == []

    engine.dispose()


def test_psql_mzml_mzid_parser(tmpdir, use_database, engine):
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
    mzid = os.path.join(fixtures_dir, 'mzml_ecoli_dsso.mzid')
    peak_list_folder = os.path.join(fixtures_dir, 'peaklist')

    id_parser = parse_mzid_into_postgresql(mzid, peak_list_folder, tmpdir, logger,
                                           use_database, engine)

    with (engine.connect() as conn):
        # DBSequence
        stmt = Table("dbsequence", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        compare_db_sequence(rs.fetchall())

        # Modification - parsed from <SearchModification>s
        stmt = Table("searchmodification", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        compare_modification(rs.fetchall())

        # Enzyme - parsed from SpectrumIdentificationProtocols
        stmt = Table("enzyme", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        compare_enzyme(rs.fetchall())

        # PeptideEvidence
        stmt = Table("peptideevidence", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_peptide_evidence(rs.fetchall())

        # ModifiedPeptide
        stmt = Table("modifiedpeptide", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_modified_peptide(rs.fetchall())

        # Spectrum
        # ToDo: create and use compare_spectrum_mzml()
        stmt = Table("spectrum", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        assert 22 == rs.rowcount
        results = rs.fetchall()
        # spectrumID from <SpectrumIdentificationResult>
        assert results[0].id == 'controllerType=0 controllerNumber=1 scan=14905'
        # spectraData_ref from <SpectrumIdentificationResult>
        assert results[0].spectra_data_id == 1 # (
            # 'SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mzML')
        assert results[0].peak_list_file_name == 'B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mzML'
        # Precursor info from mzML
        # Spectrum->precursorList->precursor[0]->selectedIonList->selectedIon[0]
        assert results[0].precursor_mz == 945.677381209342  # selected ion m/z
        assert results[0].precursor_charge == 5  # charge state
        assert results[0].mz == (b'\x00\x00\x00\x80g\x03Z@\x00\x00\x00\xe00\t[@\x00\x00\x00`\xfe\x1f['
                                 b'@\x00\x00\x00\xe0\x93\x84[@\x00\x00\x00\xc0\xca\xc4[@\x00\x00\x00\xa0{\xe3['
                                 b'@\x00\x00\x00@\x8c\xc5\\@\x00\x00\x00\xa0e\x04]@\x00\x00\x00\x00\x88\x04]@\x00\x00'
                                 b'\x00\x00\xc1D]@\x00\x00\x00\xa0\x9e\xbc]@\x00\x00\x00 '
                                 b'8\xc2]@\x00\x00\x00`%t^@\x00\x00\x00@Gx^@\x00\x00\x00\x00\x8d\xc5_@\x00\x00\x00'
                                 b'\xc0E#`@\x00\x00\x00\xa0\xc2B`@\x00\x00\x00@\x1eBa@\x00\x00\x00@\xecBa@\x00\x00'
                                 b'\x00@\x06ca@\x00\x00\x00`\x1a\xa2a@\x00\x00\x00\xc0\xc5\xe3a@\x00\x00\x00\xa0\xe0'
                                 b'\x03b@\x00\x00\x00\xa0\x9bcb@\x00\x00\x00 '
                                 b'\xb5\x83b@\x00\x00\x00@E#c@\x00\x00\x00`rbc@\x00\x00\x00 '
                                 b'\x9bbc@\x00\x00\x00@\xc4cc@\x00\x00\x00\xe0\xc3xc@\x00\x00\x00\xa0\xb6\x82c@\x00'
                                 b'\x00\x00 E\xa4c@\x00\x00\x00`q\xe2c@\x00\x00\x00@\x9d\x82d@\x00\x00\x00\xe0\xca'
                                 b'\xc4d@\x00\x00\x00\x80\x9bce@\x00\x00\x00\xa0\xb6\x83e@\x00\x00\x00\x00\xcf\xe3e'
                                 b'@\x00\x00\x00\xa0\x17\x07f@\x00\x00\x00`w\xa3f@\x00\x00\x00`\x9a\xe3f@\x00\x00\x00'
                                 b'@\xc6\xe4f@\x00\x00\x00\xa0\xdf\x04g@\x00\x00\x00\xe0\xf1"g@\x00\x00\x00\xa0\x1d$g'
                                 b'@\x00\x00\x00\x00\xe1bg@\x00\x00\x00\xa0qcg@\x00\x00\x00\x00\xccbh@\x00\x00\x00 '
                                 b'\xb2oh@\x00\x00\x00 \xf0\x81h@\x00\x00\x00`a#i@\x00\x00\x00\xe0|Ci@\x00\x00\x00 '
                                 b'X\xfdi@\x00\x00\x00\x80M#j@\x00\x00\x00\xa0hCj@\x00\x00\x00\x00\x9cdj@\x00\x00\x00'
                                 b'\xc0\xb4\x84j@\x00\x00\x00 '
                                 b'\xc9\xa2j@\x00\x00\x00\x80H\xe3j@\x00\x00\x00`o\xe4j@\x00\x00\x00\x00\x94\xbfk'
                                 b'@\x00\x00\x00\xc0\xd6\xd0k@\x00\x00\x00\xe0\xa4\xe2k@\x00\x00\x00`6\xa3l@\x00\x00'
                                 b'\x00\xe0\x1b\xe3l@\x00\x00\x00\xc0}\x04m@\x00\x00\x00\xc0\x1a$m@\x00\x00\x00\x80'
                                 b'\x95$m@\x00\x00\x00 \xcdcm@\x00\x00\x00 '
                                 b'\xcb\xc3m@\x00\x00\x00`J\x04n@\x00\x00\x00\xc0\xc9Dn@\x00\x00\x00`\xf7\x82n@\x00'
                                 b'\x00\x00\xa0\xa3\x03o@\x00\x00\x00\xe0\xcbdo@\x00\x00\x00\x00\xc5\xc4o@\x00\x00'
                                 b'\x00\x00\xf5\xc5o@\x00\x00\x00\x00\x10\x02p@\x00\x00\x00\x00\x08"p@\x00\x00\x00'
                                 b'\x80P"p@\x00\x00\x00\x00n"p@\x00\x00\x00\xe0\xf9Qp@\x00\x00\x00@\xfe\xa1p@\x00\x00'
                                 b'\x00\xc0\xfc\xa2p@\x00\x00\x00\xc0\xc8\xc1p@\x00\x00\x00`\xa5\xc2p@\x00\x00\x00'
                                 b'`;\xc3p@\x00\x00\x00\x80b\xd2p@\x00\x00\x00@\x90\x02q@\x00\x00\x00\xa0\xb9\x11q'
                                 b'@\x00\x00\x00\xe0{'
                                 b'Bq@\x00\x00\x00\xe0\x89Rq@\x00\x00\x00\xe0\xfcaq@\x00\x00\x00`5\xa2q@\x00\x00\x00'
                                 b'`\xe6\xa2q@\x00\x00\x00\x80\xf3\xe1q@\x00\x00\x00@\xbc"r@\x00\x00\x00\x80O4r@\x00'
                                 b'\x00\x00\xc0\xe8ar@\x00\x00\x00@\xe5br@\x00\x00\x00\x80\xf1rr@\x00\x00\x00\xa0\xfc'
                                 b'\x81r@\x00\x00\x00  '
                                 b'\xa2r@\x00\x00\x00`\xd0\xa2r@\x00\x00\x00@|\xc2r@\x00\x00\x00@\xdfAs@\x00\x00\x00'
                                 b'@\x8fBs@\x00\x00\x00\x00ORs@\x00\x00\x00\x00\x93js@\x00\x00\x00@\x99rs@\x00\x00'
                                 b'\x00\xa0\xbdrs@\x00\x00\x00@\xders@\x00\x00\x00`{'
                                 b'\x82s@\x00\x00\x00`\x11\x83s@\x00\x00\x00\xe0\xfb\x92s@\x00\x00\x00`\xbb\xa2s@\x00'
                                 b'\x00\x00\xc0\xcb\xb2s@\x00\x00\x00\xe0\xbc\x02t@\x00\x00\x00\xa0W2t@\x00\x00\x00'
                                 b'\xa0\xfdRt@\x00\x00\x00\xa0\x0bbt@\x00\x00\x00 \xbabt@\x00\x00\x00 '
                                 b'\x1crt@\x00\x00\x00\xc0\xfa\x81t@\x00\x00\x00@\x0b\x92t@\x00\x00\x00\xc0\x95\x12u'
                                 b'@\x00\x00\x00@P\x82u@\x00\x00\x00\xc0;\xc3u@\x00\x00\x00 '
                                 b'\x96\xd2u@\x00\x00\x00\x80C\xf2u@\x00\x00\x00\xc0=\xf3u@\x00\x00\x00\xc0K\x02v'
                                 b'@\x00\x00\x00\xc0|\x13v@\x00\x00\x00@QBv@\x00\x00\x00`.\x83v@\x00\x00\x00\xc0\x14'
                                 b'\x03w@\x00\x00\x00 '
                                 b'\x87\x12w@\x00\x00\x00`\xb8\x12w@\x00\x00\x00\x80g\x13w@\x00\x00\x00\x00\xc7"w'
                                 b'@\x00\x00\x00\xc0x#w@\x00\x00\x00\x80}bw@\x00\x00\x00\xe0\x8crw@\x00\x00\x00\xa0'
                                 b'\xe7\x82w@\x00\x00\x00\xa0\xf1\x8aw@\x00\x00\x00\x80\xdf\xc2w@\x00\x00\x00\x00\x12'
                                 b'\xf3w@\x00\x00\x00@\xb62x@\x00\x00\x00@\xc5Bx@\x00\x00\x00\xc0\xe6Rx@\x00\x00\x00'
                                 b'\x80\xe8rx@\x00\x00\x00\xe0\xf6\x82x@\x00\x00\x00 \xa8\x83x@\x00\x00\x00 '
                                 b'\xf0\xa2x@\x00\x00\x00\xe0\xa3\xd2x@\x00\x00\x00\x80R\xd3x@\x00\x00\x00\x00\xb5'
                                 b'\xe2x@\x00\x00\x00\xc0\x92\xf3x@\x00\x00\x00`>\x13y@\x00\x00\x00\xe0\xebby@\x00'
                                 b'\x00\x00`U\x93y@\x00\x00\x00\x80\x7f\xf3y@\x00\x00\x00`\xd23z@\x00\x00\x00\x00R'
                                 b'\x8bz@\x00\x00\x00@Y\x93z@\x00\x00\x00\xa0Z\x9bz@\x00\x00\x00 '
                                 b'\x11\xa3z@\x00\x00\x00@W\xa4z@\x00\x00\x00@\xe9\xb2z@\x00\x00\x00\x00\x80\xb3z'
                                 b'@\x00\x00\x00\xa0j\xb3{@\x00\x00\x00\x00s\xc3{@\x00\x00\x00\xe0\x15\xd3{'
                                 b'@\x00\x00\x00\x80#\xe3{'
                                 b'@\x00\x00\x00\xc0\xec#|@\x00\x00\x00\xe0~S|@\x00\x00\x00\xe0\x85['
                                 b'|@\x00\x00\x00`\xfdb|@\x00\x00\x00 '
                                 b'\x84c|@\x00\x00\x00\x00\x04s|@\x00\x00\x00@\x03\x9c|@\x00\x00\x00\x00\x1c\xc3'
                                 b'|@\x00\x00\x00\x00\x95\xd4|@\x00\x00\x00\xe0\x84\xe3|@\x00\x00\x00\x00\x07\x1d'
                                 b'}@\x00\x00\x00 '
                                 b'\xad#}@\x00\x00\x00\xe0B$}@\x00\x00\x00\x80\xed\xa2}@\x00\x00\x00`~\xbc}@\x00\x00'
                                 b'\x00\x80\xd4C~@\x00\x00\x00\xa0j\xa4~@\x00\x00\x00\xa0\xce\xeb~@\x00\x00\x00@\xcb'
                                 b'\xf3~@\x00\x00\x00\xe0\xa9\x13\x7f@\x00\x00\x00\xe0\x14$\x7f@\x00\x00\x00`\xd53'
                                 b'\x7f@\x00\x00\x00\xa0\xe0{'
                                 b'\x7f@\x00\x00\x00\x00\xe6\x83\x7f@\x00\x00\x00\x00\xe4\x8b\x7f@\x00\x00\x00\xe0'
                                 b'\xe1\x93\x7f@\x00\x00\x00\xc0g\xb3\x7f@\x00\x00\x00@G\xb4\x7f@\x00\x00\x00`\xad'
                                 b'\xe4\x7f@\x00\x00\x00\x00!"\x80@\x00\x00\x00\xe0\x1aZ\x80@\x00\x00\x00\xe0\x1fb'
                                 b'\x80@\x00\x00\x00\x80\xcai\x80@\x00\x00\x00\xe0\xd0q\x80@\x00\x00\x00\x00\x02r\x80'
                                 b'@\x00\x00\x00\x00\xc7y\x80@\x00\x00\x00\xc0\x07z\x80@\x00\x00\x00\xa0\x16\x02\x81'
                                 b'@\x00\x00\x00\xe0\x19\n\x81@\x00\x00\x00@vn\x81@\x00\x00\x00\x00C\x82\x81@\x00\x00'
                                 b'\x00\xc0L\x8a\x81@\x00\x00\x00\xc0#\x9a\x81@\x00\x00\x00\x00\x83\xd2\x81@\x00\x00'
                                 b'\x00\xc0j\xda\x81@\x00\x00\x00`<\xea\x81@\x00\x00\x00@W\x12\x82@\x00\x00\x00\x00X'
                                 b'\x1a\x82@\x00\x00\x00\x00\xa1*\x82@\x00\x00\x00\xe0qr\x82@\x00\x00\x00\xe0Q\x8a'
                                 b'\x82@\x00\x00\x00`s\xaa\x82@\x00\x00\x00@q\xbe\x82@\x00\x00\x00`t\xc2\x82@\x00\x00'
                                 b'\x00\xe0v\xc6\x82@\x00\x00\x00 6\xd2\x82@\x00\x00\x00 s\xd2\x82@\x00\x00\x00 '
                                 b'\xb0\xd2\x82@\x00\x00\x00\xc0L\xda\x82@\x00\x00\x00\x80|\x06\x83@\x00\x00\x00\x80'
                                 b'\x7f\n\x83@\x00\x00\x00\x80\x81\x0e\x83@\x00\x00\x00\x80\x81\x12\x83@\x00\x00\x00'
                                 b'\xe0\x86\x1a\x83@\x00\x00\x00\xc0\xba\x1a\x83@\x00\x00\x00@\x8e&\x83@\x00\x00\x00'
                                 b'`Qb\x83@\x00\x00\x00\x80\x85b\x83@\x00\x00\x00 '
                                 b'Vj\x83@\x00\x00\x00`\x8bj\x83@\x00\x00\x00\xc0\x8dr\x83@\x00\x00\x00`\xb3\x96\x83'
                                 b'@\x00\x00\x00\xa0\xf3\xd2\x83@\x00\x00\x00@v\xf2\x83@\x00\x00\x00\xa0}\xfa\x83'
                                 b'@\x00\x00\x00 '
                                 b'x\x02\x84@\x00\x00\x00`O\n\x84@\x00\x00\x00`\xe2B\x84@\x00\x00\x00\x00\xcfj\x84'
                                 b'@\x00\x00\x00@\xda\xb2\x84@\x00\x00\x00\xc0\xdc\xb6\x84@\x00\x00\x00@\xdf\xba\x84'
                                 b'@\x00\x00\x00@\xdd\xbe\x84@\x00\x00\x00`\xc2\xc2\x84@\x00\x00\x00\x80\xc4\xc6\x84'
                                 b'@\x00\x00\x00\xc0\xc7\xca\x84@\x00\x00\x00@\x98\xd2\x84@\x00\x00\x00\xa0\x9d\xd6'
                                 b'\x84@\x00\x00\x00\xe0\x98\xda\x84@\x00\x00\x00`\x18\n\x85@\x00\x00\x00\x80b\x12'
                                 b'\x85@\x00\x00\x00`\xbe2\x85@\x00\x00\x00\x00\xc06\x85@\x00\x00\x00\xe0\xc2:\x85'
                                 b'@\x00\x00\x00`\xc8>\x85@\x00\x00\x00\xa0\x16\x9b\x85@\x00\x00\x00\x80)\xcf\x85'
                                 b'@\x00\x00\x00\x80('
                                 b'\xd3\x85@\x00\x00\x00\xc0\x18\xfb\x85@\x00\x00\x00\x00\x0c\x07\x86@\x00\x00\x00 '
                                 b'!?\x86@\x00\x00\x00\xc0\xa2B\x86@\x00\x00\x00@#C\x86@\x00\x00\x00\x80('
                                 b'G\x86@\x00\x00\x00@\x05O\x86@\x00\x00\x00\x80\tS\x86@\x00\x00\x00\xe0\x10W\x86'
                                 b'@\x00\x00\x00\xa0\x1as\x86@\x00\x00\x00@-{'
                                 b'\x86@\x00\x00\x00\x00\xea\x96\x86@\x00\x00\x00\xc0\xeb\x9a\x86@\x00\x00\x00`.\x9b'
                                 b'\x86@\x00\x00\x00`\xde\x9e\x86@\x00\x00\x00`\x05\xbf\x86@\x00\x00\x00@\x06\xc3\x86'
                                 b'@\x00\x00\x00`\x06\xcb\x86@\x00\x00\x00\xa0\x1d\xe9\x86@\x00\x00\x00 '
                                 b'6#\x87@\x00\x00\x00@\r9\x87@\x00\x00\x00 dB\x87@\x00\x00\x00 F[\x87@\x00\x00\x00 '
                                 b'D]\x87@\x00\x00\x00@\xca^\x87@\x00\x00\x00\xc0J_\x87@\x00\x00\x00\xa0Pc\x87@\x00'
                                 b'\x00\x00\x00Ng\x87@\x00\x00\x00 '
                                 b'Xk\x87@\x00\x00\x00\xe0\xe3r\x87@\x00\x00\x00\xc0\xd7z\x87@\x00\x00\x00@"{'
                                 b'\x87@\x00\x00\x00`\xdd\x82\x87@\x00\x00\x00\x00*\x83\x87@\x00\x00\x00\xa0\xdb\x8a'
                                 b'\x87@\x00\x00\x00`('
                                 b'\x8b\x87@\x00\x00\x00\x00\x18\xbb\x87@\x00\x00\x00@)\xdb\x87@\x00\x00\x00\x80,'
                                 b'\xdf\x87@\x00\x00\x00\xc0.\xe3\x87@\x00\x00\x00\xc0:\xf3\x87@\x00\x00\x00\x000\xf7'
                                 b'\x87@\x00\x00\x00 >\xfb\x87@\x00\x00\x00@>\xff\x87@\x00\x00\x00 '
                                 b'9;\x88@\x00\x00\x00 '
                                 b'<?\x88@\x00\x00\x00\xc0CC\x88@\x00\x00\x00\x00LG\x88@\x00\x00\x00 '
                                 b'\xfdR\x88@\x00\x00\x00\xc0\r['
                                 b'\x88@\x00\x00\x00\x003\x93\x88@\x00\x00\x00\xa0*\x97\x88@\x00\x00\x00\xc0\xa2\xaf'
                                 b'\x88@\x00\x00\x00`\x1b\xbb\x88@\x00\x00\x00\xa0\x1e\xbf\x88@\x00\x00\x00\xc0!\xc3'
                                 b'\x88@\x00\x00\x00\x80#\xc7\x88@\x00\x00\x00\xe0\n\xe3\x88@\x00\x00\x00 '
                                 b'\x0b\xe7\x88@\x00\x00\x00\xc0K\xf9\x88@\x00\x00\x00\xa0H\xfb\x88@\x00\x00\x00\xa0'
                                 b'\x0f\x17\x89@\x00\x00\x00\x00F\x19\x89@\x00\x00\x00\xe0B\x1b\x89@\x00\x00\x00\xa0I'
                                 b'\x1f\x89@\x00\x00\x00\xc0\x9b\x1f\x89@\x00\x00\x00\xe0M#\x89@\x00\x00\x00\x80\x9e'
                                 b'#\x89@\x00\x00\x00`\xa2\'\x89@\x00\x00\x00\xe0\xebb\x89@\x00\x00\x00\x00pc\x89'
                                 b'@\x00\x00\x00\xa0\xf7f\x89@\x00\x00\x00\x80rg\x89@\x00\x00\x00\xe01\x9f\x89@\x00'
                                 b'\x00\x00\x80\x81\x9f\x89@\x00\x00\x00`3\xa3\x89@\x00\x00\x00\x80\x83\xa3\x89@\x00'
                                 b'\x00\x00\xe0\x82\xa7\x89@\x00\x00\x00\xe0X\xa9\x89@\x00\x00\x00\xa0W\xab\x89@\x00'
                                 b'\x00\x00`Y\xaf\x89@\x00\x00\x00\xa0o\xb3\x89@\x00\x00\x00 '
                                 b'v\xbb\x89@\x00\x00\x00\xc0s\xc3\x89@\x00\x00\x00\xe0U\xe3\x89@\x00\x00\x00\xc0s'
                                 b'\xfb\x89@\x00\x00\x00\xe0\xeb\x12\x8a@\x00\x00\x00\x80U\x1b\x8a@\x00\x00\x00 '
                                 b'\x1bG\x8a@\x00\x00\x00@{'
                                 b'S\x8a@\x00\x00\x00\xa0D\x83\x8a@\x00\x00\x00\xe0\x82\x89\x8a@\x00\x00\x00`G\x8b'
                                 b'\x8a@\x00\x00\x00\xc0\x83\x8d\x8a@\x00\x00\x00`\x83\x8f\x8a@\x00\x00\x00\x80M\x93'
                                 b'\x8a@\x00\x00\x00\x00P\x9b\x8a@\x00\x00\x00\xa0\xad\xa3\x8a@\x00\x00\x00 '
                                 b'\xb0\xa7\x8a@\x00\x00\x00\xa0\xa5\xb3\x8a@\x00\x00\x00\xa0\xa8\xb7\x8a@\x00\x00'
                                 b'\x00\x80\xa0\xbb\x8a@\x00\x00\x00\xa0w\xc3\x8a@\x00\x00\x00@O\xdb\x8a@\x00\x00\x00'
                                 b'`f\xe3\x8a@\x00\x00\x00\xe0p\xe7\x8a@\x00\x00\x00@\xba\xeb\x8a@\x00\x00\x00\xe0'
                                 b'\xba\xef\x8a@\x00\x00\x00\x00['
                                 b'\xf3\x8a@\x00\x00\x00@\xbd\xf3\x8a@\x00\x00\x00\x80\xc4\xf7\x8a@\x00\x00\x00\xe0K'
                                 b'\x03\x8b@\x00\x00\x00 '
                                 b'\x89#\x8b@\x00\x00\x00\xe0v+\x8b@\x00\x00\x00\xe0y/\x8b@\x00\x00\x00\x00|3\x8b'
                                 b'@\x00\x00\x00\xc0\x7f7\x8b@\x00\x00\x00\xc0\x82;\x8b@\x00\x00\x00@\x95K\x8b@\x00'
                                 b'\x00\x00@\x93S\x8b@\x00\x00\x00\xc0?c\x8b@\x00\x00\x00 '
                                 b'<g\x8b@\x00\x00\x00\x80\x97g\x8b@\x00\x00\x00@Hk\x8b@\x00\x00\x00\xc0\x9ck\x8b'
                                 b'@\x00\x00\x00 '
                                 b'\x9bo\x8b@\x00\x00\x00\xe0\x90q\x8b@\x00\x00\x00\x00\x98s\x8b@\x00\x00\x00\xa0'
                                 b'\x93u\x8b@\x00\x00\x00\x00\x9dw\x8b@\x00\x00\x00\xa0\x8fy\x8b@\x00\x00\x00\x80'
                                 b'\x9d{\x8b@\x00\x00\x00 '
                                 b')|\x8b@\x00\x00\x00\xe0\x9e\x83\x8b@\x00\x00\x00`2\x84\x8b@\x00\x00\x00`]\x9f\x8b'
                                 b'@\x00\x00\x00\xc0\xb8\x9f\x8b@\x00\x00\x00\xe0M\xa7\x8b@\x00\x00\x00@Z\xab\x8b'
                                 b'@\x00\x00\x00 '
                                 b']\xaf\x8b@\x00\x00\x00\x80^\xb3\x8b@\x00\x00\x00\x00_\xb7\x8b@\x00\x00\x00\xa0'
                                 b'^\xbb\x8b@\x00\x00\x00 '
                                 b'd\xbf\x8b@\x00\x00\x00@:\xc3\x8b@\x00\x00\x00@\x17\xdb\x8b@\x00\x00\x00\xc0\xa5'
                                 b'\xdb\x8b@\x00\x00\x00\x00h\xe3\x8b@\x00\x00\x00`q\xe7\x8b@\x00\x00\x00\xa0q\xeb'
                                 b'\x8b@\x00\x00\x00\x00l\xef\x8b@\x00\x00\x00 '
                                 b'~\xf0\x8b@\x00\x00\x00@c\xf3\x8b@\x00\x00\x00\xa0\xa6\x03\x8c@\x00\x00\x00\xc0'
                                 b'\xa81\x8c@\x00\x00\x00`\xa95\x8c@\x00\x00\x00@\xa2;\x8c@\x00\x00\x00`\xcfC\x8c'
                                 b'@\x00\x00\x00 \xc4E\x8c@\x00\x00\x00`pK\x8c@\x00\x00\x00`uS\x8c@\x00\x00\x00\xe0v['
                                 b'\x8c@\x00\x00\x00\xe0\x84`\x8c@\x00\x00\x00`"b\x8c@\x00\x00\x00`\xcbc\x8c@\x00\x00'
                                 b'\x00\x80Ye\x8c@\x00\x00\x00\xc0\xf3f\x8c@\x00\x00\x00`\xc9i\x8c@\x00\x00\x00\x80'
                                 b'\xeao\x8c@\x00\x00\x00\xc0\xf2s\x8c@\x00\x00\x00\x80\xf7w\x8c@\x00\x00\x00@\xeb{'
                                 b'\x8c@\x00\x00\x00\xc0;}\x8c@\x00\x00\x00@t\x80\x8c@\x00\x00\x00 '
                                 b'\xdd\x83\x8c@\x00\x00\x00\xe0\xe1\x86\x8c@\x00\x00\x00@g\x87\x8c@\x00\x00\x00 '
                                 b'\xf7\x93\x8c@\x00\x00\x00@\x80\xa3\x8c@\x00\x00\x00\xa0\x83\xab\x8c@\x00\x00\x00'
                                 b'\x80\xce\xbb\x8c@\x00\x00\x00\x80`\xbd\x8c@\x00\x00\x00\x80\xc6\xce\x8c@\x00\x00'
                                 b'\x00@\xf9\xd1\x8c@\x00\x00\x00\xc0\xd2\xdb\x8c@\x00\x00\x00\x80\xd1\xdd\x8c@\x00'
                                 b'\x00\x00 \x80\xde\x8c@\x00\x00\x00\xc0\xe0\xdf\x8c@\x00\x00\x00`\xed\xee\x8c@\x00'
                                 b'\x00\x00\xe0\xd1\xef\x8c@\x00\x00\x00 '
                                 b'\xd7\xf3\x8c@\x00\x00\x00\xe0\xd4\xf7\x8c@\x00\x00\x00\x80\xd0\xf9\x8c@\x00\x00'
                                 b'\x00\x00\xd9\xfb\x8c@\x00\x00\x00\x00B\x02\x8d@\x00\x00\x00@\xd8\x13\x8d@\x00\x00'
                                 b'\x00\x80\xd6\x15\x8d@\x00\x00\x00 '
                                 b'\xd8\x17\x8d@\x00\x00\x00`\xab\x18\x8d@\x00\x00\x00\xc0\xd8\x19\x8d@\x00\x00\x00'
                                 b'\xa0\xde\x1b\x8d@\x00\x00\x00\xc0\xd7\x1d\x8d@\x00\x00\x00 '
                                 b'\x07/\x8d@\x00\x00\x00`\x800\x8d@\x00\x00\x00 '
                                 b':2\x8d@\x00\x00\x00@\xba3\x8d@\x00\x00\x00\xa0N5\x8d@\x00\x00\x00 '
                                 b'\xf06\x8d@\x00\x00\x00\xc0\x8c8\x8d@\x00\x00\x00\x80\xc8C\x8d@\x00\x00\x00\xa0'
                                 b'\x8dH\x8d@\x00\x00\x00 '
                                 b'\x19J\x8d@\x00\x00\x00\x00\xd5K\x8d@\x00\x00\x00\xc0eM\x8d@\x00\x00\x00@\xf1N\x8d'
                                 b'@\x00\x00\x00\x00\xdc['
                                 b'\x8d@\x00\x00\x00\xe0+b\x8d@\x00\x00\x00\x00\xfef\x8d@\x00\x00\x00\x00!o\x8d@\x00'
                                 b'\x00\x00\x00\x99p\x8d@\x00\x00\x00\xa07r\x8d@\x00\x00\x00\xc0\xd1s\x8d@\x00\x00'
                                 b'\x00\xe0ju\x8d@\x00\x00\x00`\x04w\x8d@\x00\x00\x00`\xa3x\x8d@\x00\x00\x00`1z\x8d'
                                 b'@\x00\x00\x00 \xd4{'
                                 b'\x8d@\x00\x00\x00\xa0r}\x8d@\x00\x00\x00\xe0\xd1\x8b\x8d@\x00\x00\x00\x80n\x8d\x8d'
                                 b'@\x00\x00\x00@\x08\x8f\x8d@\x00\x00\x00\x00\xa2\x90\x8d@\x00\x00\x00\xa0<\x92\x8d'
                                 b'@\x00\x00\x00\x80\xd7\x93\x8d@\x00\x00\x00\xc0r\x95\x8d@\x00\x00\x00\x80\xa9\x96'
                                 b'\x8d@\x00\x00\x00 '
                                 b'\x0e\x97\x8d@\x00\x00\x00\x80\xa3\x98\x8d@\x00\x00\x00\x80G\xa3\x8d@\x00\x00\x00'
                                 b'\xe0N\xab\x8d@\x00\x00\x00\x00U\xb3\x8d@\x00\x00\x00\xc0s\xb4\x8d@\x00\x00\x00\xa0'
                                 b'\xe4\xb9\x8d@\x00\x00\x00\xe0\xeb\xbb\x8d@\x00\x00\x00`e\xbc\x8d@\x00\x00\x00\x80'
                                 b'\xee\xbd\x8d@\x00\x00\x00@\xef\xbf\x8d@\x00\x00\x00\xa0\xf2\xc1\x8d@\x00\x00\x00 '
                                 b'\xe9\xc3\x8d@\x00\x00\x00 '
                                 b'I\xc4\x8d@\x00\x00\x00\xe0J\xc8\x8d@\x00\x00\x00`\xee\xdd\x8d@\x00\x00\x00@\xef'
                                 b'\xdf\x8d@\x00\x00\x00`\xed\xe1\x8d@\x00\x00\x00\x80\xf1\xe3\x8d@\x00\x00\x00\xc0'
                                 b'\xf6\xe5\x8d@\x00\x00\x00\x80_\x01\x8e@\x00\x00\x00`\xe5\x11\x8e@\x00\x00\x00\x00'
                                 b'\xe2\x15\x8e@\x00\x00\x00`\xf0+\x8e@\x00\x00\x00\xc0\xf5-\x8e@\x00\x00\x00@\xf7'
                                 b'/\x8e@\x00\x00\x00\xc0G1\x8e@\x00\x00\x00\x00\xf51\x8e@\x00\x00\x00\x80\xe13\x8e'
                                 b'@\x00\x00\x00 '
                                 b'N4\x8e@\x00\x00\x00@J8\x8e@\x00\x00\x00\xa0R<\x8e@\x00\x00\x00\x00\xf6?\x8e@\x00'
                                 b'\x00\x00\x00Y@\x8e@\x00\x00\x00\xe0eA\x8e@\x00\x00\x00 ('
                                 b'D\x8e@\x00\x00\x00@-H\x8e@\x00\x00\x00\x80\x0eL\x8e@\x00\x00\x00\xa0\xf3O\x8e@\x00'
                                 b'\x00\x00@\xf9Q\x8e@\x00\x00\x00@\xfcS\x8e@\x00\x00\x00\xc0\xf9U\x8e@\x00\x00\x00'
                                 b'`\xfbW\x8e@\x00\x00\x00\xa0\xfbY\x8e@\x00\x00\x00`\xfe['
                                 b'\x8e@\x00\x00\x00\xe0\xben\x8e@\x00\x00\x00`lq\x8e@\x00\x00\x00@\x15t\x8e@\x00\x00'
                                 b'\x00\xa0\xc2v\x8e@\x00\x00\x00\xc0fy\x8e@\x00\x00\x00`\x1e|\x8e@\x00\x00\x00\x00'
                                 b'\xc6~\x8e@\x00\x00\x00\x00n\x81\x8e@\x00\x00\x00\xc0\xc7\x9e\x8e@\x00\x00\x00\x00u'
                                 b'\xa1\x8e@\x00\x00\x00\x00"\xa4\x8e@\x00\x00\x00\x00\x9e\xa4\x8e@\x00\x00\x00\xc0'
                                 b'\xcc\xa6\x8e@\x00\x00\x00\xc0y\xa9\x8e@\x00\x00\x00\x00$\xac\x8e@\x00\x00\x00\x80'
                                 b'.\xb4\x8e@\x00\x00\x00`.\xb8\x8e@\x00\x00\x00 7\xbc\x8e@\x00\x00\x00 '
                                 b'\xfc\xc3\x8e@\x00\x00\x00\xa0Y\xc9\x8e@\x00\x00\x00\xe0\xfb\xcb\x8e@\x00\x00\x00'
                                 b'\x00\xb2\xce\x8e@\x00\x00\x00\x80['
                                 b'\xd1\x8e@\x00\x00\x00`\xf9\xd3\x8e@\x00\x00\x00\xa0\xc9\xdb\x8e@\x00\x00\x00\x80'
                                 b'\xcd\xe3\x8e@\x00\x00\x00\xa0\x0c\xf4\x8e@\x00\x00\x00`\xb7\xf6\x8e@\x00\x00\x00'
                                 b'\x80c\xf9\x8e@\x00\x00\x00\xc0\x0f\xfc\x8e@\x00\x00\x00\xc0\xbc\xfe\x8e@\x00\x00'
                                 b'\x00\xe0g\x01\x8f@\x00\x00\x00 '
                                 b'\t\x12\x8f@\x00\x00\x00\xe0\x07\x14\x8f@\x00\x00\x00\xe0\x15\x16\x8f@\x00\x00\x00 '
                                 b'\x19,\x8f@\x00\x00\x00`\xe8K\x8f@\x00\x00\x00\x00Ud\x8f@\x00\x00\x00\x80Wl\x8f'
                                 b'@\x00\x00\x00\xa0\xd1s\x8f@\x00\x00\x00\xe0\xd6{'
                                 b'\x8f@\x00\x00\x00\x80k\x80\x8f@\x00\x00\x00 '
                                 b'.\x82\x8f@\x00\x00\x00`\xd9\x83\x8f@\x00\x00\x00\xc0j\x84\x8f@\x00\x00\x00\x00'
                                 b'+\x86\x8f@\x00\x00\x00\xa0g\x88\x8f@\x00\x00\x00@\xd8\x8b\x8f@\x00\x00\x00\xc0F'
                                 b'\x98\x8f@\x00\x00\x00 M\x9c\x8f@\x00\x00\x00`t\xc8\x8f@\x00\x00\x00 '
                                 b'x\xcc\x8f@\x00\x00\x00 '
                                 b'w\xd0\x8f@\x00\x00\x00\xe0|\xd4\x8f@\x00\x00\x00`\x92\xdb\x8f@\x00\x00\x00\xa0'
                                 b'\'\xe0\x8f@\x00\x00\x00`\x97\xe3\x8f@\x00\x00\x00 '
                                 b'\x13\xe4\x8f@\x00\x00\x00`\'\xe6\x8f@\x00\x00\x00\xe0\x99\xeb\x8f@\x00\x00\x00'
                                 b'\x80k\xfc\x8f@\x00\x00\x00\x80\x17\xfe\x8f@\x00\x00\x00\xa0&\x00\x90@\x00\x00\x00 '
                                 b'\'\x02\x90@\x00\x00\x00\xc0*\x04\x90@\x00\x00\x00\xe0)\x06\x90@\x00\x00\x00 '
                                 b'\x12\x0c\x90@\x00\x00\x00 '
                                 b'\x15\r\x90@\x00\x00\x00\x80\x15\x0e\x90@\x00\x00\x00\xc0\x15\x0f\x90@\x00\x00\x00'
                                 b'\xa0\x17\x10\x90@\x00\x00\x00`\x14\x11\x90@\x00\x00\x00@,$\x90@\x00\x00\x00 '
                                 b'-&\x90@\x00\x00\x00\xa0/('
                                 b'\x90@\x00\x00\x00\xe0@2\x90@\x00\x00\x00\xa0@4\x90@\x00\x00\x00\xa0B6\x90@\x00\x00'
                                 b'\x00\xc07:\x90@\x00\x00\x00\xa0EV\x90@\x00\x00\x00\x80IX\x90@\x00\x00\x00\xa0KZ'
                                 b'\x90@\x00\x00\x00\x00K\\\x90@\x00\x00\x00 '
                                 b'0r\x90@\x00\x00\x00\xa04t\x90@\x00\x00\x00 '
                                 b'7v\x90@\x00\x00\x00\x803x\x90@\x00\x00\x00\xe06\x96\x90@\x00\x00\x00@8\x98\x90'
                                 b'@\x00\x00\x00\x805\x9a\x90@\x00\x00\x00`=\x9c\x90@\x00\x00\x00\xa0\xd7\xbc\x90'
                                 b'@\x00\x00\x00\xe01\xbe\x90@\x00\x00\x00 '
                                 b'>\xed\x90@\x00\x00\x00\xc0=\xee\x90@\x00\x00\x00`^\x18\x91@\x00\x00\x00\xc0E&\x91'
                                 b'@\x00\x00\x00 '
                                 b'<2\x91@\x00\x00\x00\x00A6\x91@\x00\x00\x00@A:\x91@\x00\x00\x00\xa0;h\x91@\x00\x00'
                                 b'\x00\x80Oz\x91@\x00\x00\x00\xc0A~\x91@\x00\x00\x00 '
                                 b'D\x82\x91@\x00\x00\x00@?\x86\x91@\x00\x00\x00 '
                                 b'G\x91\x91@\x00\x00\x00\xe0A\x93\x91@\x00\x00\x00 '
                                 b'\xf6\x98\x91@\x00\x00\x00`\xac\x9b\x91@\x00\x00\x00\x80\xaf\xaf\x91@\x00\x00\x00'
                                 b'\xc0\x00\xb1\x91@\x00\x00\x00\x80\x1c\xb2\x91@\x00\x00\x00\xc0!\xb6\x91@\x00\x00'
                                 b'\x00\xe0\x1f\xba\x91@\x00\x00\x00\xe0\x96\xbb\x91@\x00\x00\x00@i\xd6\x91@\x00\x00'
                                 b'\x00\xe0g\xda\x91@\x00\x00\x00\x00}\xea\x91@\x00\x00\x00 '
                                 b'0\xfa\x91@\x00\x00\x00\x005\xfe\x91@\x00\x00\x00\x80\x84\x1a\x92@\x00\x00\x00\xc0v'
                                 b'\x1e\x92@\x00\x00\x00\xa0w '
                                 b'\x92@\x00\x00\x00\xe0y"\x92@\x00\x00\x00\xe0p&\x92@\x00\x00\x00\xa0|('
                                 b'\x92@\x00\x00\x00\x00T2\x92@\x00\x00\x00@\xb03\x92@\x00\x00\x00\xe0\x06I\x92@\x00'
                                 b'\x00\x00`[J\x92@\x00\x00\x00\xe0\xb2K\x92@\x00\x00\x00\x00\nM\x92@\x00\x00\x00\x00'
                                 b'`N\x92@\x00\x00\x00`\xb4O\x92@\x00\x00\x00\x00h^\x92@\x00\x00\x00 '
                                 b'd`\x92@\x00\x00\x00@gb\x92@\x00\x00\x00@gd\x92@\x00\x00\x00 '
                                 b'\xacj\x92@\x00\x00\x00\x80\xafn\x92@\x00\x00\x00\xc0ez\x92@\x00\x00\x00\x80\x93'
                                 b'\xb6\x92@\x00\x00\x00 \x93\xb8\x92@\x00\x00\x00`j\xba\x92@\x00\x00\x00 '
                                 b'\x9d\xba\x92@\x00\x00\x00\xc0e\xbe\x92@\x00\x00\x00@v\xd4\x92@\x00\x00\x00@\x8f'
                                 b'\xea\x92@\x00\x00\x00@\x90\xee\x92@\x00\x00\x00 '
                                 b'\x8f\xf6\x92@\x00\x00\x00\x00\x85\xf8\x92@\x00\x00\x00\xe0\x91\xfa\x92@\x00\x00'
                                 b'\x00\x00\x92\xfe\x92@\x00\x00\x00\xe0t\x02\x93@\x00\x00\x00\xc0x\x06\x93@\x00\x00'
                                 b'\x00\xe0y\n\x93@\x00\x00\x00\xe0z\x0e\x93@\x00\x00\x00\xc03A\x93@\x00\x00\x00 '
                                 b'3I\x93@\x00\x00\x00\xc0\xe1K\x93@\x00\x00\x00\xa05M\x93@\x00\x00\x00`\x92N\x93'
                                 b'@\x00\x00\x00\xe0\xddO\x93@\x00\x00\x00@5a\x93@\x00\x00\x00@\x8db\x93@\x00\x00\x00'
                                 b'\x80\xe3c\x93@\x00\x00\x00`9e\x93@\x00\x00\x00\xa0\x90f\x93@\x00\x00\x00\xc0tv\x93'
                                 b'@\x00\x00\x00\x00vz\x93@\x00\x00\x00\xe0\xaf\x82\x93@\x00\x00\x00`\xad\x84\x93'
                                 b'@\x00\x00\x00 '
                                 b'\x9d\xc2\x93@\x00\x00\x00@\x9c\xc4\x93@\x00\x00\x00\xc0\xeb\xcf\x93@\x00\x00\x00@G'
                                 b'\xd1\x93@\x00\x00\x00\xa0\x98\xd2\x93@\x00\x00\x00\xa0\xf1\xd3\x93@\x00\x00\x00'
                                 b'\xa0?\xd5\x93@\x00\x00\x00\xa0\xee\xe7\x93@\x00\x00\x00@F\xe9\x93@\x00\x00\x00\xa0'
                                 b'\x9c\xea\x93@\x00\x00\x00`\xf3\xeb\x93@\x00\x00\x00@K\xed\x93@\x00\x00\x00@\xe2'
                                 b'\x02\x94@\x00\x00\x00\xe0\xb6\x12\x94@\x00\x00\x00@\xbd\x16\x94@\x00\x00\x00 '
                                 b'\xef\x1b\x94@\x00\x00\x00@J\x1d\x94@\x00\x00\x00@\x9f\x1e\x94@\x00\x00\x00\xc0\xf1'
                                 b'\x1f\x94@\x00\x00\x00`R!\x94@\x00\x00\x00@\xa9"\x94@\x00\x00\x00\xc0\xf93\x94@\x00'
                                 b'\x00\x00\x00Q5\x94@\x00\x00\x00\xc0\xa66\x94@\x00\x00\x00\x00\xfc7\x94@\x00\x00'
                                 b'\x00@P9\x94@\x00\x00\x00\xa0\xc2~\x94@\x00\x00\x00\xa0\xbf\x84\x94@\x00\x00\x00'
                                 b'\xe0\x98\x92\x94@\x00\x00\x00`\xd1\xae\x94@\x00\x00\x00\xc0\xd7\xb2\x94@\x00\x00'
                                 b'\x00\xe0\xaf\xc6\x94@\x00\x00\x00\x00\x90\xce\x94@\x00\x00\x00`\x94\xd2\x94@\x00'
                                 b'\x00\x00@\x96\xd6\x94@\x00\x00\x00 '
                                 b'\xd0\xf6\x94@\x00\x00\x00\xa0\xd0\xfa\x94@\x00\x00\x00\xa0\xd1\xfe\x94@\x00\x00'
                                 b'\x00 \xb2.\x95@\x00\x00\x00 '
                                 b'\xb72\x95@\x00\x00\x00\xa0\xc0f\x95@\x00\x00\x00\xa0\xb0v\x95@\x00\x00\x00@\xb5z'
                                 b'\x95@\x00\x00\x00\x80\xb3~\x95@\x00\x00\x00\x80\x96\x8e\x95@\x00\x00\x00@\xde\xa0'
                                 b'\x95@\x00\x00\x00 '
                                 b'\xde\xa2\x95@\x00\x00\x00\xe0\xf3\x12\x96@\x00\x00\x00\xc0\xf7\x16\x96@\x00\x00'
                                 b'\x00\x00\xf7\x1a\x96@\x00\x00\x00 '
                                 b'\x1b;\x96@\x00\x00\x00@\x17?\x96@\x00\x00\x00\xe0\xe0\x92\x96@\x00\x00\x00`\xe2'
                                 b'\x96\x96@\x00\x00\x00\xe0\xe3\x9a\x96@\x00\x00\x00 \xfc\xba\x96@\x00\x00\x00 '
                                 b'\xff\xbe\x96@\x00\x00\x00\x00\xd6\xda\x96@\x00\x00\x00\xc0\xd8\xde\x96@\x00\x00'
                                 b'\x00 \xe0\xe2\x96@\x00\x00\x00\xe0>W\x97@\x00\x00\x00\xe0\xbbZ\x97@\x00\x00\x00@D['
                                 b'\x97@\x00\x00\x00 '
                                 b'\xbb^\x97@\x00\x00\x00\x80\xc1b\x97@\x00\x00\x00\xe0\ng\x97@\x00\x00\x00\xc0\xbe'
                                 b'\xa9\x97@\x00\x00\x00`\x08\xaf\x97@\x00\x00\x00\x00\x14\xb3\x97@\x00\x00\x00\x00'
                                 b'\x12\xb7\x97@\x00\x00\x00@A?\x98@\x00\x00\x00\xe0VG\x98@\x00\x00\x00`\x1d\xbf\x98'
                                 b'@\x00\x00\x00\x80+\xc3\x98@\x00\x00\x00 '
                                 b'\x97\x1b\x99@\x00\x00\x00@\x9c\x1f\x99@\x00\x00\x00\xa0Q;\x99@\x00\x00\x00 '
                                 b'v\x9b\x99@\x00\x00\x00\x80\x8f\x9f\x9a@\x00\x00\x00 \xb1\xe7\x9a@\x00\x00\x00 '
                                 b'\xb5\xeb\x9a@\x00\x00\x00\x80\xbd\xef\x9a@\x00\x00\x00 \xb9\xf3\x9a@\x00\x00\x00 '
                                 b'q\'\x9b@\x00\x00\x00\x00q+\x9b@\x00\x00\x00\xc0\x95g\x9b@\x00\x00\x00\xc0\x98k\x9b'
                                 b'@\x00\x00\x00@\xa0o\x9b@\x00\x00\x00 '
                                 b'\x9ds\x9b@\x00\x00\x00\x00R\xa7\x9b@\x00\x00\x00\x00V\xab\x9b@\x00\x00\x00\xa0U'
                                 b'\xaf\x9b@\x00\x00\x00 '
                                 b'E4\x9e@\x00\x00\x00\x00e|\x9f@\x00\x00\x00\xe0D\t\xa5@\x00\x00\x00\xe0\x96\xae\xa6'
                                 b'@\x00\x00\x00`\xce\x8a\xae@\x00\x00\x00\x00\xbf\xa5\xae@')
        assert results[0].intensity == (b'\x00\x00\x00 \xc7P\xdc@\x00\x00\x00\xa0\xdf\x9c\xaf@\x00\x00\x00\x80\x0f\xe8'
                                        b'\xaf@\x00\x00\x00`\x95<\x05A\x00\x00\x00\xc0\xea\xb1\xb5@\x00\x00\x00\xa0'
                                        b'\x96\x05\xb1@\x00\x00\x00`\x914\xbc@\x00\x00\x00\xe0\xbf\x02\xbe@\x00\x00'
                                        b'\x00@\xff\x03\xf6@\x00\x00\x00 \x11g\xb7@\x00\x00\x00 '
                                        b'\xc7\x0b\xab@\x00\x00\x00\xa0\x13\xf4\xac@\x00\x00\x00\x80!\n\xab@\x00\x00'
                                        b'\x00@\x12\xd0\xae@\x00\x00\x00 3\x1b\xe3@\x00\x00\x00 '
                                        b'\xe5\x1c\xe3@\x00\x00\x00\xa0\xcd\xb1\xd7@\x00\x00\x00\xc0\xfb\xd8\xcc@\x00'
                                        b'\x00\x00\x00\x9dF\xef@\x00\x00\x00`\x18\xfb\xb8@\x00\x00\x00\x00\xbc\xd6'
                                        b'\xb0@\x00\x00\x00\xc0\xec1\xf0@\x00\x00\x00\xa0\xa0\xdd\xb0@\x00\x00\x00'
                                        b'\xa0\x89g\xe1@\x00\x00\x00 '
                                        b'\xe4~\xb2@\x00\x00\x00`\x18\xca\xe6@\x00\x00\x00\x80\xee\xa1\xb4@\x00\x00'
                                        b'\x00\xa0f\x9e\xf3@\x00\x00\x00@*\xa6\xb2@\x00\x00\x00\xe0`\x96\xac@\x00\x00'
                                        b'\x00\xc0\xf4\xe7\xbf@\x00\x00\x00@\x9c\xa5\xbb@\x00\x00\x00\xa0\x107\xc3'
                                        b'@\x00\x00\x00`C^\xb7@\x00\x00\x00`\xb5 \xae@\x00\x00\x00 '
                                        b'\xdd;\xf2@\x00\x00\x00 5b\xb6@\x00\x00\x00\xe01\xa7\xdc@\x00\x00\x00 '
                                        b'r7\xae@\x00\x00\x00@c6\xc8@\x00\x00\x00\x00d\x07\xb1@\x00\x00\x00@\xb9\xca'
                                        b'\xf6@\x00\x00\x00\x80\xd4\x97\xb4@\x00\x00\x00\x80\xe6\xce\xb7@\x00\x00\x00'
                                        b'\xe0\xc6\xb5\xad@\x00\x00\x00`\x8f$\xce@\x00\x00\x00\xa0sF\xbb@\x00\x00\x00 '
                                        b'N\x87\xc3@\x00\x00\x00`\xbf_\xad@\x00\x00\x00\x00\xd5_\xbc@\x00\x00\x00'
                                        b'@\x0e%\xf6@\x00\x00\x00@\xfbR\xbc@\x00\x00\x00`\xd8*\xb3@\x00\x00\x00\xe0^R'
                                        b'\xe3@\x00\x00\x00\xe0!k\xaf@\x00\x00\x00\xa0\xd9\xbd\xf1@\x00\x00\x00 '
                                        b'\xeby\xc3@\x00\x00\x00\xc0A\x9d\xc9@\x00\x00\x00@\xd5\x16\xd7@\x00\x00\x00'
                                        b'\x80\xbd\xab\xb8@\x00\x00\x00@\x18\xab\xb0@\x00\x00\x00\xc0S\xc5\xab@\x00'
                                        b'\x00\x00`\x13\xef\xb3@\x00\x00\x00@7\xc7\xee@\x00\x00\x00 '
                                        b'\xf9\xf5\xc5@\x00\x00\x00\x00\xe1\x80\xeb@\x00\x00\x00 '
                                        b'B\x96\xc8@\x00\x00\x00\x80dA\xba@\x00\x00\x00\xe0\xc2\xb8\xd0@\x00\x00\x00'
                                        b'\xe0\xfd\x91\xb9@\x00\x00\x00\xc0\x83\xf5\xd2@\x00\x00\x00\xc0:\x12\xb1'
                                        b'@\x00\x00\x00\xc0Gj\xad@\x00\x00\x00`[\x0b\xab@\x00\x00\x00 '
                                        b'b\x8a\xb7@\x00\x00\x00\x00\x13\xab\xb1@\x00\x00\x00@\xadC\xbd@\x00\x00\x00'
                                        b'\xa0\x9a\x0b\xe0@\x00\x00\x00\x804\x85\xd0@\x00\x00\x00`R\xc2\xf6@\x00\x00'
                                        b'\x00@\x95\x86\xbc@\x00\x00\x00\x80\xf3\xef\xc1@\x00\x00\x00\x80\x98\xfc\xd2'
                                        b'@\x00\x00\x00\xc0\xb3\xcd\xb1@\x00\x00\x00@\xa92\xb6@\x00\x00\x00\x80\x1e'
                                        b'\xc9\xbe@\x00\x00\x00\xc0\x8e{\xb2@\x00\x00\x00\xa0,'
                                        b'\xde\xb5@\x00\x00\x00\x80\x91\xe4\xca@\x00\x00\x00\x00N\xe7\xd8@\x00\x00'
                                        b'\x00\xc0\xbe\xf5\x05A\x00\x00\x00`\x15\x19\xd5@\x00\x00\x00\x80\x94\xee\xc2'
                                        b'@\x00\x00\x00@\xf4z\xb9@\x00\x00\x00\xe0\x12x\xaf@\x00\x00\x00 '
                                        b'\x93\xf3\xd6@\x00\x00\x00\xa0\xd0/\xc6@\x00\x00\x00\x80R\xfa\xab@\x00\x00'
                                        b'\x00\x00\xd6\xec\xcf@\x00\x00\x00\xa0\x1d\xe3\xe2@\x00\x00\x00@\xf0\xc0\xb1'
                                        b'@\x00\x00\x00\xe0\t\xf3\xb0@\x00\x00\x00@\xd4\x03\xc5@\x00\x00\x00\x00\xce'
                                        b'\x91\xb5@\x00\x00\x00 '
                                        b'\x8f\x1c\xc5@\x00\x00\x00\x00\x91\xbc\xdf@\x00\x00\x00@\xbc\xd6\xb9@\x00'
                                        b'\x00\x00\x00\x94i\xb5@\x00\x00\x00\xa0d\xaf\x02A\x00\x00\x00@\x19\x1a\xe4'
                                        b'@\x00\x00\x00\xe0\x1a\x8b\xd1@\x00\x00\x00\xa0{'
                                        b'\xfd\xae@\x00\x00\x00\x80\xbe\x03\xc0@\x00\x00\x00 \xa7R\xe8@\x00\x00\x00 '
                                        b'\xb7C\xc6@\x00\x00\x00\x80\x87\xaf\xea@\x00\x00\x00\xa0('
                                        b'\xee\xc0@\x00\x00\x00\xc0\x17~\xb5@\x00\x00\x00 '
                                        b'\xf64\xb6@\x00\x00\x00\xe0i\x7f\xb2@\x00\x00\x00@\xf8o\x0eA\x00\x00\x00 '
                                        b'\xcd/\xd4@\x00\x00\x00\x80-y\xe1@\x00\x00\x00\xe0)\x85\xbf@\x00\x00\x00'
                                        b'\x00mZ\xae@\x00\x00\x00\xc0?W\xd1@\x00\x00\x00 '
                                        b'\xf5\xf4\xd3@\x00\x00\x00`\xdf\xfa\xb9@\x00\x00\x00\x00\xaf>\xbd@\x00\x00'
                                        b'\x00 '
                                        b'cu\xb4@\x00\x00\x00\xa0`z\xc7@\x00\x00\x00\x00W\xd7\xc9@\x00\x00\x00\x80'
                                        b'\xf1\xd0\xb5@\x00\x00\x00\xe0\x04H\xce@\x00\x00\x00\x80s\xb1\xe2@\x00\x00'
                                        b'\x00`\x9d\xa6\xb4@\x00\x00\x00 \xbe*\xbc@\x00\x00\x00 '
                                        b'\xf4$\xe7@\x00\x00\x00\xa0\x1c\xcd\xe6@\x00\x00\x00\xe0\xd7\xcf\xba@\x00'
                                        b'\x00\x00\x00s\xbb\xc1@\x00\x00\x00\x80A\xdd\xd1@\x00\x00\x00\xc0\xeeu\xae'
                                        b'@\x00\x00\x00 '
                                        b'\xbb\x0b\xd3@\x00\x00\x00\xa0\x91\x15\xb6@\x00\x00\x00\xe0\xde\xe2\xb0@\x00'
                                        b'\x00\x00\x00\xf6\xcd\xc0@\x00\x00\x00@\x95\x95\xc5@\x00\x00\x00\xe0\xb96'
                                        b'\xaf@\x00\x00\x00\xa0\x15\xa6\xca@\x00\x00\x00\xc0\xde\xdb\xe5@\x00\x00\x00 '
                                        b'\x10:\xb7@\x00\x00\x00 '
                                        b'\x88\xde\xb0@\x00\x00\x00\x00\xb0\x10\xc7@\x00\x00\x00@\xacj\x04A\x00\x00'
                                        b'\x00\x80+\x85\xc2@\x00\x00\x00@\xc2K\xda@\x00\x00\x00\x00=C\xc4@\x00\x00'
                                        b'\x00\x00\xc5n\xc4@\x00\x00\x00\xa0G|\xb0@\x00\x00\x00@l\x02\xc6@\x00\x00'
                                        b'\x00`c|\xca@\x00\x00\x00 Kn\xb7@\x00\x00\x00 '
                                        b'\x10\x8f\x11A\x00\x00\x00\xe0W\xf4\xf7@\x00\x00\x00\x80N\x97\xd0@\x00\x00'
                                        b'\x00\xa0\xb8\xb2\xbc@\x00\x00\x00@\xd8\xb9\xb4@\x00\x00\x00`5\xfb\xc1@\x00'
                                        b'\x00\x00\x80\x8b!\xcb@\x00\x00\x00\xa0\xdc\xae\xe0@\x00\x00\x00\xa0\xf8'
                                        b'|\xb1@\x00\x00\x00 '
                                        b'\xaak\xc9@\x00\x00\x00\x80\x16"\xb6@\x00\x00\x00\xa0\x02/\xd4@\x00\x00\x00'
                                        b'@\xcb\x17\x03A\x00\x00\x00 p\x8a\xe9@\x00\x00\x00 '
                                        b']H\xe7@\x00\x00\x00\x80+\x05\xd2@\x00\x00\x00\x00\\*\xb6@\x00\x00\x00\x00m'
                                        b'.\xbd@\x00\x00\x00`\x14\xd5\xbb@\x00\x00\x00\x80\xaf,'
                                        b'\xb9@\x00\x00\x00\xc02T\xe0@\x00\x00\x00\x00L\xf8\xb0@\x00\x00\x00\x80\xbcK'
                                        b'\xc2@\x00\x00\x00\xa0['
                                        b'\xdb\xcb@\x00\x00\x00@\xfa\xc2\xb0@\x00\x00\x00`_\x9e\xaf@\x00\x00\x00'
                                        b'\xc08a\xc0@\x00\x00\x00\x80E\xba\xae@\x00\x00\x00`]\xf0\xc2@\x00\x00\x00'
                                        b'\xc0\xc6z\xb0@\x00\x00\x00 '
                                        b'\xfd\x16\xd9@\x00\x00\x00\xe0\xe7\t\xbb@\x00\x00\x00\xc0k\xcc\xc2@\x00\x00'
                                        b'\x00\x80)\xf2\xfe@\x00\x00\x00@g\\\xe7@\x00\x00\x00\xa0\xd8=\xbe@\x00\x00'
                                        b'\x00\xa0\xdf[\xc3@\x00\x00\x00\xe0*<\xc4@\x00\x00\x00`\xdb '
                                        b'\xce@\x00\x00\x00@\x81I\xb2@\x00\x00\x00 '
                                        b'\xa5\x9b\xc6@\x00\x00\x00\xa0\xb3\xff\xdb@\x00\x00\x00`\xf8\xfc\xb4@\x00'
                                        b'\x00\x00 '
                                        b'G\xbf\x03A\x00\x00\x00`\xbf\xdd\xdf@\x00\x00\x00\xc02=\xe1@\x00\x00\x00\x80'
                                        b'&\xae\xb1@\x00\x00\x00\xa0:\x01\xb0@\x00\x00\x00@\x11\x9a\xd9@\x00\x00\x00'
                                        b'\x00\xfb\xb2\xb9@\x00\x00\x00\xa0O;\xb4@\x00\x00\x00\x00\x1b\xc7\xc1@\x00'
                                        b'\x00\x00\x00v2\xb3@\x00\x00\x00 \x07C\xcf@\x00\x00\x00 '
                                        b'\xa0<\xaf@\x00\x00\x00@z\xee\xb1@\x00\x00\x00\x00\xecK\xb0@\x00\x00\x00\xe0'
                                        b'\xa94\xb5@\x00\x00\x00\xa0\x98\xa9\xb6@\x00\x00\x00`\x80\x8d\xbd@\x00\x00'
                                        b'\x00\xa0\x84<\xbf@\x00\x00\x00`\x04\xee\xba@\x00\x00\x00\xe0r\x0e\xc6@\x00'
                                        b'\x00\x00\xe0R\x1e\xee@\x00\x00\x00`!\x08\xde@\x00\x00\x00`\xab('
                                        b'\xc6@\x00\x00\x00\x80\x8f\xda\xaf@\x00\x00\x00\xc0\x8d\xd1\xb0@\x00\x00\x00'
                                        b'\x00\xfd\xae\xb0@\x00\x00\x00\xe0\xba\x00\xcc@\x00\x00\x00@L\x02\x11A\x00'
                                        b'\x00\x00`\x1f\x8a\x01A\x00\x00\x00\xa0T\n\xe8@\x00\x00\x00\x80\xdd\x8a\xe3'
                                        b'@\x00\x00\x00\xe0\xe7y\xc4@\x00\x00\x00@2G\xb8@\x00\x00\x00\xc0\x9c\x83\xb3'
                                        b'@\x00\x00\x00\xc0\x18\xbf\xea@\x00\x00\x00\xe0O\x05"A\x00\x00\x00\x80\xd5$'
                                        b'\xc6@\x00\x00\x00\xc0\x10\xdc\x03A\x00\x00\x00\x80\xa0\xa0\xd7@\x00\x00\x00'
                                        b'\x80\xb0\xea\xb2@\x00\x00\x00 '
                                        b'\n\xd2\xc0@\x00\x00\x00\x80\xd9w\x03A\x00\x00\x00@\xc1\xc0\xe7@\x00\x00\x00'
                                        b'\xa0\xfd\x95\xb0@\x00\x00\x00\xc0\xd7\x83\xb1@\x00\x00\x00@Z}\xb8@\x00\x00'
                                        b'\x00@\x00\x8a\xb3@\x00\x00\x00@,'
                                        b'\xdb\xed@\x00\x00\x00\x00\x93\x81\xe8@\x00\x00\x00@6T\xc9@\x00\x00\x00\xe0'
                                        b'\xa8\xb2\xb9@\x00\x00\x00\x80\x94\xdb\xc9@\x00\x00\x00\x00\xd1l\xc0@\x00'
                                        b'\x00\x00\xe0\n\xc0\xb1@\x00\x00\x00\xe0\x8f\x10\xd8@\x00\x00\x00 '
                                        b'\xf9\xfc\xbd@\x00\x00\x00\xc0\x86\x1b\xaf@\x00\x00\x00\xe0`\xaf\xb3@\x00'
                                        b'\x00\x00@\x87a\xad@\x00\x00\x00@\x9f\r\xe7@\x00\x00\x00\x80\xc4\xc9\xdb'
                                        b'@\x00\x00\x00\x80y8\xbf@\x00\x00\x00\x00l['
                                        b'\xb4@\x00\x00\x00@\x1b\xa4\xb0@\x00\x00\x00\x00\nY\xd2@\x00\x00\x00\xe0\xf2'
                                        b'\xcb\xb0@\x00\x00\x00\xa0FU\xb1@\x00\x00\x00\xe0\x8d\xd6\xb4@\x00\x00\x00'
                                        b'\x003a\xf2@\x00\x00\x00 \xcf\xf4\xbd@\x00\x00\x00\x00;\x9e\xe8@\x00\x00\x00 '
                                        b'r9\xb2@\x00\x00\x00\xa0x\x1e\xc4@\x00\x00\x00 '
                                        b'\xdbW\xc0@\x00\x00\x00\x80\xebo\xb4@\x00\x00\x00\x00\xccL\xc9@\x00\x00\x00 '
                                        b'\x8c\xaa\xb8@\x00\x00\x00\x806\xea\xb3@\x00\x00\x00\xe0\x9c\xf6\xba@\x00'
                                        b'\x00\x00\x00P\x83\xc9@\x00\x00\x00`\xc9\xac\xaf@\x00\x00\x00\x00p\xfc\xe3'
                                        b'@\x00\x00\x00@\xfa\xe5\xdd@\x00\x00\x00\xa0:n\xb5@\x00\x00\x00\x00\xcf\x99'
                                        b'\xb1@\x00\x00\x00\xc0\x1ep\xb0@\x00\x00\x00 '
                                        b'\x80\xa2\xb3@\x00\x00\x00\xa0\xa9\xea\xb9@\x00\x00\x00\xc0x\n\xf8@\x00\x00'
                                        b'\x00\x00\x8f\xbf\xb2@\x00\x00\x00\xe0\r\xdf\xb3@\x00\x00\x00\xe0\xb2\x17'
                                        b'\xf2@\x00\x00\x00\x80\xba[\xd6@\x00\x00\x00\x00\x8e{'
                                        b'\xbd@\x00\x00\x00\xe0\x14\x16\xb6@\x00\x00\x00\xc0>S\xc3@\x00\x00\x00 '
                                        b'\xfa\xbc\xea@\x00\x00\x00\xc0\x10c\xfc@\x00\x00\x00\xa0\x05\xc2\xd2@\x00'
                                        b'\x00\x00\x00)\x92\xe0@\x00\x00\x00\x00\xc5Z\xbe@\x00\x00\x00\x80\xeec\xc5'
                                        b'@\x00\x00\x00\xc0\xb6}\xb2@\x00\x00\x00 '
                                        b'\xa9\xb5\xee@\x00\x00\x00\x00\x9b\xd9\xeb@\x00\x00\x00\x80\xf6\t\xd2@\x00'
                                        b'\x00\x00\xe0yB\xaf@\x00\x00\x00@\xfe\xe0\xb4@\x00\x00\x00\xe0h\x07\xb5@\x00'
                                        b'\x00\x00`|$\xb7@\x00\x00\x00 \xf8I\xef@\x00\x00\x00 '
                                        b'\xb2s\xe0@\x00\x00\x00`%i\xd7@\x00\x00\x00\xe0n\xbc\xb5@\x00\x00\x00\xe0'
                                        b'`\xec\xd1@\x00\x00\x00\x00\x8b\x90\xb4@\x00\x00\x00\xc0\x0e\xcc\xb8@\x00'
                                        b'\x00\x00`b\x98\xb5@\x00\x00\x00\x00\x0b@\xb9@\x00\x00\x00 '
                                        b'\xc3!\xf0@\x00\x00\x00\x80o\xed\xeb@\x00\x00\x00\x80\x843\xe1@\x00\x00\x00 '
                                        b'\xde\xc6\xc6@\x00\x00\x00 \xe5)\xbf@\x00\x00\x00 '
                                        b'\x82\x96\xb5@\x00\x00\x00`Z,'
                                        b'\xb1@\x00\x00\x00\x00`e\xb3@\x00\x00\x00\x80\xbeS\xb8@\x00\x00\x00\xc0\x14'
                                        b'\xf0\xc1@\x00\x00\x00\xc0$t\xc7@\x00\x00\x00\xa0J\xe5\xcc@\x00\x00\x00\xa0'
                                        b'?\x99\xe6@\x00\x00\x00\xe0\xd5\xc1\xc5@\x00\x00\x00`\x13\x81\xe6@\x00\x00'
                                        b'\x00\x00\xac\x1e\xd5@\x00\x00\x00\x00k\x8f\xba@\x00\x00\x00\x80\xac\xce\xc9'
                                        b'@\x00\x00\x00`gd\xbb@\x00\x00\x00\xc0i\xb0\xc0@\x00\x00\x00\xc0.\x05\xb1'
                                        b'@\x00\x00\x00@\xb3\xfb\xe1@\x00\x00\x00\xc0\xdee\xb7@\x00\x00\x00`v$\xdb'
                                        b'@\x00\x00\x00\x00=\xf9\xc8@\x00\x00\x00\x00@f\xcb@\x00\x00\x00\x00\xec\xfc'
                                        b'\xcc@\x00\x00\x00\xc0\xb3\xd1\xc0@\x00\x00\x00\xc0\x08\xda\xf5@\x00\x00\x00'
                                        b'\xe0\x1b\xf9\xdf@\x00\x00\x00\xe0w\xf7\xbe@\x00\x00\x00\xa0\xaci\xb7@\x00'
                                        b'\x00\x00\x80q\xfa\xc1@\x00\x00\x00\xc0r\xab\xb4@\x00\x00\x00\xa0\xa6\xed'
                                        b'\xb1@\x00\x00\x00@xg\xb4@\x00\x00\x00\xe0g+\xb2@\x00\x00\x00\x80\xf5V\x19A'
                                        b'\x00\x00\x00`c\xdd\xbb@\x00\x00\x00\xa0z\x15\x03A\x00\x00\x00@f\xf1\xc1'
                                        b'@\x00\x00\x00\x80\x1e\x9c\xc0@\x00\x00\x00@\x87\x03\xe2@\x00\x00\x00 '
                                        b'\x1b\x8c\xb8@\x00\x00\x00\x00\xe2l\xc7@\x00\x00\x00\x00z\xa2\xc5@\x00\x00'
                                        b'\x00@\x8a\x95\xcd@\x00\x00\x00 '
                                        b'<`\xc5@\x00\x00\x00`\xc1\xf3\xb6@\x00\x00\x00\xc0['
                                        b'\xaf\xbe@\x00\x00\x00`\xa5S\xca@\x00\x00\x00\xc060\xe0@\x00\x00\x00@%W\xdb'
                                        b'@\x00\x00\x00\x80NM\tA\x00\x00\x00\xa0\xa8\xfb\tA\x00\x00\x00\xa0S\xdc\xbd'
                                        b'@\x00\x00\x00\x80F\xa4\xf6@\x00\x00\x00 '
                                        b'\x0c\xdd\xdf@\x00\x00\x00\x00\x13\x1c\xaf@\x00\x00\x00\x80N|\xba@\x00\x00'
                                        b'\x00\x80\xd4\x06)A\x00\x00\x00\x00\xf7\xc6"A\x00\x00\x00\xe0\x0f\xc1\x11A'
                                        b'\x00\x00\x00\x80\x11k\xf6@\x00\x00\x00@"\x80\xd9@\x00\x00\x00@\xe9\xca\xb3'
                                        b'@\x00\x00\x00\x00\xc0I\xb2@\x00\x00\x00\x00\xed\x9a\xe1@\x00\x00\x00 '
                                        b'gz\xe5@\x00\x00\x00\xe0\xed\xd7\xc1@\x00\x00\x00 '
                                        b'\xb6\xdd\xd0@\x00\x00\x00@Y\x88\x02A\x00\x00\x00\xe0\xe8\xe1\x00A\x00\x00'
                                        b'\x00 '
                                        b')\xcd\xf9@\x00\x00\x00\xe0\x1a\x97\xfe@\x00\x00\x00\x80tg\xed@\x00\x00\x00'
                                        b'\xc0\x16`\xe1@\x00\x00\x00\xa0\xa4\xbf\xc0@\x00\x00\x00\xc0m\xea\xd8@\x00'
                                        b'\x00\x00\xe0c8\xbe@\x00\x00\x00\x80D\xf4\xc2@\x00\x00\x00\xe0\xcf\xb7\xb4'
                                        b'@\x00\x00\x00\x80G\xce\xb6@\x00\x00\x00\xe0\xd0\x08\xbb@\x00\x00\x00\x00'
                                        b'\xdf/\xb9@\x00\x00\x00\x80\x18\xc6-A\x00\x00\x00\x00\n\x0f)A\x00\x00\x00'
                                        b'@\x97\xaf\x19A\x00\x00\x00`\xcc)\x05A\x00\x00\x00\xa0k\xc8\xe5@\x00\x00\x00 '
                                        b'\x1a\x9e\xbe@\x00\x00\x00`Qv\xb6@\x00\x00\x00\xa0\x06s\xb9@\x00\x00\x00\xa0'
                                        b'-\xb5\xd9@\x00\x00\x00\xc0\xc01\xd8@\x00\x00\x00\xc0E\x13\xd6@\x00\x00\x00'
                                        b'`\xb1a\xd4@\x00\x00\x00@\xb4\xc0\xbe@\x00\x00\x00 '
                                        b'3\xa8\xb2@\x00\x00\x00\xe0\n6\xb5@\x00\x00\x00\x00\x0e\x99\xbc@\x00\x00\x00'
                                        b'@\xcdS\xc8@\x00\x00\x00\x80{~\xd1@\x00\x00\x00\xe0\xc1\xc8\xb4@\x00\x00\x00 '
                                        b'\x06\xc5\xb3@\x00\x00\x00\x00g\xba\xb8@\x00\x00\x00\x80?B\x19A\x00\x00\x00'
                                        b'\x00\x1a\x18\x04A\x00\x00\x00 '
                                        b'\xa7\x17\xeb@\x00\x00\x00\xa0\xf6D\xbd@\x00\x00\x00 \xd16\xd9@\x00\x00\x00 '
                                        b'h\xca\xd1@\x00\x00\x00 '
                                        b'\xa5\x99\xd5@\x00\x00\x00\x00\xe1\x01\xbc@\x00\x00\x00\xc0\xb6\xa8\xc4@\x00'
                                        b'\x00\x00\x80\x0c\xe3\xd6@\x00\x00\x00`,'
                                        b'v\xdc@\x00\x00\x00\x80\x87\xf2\xc1@\x00\x00\x00`u\xf1\xc1@\x00\x00\x00@\xb8'
                                        b'\x00\xb1@\x00\x00\x00\xa0\xce\x90\xc5@\x00\x00\x00`X\x1e\xb7@\x00\x00\x00'
                                        b'@`R\xb0@\x00\x00\x00`\xb6\x8e\xb0@\x00\x00\x00\xc0\xa6\x9f\xc0@\x00\x00\x00'
                                        b'\x80\x8e\xae\xe9@\x00\x00\x00\x00\xbc\xf0\xd4@\x00\x00\x00\x80r\x08\xbe'
                                        b'@\x00\x00\x00 '
                                        b'\x867\xbd@\x00\x00\x00\xe0\xcc\xfd\xb8@\x00\x00\x00\xc0\x16\x95\xcd@\x00'
                                        b'\x00\x00\xe0\x81\xa2\xc5@\x00\x00\x00`\x0c\xba\xc0@\x00\x00\x00`ML\xb5@\x00'
                                        b'\x00\x00\xc0\xe2\xdc\xc9@\x00\x00\x00\x80\xe8\x05\xbd@\x00\x00\x00@Jy\xda'
                                        b'@\x00\x00\x00\xc0s\xeb\xd7@\x00\x00\x00\xa0\xean\xbe@\x00\x00\x00`W\x98\xb7'
                                        b'@\x00\x00\x00\xe0\xb3\xab\xbe@\x00\x00\x00\xc0%:\xb5@\x00\x00\x00\xe0GA\xe6'
                                        b'@\x00\x00\x00\x80~x\xf8@\x00\x00\x00`\xea\xf6\xf0@\x00\x00\x00@\xbd\xf7\xc0'
                                        b'@\x00\x00\x00\xc08*\xeb@\x00\x00\x00`\x04\x7f\xd9@\x00\x00\x00\x80\x04}\xc2'
                                        b'@\x00\x00\x00\xe0\xe7\x16\xb8@\x00\x00\x00\xc0\x88\x0c\xbb@\x00\x00\x00'
                                        b'@\xf4\xea\xc2@\x00\x00\x00\xe09\x97\xd5@\x00\x00\x00@\xaa\xa0\xcb@\x00\x00'
                                        b'\x00`\x88\xd7\xcd@\x00\x00\x00\x007\x01\xc1@\x00\x00\x00@\x87N\xce@\x00\x00'
                                        b'\x00\x00\xfe\x97\xd0@\x00\x00\x00\x80\x1c\xd0\xc1@\x00\x00\x00\x00LQ\xdc'
                                        b'@\x00\x00\x00\xa0\xc14\xc2@\x00\x00\x00\x80GB\xb9@\x00\x00\x00`\xd7V\xbf'
                                        b'@\x00\x00\x00\xe0\xfc\xab\xb9@\x00\x00\x00\xa0PX\xba@\x00\x00\x00\x80A\xa5'
                                        b'\xc1@\x00\x00\x00`\x8d\x98\xe0@\x00\x00\x00@/S\xf4@\x00\x00\x00\x00\x05\xc6'
                                        b'\xf9@\x00\x00\x00\xc0-\xfb\xf4@\x00\x00\x00\x00|\x99\xf1@\x00\x00\x00\x80'
                                        b'\xde#\xea@\x00\x00\x00\x80\xb8A\xe0@\x00\x00\x00`\'\xb1\xd2@\x00\x00\x00'
                                        b'\xe0\x0e\xfa\xc6@\x00\x00\x00@\xbeB\xc9@\x00\x00\x00 '
                                        b'zm#A\x00\x00\x00\xa0\x12\x836A\x00\x00\x00\xc0\xcfB=A\x00\x00\x00 '
                                        b'q\x7f;A\x00\x00\x00\x00\xf491A\x00\x00\x00\xc0\xd3\x02"A\x00\x00\x00\xc0V'
                                        b'\xcc\xba@\x00\x00\x00`^h\xf6@\x00\x00\x00\xe0Q*\xc5@\x00\x00\x00`5/\xed'
                                        b'@\x00\x00\x00 '
                                        b'\xd5\x91\xdc@\x00\x00\x00\x00\x01\xdc\xb6@\x00\x00\x00@S\x02\xbd@\x00\x00'
                                        b'\x00\xe0gA\xcb@\x00\x00\x00\x00\xa0\t\xd4@\x00\x00\x00\xc0\xbe\x81\xb2@\x00'
                                        b'\x00\x00`9\xd9\xd7@\x00\x00\x00\x00u\xd8\xc8@\x00\x00\x00\xa0T\t\xc6@\x00'
                                        b'\x00\x00\xc0\x0c\xd7\xc2@\x00\x00\x00@{'
                                        b'%\xc2@\x00\x00\x00\x00\xa6\xf8\xc1@\x00\x00\x00@\xb2\r\xe9@\x00\x00\x00'
                                        b'\xa0C\xac\xf2@\x00\x00\x00`\x9a\x0e\xf2@\x00\x00\x00@4\x19\xe8@\x00\x00\x00'
                                        b'\x80\xe0\x9f\xdf@\x00\x00\x00\xe0\x7fL\xba@\x00\x00\x00\xa0\xc0\xd8\xb7'
                                        b'@\x00\x00\x00@K\'\xbc@\x00\x00\x00\x00\x13\xe2\xca@\x00\x00\x00\x00\x13'
                                        b'~\xe1@\x00\x00\x00 \xcc\x16\xe3@\x00\x00\x00 '
                                        b'Cd\xb6@\x00\x00\x00@\xe0i\xeb@\x00\x00\x00\xe0\xd1\xb1\xbc@\x00\x00\x00\xa0'
                                        b'\xc2\x7f\xe6@\x00\x00\x00`\xe8S\xe6@\x00\x00\x00\xe0Y\xdf\xde@\x00\x00\x00 '
                                        b'\x8e\xbc\xc1@\x00\x00\x00 '
                                        b'c\xaf\xc1@\x00\x00\x00`\x99\xeb\xb7@\x00\x00\x00\x00\t\x15\xc8@\x00\x00\x00'
                                        b'\x80\x08\xf6\xc5@\x00\x00\x00\xa0)"\xbd@\x00\x00\x00\x80\x80\x96\xe8@\x00'
                                        b'\x00\x00\xe0\xd7V\xfd@\x00\x00\x00\xc0\nn\x00A\x00\x00\x00`\x8b7\xf5@\x00'
                                        b'\x00\x00`\x8f\xcc\xe7@\x00\x00\x00`Z\xe1\xd9@\x00\x00\x00\xc0\xe7\xc6\xbd'
                                        b'@\x00\x00\x00\xc0\r\xec\xdb@\x00\x00\x00 '
                                        b'|\x81\xe2@\x00\x00\x00\xc0w\xd9\xdd@\x00\x00\x00`+\x8c\xd5@\x00\x00\x00'
                                        b'\x800o\xcb@\x00\x00\x00 '
                                        b'l\xbc\xd2@\x00\x00\x00@\x0f\xbc\xc7@\x00\x00\x00\xe0m|\xb7@\x00\x00\x00'
                                        b'\xe0kH\x11A\x00\x00\x00\xc0t\x11\x18A\x00\x00\x00\xe0\xf0R\x12A\x00\x00\x00'
                                        b'\xc0\xdbb\xbb@\x00\x00\x00@\xa5\x8c\x06A\x00\x00\x00\x00L\xe2\xe3@\x00\x00'
                                        b'\x00\x803\xdd\xd1@\x00\x00\x00\x00\xf7\xc8\xe1@\x00\x00\x00\x00fq\xd6@\x00'
                                        b'\x00\x00`\xe5\x96\xcb@\x00\x00\x00 '
                                        b'\xd3\xd2\xbb@\x00\x00\x00\x80\xea\xc0\xc9@\x00\x00\x00\xc0\xfc\xfb\xc5@\x00'
                                        b'\x00\x00`\x0b\x94\xc6@\x00\x00\x00\xc0-\x91\xc9@\x00\x00\x00\x00\xb7\xf2'
                                        b'\xc1@\x00\x00\x00 '
                                        b'\xa7\xfe\xee@\x00\x00\x00\xe0\x927\xe7@\x00\x00\x00\x80\xa1\xc4\x04A\x00'
                                        b'\x00\x00\xa0g\x96\x0bA\x00\x00\x00\x80\x85$\x07A\x00\x00\x00\x80\xba\xf0'
                                        b'\xf7@\x00\x00\x00\xe0\xbda\xe2@\x00\x00\x00\xe0\xef\x80\xc9@\x00\x00\x00'
                                        b'`\x05\x94\xcb@\x00\x00\x00\xa0\x01\x0e\xba@\x00\x00\x00\xe0\xae\x9d\xbb'
                                        b'@\x00\x00\x00\x80\'\xb4\xb7@\x00\x00\x00\x80Dm\xc1@\x00\x00\x00@\x95\xcb'
                                        b'\xe9@\x00\x00\x00 '
                                        b'.\xd8\xd8@\x00\x00\x00\xe0\xd8H\x16A\x00\x00\x00\x80s\x0f\x04A\x00\x00\x00 '
                                        b'\x95\xda\xdf@\x00\x00\x00\xe0w\xd7\xb4@\x00\x00\x00\x80 '
                                        b'\x1c\xe8@\x00\x00\x00\xa0B\xcd\xde@\x00\x00\x00\xe0\xec|\xb6@\x00\x00\x00 '
                                        b'\xe9\xb7\xd1@\x00\x00\x00\xa0W\x98\xc4@\x00\x00\x00\xe0k}\xc6@\x00\x00\x00 '
                                        b'W\xa1\xb8@\x00\x00\x00\x80%\x17\xec@\x00\x00\x00\xc0\x16\xc9\xe8@\x00\x00'
                                        b'\x00\x80\xc2\xcd\xd3@\x00\x00\x00\x80\x1b\xb5\xc5@\x00\x00\x00\x00?N\xf2'
                                        b'@\x00\x00\x00 '
                                        b'w3\xc5@\x00\x00\x00\xe0\x1d\xb5\xdb@\x00\x00\x00@\x03"\xbf@\x00\x00\x00'
                                        b'\xc0I\x89\xc0@\x00\x00\x00`D\x86\xc0@\x00\x00\x00`{'
                                        b'\x11\xb5@\x00\x00\x00\xe0\xac8\xb7@\x00\x00\x00\x804P\xd0@\x00\x00\x00\x00'
                                        b'\xd3q\xd0@\x00\x00\x00\x80\xd5a\xc9@\x00\x00\x00 '
                                        b'\xf3g\xb9@\x00\x00\x00\x80\x84\xfb\xe1@\x00\x00\x00 ,'
                                        b'\xc8\xf6@\x00\x00\x00`\xef\x15\xf8@\x00\x00\x00\xc0\xb7\xb7\xf7@\x00\x00'
                                        b'\x00\xc0l)\xe1@\x00\x00\x00\x80\xb9\xbf\xd1@\x00\x00\x00\x00}\xd5\xe3@\x00'
                                        b'\x00\x00\x00\xee\xc5\xda@\x00\x00\x00\x80+\r\xd1@\x00\x00\x00\x80a\xef\xdb'
                                        b'@\x00\x00\x00\x00\x9d&\xdc@\x00\x00\x00\x80\xc6\xad\xcb@\x00\x00\x00\xe0'
                                        b'/\x8d\xb5@\x00\x00\x00 )\x89\xe7@\x00\x00\x00 '
                                        b'GI\xeb@\x00\x00\x00\x80t\xcf\xd1@\x00\x00\x00\xe0\xd8\xb6\xc6@\x00\x00\x00'
                                        b'\x80P\xc2\xd7@\x00\x00\x00\xa08I\xce@\x00\x00\x00\xe0tx\xcf@\x00\x00\x00'
                                        b'\x00\x15\x92\xc1@\x00\x00\x00\x80\xcd\x04\xdc@\x00\x00\x00\xe0\xab\xa2\xe0'
                                        b'@\x00\x00\x00\x80\xa0\xae\xc2@\x00\x00\x00`\xda\xd3\xbc@\x00\x00\x00\x00'
                                        b')\xe1\xb7@\x00\x00\x00\x80\xdc\x98\xbe@\x00\x00\x00\xc0\xa2\xdd\xb4@\x00'
                                        b'\x00\x00\x00\x1a\xa4\xcb@\x00\x00\x00\x00i\x9a\xb8@\x00\x00\x00 '
                                        b'\xed\xa4\xb6@\x00\x00\x00\x00\xed\x13\xf2@\x00\x00\x00`\xb1\x00\xd5@\x00'
                                        b'\x00\x00\xe0\x8d\xf5\xc1@\x00\x00\x00\xe0\xdds\xbd@\x00\x00\x00\xe0\xbe\x95'
                                        b'\xcd@\x00\x00\x00@\xc0@\xe0@\x00\x00\x00\xc0\x01\xb1\xd8@\x00\x00\x00\xe0'
                                        b'\xe4P\xc0@\x00\x00\x00`\x195\xbb@\x00\x00\x00\x00\xa2\x87\xba@\x00\x00\x00'
                                        b'\xa0 a\xb5@\x00\x00\x00@\x91K\xb7@\x00\x00\x00\xe0\xe9\xca\xc1@\x00\x00\x00 '
                                        b'\xff\x7f\xc6@\x00\x00\x00`\xd8A\xf0@\x00\x00\x00@\x9e\xf5\xda@\x00\x00\x00'
                                        b'`\x15\x11\xc6@\x00\x00\x00\xe0\x1cp\xb3@\x00\x00\x00\xc0\x91\x86\xd5@\x00'
                                        b'\x00\x00 '
                                        b'\xaa\xb4\xcc@\x00\x00\x00`C\xc9\xb5@\x00\x00\x00\x00\xd7\xf1\xd1@\x00\x00'
                                        b'\x00\xe0\xd1\xee\xb4@\x00\x00\x00\xa0\xedv\xc0@\x00\x00\x00\xa0h\x05\xe1'
                                        b'@\x00\x00\x00\xa0\xef\x9a\xdf@\x00\x00\x00`\xd0\xe4\xd3@\x00\x00\x00\xe0'
                                        b'\xee}\xb7@\x00\x00\x00\xc0e\x14\xb4@\x00\x00\x00 '
                                        b'\x8f\xfc\xc6@\x00\x00\x00\xe0\xa4+\xd3@\x00\x00\x00\x00\x82|\xdd@\x00\x00'
                                        b'\x00@\x12\xc0\xed@\x00\x00\x00\xc0\x0f<\xf0@\x00\x00\x00\xc0\xa4\xc2\xe3'
                                        b'@\x00\x00\x00\x80\x96\xc9\xd5@\x00\x00\x00\xa0\xe8H\xc0@\x00\x00\x00\xa0'
                                        b'~~\xd7@\x00\x00\x00@^\x9f\xd6@\x00\x00\x00\xe0|\xe3\xd0@\x00\x00\x00\x80'
                                        b'\xce\xa0\xb7@\x00\x00\x00\x00\xe7-\xd9@\x00\x00\x00\xa0\xf9-\xc9@\x00\x00'
                                        b'\x00\xc0<\x81\xbe@\x00\x00\x00\xc0\x06\x1e\xd3@\x00\x00\x00\xe0\xdc\x05\xde'
                                        b'@\x00\x00\x00\xa0\xe0;\xca@\x00\x00\x00@\xa7S\xb5@\x00\x00\x00@\xc3\x11\xcb'
                                        b'@\x00\x00\x00\xe0We\xbc@\x00\x00\x00@\x191\xc9@\x00\x00\x00`\xa9\xca\xc4'
                                        b'@\x00\x00\x00@:G\xe7@\x00\x00\x00 '
                                        b'\xa6\x89\xd8@\x00\x00\x00\xa0\xad\x07\xd7@\x00\x00\x00\xa0\xb9\xd4\xb4@\x00'
                                        b'\x00\x00\xc0\xca\xc0\x14A\x00\x00\x00`\x0fT\x06A\x00\x00\x00\x80\x03\x0e'
                                        b'\xf1@\x00\x00\x00\x00\x7fa\xce@\x00\x00\x00\x80s;\xb7@\x00\x00\x00@:\xd1'
                                        b'\xb7@\x00\x00\x00\x80!\xc7\xd2@\x00\x00\x00\x00\xc8\xe2\xc7@\x00\x00\x00'
                                        b'\x80\r\xdb\xb7@\x00\x00\x00\x80\x17\xec\xb7@\x00\x00\x00\x00\xeb\xba\xc7'
                                        b'@\x00\x00\x00\xa0\x1b\xd0\xe0@\x00\x00\x00\xa0N\x1f\xea@\x00\x00\x00 '
                                        b'5P\xdc@\x00\x00\x00\xa0\xe0\xa0\xd1@\x00\x00\x00\x00\xeco\xe1@\x00\x00\x00'
                                        b'\xa0\xae\xcb\xd3@\x00\x00\x00\x80I<\xc3@\x00\x00\x00@%\x98\xba@\x00\x00\x00 '
                                        b'%\xf2\xbb@\x00\x00\x00\xe0\xea\xd8\xbd@\x00\x00\x00@\xceM\xc4@\x00\x00\x00'
                                        b'\xe0\xd0=\xc7@\x00\x00\x00@I\xb4\xd7@\x00\x00\x00`\xd6\x92\xc6@\x00\x00\x00'
                                        b'@\x03\x8b\xc1@\x00\x00\x00 {'
                                        b'\xdd\xd0@\x00\x00\x00@\x86\x9a\xde@\x00\x00\x00\x00e\x02\xe6@\x00\x00\x00'
                                        b'\xe0N\x05\xd9@\x00\x00\x00@\\3\xbd@\x00\x00\x00\x80\xe8\x96\xbc@\x00\x00'
                                        b'\x00\xa0j$\xc6@\x00\x00\x00\xa0\xb0\x92\xb5@\x00\x00\x00\xe0\xc3\xcc\xba'
                                        b'@\x00\x00\x00`)a\xcd@\x00\x00\x00`<\xcb\xd3@\x00\x00\x00\xe0u_\xb8@\x00\x00'
                                        b'\x00\x80\xad\xbb\xbd@\x00\x00\x00\xa0\xb0\xcc\xbd@\x00\x00\x00@\xd1\x9a\xe2'
                                        b'@\x00\x00\x00\x00zz\xeb@\x00\x00\x00@\xa8\xb3\xe4@\x00\x00\x00\x00bV\xdc'
                                        b'@\x00\x00\x00 '
                                        b'\xe8\xd9\xc1@\x00\x00\x00\xe0\x92\xbe\xc0@\x00\x00\x00\xa0\xba:\xc8@\x00'
                                        b'\x00\x00\x00\x08E\xcc@\x00\x00\x00@\xa3\x0b\xd0@\x00\x00\x00 \xbc('
                                        b'\xc3@\x00\x00\x00@\xe9\xf3\xba@\x00\x00\x00 '
                                        b'\xc5\xf2\xf3@\x00\x00\x00@g\x9b\xe8@\x00\x00\x00\xe0\xa7\xb1\xd4@\x00\x00'
                                        b'\x00\x00\xf8\x16\xe3@\x00\x00\x00\x80['
                                        b'r\xe0@\x00\x00\x00`\xe2\xbc\xc2@\x00\x00\x00 '
                                        b';s\xcb@\x00\x00\x00\x80\x1c\xa4\xbd@\x00\x00\x00 \xd7 '
                                        b'\xc7@\x00\x00\x00\xc0t\xad\xeb@\x00\x00\x00\xe0Z\x02\xde@\x00\x00\x00\x80'
                                        b'\xf5\xd4\xc4@\x00\x00\x00\x00\xa9\x06\xb9@\x00\x00\x00\xc0C\xc8\xbe@\x00'
                                        b'\x00\x00@O\x00\xba@\x00\x00\x00\xc0ZW\xd6@\x00\x00\x00\xe0cG\xd4@\x00\x00'
                                        b'\x00\xa0\xe7\xa8\xc0@\x00\x00\x00`3\xd6\xd1@\x00\x00\x00\xe0\xfc\xbe\xc5'
                                        b'@\x00\x00\x00\xa0\xed\x9f\xe5@\x00\x00\x00\xe0\xd5\xd8\xdd@\x00\x00\x00 '
                                        b'\r\x89\xd1@\x00\x00\x00\xc0XM\xc5@\x00\x00\x00`\x1b\xd5\xba@\x00\x00\x00@z'
                                        b'-\xd3@\x00\x00\x00\xa0\xdd\x08\xc8@\x00\x00\x00\xa0\x98\x0e\xbd@\x00\x00'
                                        b'\x00\xe0\x944\xcb@\x00\x00\x00\x80\xc4\xd8\xcf@\x00\x00\x00\xa0\\\xa9\xc0'
                                        b'@\x00\x00\x00\x00N\xa7\xd3@\x00\x00\x00\xc0\xf6t\xbe@\x00\x00\x00\x00\xbe'
                                        b'\x0e\xb8@\x00\x00\x00 '
                                        b'I\xbc\xb4@\x00\x00\x00\xc0\xc8G\xdd@\x00\x00\x00\x80\xe2l\xd2@\x00\x00\x00'
                                        b'\xe0\x18<\xc7@\x00\x00\x00 '
                                        b'\xec\x8d\xb4@\x00\x00\x00\xc0A\xa3\xb7@\x00\x00\x00\x00\xe4\x8d\xbd@\x00'
                                        b'\x00\x00\xc0\xd6\xec\xb5@\x00\x00\x00\xa0*\xa1\xc2@\x00\x00\x00\x80N\x94'
                                        b'\xb9@\x00\x00\x00@\xe8\x96\xc3@\x00\x00\x00\xa0)\'\xcd@\x00\x00\x00\x00\x9c'
                                        b'\x0b\xb4@\x00\x00\x00\x80V\xe6\xef@\x00\x00\x00\xc0\xf6\xeb\xe3@\x00\x00'
                                        b'\x00`\xe1\x9b\xd5@\x00\x00\x00`\xdd\x9a\xbd@\x00\x00\x00\x00f\x96\xdc@\x00'
                                        b'\x00\x00\x00H\xed\xd6@\x00\x00\x00\xa0C\xe0\xe2@\x00\x00\x00\xc0\xa3$\xe6'
                                        b'@\x00\x00\x00\x80\x9e\xd4\xd4@\x00\x00\x00 \xe2{'
                                        b'\xc0@\x00\x00\x00`\x15\x10\xce@\x00\x00\x00\xc0\x1c\x06\xd2@\x00\x00\x00'
                                        b'\x80m\x94\xc1@\x00\x00\x00\x00s\xb1\xbb@\x00\x00\x00\xa0\n\xee\xb4@\x00\x00'
                                        b'\x00`\xf1\xfa\xb2@\x00\x00\x00\xe0\x083\xb3@\x00\x00\x00\x00\xf1=\xb5@\x00'
                                        b'\x00\x00\xc0\xe9\x9f\xb2@')

        # Match
        stmt = Table("match", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        assert 22 == rs.rowcount
        results = rs.fetchall()
        assert results[0].id == 'SII_3_1'  # id from first <SpectrumIdentificationItem>
        # spectrumID from <SpectrumIdentificationResult>
        assert results[0].spectrum_id == 'controllerType=0 controllerNumber=1 scan=14905'
        # spectraData_ref from <SpectrumIdentificationResult>
        # assert results[0].spectra_data_ref == \
        #        'SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mzML'
        assert results[0].spectra_data_id == 1
        # peptide_ref from <SpectrumIdentificationItem>
        assert results[0].pep1_id == 4 #  \
               # '6_VAEmetETPHLIHKVALDPLTGPMPYQGR_11_MGHAGAIIAGGKGTADEK_11_12_p1'
        # peptide_ref from matched <SpectrumIdentificationItem> by crosslink_identification_id
        assert results[0].pep2_id == 5 # \
               # '6_VAEmetETPHLIHKVALDPLTGPMPYQGR_11_MGHAGAIIAGGKGTADEK_11_12_p0'
        assert results[0].charge_state == 5  # chargeState from <SpectrumIdentificationItem>
        assert results[0].pass_threshold  # passThreshold from <SpectrumIdentificationItem>
        assert results[0].rank == 1  # rank from <SpectrumIdentificationItem>
        # scores parsed from score related cvParams in <SpectrumIdentificationItem>
        assert results[0].scores == {"xi:score": 33.814201}
        # experimentalMassToCharge from <SpectrumIdentificationItem>
        assert results[0].exp_mz == 945.677359
        # calculatedMassToCharge from <SpectrumIdentificationItem>
        assert results[0].calc_mz == pytest.approx(945.6784858667701, abs=1e-12)

        # SpectrumIdentificationProtocol
        stmt = Table("spectrumidentificationprotocol", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_spectrum_identification_protocol(rs.fetchall())

        # AnalysisCollection
        stmt = Table("analysiscollectionspectrumidentification", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_analysis_collection_mzml(rs.fetchall())

        # Upload
        stmt = Table("upload", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        assert 1 == rs.rowcount
        results = rs.fetchall()

        assert results[0].identification_file_name == 'mzml_ecoli_dsso.mzid'
        assert results[0].provider == {'ContactRole': [{'Role': 'researcher', 'contact_ref': 'PERSON_DOC_OWNER'}],
                                       'id': 'PROVIDER'}
        assert results[0].audit_collection == {
            'Organization': {'contact name': 'TU Berlin',
                             'id': 'ORG_DOC_OWNER',
                             'name': 'TU Berlin'},
            'Person': {'Affiliation': [{'organization_ref': 'ORG_DOC_OWNER'}],
                       'contact address': 'TIB 4/4-3 Gebäude 17, Aufgang 1, Raum 476 '
                                          'Gustav-Meyer-Allee 25 13355 Berlin',
                       'contact email': 'lars.kolbowski@tu-berlin.de',
                       'firstName': 'Lars',
                       'id': 'PERSON_DOC_OWNER',
                       'lastName': 'Kolbowski'}}
        assert results[0].analysis_sample_collection == {}
        assert results[0].bib == []
        assert results[0].spectra_formats == [
            {'FileFormat': 'mzML format',
             'SpectrumIDFormat': 'mzML unique identifier',
             'id': 'SD_0_recal_B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mzML',
             'location': 'B190717_20_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX01_rep2.mzML'},
            {'FileFormat': 'mzML format',
             'SpectrumIDFormat': 'mzML unique identifier',
             'id': 'SD_0_recal_B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mzML',
             'location': 'B190717_13_HF_LS_IN_130_ECLP_DSSO_01_SCX23_hSAX05_rep2.mzML'}]
        assert results[0].contains_crosslinks
        # assert results[0].upload_warnings == [
        #     'mzidentML file does not specify any fragment ions (child terms of MS_1002473) within '
        #     '<AdditionalSearchParams>. Falling back to b and y ions.']

    engine.dispose()


# noinspection PyTestUnpassedFixture
def test_sqlite_mgf_xispec_mzid_parser(tmpdir):
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
    mzid = os.path.join(fixtures_dir, 'mgf_ecoli_dsso.mzid')
    peak_list_folder = os.path.join(fixtures_dir, 'peaklist')
    test_database = os.path.join(str(tmpdir), 'test.db')

    conn_str = f'sqlite:///{test_database}'
    engine = create_engine(conn_str)
    id_parser = parse_mzid_into_sqlite_xispec(mzid, peak_list_folder, tmpdir, logger, engine)

    with engine.connect() as conn:
        # DBSequence
        stmt = Table("DBSequence", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        assert len(rs.fetchall()) == 12

        # Modification - parsed from <SearchModification>s
        stmt = Table("SearchModification", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        compare_modification(rs.fetchall())

        # Enzyme - parsed from SpectrumIdentificationProtocols
        stmt = Table("Enzyme", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        compare_enzyme(rs.fetchall())

        # PeptideEvidence
        stmt = Table("PeptideEvidence", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_peptide_evidence(rs.fetchall())

        # ModifiedPeptide
        stmt = Table("ModifiedPeptide", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_modified_peptide(rs.fetchall())

        # Spectrum
        compare_spectrum_mgf(conn, peak_list_folder)

        # Match
        stmt = Table("Match", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        conn.execute(stmt)

        # SpectrumIdentificationProtocol
        stmt = Table("SpectrumIdentificationProtocol", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_spectrum_identification_protocol(rs.fetchall())

        # AnalysisCollection
        stmt = Table("analysiscollectionspectrumidentification", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_analysis_collection_mgf(rs.fetchall())

        # Upload - not written for xiSPEC
        stmt = Table("Upload", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        assert len(rs.fetchall()) == 0

    engine.dispose()


# noinspection PyTestUnpassedFixture
def test_sqlite_mzml_xispec_mzid_parser(tmpdir):
    # file paths
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'mzid_parser')
    mzid = os.path.join(fixtures_dir, 'mzml_ecoli_dsso.mzid')
    peak_list_folder = os.path.join(fixtures_dir, 'peaklist')
    test_database = os.path.join(str(tmpdir), 'test.db')

    conn_str = f'sqlite:///{test_database}'
    engine = create_engine(conn_str)

    id_parser = parse_mzid_into_sqlite_xispec(mzid, peak_list_folder, tmpdir, logger, engine)

    with engine.connect() as conn:
        # DBSequence
        stmt = Table("DBSequence", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        assert len(rs.fetchall()) == 12

        # Modification - parsed from <SearchModification>s
        stmt = Table("SearchModification", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        compare_modification(rs.fetchall())

        # Enzyme - parsed from SpectrumIdentificationProtocols
        stmt = Table("Enzyme", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        compare_enzyme(rs.fetchall())

        # PeptideEvidence
        stmt = Table("PeptideEvidence", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_peptide_evidence(rs.fetchall())

        # ModifiedPeptide
        stmt = Table("ModifiedPeptide", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_modified_peptide(rs.fetchall())

        # Spectrum
        stmt = Table("Spectrum", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        conn.execute(stmt)
        # ToDo: create and use compare_spectrum_mzml()

        # Match
        stmt = Table("Match", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        conn.execute(stmt)

        # SpectrumIdentificationProtocol
        stmt = Table("SpectrumIdentificationProtocol", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_spectrum_identification_protocol(rs.fetchall())

        # AnalysisCollection
        stmt = Table("analysiscollectionspectrumidentification", id_parser.writer.meta,
                     autoload_with=id_parser.writer.engine, quote=False).select()
        rs = conn.execute(stmt)
        compare_analysis_collection_mzml(rs.fetchall())

        # Upload - not written for xiSPEC
        stmt = Table("Upload", id_parser.writer.meta, autoload_with=id_parser.writer.engine,
                     quote=False).select()
        rs = conn.execute(stmt)
        assert len(rs.fetchall()) == 0

    engine.dispose()
