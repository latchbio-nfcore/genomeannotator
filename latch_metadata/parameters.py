
from dataclasses import dataclass
import typing
import typing_extensions

from flytekit.core.annotation import FlyteAnnotation

from latch.types.metadata import NextflowParameter
from latch.types.file import LatchFile
from latch.types.directory import LatchDir, LatchOutputDir

# Import these into your `__init__.py` file:
#
# from .parameters import generated_parameters

generated_parameters = {
    'assembly': NextflowParameter(
        type=LatchFile,
        default=None,
        section_title='Input/output options',
        description='Path to the genome assembly.',
    ),
    'outdir': NextflowParameter(
        type=typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})],
        default=None,
        section_title=None,
        description='The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure.',
    ),
    'email': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Email address for completion summary.',
    ),
    'multiqc_title': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='MultiQC report title. Printed as page header, used for filename if not otherwise specified.',
    ),
    'rnaseq_samples': NextflowParameter(
        type=typing.Optional[LatchFile],
        default=None,
        section_title=None,
        description='Path to samplesheet for RNAseq data.',
    ),
    'proteins': NextflowParameter(
        type=typing.Optional[LatchFile],
        default=None,
        section_title=None,
        description='Path to a fasta file with proteins',
    ),
    'proteins_targeted': NextflowParameter(
        type=typing.Optional[LatchFile],
        default=None,
        section_title=None,
        description='Path to a fasta file with proteins',
    ),
    'transcripts': NextflowParameter(
        type=typing.Optional[LatchFile],
        default=None,
        section_title=None,
        description='Path to a fasta file with transcripts/ESTs',
    ),
    'rm_lib': NextflowParameter(
        type=typing.Optional[LatchFile],
        default=None,
        section_title=None,
        description='Path to a fasta file with known repeat sequences for this organism',
    ),
    'references': NextflowParameter(
        type=typing.Optional[LatchFile],
        default=None,
        section_title=None,
        description='Path to samplesheet for Reference genomes and annotations.',
    ),
    'npart_size': NextflowParameter(
        type=typing.Optional[int],
        default=200000000,
        section_title='Options for pipeline behavior',
        description='Chunk size for splitting the assembly.',
    ),
    'max_intron_size': NextflowParameter(
        type=typing.Optional[int],
        default=None,
        section_title=None,
        description='Maximum length of expected introns in bp.',
    ),
    'min_contig_size': NextflowParameter(
        type=typing.Optional[int],
        default=5000,
        section_title=None,
        description='Minimum size of contig to consider',
    ),
    'rm_species': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Taxonomic group to guide repeat masking.',
    ),
    'rm_db': NextflowParameter(
        type=typing.Optional[LatchFile],
        default=None,
        section_title=None,
        description='A database of curated repeats in EMBL format.',
    ),
    'busco_lineage': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Name of a BUSCO taxonomic group to evaluate the completeness of annotated gene set(s).',
    ),
    'busco_db_path': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Path to the local BUSCO data.',
    ),
    'dummy_gff': NextflowParameter(
        type=typing.Optional[str],
        default='PIPELINE_BASE/assets/empty.gff3',
        section_title=None,
        description='A placeholder gff file to help trigger certain processes.',
    ),
    'aug_species': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title='Options for ab-initio gene finding',
        description='AUGUSTUS species model to use.',
    ),
    'aug_options': NextflowParameter(
        type=typing.Optional[str],
        default='--alternatives-from-evidence=on --minexonintronprob=0.08 --minmeanexonintronprob=0.4 --maxtracks=3',
        section_title=None,
        description='Options to pass to AUGUSTUS.',
    ),
    'aug_config_container': NextflowParameter(
        type=typing.Optional[str],
        default='/usr/local/config',
        section_title=None,
        description='Location of the AUGUSTUS config directory within the docker container',
    ),
    'aug_config_dir': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='A custom config directory for AUGUSTUS',
    ),
    'aug_extrinsic_cfg': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Custom AUGUSTUS extrinsic config file path',
    ),
    'aug_chunk_length': NextflowParameter(
        type=typing.Optional[int],
        default=3000000,
        section_title=None,
        description='Length of annotation chunks in AUGUSTUS',
    ),
    'aug_training': NextflowParameter(
        type=typing.Optional[bool],
        default=False,
        section_title=None,
        description='Enable training of a new AUGUSTUS profile.',
    ),
    'pri_prot': NextflowParameter(
        type=typing.Optional[int],
        default=3,
        section_title=None,
        description='Priority for protein-derived hints for gene building.',
    ),
    'pri_prot_target': NextflowParameter(
        type=typing.Optional[int],
        default=5,
        section_title=None,
        description='Priority for targeted protein evidences',
    ),
    'pri_est': NextflowParameter(
        type=typing.Optional[int],
        default=4,
        section_title=None,
        description='Priority for transcript evidences',
    ),
    'pri_rnaseq': NextflowParameter(
        type=typing.Optional[int],
        default=4,
        section_title=None,
        description='Priority for RNAseq splice junction evidences',
    ),
    'pri_wiggle': NextflowParameter(
        type=typing.Optional[int],
        default=2,
        section_title=None,
        description='Priority for RNAseq exon coverage evidences',
    ),
    'pri_trans': NextflowParameter(
        type=typing.Optional[int],
        default=4,
        section_title=None,
        description='Priority for trans-mapped gene model evidences',
    ),
    't_est': NextflowParameter(
        type=typing.Optional[str],
        default='E',
        section_title=None,
        description='Evidence label for transcriptome data',
    ),
    't_prot': NextflowParameter(
        type=typing.Optional[str],
        default='P',
        section_title=None,
        description='Evidence label for protein data',
    ),
    't_rnaseq': NextflowParameter(
        type=typing.Optional[str],
        default='E',
        section_title=None,
        description='Evidence label for RNAseq data',
    ),
    'spaln_taxon': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title='Options for protein data processing',
        description='Taxon model to use for SPALN protein alignments.',
    ),
    'spaln_options': NextflowParameter(
        type=typing.Optional[str],
        default='-M',
        section_title=None,
        description='SPALN custom options.',
    ),
    'spaln_protein_id': NextflowParameter(
        type=typing.Optional[int],
        default=60,
        section_title=None,
        description='SPALN id threshold for aligning.',
    ),
    'min_prot_length': NextflowParameter(
        type=typing.Optional[int],
        default=35,
        section_title=None,
        description='Minimum size of a protein sequence to be included.',
    ),
    'nproteins': NextflowParameter(
        type=typing.Optional[int],
        default=200,
        section_title=None,
        description='Numbe of proteins per alignment job.',
    ),
    'spaln_q': NextflowParameter(
        type=typing.Optional[int],
        default=5,
        section_title=None,
        description='Q value for the SPALN alignment algorithm.',
    ),
    'spaln_protein_id_targeted': NextflowParameter(
        type=typing.Optional[int],
        default=90,
        section_title=None,
        description='ID threshold for targeted protein alignments.',
    ),
    'pasa_nmodels': NextflowParameter(
        type=typing.Optional[int],
        default=1000,
        section_title='Options for PASA behavior',
        description='Number of PASA models to select for AUGUSTUS training.',
    ),
    'pasa_config_file': NextflowParameter(
        type=typing.Optional[str],
        default='PIPELINE_BASE/assets/pasa/alignAssembly.config',
        section_title=None,
        description='Built-in config file for PASA.',
    ),
    'evm_weights': NextflowParameter(
        type=typing.Optional[str],
        default='None',
        section_title='Options for EvidenceModeler behavior',
        description='Weights file for EVM.',
    ),
    'nevm': NextflowParameter(
        type=typing.Optional[int],
        default=10,
        section_title=None,
        description='Number of EVM jobs per chunk.',
    ),
    'trinity': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title='Options for tool behavior',
        description='Activate the trinity assembly sub-pipeline',
    ),
    'pasa': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Activate the PASA sub-pipeline',
    ),
    'evm': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Activate the EvidenceModeler sub-pipeline',
    ),
    'ncrna': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Activate search for ncRNAs with RFam/infernal',
    ),
}

