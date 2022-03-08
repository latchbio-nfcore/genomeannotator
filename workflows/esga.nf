/*
========================================================================================
    VALIDATE INPUTS
========================================================================================
*/

def summary_params = NfcoreSchema.paramsSummaryMap(workflow, params)

// Validate input parameters
WorkflowEsga.initialise(params, log)

// TODO nf-core: Add all file path parameters for the pipeline to the list below
// Check input path parameters to see if they exist
def checkPathParamList = [ params.multiqc_config, params.assembly ]
for (param in checkPathParamList) { if (param) { file(param, checkIfExists: true) } }

// Check mandatory parameters
if (params.assembly) { ch_genome = file(params.assembly, checkIfExists: true) } else { exit 1, 'No assembly specified!' }
if (params.proteins) { ch_proteins = file(params.proteins, checkIfExists: true) } else { ch_proteins = Channel.empty() }
if (params.proteins_targeted) { ch_proteins_targeted = file(params.proteins_targeted, checkIfExists: true) } else { ch_proteins_targeted = Channel.empty() }
if (params.transcripts) { ch_transcripts = file(params.transcripts, checkIfExists: true) } else { ch_transcripts = Channel.empty() }
if (params.rnaseq_samples) { ch_samplesheet = file(params.rnaseq_samples, checkIfExists: true) } else { ch_samplesheet = Channel.empty() }
if (params.rm_lib) { ch_repeats = Channel.fromPath(file(params.rm_lib, checkIfExists: true)) } else { ch_repeats = Channel.from([])}
if (params.aug_config_dir) { ch_aug_config_folder = file(params.aug_config_dir, checkIfExists: true) } else { ch_aug_config_folder = Channel.from(params.aug_config_container) }
if (params.references) { ch_ref_genomes = Channel.fromPath(params.references, checkIfExists: true)  } else { ch_ref_genomes = Channel.empty() }

/*
========================================================================================
    CONFIG FILES
========================================================================================
*/

ch_multiqc_config        = file("$projectDir/assets/multiqc_config.yaml", checkIfExists: true)
ch_multiqc_custom_config = params.multiqc_config ? Channel.fromPath(params.multiqc_config) : Channel.empty()
ch_aug_extrinsic_cfg = params.aug_extrinsic_cfg ? Channel.from( file(params.aug_extrinsic_cfg, checkIfExists: true) ) : Channel.from( file("${workflow.projectDir}/assets/augustus/augustus_default.cfg"))
ch_evm_weights = params.evm_weights ? Channel.from(file(params.evm_weights, checkIfExists: true)) : Channel.from(file("${baseDir}/assets/evm/weights.txt", checkIfExists: true))

/*
========================================================================================
    IMPORT LOCAL MODULES/SUBWORKFLOWS
========================================================================================
*/

//
// SUBWORKFLOW: Consisting of a mix of local and nf-core/modules
//

include { ASSEMBLY_PREPROCESS } from '../subworkflows/local/assembly_preprocess'
include { REPEATMASKER } from '../subworkflows/local/repeatmasker'
include { SPALN_ALIGN_PROTEIN ; SPALN_ALIGN_PROTEIN as SPALN_ALIGN_MODELS } from '../subworkflows/local/spaln_align_protein'
include { RNASEQ_ALIGN } from '../subworkflows/local/rnaseq_align'
include { MINIMAP_ALIGN_TRANSCRIPTS ; MINIMAP_ALIGN_TRANSCRIPTS as TRINITY_ALIGN_TRANSCRIPTS } from '../subworkflows/local/minimap_align_transcripts'
include { AUGUSTUS_PIPELINE } from '../subworkflows/local/augustus_pipeline'
include { PASA_PIPELINE } from '../subworkflows/local/pasa_pipeline'
include { GENOME_ALIGN } from '../subworkflows/local/genome_align'
include { EVM } from '../subworkflows/local/evm.nf'

/*
========================================================================================
    IMPORT NF-CORE MODULES/SUBWORKFLOWS
========================================================================================
*/

//
// MODULE: Installed directly from nf-core/modules
//
include { SAMTOOLS_MERGE } from '../modules/local/samtools/merge'
include { MULTIQC                     } from '../modules/nf-core/modules/multiqc/main'
include { CUSTOM_DUMPSOFTWAREVERSIONS } from '../modules/nf-core/modules/custom/dumpsoftwareversions/main'
include { TRINITY_GENOMEGUIDED } from '../modules/local/trinity/genomeguided'
include { AUGUSTUS_BAM2HINTS } from '../modules/local/augustus/bam2hints'
include { REPEATMODELER } from '../modules/local/repeatmodeler'
include { AUGUSTUS_STAGECONFIG } from '../modules/local/augustus/stageconfig'

