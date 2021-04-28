# Handling MALDI-TOF data
## Overview
The MALDI-TOF instrument is connected and operated through a desktop computer. Spectrum generated by the MALDI-TOF is stored
on this computer in the following directory:

```text
D:/data/MaldiBiotyperRealTimeClassification/
```

Each directory in the above path represents a project and is named with the project's uid (note: this is distinct from the
project's name, which is user specified). A project directory contains individual directories for each analyte. Analyte
directories are similarly named with the analyte uid. The following is a visual of the layout:

```text
./MaldiBiotyperRealTimeClassification/
├── 10c34631-9737-45fb-9ffe-d9c5d467e7aa        # project dir
│   ├── 1fb112e2-54cf-430e-afca-e594b923f2a7    # analyte dirs
│   ├── 32a3177c-1c9b-41f7-8706-a5aecc20a8dc

                ...

│   └──562dc9bd-6d83-4059-8192-c8f3b1475590
└── ea3a17f1-9cee-4e59-adfc-182dd55d58f0        # project dir
    ├── 010f73b4-b2a5-4267-bbae-c2ab2f8759cf    # analyte dirs
    ├── 04a7957b-77ff-4df0-bea0-9f20caccb01b

                ...

    └── 080bd328-9467-44d0-ab3a-47fed8ae0cb6
```

Each analyte directory contains the same set of files, most of which specify the configuration and parameters of the
instrument at the time of generating spectrum. The two most important files are `fid` and `acqu` - these files encode
intensity values and information to calculate m/z, respectively. Here are the location of these files for an analyte:
```text
./ae9802cd-88ea-4c9c-8e3e-3e3116360a04      # project dir
└── fa2a5b19-ec84-41da-b231-5d25d529838a    # analyte dir
    └── 0_B9                                # spot
        └── 1
            └── 1SLin
                ├── acqu
                └── fid
```

For each project there is one final important file, the `runInfo.json` file. This file contains information about the project
and analytes such as sample name, which we use to match the spectrum data to sample records. The `runInfo.json` is located
here:
```text
./ae9802cd-88ea-4c9c-8e3e-3e3116360a04      # project dir
└── runInfo.json
```


## Obtaining the spectra
Collecting sample spectra from the MALDI-TOF is simply done by copying project directories to external media from following
directory on the instrument computer:
```text
D:/data/MaldiBiotyperRealTimeClassification/
```

Transferring spectra data can be slow as there are many small files to be copied. Moreover, the above directory contains all
historical spectra. I recommend zip-compressing only relevant project directories prior to copying to external media. I
previously did this by relying on directory creation date. However this isn't always possible and project directories are
named with uids, so sometimes it is more efficient to copy the entire directory and extract target sample spectrum later. The
below sections describe the process of extracting target spectra.


## The runInfo.json file
Each project directory has a `runInfo.json` file that contains information relating to the project as well as each analyte.
The data is formatted as json with the following structure:
```text
{
  "ProjectUid": "ae9802cd-88ea-4c9c-8e3e-3e3116360a04",
  "ProjectName": "KPN_sample_run",
  "ProjectType": "BioTyperMeasurement",
  "TargetId": "1011022437",
  "Analytes": [
      {
      "AnalyteUid": "46790822-eef7-43f2-a351-6a9f0727f320",
      "AnalyteId": "KPN001",
      "AnalyteType": "Sample",
      "Spot": "A1:0",
      "SpectrumUid": "127dc178-a366-4e89-b583-c14a57e8bb2b",
      "Context": "id",
      "SubPath": "46790822-eef7-43f2-a351-6a9f0727f320\\0_A1\\1",
      "MsblMethod": null,
      "Antibiotic": null
    },

    <further analyte records>

  ]
}
```

Here we can see that `ProjectUid` relates to the project directory name and `AnalyteUid` to the analyte directory name. The
`ProjectName` and `AnalyteId` variables contain user-entered values for these (i.e. the actual project name and
analyte/sample identifier). Other important variables in the analyte record are `SubPath` and `SpectrumUid`. The `SubPath`
variable is useful to easily obtain the directory of the spectrum files. I generally use the `SpectrumUid` as the primary
identifier for the spectrum data.


## Matching sample records with spectra
Spectrum data can be matched to existing sample data through the `AnalyteId` variable from the `runInfo.json` file:
```text
Sample data <-> AnalyteId <-> Spectrum data
```

The `scripts/match_spectra.py` script demonstrates the basic process of matching identifiers, and this involves:
1. reading sample data and `runInfo.json` data into memory
2. discovering matching sample data identifiers and `AnalyteUid`
3. writing out matched data
4. copying matched spectra to an output directory

To run this script, execute:
```bash
mkdir -p output/
scripts/match_spectra.py \
    --sample_sheet_fp data/sample_data.tsv \
    --spectra_dir data/spectra/ \
    --output_dir output/
```

The output directory will contain the matched spectra and a datasheet with matched sample information.
