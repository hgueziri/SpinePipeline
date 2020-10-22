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

    if len(sys.argv) > 3:
        threshold = float(sys.argv[3])
    else:
        threshold = 150

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
    outputVolume.SetOrigin(inputVolume.GetOrigin())
    outputVolume.SetDirection(inputVolume.GetDirection())
    inputRegion = inputVolume.GetLargestPossibleRegion()
    outputVolume.SetRegions(inputRegion)
    outputVolume.Allocate()
    outputVolume.FillBuffer(0)

    smoothFilter = itk.SmoothingRecursiveGaussianImageFilter[ImageType, ImageType].New()
    smoothFilter.SetInput(inputVolume)
    smoothFilter.SetSigma(1.0)

    BinaryThresholdImageFilterType = itk.BinaryThresholdImageFilter[ImageType, ImageType]
    vertebraThresholdFilter = BinaryThresholdImageFilterType.New()
    vertebraThresholdFilter.SetInput(smoothFilter.GetOutput())
    vertebraThresholdFilter.SetUpperThreshold(threshold) ## threshold at 150 H.U.
    vertebraThresholdFilter.SetInsideValue(0)
    vertebraThresholdFilter.SetOutsideValue(1)
    vertebraThresholdFilter.Update()

    vertebraImage = vertebraThresholdFilter.GetOutput()

    """ Posterior surface extraction with vertical raycasting
    inputSize = inputRegion.GetSize()
    for z in range(inputSize[2]):
        for x in range(inputSize[0]):
            line = []
            coords = []
            found = False
            for y in range(inputSize[1]-1, -1, -1):
                index = [x, y, z]
                v = vertebraImage.GetPixel(index)
                line.append(v)
                coords.append(index)
                if v > 0:
                    found = True
            if found:
                idelem = np.argmax(line)
                index = coords[idelem]
                outputVolume.SetPixel(index, 1)
    #"""

    inputSize = inputRegion.GetSize()
    probeSize = 40 / inputVolume.GetSpacing()[0] # mm
    xmid = inputSize[0] / 2.0
    leftProbeIndex = xmid - int( probeSize / 2)
    rightProbeIndex = xmid + int( probeSize / 2)
    for z in range(inputSize[2]):
        for probeTip in [leftProbeIndex, rightProbeIndex]:
            indexTip = [probeTip, int(inputSize[1] * 0.95), z]
            for xi in range(inputSize[0]):
                index = [xi, int(inputSize[1] * 0.2), z]
                path = itk.PolyLineParametricPath[3].New()
                path.Initialize()
                path.AddVertex(indexTip)
                path.AddVertex(index)
                found = False
                t = 0
                while (not found) and (t <= 1):
                    continuousIndex = path.Evaluate(t)
                    imageIndex = [ int(round(continuousIndex[i])) for i in range(3) ]
                    if inputRegion.IsInside(imageIndex):
                        v = vertebraImage.GetPixel(imageIndex)
                        t = t + 0.002
                        if v > 0:
                            found = True
                    else:
                        break
                if found:
                    outputVolume.SetPixel(imageIndex, 1)

    DistanceFilterType = itk.SignedMaurerDistanceMapImageFilter[ImageType, ImageType]
    distanceFilter = DistanceFilterType.New()
    distanceFilter.SetInput(outputVolume)
    distanceFilter.SetBackgroundValue(0)

    # BinaryThresholdImageFilterType = itk.BinaryThresholdImageFilter[ImageType, ImageType]
    thresholdFilter = BinaryThresholdImageFilterType.New()
    thresholdFilter.SetInput(distanceFilter.GetOutput())
    thresholdFilter.SetLowerThreshold(-0.4)
    thresholdFilter.SetUpperThreshold(0.4)
    thresholdFilter.SetInsideValue(1)
    thresholdFilter.SetOutsideValue(0)
    thresholdFilter.Update()


    WriterType = itk.ImageFileWriter[ImageType]
    writer = WriterType.New()
    writer.SetFileName(outputFilename)
    writer.SetInput(thresholdFilter.GetOutput())
    # writer.SetInput(outputVolume)
    try:
        writer.Update()
    except:
        print('Cannot write file ' + outputFilename)
        exit(0)

    # print('done.')

#"""

