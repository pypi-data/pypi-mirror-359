import npsam as ns

files = [
    'Ag_HAADF.png',
]
s = ns.NPSAM(files)

s.set_scaling('1.0 px')

for im in s:
    im.import_segmentation_from_image('Ag_HAADF_Phansalkar_r15.png')

