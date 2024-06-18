from dataclasses import dataclass
from enum import Enum
import os
import subprocess
import requests
import shutil
from pathlib import Path
import typing
import typing_extensions

from latch.resources.workflow import workflow
from latch.resources.tasks import nextflow_runtime_task, custom_task
from latch.types.file import LatchFile
from latch.types.directory import LatchDir, LatchOutputDir
from latch.ldata.path import LPath
from latch_cli.nextflow.workflow import get_flag
from latch_cli.nextflow.utils import _get_execution_name
from latch_cli.utils import urljoins
from latch.types import metadata
from flytekit.core.annotation import FlyteAnnotation

from latch_cli.services.register.utils import import_module_by_path

meta = Path("latch_metadata") / "__init__.py"
import_module_by_path(meta)
import latch_metadata

@custom_task(cpu=0.25, memory=0.5, storage_gib=1)
def initialize() -> str:
    token = os.environ.get("FLYTE_INTERNAL_EXECUTION_ID")
    if token is None:
        raise RuntimeError("failed to get execution token")

    headers = {"Authorization": f"Latch-Execution-Token {token}"}

    print("Provisioning shared storage volume... ", end="")
    resp = requests.post(
        "http://nf-dispatcher-service.flyte.svc.cluster.local/provision-storage",
        headers=headers,
        json={
            "storage_gib": 100,
        }
    )
    resp.raise_for_status()
    print("Done.")

    return resp.json()["name"]






