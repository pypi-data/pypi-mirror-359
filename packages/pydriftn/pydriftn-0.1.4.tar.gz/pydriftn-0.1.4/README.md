# pydriftn - The Microlensing Driftscan Project

Driftscan techniques have not been widely used so far for fast photometry, and a fair amount of development of new techniques has been required to extract photometric time series with sub-arcsecond sampling from photometric data.
The functions presented in this repository are designed to accomplish the drift scan time series extraction, and work on a single selected field of interest without dithering patterns.

For this science case, the input to the pipeline is two pointed optical colour images of a field (in this case DECam g and r-band images) and a series of 20 second rapid-cadence (VR) images of the field with a constant drift rate in Declination. 
The output is a catalogue of light curves for stars across the field, with brightness measurements subsampled along the drifted image, producing an effective candence much shorter than the exposure duration. 
The driftscan image, or DSI, can be searched for sub-second transient signals. The Driftscan techique is especially powerful in searching for very short duration microlensing signals produced by a population of asteroid-mas primordial black holes.

Other science applications include the ability to screen for milli-second optical transient phenomena (e.g counterparts to GRBs, FRBs) by distinguishing between DSI trails from field stars, and point sources from out-of-nowhere signals.


## Contents

1. Main Catalogue Generation in GenerateCatalogue.py
   
Generates a deep catalogue from pointed g, r images from the sky. Use is for linking coordinates of DSIs, WCS corrections across the detector plane.
Finds a number of bright, isolated reference stars per CCD chip. Use is for WCS corrections and measuring DSI singal-to-noise contamination from atmospheric seeing.

2. DSI centroiding in DriftAstrom.py
   
Locates the centroids of DSI on CCD chip by convolution with a DSI template and centroiding function. Centroids are matched to reference stars to WCS correct each exposure for tangent plane distortions. 

3. Sky value estimation in DriftSkysub.py 

4. DSI extraction in DriftExtract.py
   
Extraction function is run on all located DSI, and then matched to reference star with the most similar drift patten. The best match reference star is used to normalise out atmospheric seeing pattens in the DSI.

5. Point Source detection in DriftClassify.py WORK IN PROGRESS
    
Uses the reference catalgoue and the DSI shape to distinguish between drifted stars, millisecond optical transients and other phenomena (like satellites)

6. Drift Recalibration of Astrometry WORK IN PROGRESS


## Getting Started
Python 3.x is needed to run the pipeline.
To install the required packages, run:
```
python3 -m build
```
Alternatively, run:
```
pip3 install -r requirements.txt
```

## Data
The 10-night DECam data is stored in Data Central and NOIRLab.
Access to data is TBD.

## Docker development environment
1. Edit Dockerfile to have user account details (UID and GID) to match the user on your system. You would need to run `echo $UID` on your local terminal, then copy and paste the output UID into the Dockerfile.
2. Run `sh build.sh`
3. Edit `load.sh` to your liking, especially the `source` part. You may remove ~/.vimrc from the mounts
4. Run `sh load.sh`
5. Develop as usual.

## Building the documentation
- Requires sphinx
- In the Docker environment run:
```
pip install . --break-system-packages
cd docs
make html
```

## Demo
## Running GenerateCatalogue.py
Example Python code:
```
from pydriftn.GenerateCatalogue import Cataloguer

cat_generator = Cataloguer(g_path, r_path, ccd_names, output_path)
catalogue = cat_generator.generate_whole_catalogue()
```

### Running the pipeline
Example parameters are stored in `demo/demo_values.yaml`.
You can create and use a different one that suits your purpose.

To run:
```
cd src
python3 demo.py -y /path/to/values/yaml
```
This script currently ignores `GenerateCatalogue.py` and uses an existing master catalogue in `demo`.

Expected output:
1. `demo/{your_output_path}/driftastrom-exp_{exposure_number}.csv` - output of DriftAstrometry.
2. `demo/{your_output_path}/driftskysub-exp_{exposure_number}.csv` - output of SkyEstimator.
3. `demo/{your_output_path}/'driftextract-exp_{exposure_number}.csv` - output of TimeSeriesGenerator. If you give `read_targets: True` and specify target stars in the values yaml, the script will only do the extraction for the target stars that can be found in the specified CCD(s) in your data. The path will change to be `demo/{your_output_path}/'target-driftextract-exp_{exposure_number}.csv`.
4. `demo/{your_output_path}/{your_pdf_output_path}.pdf` - plots.
5. `demo/{your_output_path}/{your_pdf_output_path}-median.pdf` - plot of medians of drifts (if number of drifts files > 1).

