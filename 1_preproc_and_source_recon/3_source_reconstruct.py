"""Source reconstruction: forward modelling, beamforming and parcellation.

Note, before this script is run the /coreg directory created by coregister.py
must be copied and renamed to /src.
"""

import pathlib
from glob import glob
from dask.distributed import Client

from osl import source_recon, utils

# Directories
PREPROC_DIR = "data/preproc"
SRC_DIR = "data/src"

# Files
PREPROC_FILE = (
    PREPROC_DIR
    + "/mf2pt2_{subject}_ses-rest_task-rest_meg"
    + "/mf2pt2_{subject}_ses-rest_task-rest_meg_preproc_raw.fif"
)

# Settings
config = """
    source_recon:
    - forward_model:
        model: Single Layer
    - beamform_and_parcellate:
        freq_range: [1, 80]
        chantypes: [mag, grad]
        rank: {meg: 60}
        parcellation_file: Glasser52_binary_space-MNI152NLin6_res-8x8x8.nii.gz
        method: spatial_basis
        orthogonalisation: symmetric
"""

if __name__ == "__main__":
    utils.logger.set_up(level="INFO")

    # Get subjects
    subjects = []
    for subject in sorted(glob(PREPROC_FILE.format(subject="*"))):
        subjects.append(pathlib.Path(subject).stem.split("_")[1])

    # Setup files
    preproc_files = []
    for subject in subjects:
        preproc_files.append(PREPROC_FILE.format(subject=subject))

    # Setup parallel processing
    client = Client(n_workers=16, threads_per_worker=1)

    # Run beamforming and parcellation
    source_recon.run_src_batch(
        config,
        src_dir=SRC_DIR,
        subjects=subjects,
        preproc_files=preproc_files,
        gen_report=False,
        dask_client=True,
    )