@nextflow_runtime_task(cpu=4, memory=8, storage_gib=100)
def nextflow_runtime(pvc_name: str, assembly: LatchFile, outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], multiqc_title: typing.Optional[str], rnaseq_samples: typing.Optional[LatchFile], proteins: typing.Optional[LatchFile], proteins_targeted: typing.Optional[LatchFile], transcripts: typing.Optional[LatchFile], rm_lib: typing.Optional[LatchFile], references: typing.Optional[LatchFile], max_intron_size: typing.Optional[int], rm_species: typing.Optional[str], rm_db: typing.Optional[LatchFile], busco_lineage: typing.Optional[str], busco_db_path: typing.Optional[str], aug_species: typing.Optional[str], aug_config_dir: typing.Optional[str], aug_extrinsic_cfg: typing.Optional[str], spaln_taxon: typing.Optional[str], trinity: typing.Optional[bool], pasa: typing.Optional[bool], evm: typing.Optional[bool], ncrna: typing.Optional[bool], npart_size: typing.Optional[int], min_contig_size: typing.Optional[int], dummy_gff: typing.Optional[str], aug_options: typing.Optional[str], aug_config_container: typing.Optional[str], aug_chunk_length: typing.Optional[int], aug_training: typing.Optional[bool], pri_prot: typing.Optional[int], pri_prot_target: typing.Optional[int], pri_est: typing.Optional[int], pri_rnaseq: typing.Optional[int], pri_wiggle: typing.Optional[int], pri_trans: typing.Optional[int], t_est: typing.Optional[str], t_prot: typing.Optional[str], t_rnaseq: typing.Optional[str], spaln_options: typing.Optional[str], spaln_protein_id: typing.Optional[int], min_prot_length: typing.Optional[int], nproteins: typing.Optional[int], spaln_q: typing.Optional[int], spaln_protein_id_targeted: typing.Optional[int], pasa_nmodels: typing.Optional[int], pasa_config_file: typing.Optional[str], evm_weights: typing.Optional[str], nevm: typing.Optional[int]) -> None:
    try:
        shared_dir = Path("/nf-workdir")



        ignore_list = [
            "latch",
            ".latch",
            "nextflow",
            ".nextflow",
            "work",
            "results",
            "miniconda",
            "anaconda3",
            "mambaforge",
        ]

        shutil.copytree(
            Path("/root"),
            shared_dir,
            ignore=lambda src, names: ignore_list,
            ignore_dangling_symlinks=True,
            dirs_exist_ok=True,
        )

        cmd = [
            "/root/nextflow",
            "run",
            str(shared_dir / "main.nf"),
            "-work-dir",
            str(shared_dir),
            "-profile",
            "docker",
            "-c",
            "latch.config",
                *get_flag('assembly', assembly),
                *get_flag('outdir', outdir),
                *get_flag('email', email),
                *get_flag('multiqc_title', multiqc_title),
                *get_flag('rnaseq_samples', rnaseq_samples),
                *get_flag('proteins', proteins),
                *get_flag('proteins_targeted', proteins_targeted),
                *get_flag('transcripts', transcripts),
                *get_flag('rm_lib', rm_lib),
                *get_flag('references', references),
                *get_flag('npart_size', npart_size),
                *get_flag('max_intron_size', max_intron_size),
                *get_flag('min_contig_size', min_contig_size),
                *get_flag('rm_species', rm_species),
                *get_flag('rm_db', rm_db),
                *get_flag('busco_lineage', busco_lineage),
                *get_flag('busco_db_path', busco_db_path),
                *get_flag('dummy_gff', dummy_gff),
                *get_flag('aug_species', aug_species),
                *get_flag('aug_options', aug_options),
                *get_flag('aug_config_container', aug_config_container),
                *get_flag('aug_config_dir', aug_config_dir),
                *get_flag('aug_extrinsic_cfg', aug_extrinsic_cfg),
                *get_flag('aug_chunk_length', aug_chunk_length),
                *get_flag('aug_training', aug_training),
                *get_flag('pri_prot', pri_prot),
                *get_flag('pri_prot_target', pri_prot_target),
                *get_flag('pri_est', pri_est),
                *get_flag('pri_rnaseq', pri_rnaseq),
                *get_flag('pri_wiggle', pri_wiggle),
                *get_flag('pri_trans', pri_trans),
                *get_flag('t_est', t_est),
                *get_flag('t_prot', t_prot),
                *get_flag('t_rnaseq', t_rnaseq),
                *get_flag('spaln_taxon', spaln_taxon),
                *get_flag('spaln_options', spaln_options),
                *get_flag('spaln_protein_id', spaln_protein_id),
                *get_flag('min_prot_length', min_prot_length),
                *get_flag('nproteins', nproteins),
                *get_flag('spaln_q', spaln_q),
                *get_flag('spaln_protein_id_targeted', spaln_protein_id_targeted),
                *get_flag('pasa_nmodels', pasa_nmodels),
                *get_flag('pasa_config_file', pasa_config_file),
                *get_flag('evm_weights', evm_weights),
                *get_flag('nevm', nevm),
                *get_flag('trinity', trinity),
                *get_flag('pasa', pasa),
                *get_flag('evm', evm),
                *get_flag('ncrna', ncrna)
        ]

        print("Launching Nextflow Runtime")
        print(' '.join(cmd))
        print(flush=True)

        env = {
            **os.environ,
            "NXF_HOME": "/root/.nextflow",
            "NXF_OPTS": "-Xms2048M -Xmx8G -XX:ActiveProcessorCount=4",
            "K8S_STORAGE_CLAIM_NAME": pvc_name,
            "NXF_DISABLE_CHECK_LATEST": "true",
        }
        subprocess.run(
            cmd,
            env=env,
            check=True,
            cwd=str(shared_dir),
        )
    finally:
        print()

        nextflow_log = shared_dir / ".nextflow.log"
        if nextflow_log.exists():
            name = _get_execution_name()
            if name is None:
                print("Skipping logs upload, failed to get execution name")
            else:
                remote = LPath(urljoins("latch:///your_log_dir/nf_nf_core_genomeannotator", name, "nextflow.log"))
                print(f"Uploading .nextflow.log to {remote.path}")
                remote.upload_from(nextflow_log)