Note: you will get (1), (2), and (3) for each drift file you have but only one pdf plot each, i.e., (4) and (5) as a summary. 

You may want to change the `drifts_dirs` list in the yaml file to point to your data.
Keep the list template even when there is only one directory.

If you set `read_mask` to be `True`, `src/demo.py` script will look for a dqmask FITS file for each drift image file in the input directory, based on the indicating keywords given.
You will then get an additional column in the csv outputs indicating whether the star was affected by cosmic ray or not.
In Data Central cloud, we saved the drift images as `c4d_2021B0023-exp_{exposure_number}-image.fits` and the dqmask files as `c4d_2021B0023-exp_{exposure_number}-dqmask.fits`, hence we put 'image' as the `img_keyword` and 'dqmask' as the `mask_keyword`. Change these values as needed. 

The demo script will generate one page in the full extractions PDF output for each of this drift directory,
and one plot for each drift directory in the median extractions PDF output.
Inside the root/parent output directory, the output CSV files will also be sorted into child directories with names matching these `drifts_dirs`.

For example, if you have
```
drifts_dirs:
  - /data/night_1/
  - /data/night_2/
```

And have
```
output_dir: 'demo/output'
```

You will get 
```
demo
  - output
      - night_1
          - driftastrom-exp_{exposure_number}.csv
          - driftskysub-exp_{exposure_number}.csv
          - driftextract-exp_{exposure_number}.csv
          ( * the number of drift files in night_1 directory )
      - night_2
          - driftastrom-exp_{exposure_number}.csv
          - driftskysub-exp_{exposure_number}.csv
          - driftextract-exp_{exposure_number}.csv
          ( * the number of drift files in night_2 directory )
      - demo-extractions.pdf
      - demo-extractions-median.pdf     
```

This demo code utilises multiprocessing to optimise the process. The number of worker is left blank, you could use up to 30 workers if running on dccompute4 in Data Central.

### Notebooks
There are two notebooks to help you play around with the functions in the pipeline, without needing to run the pipeline from end to end. The notebooks only run on a single input as they are meant for investigation. You would need to change the filepaths to point to your files.
1. src/sandbox/generate_catalogue_notebook.ipynb with functions from GenerateCatalogue.py, broken into executable cells, with added visualisations of what's being done at each step. The notebook only processes one CCD from one exposure at a time. 
2. src/sandbox/drift_astrom_skysub_extract.ipynb with functions from DriftAstrom.py, DriftSkysub.py and DriftExtracct.py - also broken into executable cells and has added output visualisations. The notebook only processes one target star from one CCD and one exposure at a time. 

### Sample OGLE catalogue
`demo/ogle_rr_lyrae.csv` was obtained from combining [these tables](https://vizier.cds.unistra.fr/viz-bin/VizieR-3?-source=J/AcA/66/131&-out.max=50&-out.form=HTML%20Table&-out.add=_r&-out.add=_RAJ,_DEJ&-sort=_r&-oc.form=sexa).

## Work in Progress
1. Saving new WCS (DriftAstrom.py),
2. Adding sum functionality to cosmic ray masking function (DriftAstrom.py),
3. Saving annulus data (DriftSkysub.py),
4. Bug fixes for the fitting function (DriftExtract.py) - this includes the unexpected zero median for some of the normalised drift arrays,
5. Suggestion for proof of concept: generate synthetic data with microlensing events injected to see whether the pipeline can recover them.
6. Centroid IDs and Reference Star IDs in DriftAstrom, DriftSkysub and DriftExtract output may not be consistent across various exposures. The current workaround is to provide a target list whose coordinates act as a central reference to crossmatch between exposures (provided that the list is not too crowded). One way to improve this is through improving the matching between the stars in the pointed catalogue and the drifts. The algorithm may be more iterative (e.g. find a global systematic shift/offset first) and include other factors than just the spatial positions (e.g. the brightnesses), especially in more crowded fields. ![drifts_vs_pointed](demo/pointed_vs_drift.png)
