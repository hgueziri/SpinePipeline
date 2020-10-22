import itk
import sys
import numpy as np

"""This pipeline prepares pre-operative CT images for the registration framework in IBIS. Specifically, the pipeline:
    * Rotate MINC image to be RAS to be visualized properly in IBIS
    * [TODO] Create a segmentation image of the posterior surface of the vertebra 
"""

if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit(0)

    inputFilename = sys.argv[1]
    outputFilename = sys.argv[2]

    mincTransform = np.eye(3)
    mincTransform[0, 0] = -1
    mincTransform[1, 1] = -1

    ImageType = itk.Image[itk.F, 3]
    ReaderType = itk.ImageFileReader[ImageType]
    reader = ReaderType.New()
    reader.SetFileName(inputFilename)
    try:
        reader.Update()
    except:
        print('Cannot read file ' + inputFilename)
    inputVolume = reader.GetOutput()

    outputVolume = ImageType.New()
    outputVolume.SetSpacing(inputVolume.GetSpacing())
    inputOrigin = inputVolume.GetOrigin()

    offsetOrigin = itk.Point[itk.D, 3]()

    for x in range(3):
        offsetOrigin[x] = inputVolume.GetLargestPossibleRegion().GetSize()[x] * inputVolume.GetSpacing()[x]
    offsetOrigin[2] = 0
    outputOrigin = np.dot( mincTransform, np.array(offsetOrigin) ) + np.array(inputOrigin)

    outputVolume.SetOrigin(outputOrigin)

    MatrixType = itk.Matrix[itk.D, 3, 3]
    mincItkTransform = MatrixType()
    mincItkTransform.SetIdentity()
    outputVolume.SetDirection(mincItkTransform)

    inputRegion = inputVolume.GetLargestPossibleRegion()
    outputVolume.SetRegions(inputRegion)
    outputVolume.Allocate()

    inputSize = inputRegion.GetSize()
    for x in range(inputSize[0]):
        for y in range(inputSize[1]):
            for z in range(inputSize[2]):
                index = [x, y, z]
                v = inputVolume.GetPixel(index)
                index = [inputSize[0] - x, inputSize[1] - y, z]
                outputVolume.SetPixel(index, v)

    WriterType = itk.ImageFileWriter[ImageType]
    writer = WriterType.New()
    writer.SetFileName(outputFilename)
    writer.SetInput(outputVolume)
    try:
        writer.Update()
    except:
        print('Cannot write file ' + outputFilename)
        exit(0)

    # print('done.')
    