@workflow(metadata._nextflow_metadata)
def nf_nf_core_genomeannotator(assembly: LatchFile, outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], multiqc_title: typing.Optional[str], rnaseq_samples: typing.Optional[LatchFile], proteins: typing.Optional[LatchFile], proteins_targeted: typing.Optional[LatchFile], transcripts: typing.Optional[LatchFile], rm_lib: typing.Optional[LatchFile], references: typing.Optional[LatchFile], max_intron_size: typing.Optional[int], rm_species: typing.Optional[str], rm_db: typing.Optional[LatchFile], busco_lineage: typing.Optional[str], busco_db_path: typing.Optional[str], aug_species: typing.Optional[str], aug_config_dir: typing.Optional[str], aug_extrinsic_cfg: typing.Optional[str], spaln_taxon: typing.Optional[str], trinity: typing.Optional[bool], pasa: typing.Optional[bool], evm: typing.Optional[bool], ncrna: typing.Optional[bool], npart_size: typing.Optional[int] = 200000000, min_contig_size: typing.Optional[int] = 5000, dummy_gff: typing.Optional[str] = 'PIPELINE_BASE/assets/empty.gff3', aug_options: typing.Optional[str] = '--alternatives-from-evidence=on --minexonintronprob=0.08 --minmeanexonintronprob=0.4 --maxtracks=3', aug_config_container: typing.Optional[str] = '/usr/local/config', aug_chunk_length: typing.Optional[int] = 3000000, aug_training: typing.Optional[bool] = False, pri_prot: typing.Optional[int] = 3, pri_prot_target: typing.Optional[int] = 5, pri_est: typing.Optional[int] = 4, pri_rnaseq: typing.Optional[int] = 4, pri_wiggle: typing.Optional[int] = 2, pri_trans: typing.Optional[int] = 4, t_est: typing.Optional[str] = 'E', t_prot: typing.Optional[str] = 'P', t_rnaseq: typing.Optional[str] = 'E', spaln_options: typing.Optional[str] = '-M', spaln_protein_id: typing.Optional[int] = 60, min_prot_length: typing.Optional[int] = 35, nproteins: typing.Optional[int] = 200, spaln_q: typing.Optional[int] = 5, spaln_protein_id_targeted: typing.Optional[int] = 90, pasa_nmodels: typing.Optional[int] = 1000, pasa_config_file: typing.Optional[str] = 'PIPELINE_BASE/assets/pasa/alignAssembly.config', evm_weights: typing.Optional[str] = 'None', nevm: typing.Optional[int] = 10) -> None:
    """
    nf-core/genomeannotator

    Sample Description
    """

    pvc_name: str = initialize()
    nextflow_runtime(pvc_name=pvc_name, assembly=assembly, outdir=outdir, email=email, multiqc_title=multiqc_title, rnaseq_samples=rnaseq_samples, proteins=proteins, proteins_targeted=proteins_targeted, transcripts=transcripts, rm_lib=rm_lib, references=references, npart_size=npart_size, max_intron_size=max_intron_size, min_contig_size=min_contig_size, rm_species=rm_species, rm_db=rm_db, busco_lineage=busco_lineage, busco_db_path=busco_db_path, dummy_gff=dummy_gff, aug_species=aug_species, aug_options=aug_options, aug_config_container=aug_config_container, aug_config_dir=aug_config_dir, aug_extrinsic_cfg=aug_extrinsic_cfg, aug_chunk_length=aug_chunk_length, aug_training=aug_training, pri_prot=pri_prot, pri_prot_target=pri_prot_target, pri_est=pri_est, pri_rnaseq=pri_rnaseq, pri_wiggle=pri_wiggle, pri_trans=pri_trans, t_est=t_est, t_prot=t_prot, t_rnaseq=t_rnaseq, spaln_taxon=spaln_taxon, spaln_options=spaln_options, spaln_protein_id=spaln_protein_id, min_prot_length=min_prot_length, nproteins=nproteins, spaln_q=spaln_q, spaln_protein_id_targeted=spaln_protein_id_targeted, pasa_nmodels=pasa_nmodels, pasa_config_file=pasa_config_file, evm_weights=evm_weights, nevm=nevm, trinity=trinity, pasa=pasa, evm=evm, ncrna=ncrna)