/*
========================================================================================
    RUN MAIN WORKFLOW
========================================================================================
*/

// Info required for completion email and summary
def multiqc_report = []

workflow ESGA {

    ch_versions = Channel.empty()
    ch_merged_transcripts = ch_transcripts
    ch_hints = Channel.empty()
    ch_repeats_lib = Channel.empty()
    ch_proteins_gff = Channel.empty()
    ch_transcripts_gff = Channel.empty()
    ch_genes_gff = Channel.empty()

    //
    // MODULE: Stage Augustus config dir to be editable
    //
    AUGUSTUS_STAGECONFIG(ch_aug_config_folder)
    ch_aug_config_folder = AUGUSTUS_STAGECONFIG.out.config_dir

    //
    // SUBWORKFLOW: Validate and pre-process the assembly
    //
    ASSEMBLY_PREPROCESS(
        ch_genome
    )
    ch_versions = ch_versions.mix(ASSEMBLY_PREPROCESS.out.versions)

    //
    // SUBWORKFLOW: Align genomes and map annotations
    //
    if (params.references) {
       GENOME_ALIGN(
          ASSEMBLY_PREPROCESS.out.fasta,
          ch_ref_genomes
       )
       ch_versions = ch_versions.mix(GENOME_ALIGN.out.versions)
       ch_hints = ch_hints.mix(GENOME_ALIGN.out.hints)
       ch_genes_gff = ch_genes_gff.mix(GENOME_ALIGN.out.gff)
    }          

    //  
    // SUBWORKFLOW: Repeatmasking and optional modelling
    //
    if (!params.rm_lib && !params.rm_species) {
       REPEATMODELER(
          ASSEMBLY_PREPROCESS.out.fasta
       )
       ch_repeats = REPEATMODELER.out.fasta
    }
    REPEATMASKER(
       ASSEMBLY_PREPROCESS.out.fasta,
       ch_repeats,
       params.rm_species
    )
    ch_versions = ch_versions.mix(REPEATMASKER.out.versions)

    //
    // SUBWORKFLOW: Align proteins from related organisms with SPALN
    if (params.proteins) {
       SPALN_ALIGN_PROTEIN(
          ASSEMBLY_PREPROCESS.out.fasta,
          ch_proteins,
          params.spaln_protein_id
       )
       ch_versions = ch_versions.mix(SPALN_ALIGN_PROTEIN.out.versions)
       ch_hints = ch_hints.mix(SPALN_ALIGN_PROTEIN.out.hints)
       ch_proteins_gff = ch_proteins_gff.mix(SPALN_ALIGN_PROTEIN.out.gff)
    }

    // 
    // SUBWORKFLOW: Align species-specific proteins 
    if (params.proteins_targeted) {
       SPALN_ALIGN_MODELS(
          ASSEMBLY_PREPROCESS.out.fasta,
          ch_proteins_targeted,
          params.spaln_protein_id_targeted
       )
       ch_versions = ch_versions.mix(SPALN_ALIGN_MODELS.out.versions)
       ch_hints = ch_hints.mix(SPALN_ALIGN_MODELS.out.hints)
       ch_genes_gff = ch_genes_gff.mix(SPALN_ALIGN_MODELS.out.gff)
    }

    //
    // SUBWORKFLOW: Align RNAseq reads
    //
    if (params.rnaseq_samples) {
       RNASEQ_ALIGN(
          ASSEMBLY_PREPROCESS.out.fasta.collect(),
          ch_samplesheet
       )
       // 
       // MODULE: Merge all BAM files
       //
       RNASEQ_ALIGN.out.bam.map{ meta, bam ->
        new_meta = [:]
        new_meta.id = meta.ref
        tuple(new_meta,bam)
       }.groupTuple(by:[0])
       .set{bam_mapped}

       //
       // MODULE: Merge BAM files
       //
       SAMTOOLS_MERGE(
          bam_mapped
       )
       AUGUSTUS_BAM2HINTS(
          SAMTOOLS_MERGE.out.bam,
          params.pri_rnaseq
       )
       ch_hints = ch_hints.mix(AUGUSTUS_BAM2HINTS.out.gff)
       ch_versions = ch_versions.mix(RNASEQ_ALIGN.out.versions.first(),AUGUSTUS_BAM2HINTS.out.versions,SAMTOOLS_MERGE.out.versions)

       //
       // SUBWORKFLOW: Assemble transcripts using Trinity and align to genome
       //
       if (params.trinity) {
          TRINITY_GENOMEGUIDED(
             SAMTOOLS_MERGE.out.bam,
             params.max_intron_size
          )
          ch_transcripts = ch_transcripts.mix(TRINITY_GENOMEGUIDED.out.fasta)
          ch_versions = ch_versions.mix(TRINITY_GENOMEGUIDED.out.versions)
       }
    }

    //
    // SUBWORKFLOW: Align transcripts to the genome
    //
    if (params.transcripts || params.trinity) {
       MINIMAP_ALIGN_TRANSCRIPTS(
          ASSEMBLY_PREPROCESS.out.fasta.collect(),
          ch_transcripts
       )
       ch_versions = ch_versions.mix(MINIMAP_ALIGN_TRANSCRIPTS.out.versions)
       ch_transcripts_gff = ch_transcripts_gff.mix(MINIMAP_ALIGN_TRANSCRIPTS.out.gff)
       ch_hints = ch_hints.mix(MINIMAP_ALIGN_TRANSCRIPTS.out.hints)
    }

    //
    // SUBWORKFLOW: Assemble transcripts into gene models
    //
    if (params.pasa) {
        PASA_PIPELINE(
           ASSEMBLY_PREPROCESS.out.fasta,
           ch_transcripts
        )
        ch_versions = ch_versions.mix(PASA_PIPELINE.out.versions)
        ch_genes_gff = ch_genes_gff.mix(PASA_PIPELINE.out.gff)
    }

    //
    // SUBWORKFLOW: Train augustus prediction model
    //
    if (params.aug_training) {

       if (params.proteins_targeted) {
          AUGUSTUS_TRAINING(
             SPALN_ALIGN_MODELS.out.gff
          )
          ch_aug_config_final = AUGUSTUS_TRAINING.out.aug_config_folder             
       } else if (params.pasa) {
          AUGUSTUS_TRAINING(
             PASA_PIPELINE.out.gff_training
          )
          ch_aug_config_final = AUGUSTUS_TRAINING.out.aug_config_folder
       }

    } else {
       ch_aug_config_final = ch_aug_config_folder
    }

    //
    // SUBWORKFLOW: Predict gene models using AUGUSTUS
    //
    all_hints = ch_hints.unique().collectFile(name: 'hints.gff')

    AUGUSTUS_PIPELINE(
       REPEATMASKER.out.fasta,
       all_hints,
       ch_aug_config_folder,
       ch_aug_extrinsic_cfg,
    )
    ch_versions = ch_versions.mix(AUGUSTUS_PIPELINE.out.versions)
    ch_genes_gff = ch_genes_gff.mix(AUGUSTUS_PIPELINE.out.gff)

    //
    // SUBWORKFLOW: Consensus gene building with EVM
    //
    if (params.evm) {
       EVM(
          REPEATMASKER.out.fasta,
          ch_genes_gff.map { m,g -> g },
          ch_proteins_gff.map {m,p -> p },
          ch_transcripts_gff.map { m,t -> t},
          ch_evm_weights
       )
    }

    //
    // MODULE: Collect all software versions
    //

    CUSTOM_DUMPSOFTWAREVERSIONS (
        ch_versions.unique().collectFile(name: 'collated_versions.yml')
    )

    //
    // MODULE: MultiQC
    //
    workflow_summary    = WorkflowEsga.paramsSummaryMultiqc(workflow, summary_params)
    ch_workflow_summary = Channel.value(workflow_summary)

    ch_multiqc_files = Channel.empty()
    ch_multiqc_files = ch_multiqc_files.mix(Channel.from(ch_multiqc_config))
    ch_multiqc_files = ch_multiqc_files.mix(ch_multiqc_custom_config.collect().ifEmpty([]))
    ch_multiqc_files = ch_multiqc_files.mix(ch_workflow_summary.collectFile(name: 'workflow_summary_mqc.yaml'))
    ch_multiqc_files = ch_multiqc_files.mix(CUSTOM_DUMPSOFTWAREVERSIONS.out.mqc_yml.collect())

    MULTIQC (
        ch_multiqc_files.collect()
    )
    multiqc_report = MULTIQC.out.report.toList()
    ch_versions    = ch_versions.mix(MULTIQC.out.versions)
}

/*
========================================================================================
    COMPLETION EMAIL AND SUMMARY
========================================================================================
*/

workflow.onComplete {
    if (params.email || params.email_on_fail) {
        NfcoreTemplate.email(workflow, params, summary_params, projectDir, log, multiqc_report)
    }
    NfcoreTemplate.summary(workflow, params, log)
}

/*
========================================================================================
    THE END
========================================================================================
*/

